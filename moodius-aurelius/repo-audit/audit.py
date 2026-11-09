#!/usr/bin/env python3
"""Moodius repo audit. Reports first; changes only what the owner ticks.

    python3 audit.py scan  [--out report.md] [--previous old-issue.md] [--open-pr-branches prs.txt]
    python3 audit.py apply --body issue.md [--summary summary.md] [--branches-out branches.txt] [--dry-run]

scan writes a Markdown checklist (the weekly issue body). Every actionable line ends with a hidden
marker <!-- audit:<action>:<path in base64> -->. apply reads an issue body, takes only the ticked
lines, re-checks each one against the repo as it is now, and then:
  archive        git mv to moodius-aurelius/_archive/ (same sub-path) and log it in _archive/MOVED.csv
  delete         git rm a byte-identical duplicate (only if another copy still exists)
  scrub          replace personal terms (AUDIT_PERSONAL_TERMS) and private emails in that file
  delete-branch  writes the branch to --branches-out; the workflow deletes it and logs its last commit
Stdlib only. Run from the repo root (or anywhere inside the repo).
"""
import argparse, base64, csv, datetime as dt, fnmatch, glob, hashlib, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MARK = re.compile(r"^\s*- \[( |x|X)\] .*<!-- audit:([a-z-]+):([A-Za-z0-9_=-]+) -->\s*$")
SECRET_PATTERNS = {
    "Anthropic key": r"sk-ant-[A-Za-z0-9_-]{20,}",
    "Stripe secret key": r"(?:sk|rk)_(?:live|test)_[A-Za-z0-9]{16,}",
    "Resend key": r"\bre_[A-Za-z0-9]{8,}_[A-Za-z0-9]{8,}",
    "Meta / Instagram token": r"\b(?:EAA[A-Za-z0-9]{40,}|IG[A-Za-z]{2}[A-Za-z0-9_-]{60,})",
    "GitHub token": r"\b(?:ghp|gho|ghs|ghu|github_pat)_[A-Za-z0-9_]{30,}",
    "AWS key": r"\bAKIA[0-9A-Z]{16}\b",
    "Google API key": r"\bAIza[0-9A-Za-z_-]{35}\b",
    "Database URL with password": r"postgres(?:ql)?://[^:\s/]+:[^@\s]{6,}@",
    "Private key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "Hard-coded secret": r"(?i)\b(?:api[_-]?key|secret|token|password)\b\s*[:=]\s*['\"][A-Za-z0-9_\-]{24,}['\"]",
}
EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
EMAIL_OK = ("moodius.co.uk", "example.com", "example.org", "noreply", "users.noreply.github.com",
            "anthropic.com", "resend.dev", "localhost")
URL_BRANCH = re.compile(r"(?:raw\.githubusercontent\.com/[^/\s]+/[^/\s]+/|github\.com/[^/\s]+/[^/\s]+/(?:blob|tree|raw)/)"
                        r"([A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)?)")


def sh(*args, check=True):
    r = subprocess.run(args, capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError(f"{' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def enc(path):
    return base64.urlsafe_b64encode(path.encode()).decode()


def dec(token):
    return base64.urlsafe_b64decode(token.encode()).decode()


def load_rules():
    with open(os.path.join(HERE, "rules.json")) as f:
        return json.load(f)


def protected(path, rules):
    return any(path == p or path.startswith(p.rstrip("/") + "/") for p in rules["never_touch"])


def personal_terms():
    raw = os.environ.get("AUDIT_PERSONAL_TERMS", "")
    return sorted({t.strip() for t in raw.split(",") if t.strip()}, key=len, reverse=True)


def mb(n):
    return f"{n / 2**20:.1f} MB"


class Repo:
    def __init__(self, rules, today=None):
        self.rules = rules
        self.today = today or dt.date.today()
        self.files = [p for p in sh("git", "ls-files", "-z").split("\0") if p and os.path.isfile(p)]
        self.size = {p: os.path.getsize(p) for p in self.files}
        self.text_exts = tuple(rules["text_exts"])
        self._tokens = None

    def text_files(self):
        return [p for p in self.files if p.lower().endswith(self.text_exts) and self.size[p] < 8 * 2**20]

    def read(self, p):
        with open(p, encoding="utf-8", errors="ignore") as f:
            return f.read()

    def tokens(self):
        """Every file-name-like token mentioned in any text file (for 'is this file referenced?')."""
        if self._tokens is None:
            toks = set()
            for p in self.text_files():
                for t in re.findall(r"[A-Za-z0-9_.\-/{}*]+", self.read(p)):
                    toks.add(t)
                    for part in t.split("/"):
                        toks.add(part)
                        toks.add(os.path.splitext(part)[0])
            self._tokens = toks
        return self._tokens

    def referenced(self, path):
        base = os.path.basename(path)
        stem = os.path.splitext(base)[0]
        t = self.tokens()
        if base in t or stem in t or path in t:
            return True
        # variants of a mentioned file: R003-x-cover.jpg, R003-x-b.mp4, reel-2-v2.mp4
        root = re.sub(r"-(?:cover|thumb|b|v\d+|light|dark)$", "", stem)
        if root != stem and root in t:
            return True
        # names built by a script from a slug: C-harbour-seal-avatar-320-circle.png <- "harbour-seal"
        parts = stem.split("-")
        for n in range(len(parts) - 1, 1, -1):
            head = "-".join(parts[:n])
            if head in t or (len(parts[0]) == 1 and "-".join(parts[1:n]) in t and n > 2):
                return True
        # content IDs the docs use on their own: R004, AD05, P002, HI04a, S11D
        m = re.match(r"([A-Z]{1,3}\d{2,3}[A-Za-z]?)(?:[-_]|$)", stem)
        return bool(m and m.group(1) in t)


# ---------------------------------------------------------------- checks

def check_published(repo):
    rules, items, seen = repo.rules, [], set()
    cutoff = repo.today - dt.timedelta(days=rules["grace_days"])

    def add(path, why):
        if path in seen or protected(path, rules) or any(path.startswith(d + "/") for d in seen):
            return
        seen.add(path)
        size = sum(s for p, s in repo.size.items() if p == path or p.startswith(path + "/"))
        items.append({"action": "archive", "path": path, "detail": why, "size": size})

    # 1. explicit ledger rows (account thread appends: path, published_at, metricool_id, note)
    led = rules["published_ledger"]
    texts = [open(led).read()] if os.path.exists(led) else []
    for ref in rules.get("ledger_refs", []):   # the account thread writes the ledger on its own branch
        texts.append(sh("git", "show", f"{ref}:{led}", check=False))
    for text in texts:
        for row in csv.DictReader(text.splitlines()):
            try:
                when = dt.date.fromisoformat((row.get("published_at") or "")[:10])
            except ValueError:
                continue
            p = (row.get("path") or "").strip()
            if when <= cutoff and p and (p in repo.size or any(f.startswith(p + "/") for f in repo.files)):
                add(p, f"published {when} (ledger{', Metricool ' + row['metricool_id'] if row.get('metricool_id') else ''})")

    # 2. reels whose tracker slot is in the past (hook text match between batch scripts and tracker)
    slots = {}
    if os.path.exists(rules["tracker"]):
        for row in csv.DictReader(open(rules["tracker"])):
            hook = (row.get("hook_or_prompt") or "").strip()
            try:
                slots.setdefault(hook, []).append(dt.date.fromisoformat(row.get("date", "")))
            except ValueError:
                pass
    for batch in sorted(glob.glob(rules["script_batches"])):
        try:
            scripts = json.load(open(batch)).get("scripts", [])
        except (ValueError, AttributeError):
            continue
        for s in scripts if isinstance(scripts, list) else []:
            if not isinstance(s, dict) or not s.get("id"):
                continue
            dates = slots.get((s.get("hook") or "").strip(), []) + slots.get((s.get("hook_b") or "").strip(), [])
            if not dates or max(dates) > cutoff:
                continue
            for p in sorted(glob.glob(os.path.join(rules["renders_dir"], f"{s['id']}-*"))):
                if p in repo.size:
                    add(p, f"{s['id']} slot was {max(dates)} (tracker)")

    # 3. whole folders whose posting window has ended (rules.json retired_folders)
    for f in rules.get("retired_folders", []):
        if dt.date.fromisoformat(f["last_day"]) <= cutoff and any(x.startswith(f["path"] + "/") for x in repo.files):
            add(f["path"], f"{f.get('note', 'folder')}, window ended {f['last_day']}")

    # 4. dated upload packs and week folders whose date has passed
    for pattern in rules["dated_pack_globs"]:
        for d in sorted(glob.glob(pattern)):
            try:
                when = dt.date.fromisoformat(os.path.basename(d))
            except ValueError:
                continue
            if when <= cutoff and any(f.startswith(d + "/") for f in repo.files):
                add(d, f"pack dated {when}, past")
    return items


def check_duplicates(repo):
    rules, by_hash = repo.rules, {}
    for line in sh("git", "ls-files", "-s", "-z").split("\0"):
        if not line:
            continue
        meta, path = line.split("\t", 1)
        if path in repo.size and repo.size[path] >= 1024 and path.startswith(rules["root"] + "/"):
            by_hash.setdefault(meta.split()[1], []).append(path)
    items, notes = [], []
    for paths in by_hash.values():
        if len(paths) < 2:
            continue
        copies = [p for p in paths if any(c in p for c in rules["copy_dirs"])]
        if copies and len(copies) < len(paths):
            for p in copies:   # upload packs and fix folders hold deliberate copies; they leave with their pack
                notes.append(f"`{p}` is the posted copy of `{[q for q in paths if q not in copies][0]}` (kept until its pack is archived)")
            paths = [p for p in paths if p not in copies]
            if len(paths) < 2:
                continue
        refd = [p for p in paths if repo.referenced(p)]
        keep = sorted(refd or paths, key=lambda p: (len(p), p))[0]
        for p in sorted(paths):
            if p == keep:
                continue
            if protected(p, rules) or p in refd:
                notes.append(f"`{p}` = `{keep}` (both in use, kept)")
            else:
                items.append({"action": "delete", "path": p, "detail": f"identical to `{keep}`", "size": repo.size[p]})
    return items, notes


def check_unreferenced(repo):
    rules = repo.rules
    exts = tuple(rules["unreferenced_exts"])
    cand = [p for p in repo.files if p.startswith(rules["root"] + "/") and p.lower().endswith(exts)
            and not protected(p, rules) and not repo.referenced(p)]
    # whole folders with nothing referenced become one line
    by_dir = {}
    for p in cand:
        by_dir.setdefault(os.path.dirname(p), []).append(p)
    items = []
    for d, ps in by_dir.items():
        in_dir = [f for f in repo.files if os.path.dirname(f) == d]
        if len(ps) > 2 and len(ps) == len(in_dir) and not repo.referenced(d):
            items.append({"action": "archive", "path": d, "detail": f"folder, {len(ps)} files, none mentioned anywhere",
                          "size": sum(repo.size[p] for p in ps)})
        else:
            items += [{"action": "archive", "path": p, "detail": "not mentioned in any script or doc",
                       "size": repo.size[p]} for p in ps]
    return sorted(items, key=lambda i: -i["size"])


def check_sizes(repo):
    rules, root = repo.rules, repo.rules["root"]
    limit = rules["size_hog_mb"] * 2**20
    hogs = sorted(((s, p) for p, s in repo.size.items() if s >= limit), reverse=True)
    by_area = {}
    for p, s in repo.size.items():
        parts = p.split("/")
        area = "/".join(parts[:2]) if parts[0] == root and len(parts) > 2 else parts[0]
        by_area[area] = by_area.get(area, 0) + s
    return hogs, sorted(by_area.items(), key=lambda kv: -kv[1]), sum(repo.size.values())


def check_branches(repo, open_pr_branches):
    rules = repo.rules
    default = os.environ.get("AUDIT_DEFAULT_BRANCH", "main")
    url_refs = {}
    for p in repo.text_files():
        for m in URL_BRANCH.finditer(repo.read(p)):
            for cand in (m.group(1), m.group(1).split("/")[0]):
                url_refs.setdefault(cand, set()).add(p)
    out = sh("git", "for-each-ref", "refs/remotes/origin", "--format=%(refname:short)\t%(committerdate:unix)\t%(objectname)", check=False)
    items, kept, stale = [], [], []
    now = dt.datetime.now(dt.timezone.utc).timestamp()
    for line in out.splitlines():
        ref, ts, sha = line.split("\t")
        name = ref.split("/", 1)[1] if "/" in ref else ref
        if name in ("HEAD", default) or ref == "origin":
            continue
        merged = subprocess.run(["git", "merge-base", "--is-ancestor", ref, f"origin/{default}"]).returncode == 0
        age = int((now - int(ts)) / 86400)
        if name in rules.get("keep_branches", {}):
            kept.append(f"`{name}`: {rules['keep_branches'][name]} (rules.json keep_branches)")
        elif name in open_pr_branches:
            kept.append(f"`{name}`: open pull request")
        elif name in url_refs:
            kept.append(f"`{name}`: {len(url_refs[name])} file(s) link to it by URL (Metricool media), kept")
        elif merged:
            items.append({"action": "delete-branch", "path": name, "detail": f"fully merged into {default}, last commit {age} days ago ({sha[:7]})", "size": 0})
        elif age >= rules["stale_branch_days"]:
            stale.append(f"`{name}`: not merged, no commits for {age} days")
    return items, kept, stale


def check_secrets(repo):
    hits = []
    pats = {k: re.compile(v) for k, v in SECRET_PATTERNS.items()}
    for p in repo.files:
        b = os.path.basename(p)
        if b in (".env", ".dev.vars") or (b.startswith(".env.") and not b.endswith((".example", ".sample"))):
            hits.append(f"`{p}`: environment file committed")
    for p in repo.text_files():
        for n, line in enumerate(repo.read(p).splitlines(), 1):
            for name, rx in pats.items():
                if rx.search(line) and not re.search(r"(?i)example|placeholder|your[-_ ]|xxxx|<[^>]+>|\.\.\.|\$\{|\$[A-Z_]{3,}|localhost|127\.0\.0\.1|@db:", line):
                    hits.append(f"`{p}` line {n}: looks like a {name} (value not shown)")
    return hits


def personal_hits(text, terms):
    lines = []
    rx = re.compile(r"(?<![\w@.])(?:" + "|".join(re.escape(t) for t in terms) + r")(?!\w)", re.I) if terms else None
    for n, line in enumerate(text.splitlines(), 1):
        if (rx and rx.search(line)) or any(not e.lower().endswith(EMAIL_OK) and "noreply" not in e.lower()
                                           for e in EMAIL.findall(line)):
            lines.append(n)
    return lines


def check_personal(repo):
    terms, items = personal_terms(), []
    for p in repo.text_files():
        lines = personal_hits(repo.read(p), terms)
        if lines and p.startswith(".github/"):
            repo.personal_notes = getattr(repo, "personal_notes", []) + [
                f"`{p}`: {len(lines)} line(s) (workflow file: edit by hand, Actions cannot change workflows)"]
        elif lines:
            code = p.endswith((".py", ".ts", ".tsx", ".js", ".mjs"))
            shown = ", ".join(map(str, lines[:8])) + ("..." if len(lines) > 8 else "")
            items.append({"action": "scrub", "path": p, "size": 0,
                          "detail": f"{len(lines)} line(s): {shown}{' (code: run its tests after)' if code else ''}"})
    return sorted(items, key=lambda i: i["path"]), bool(terms)


# ---------------------------------------------------------------- report

def line(item, ticked):
    size = f", {mb(item['size'])}" if item["size"] >= 2**20 else ""
    return f"- [{'x' if ticked else ' '}] `{item['path']}`: {item['detail']}{size} <!-- audit:{item['action']}:{enc(item['path'])} -->"


def previous_ticks(path):
    if not path or not os.path.exists(path):
        return set()
    out = set()
    for ln in open(path, encoding="utf-8"):
        m = MARK.match(ln)
        if m and m.group(1) in "xX":
            out.add((m.group(2), m.group(3)))
    return out


def scan(args):
    rules = load_rules()
    repo = Repo(rules)
    prs = set(open(args.open_pr_branches).read().split()) if args.open_pr_branches and os.path.exists(args.open_pr_branches) else set()
    ticks = previous_ticks(args.previous)
    limit = rules["list_limit"]

    published = check_published(repo)
    dups, dup_notes = check_duplicates(repo)
    dups = [i for i in dups if not any(i["path"].startswith(p["path"] + "/") for p in published)]
    taken = {i["path"] for i in published + dups}
    unref = [i for i in check_unreferenced(repo)
             if i["path"] not in taken and not any(i["path"].startswith(t + "/") for t in taken)]
    hogs, areas, total = check_sizes(repo)
    branches, kept, stale = check_branches(repo, prs)
    secrets = check_secrets(repo)
    personal, have_terms = check_personal(repo)

    out = [f"Weekly repo audit, {repo.today.isoformat()}. Nothing has been changed.",
           "",
           "**How to use it:** tick the lines you want done, then comment `/apply` on this issue. "
           "A workflow re-checks each ticked line, makes the change on a new branch and opens a pull request "
           "for you to merge (merged branches are deleted straight away, with their last commit logged so they can be restored). "
           "Unticked lines are left alone. Archived files keep their sub-path under `moodius-aurelius/_archive/` "
           "and are logged in `_archive/MOVED.csv`.",
           "",
           "| Check | Found |", "|---|---|",
           f"| Published, can be archived | {len(published)} |",
           f"| Duplicate files | {len(dups)} |",
           f"| Files nothing mentions | {len(unref)} |",
           f"| Files over {rules['size_hog_mb']} MB | {len(hogs)} |",
           f"| Branches merged into main | {len(branches)} |",
           f"| Possible secrets | {len(secrets)} |",
           f"| Files naming the owner personally | {len(personal)} |",
           f"| Tracked size | {mb(total)} |", ""]

    def section(title, items, empty, note=None):
        out.append(f"### {title}")
        if note:
            out.append(note)
        if not items:
            out.append(empty)
        for it in items[:limit]:
            out.append(line(it, (it["action"], enc(it["path"])) in ticks))
        if len(items) > limit:
            out.append(f"\n_{len(items) - limit} more not listed; they come up next week once these are dealt with._")
        out.append("")

    section("1. Already published: move to the archive", published, "Nothing past its date.",
            f"Renders and packs whose slot is more than {rules['grace_days']} days old. Metricool keeps its own copy, "
            "so moving the repo file does not touch the live post. The tracker and ledgers are never edited.")
    section("2. Duplicate files: delete the extra copy", dups, "No duplicates.",
            "Byte-identical files. The copy that scripts or docs mention is kept.")
    if dup_notes:
        out += ["<details><summary>Identical but both in use (no action)</summary>", ""] + [f"- {n}" for n in dup_notes[:limit]] + ["", "</details>", ""]
    section("3. Files nothing mentions: move to the archive", unref, "Every media file is mentioned somewhere.",
            "Images, video, audio and PDFs whose name appears in no script, doc, tracker or ledger.")
    out.append(f"### 4. Large files (report only)")
    out.append("Git keeps every version of these forever. Going forward new video and audio should live in the project "
               "folder (or Git LFS), not in commits; existing paths stay so links keep working.")
    out += [f"- `{p}`: {mb(s)}" for s, p in hogs[:limit]] or ["None."]
    out += ["", "<details><summary>Size by area</summary>", ""] + [f"- `{a}`: {mb(s)}" for a, s in areas[:25]] + ["", "</details>", ""]
    section("5. Branches merged into main: delete", branches, "No merged branches left.")
    if kept or stale:
        out += ["<details><summary>Branches kept or needing a decision</summary>", ""] + [f"- {k}" for k in kept + stale] + ["", "</details>", ""]
    out.append("### 6. Possible secrets (report only)")
    out.append("If any of these is real: revoke it at the provider first, then remove it. Deleting the file does not remove it from git history.")
    out += [f"- {h}" for h in secrets[:limit]] or ["None found."]
    out.append("")
    if len(personal) > 1:
        personal = [{"action": "scrub-all", "path": "*", "size": 0,
                     "detail": f"all {len(personal)} files below and any found when /apply runs"}] + personal
    section("7. Files that name the owner personally: scrub", personal, "None found.",
            "The page is anonymous and this repo is public. Ticking a line replaces the personal terms in that file with "
            "\"the owner\" and removes private email addresses. Old commits still contain them: **making the repo private is "
            "the only full fix** (Settings > General > Danger Zone > Change visibility)."
            + ("" if have_terms else "\n\n> The `AUDIT_PERSONAL_TERMS` secret is not set, so only email addresses were checked."))
    out += [f"- {n}" for n in getattr(repo, "personal_notes", [])] + ([""] if getattr(repo, "personal_notes", []) else [])
    report = "\n".join(out).rstrip() + "\n"
    if len(report) > 60000:
        report = report[:59000] + "\n\n_Report cut to fit an issue; run `python3 moodius-aurelius/repo-audit/audit.py scan` for the full list._\n"
    if args.out:
        open(args.out, "w", encoding="utf-8").write(report)
    else:
        sys.stdout.write(report)


# ---------------------------------------------------------------- apply

def scrub_text(text, terms, replacement):
    text = EMAIL.sub(lambda m: m.group(0) if m.group(0).lower().endswith(EMAIL_OK) or "noreply" in m.group(0).lower()
                     else "[email removed]", text)
    for t in terms:
        def rep(m, text=text):
            before = text[max(0, m.start() - 2):m.start()]
            cap = m.start() == 0 or before.endswith(("\n", ". ", "# ", "| ", "> ")) or before.strip() in ("", "-", "*")
            return replacement[:1].upper() + replacement[1:] if cap else replacement
        text = re.sub(r"(?<![\w@.])" + re.escape(t) + r"(?!\w)", rep, text, flags=re.I)
    return text


def apply(args):
    rules = load_rules()
    body = open(args.body, encoding="utf-8").read()
    ticked = []
    for ln in body.splitlines():
        m = MARK.match(ln)
        if m and m.group(1) in "xX":
            ticked.append((m.group(2), dec(m.group(3))))
    done, skipped, branches = [], [], []
    terms = personal_terms()
    replacement = os.environ.get("AUDIT_PERSONAL_REPLACEMENT", "the owner")
    tracked = set(p for p in sh("git", "ls-files", "-z").split("\0") if p)
    moved_rows = []
    for action, path in ticked:
        exists = os.path.exists(path) and (path in tracked or any(f.startswith(path + "/") for f in tracked))
        if action == "delete-branch":
            ok = subprocess.run(["git", "merge-base", "--is-ancestor", f"origin/{path}", "origin/" + os.environ.get("AUDIT_DEFAULT_BRANCH", "main")]).returncode == 0
            if path in rules.get("keep_branches", {}):
                skipped.append(f"`{path}`: in keep_branches ({rules['keep_branches'][path]})")
            elif ok:
                branches.append(path)
                done.append(f"delete branch `{path}`")
            else:
                skipped.append(f"`{path}`: branch gone or no longer fully merged")
            continue
        if action == "scrub-all":
            for p in sorted(tracked):
                if p.startswith(".github/") or not os.path.isfile(p) or not p.lower().endswith(tuple(rules["text_exts"])):
                    continue
                text = open(p, encoding="utf-8", errors="ignore").read()
                new = scrub_text(text, terms, replacement)
                if new != text:
                    if not args.dry_run:
                        open(p, "w", encoding="utf-8").write(new)
                        sh("git", "add", p)
                    done.append(f"scrub `{p}`")
            if not terms:
                skipped.append("scrub-all: AUDIT_PERSONAL_TERMS not set, only emails were checked")
            continue
        if not exists:
            skipped.append(f"`{path}`: no longer in the repo")
            continue
        if action in ("archive", "delete") and not path.startswith(rules["root"] + "/"):
            skipped.append(f"`{path}`: outside {rules['root']}/")
            continue
        if action == "delete" and not os.path.isfile(path):
            skipped.append(f"`{path}`: not a file")
            continue
        if action == "scrub" and path not in tracked:
            skipped.append(f"`{path}`: not a tracked file")
            continue
        if protected(path, rules) and action != "scrub":
            skipped.append(f"`{path}`: protected path")
            continue
        if action == "archive":
            rel = os.path.relpath(path, rules["root"])
            dest = os.path.join(rules["archive_dir"], rel)
            if not args.dry_run:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                sh("git", "mv", path, dest)
            moved_rows.append([path, dest, dt.date.today().isoformat()])
            done.append(f"archive `{path}` -> `{dest}`")
        elif action == "delete":
            digest = hashlib.sha1(open(path, "rb").read()).hexdigest()
            twins = [f for f in tracked if f != path and os.path.isfile(f) and os.path.getsize(f) == os.path.getsize(path)
                     and hashlib.sha1(open(f, "rb").read()).hexdigest() == digest]
            if not twins:
                skipped.append(f"`{path}`: no identical copy left, kept")
                continue
            if not args.dry_run:
                sh("git", "rm", "-q", path)
            done.append(f"delete `{path}` (copy of `{twins[0]}`)")
        elif action == "scrub":
            text = open(path, encoding="utf-8").read()
            new = scrub_text(text, terms, replacement)
            if new == text:
                skipped.append(f"`{path}`: nothing to scrub" + ("" if terms else " (AUDIT_PERSONAL_TERMS not set)"))
                continue
            if not args.dry_run:
                open(path, "w", encoding="utf-8").write(new)
                sh("git", "add", path)
            done.append(f"scrub `{path}`")
        else:
            skipped.append(f"`{path}`: unknown action {action}")
    if moved_rows and not args.dry_run:
        led = rules["moved_ledger"]
        new = not os.path.exists(led)
        os.makedirs(os.path.dirname(led), exist_ok=True)
        with open(led, "a", newline="") as f:
            w = csv.writer(f)
            if new:
                w.writerow(["old_path", "new_path", "moved_on"])
            w.writerows(moved_rows)
        sh("git", "add", led)
    if args.branches_out:
        open(args.branches_out, "w").write("\n".join(branches) + ("\n" if branches else ""))
    summary = [f"Applied {len(done)} ticked item(s){' (dry run)' if args.dry_run else ''}."]
    summary += [f"- {d}" for d in done]
    if skipped:
        summary += ["", "Skipped:"] + [f"- {s}" for s in skipped]
    text = "\n".join(summary) + "\n"
    if args.summary:
        open(args.summary, "w", encoding="utf-8").write(text)
    sys.stdout.write(text)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan")
    s.add_argument("--out")
    s.add_argument("--previous")
    s.add_argument("--open-pr-branches")
    a = sub.add_parser("apply")
    a.add_argument("--body", required=True)
    a.add_argument("--summary")
    a.add_argument("--branches-out")
    a.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    os.chdir(sh("git", "rev-parse", "--show-toplevel").strip())
    (scan if args.cmd == "scan" else apply)(args)


if __name__ == "__main__":
    main()
