#!/usr/bin/env python3
"""Pick the final renders that may be public, and rewrite media links to the public repo.

    python3 mirror.py list                      # tracked files that go to the public media repo
    python3 mirror.py copy TARGET_DIR [--ref R]  # copy them into a checkout of the public repo (never deletes);
                                                # --ref copies from another branch, e.g. origin/claude/project-thread-bxasif
    python3 mirror.py repoint FILE... [--write] # swap raw.githubusercontent links from this repo to the public one

Only .mp4/.jpg/.jpeg/.png under the folders in ALLOW are mirrored, at the same path, so a link changes by its
repo and branch prefix only. No scripts, docs, data, strategy or personal files ever leave this repo.
Stdlib only.
"""
import fnmatch, os, re, subprocess, sys

PUBLIC = "bobmarleyrafa1999-lab/moodius-media"
PUBLIC_BRANCH = "main"
EXTS = (".mp4", ".jpg", ".jpeg", ".png")
ALLOW = [
    "moodius-aurelius/week*/*",
    "moodius-aurelius/reels/*",
    "moodius-aurelius/fixes-*/*",
    "moodius-aurelius/strategy/upload-pack/*",
    "moodius-aurelius/strategy/manifesto-stories/*",
    "moodius-aurelius/strategy/highlight-covers/*",
    "moodius-aurelius/strategy/grid-patterns/*",
    "moodius-aurelius/reels-engine/renders/*",
    "moodius-aurelius/research/adaptations/renders/*",
    "moodius-aurelius/substack/renders/*",
    "moodius-aurelius/business/funnel/reels/renders/*",
    "moodius-aurelius/hook-intel/reports/reels/*/renders/*",
    "moodius-aurelius/audio/renders/*",
    "moodius-aurelius/threads/*",
    "moodius-aurelius/pinterest/out/*",
    "moodius-aurelius/profile/*",
    "moodius-aurelius/brand/*",
    "moodius-aurelius/_archive/*",
]
DENY = ["*/hook-intel/data/*", "*/business/journal/out/*", "*/thumbs/*", "*/_build/*"]
LINK = re.compile(r"raw\.githubusercontent\.com/bobmarleyrafa1999-lab/media/(?:claude/project-thread-[A-Za-z0-9]+|[A-Za-z0-9._-]+)/")


def selected(paths):
    for p in paths:
        if p.lower().endswith(EXTS) and any(fnmatch.fnmatch(p, g) for g in ALLOW) \
                and not any(fnmatch.fnmatch(p, g) for g in DENY):
            yield p


def tracked(ref=None):
    if ref:
        out = subprocess.run(["git", "ls-tree", "-r", "-z", "--name-only", ref], capture_output=True, text=True, check=True).stdout
        return [p for p in out.split("\0") if p]
    out = subprocess.run(["git", "ls-files", "-z"], capture_output=True, text=True, check=True).stdout
    return [p for p in out.split("\0") if p and os.path.isfile(p)]


def content(p, ref=None):
    if ref:
        return subprocess.run(["git", "show", f"{ref}:{p}"], capture_output=True, check=True).stdout
    with open(p, "rb") as f:
        return f.read()


def repoint(text):
    return LINK.sub(f"raw.githubusercontent.com/{PUBLIC}/{PUBLIC_BRANCH}/", text)


def main(argv):
    if not argv or argv[0] not in ("list", "copy", "repoint"):
        sys.exit(__doc__)
    cmd, rest = argv[0], argv[1:]
    if cmd == "repoint":
        write = "--write" in rest
        for f in [r for r in rest if r != "--write"]:
            text = open(f, encoding="utf-8").read()
            new = repoint(text)
            n = len(LINK.findall(text))
            if n and write:
                open(f, "w", encoding="utf-8").write(new)
            print(f"{f}: {n} link(s){' rewritten' if n and write else ''}")
        return
    os.chdir(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True).stdout.strip())
    ref = rest[rest.index("--ref") + 1] if "--ref" in rest else None
    files = sorted(selected(tracked(ref)))
    if cmd == "list":
        print("\n".join(files))
        return
    target, copied = rest[0], 0
    for p in files:
        dst = os.path.join(target, p)
        data = content(p, ref)
        if os.path.exists(dst) and open(dst, "rb").read() == data:
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "wb") as f:
            f.write(data)
        copied += 1
    print(f"{len(files)} public files{' on ' + ref if ref else ''}, {copied} new or changed")

if __name__ == "__main__":
    main(sys.argv[1:])
