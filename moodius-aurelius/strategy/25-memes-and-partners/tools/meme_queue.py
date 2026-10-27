#!/usr/bin/env python3
"""Moodius meme curation queue. Plain Python + Pillow, no network, no logins.

Discover -> Remove duplicates -> Review humour and context -> Check reuse status
-> Prepare draft -> Owner approval -> Schedule -> Measure

The queue is one CSV (data/queue.csv) so it opens in Numbers/Excel/Sheets.

Usage (from this folder's parent):
  python3 tools/meme_queue.py import saved-links.txt   # one link per line: URL | creator | note
  python3 tools/meme_queue.py import finds.csv         # columns: url, creator, platform, reuse_terms, note
  python3 tools/meme_queue.py concepts                 # load data/concepts.json as original drafts
  python3 tools/meme_queue.py batch [N]                # next N items to review, highest score first
  python3 tools/meme_queue.py set ID field=value ...   # e.g. reuse_status=permission-needed humour=4
  python3 tools/meme_queue.py inspire ID NEWID "setup" "punch"   # write an original joke from an inspiration-only find
  python3 tools/meme_queue.py decide approve MM01 MM02 # or edit / reject, with --note "..."
  python3 tools/meme_queue.py render [ID ...]          # 1080x1350 previews into renders/
  python3 tools/meme_queue.py learn                    # what the owner's choices say (never loosens rules)

Nothing here posts, schedules or contacts anyone. Scheduling stays with the
account thread after the owner approves.
"""
import csv, json, os, re, sys, difflib, datetime
from urllib.parse import urlsplit, parse_qsl, urlencode

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
QUEUE = os.path.join(ROOT, "data", "queue.csv")
CONCEPTS = os.path.join(ROOT, "data", "concepts.json")
LEARNED = os.path.join(ROOT, "data", "learned.json")
RENDERS = os.path.join(ROOT, "renders")
FONTS = os.path.join(ROOT, "fonts")

FIELDS = ["id", "kind", "status", "url", "url_key", "creator", "platform", "found_on",
          "reuse_status", "reuse_terms", "licence_commercial", "licence_edits", "watermark_kept",
          "permission_ref", "inspired_by", "pillar", "theme", "setup", "punch", "caption",
          "image_context", "humour", "relevance", "thought", "flags", "decision",
          "decision_note", "decided_at"]

REUSE = ("original", "authorised", "permission-needed", "inspiration-only")
STATUSES = ("discovered", "reviewed", "drafted", "approved", "edit", "rejected", "scheduled", "measured")

# Hard rules. A match never auto-rejects and never auto-passes: it flags the
# item so a person looks at text, image and context together.
EXCLUDE = {
    "politics": r"\b(tory|tories|labour|reform uk|trump|biden|leftist|woke|right-?wing|left-?wing|election|brexit|immigra\w*)\b",
    "gender-war": r"\b(feminis\w*|alpha male|sigma|red ?pill|women are|men are|females?\b|simp\w*|manosphere|#youngmen)\b",
    "religion-mockery": r"\b(atheists? are|christians? are|muslims? are|jews? are|hindus? are|religion is (a )?(joke|stupid))\b",
    "body-shaming": r"\b(fat|skinny|ugly|obese|dad bod|beer belly|thunder thighs)\b",
    "sexual": r"\b(sex|nsfw|nude|naked|horny|onlyfans|thirst trap)\b",
    "tragedy": r"\b(9/11|holocaust|genocide|terror\w*|suicid\w*|school shooting|cancer|war crime)\b",
    "health-claim": r"\b(cures?|heals?|treats? (anxiety|depression|adhd)|studies show|science says|proven to|clinically|detox)\b",
    "humiliation": r"\b(idiots?|morons?|losers?|stupid people|clowns?|cringe)\b",
    "rage-bait": r"\b(unpopular opinion|fight me|controversial|ratio|triggered)\b",
}
TOO_CLOSE = 0.6   # an original written from an inspiration-only find must stay below this similarity

TRACKING = {"utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "igsh", "igshid",
            "si", "fbclid", "ref", "share_id", "s", "t"}


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")


def url_key(url):
    """Normalise a link so the same post saved twice is caught as a duplicate."""
    if not url:
        return ""
    p = urlsplit(url.strip())
    host = p.netloc.lower().removeprefix("www.").removeprefix("m.").removeprefix("old.")
    path = re.sub(r"/+$", "", p.path)
    m = re.match(r"^/(?:[^/]+/)?(?:p|reel|reels|tv)/([^/]+)", path)
    if host.endswith("instagram.com") and m:
        return "instagram.com/p/" + m.group(1)
    q = [(k, v) for k, v in parse_qsl(p.query) if k.lower() not in TRACKING]
    return host + path + ("?" + urlencode(sorted(q)) if q else "")


def text_of(row):
    return " ".join(x for x in (row.get("setup", ""), row.get("punch", ""), row.get("caption", "")) if x).strip()


def similarity(a, b):
    a, b = re.sub(r"\W+", " ", a.lower()).strip(), re.sub(r"\W+", " ", b.lower()).strip()
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def flags_for(row):
    blob = " ".join([text_of(row), row.get("image_context", ""), row.get("reuse_terms", "")]).lower()
    return sorted(k for k, rx in EXCLUDE.items() if re.search(rx, blob))


def load():
    if not os.path.exists(QUEUE):
        return []
    with open(QUEUE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save(rows):
    os.makedirs(os.path.dirname(QUEUE), exist_ok=True)
    with open(QUEUE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})


def score(row):
    try:
        base = sum(int(row.get(k) or 0) for k in ("humour", "relevance", "thought"))
    except ValueError:
        base = 0
    weights = {}
    if os.path.exists(LEARNED):
        with open(LEARNED) as f:
            weights = json.load(f).get("theme_weight", {})
    return base * weights.get(row.get("theme", ""), 1.0)


def gate(row):
    """Return the list of reasons this item cannot be approved yet. Scores never override these."""
    why = []
    rs = row.get("reuse_status", "")
    if rs not in REUSE:
        why.append("reuse status not set")
    elif rs == "permission-needed":
        why.append("no written permission yet")
    elif rs == "inspiration-only" and row.get("kind") != "inspired":
        why.append("inspiration only: write an original joke with `inspire`, never repost")
    elif rs == "authorised":
        if row.get("licence_commercial") != "yes":
            why.append("permission must cover commercial use")
        if row.get("licence_edits") != "yes":
            why.append("permission must cover edits/cropping")
        if row.get("watermark_kept") != "yes":
            why.append("creator watermark must stay")
        if not row.get("permission_ref"):
            why.append("save where the permission is written (DM screenshot / email / licence URL)")
        if not row.get("creator"):
            why.append("creator unknown")
    if row.get("kind") != "original" and not row.get("image_context"):
        why.append("describe the image and context (a harmless caption doesn't clear a bad image)")
    if row.get("flags"):
        why.append("flagged for review: " + row["flags"])
    return why


def import_file(path, rows):
    keys = {r["url_key"] for r in rows if r.get("url_key")}
    texts = [text_of(r) for r in rows]
    added = dups = 0
    if path.endswith(".csv"):
        src = list(csv.DictReader(open(path, newline="", encoding="utf-8")))
    else:
        src = []
        for line in open(path, encoding="utf-8"):
            if not line.strip() or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            src.append({"url": parts[0], "creator": parts[1] if len(parts) > 1 else "",
                        "note": parts[2] if len(parts) > 2 else ""})
    n = sum(1 for r in rows if r["id"].startswith("C"))
    for s in src:
        k = url_key(s.get("url", ""))
        note = s.get("note", "") or s.get("caption", "")
        if k and k in keys:
            dups += 1
            continue
        if note and any(similarity(note, t) > 0.9 for t in texts if t):
            dups += 1
            continue
        n += 1
        host = urlsplit(s.get("url", "")).netloc.lower().removeprefix("www.")
        row = {"id": f"C{n:03d}", "kind": "candidate", "status": "discovered", "url": s.get("url", ""),
               "url_key": k, "creator": s.get("creator", ""), "platform": s.get("platform", "") or host,
               "found_on": now()[:10], "reuse_status": s.get("reuse_status", ""),
               "reuse_terms": s.get("reuse_terms", ""), "caption": note}
        row["flags"] = ",".join(flags_for(row))
        rows.append(row)
        keys.add(k)
        texts.append(note)
        added += 1
    return added, dups


def load_concepts(rows):
    have = {r["id"] for r in rows}
    data = json.load(open(CONCEPTS, encoding="utf-8"))["concepts"]
    added = 0
    for c in data:
        if c["id"] in have:
            continue
        row = {"id": c["id"], "kind": "original", "status": "drafted", "reuse_status": "original",
               "pillar": c["pillar"], "theme": c["theme"], "setup": c["setup"], "punch": c["punch"],
               "caption": c["caption"], "image_context": c["visual"],
               "humour": c["scores"]["humour"], "relevance": c["scores"]["relevance"],
               "thought": c["scores"]["thought"], "found_on": now()[:10]}
        row["flags"] = ",".join(flags_for(row))
        rows.append(row)
        added += 1
    return added


def inspire(rows, src_id, new_id, setup, punch):
    src = next((r for r in rows if r["id"] == src_id), None)
    if not src:
        raise SystemExit(f"{src_id} not found")
    new = {"id": new_id, "kind": "inspired", "status": "drafted", "reuse_status": "inspiration-only",
           "inspired_by": src_id, "setup": setup, "punch": punch, "pillar": src.get("pillar", ""),
           "theme": src.get("theme", ""), "image_context": "Original layout, own or CC0 image (fill in)",
           "found_on": now()[:10]}
    sim = similarity(setup + " " + punch, text_of(src))
    fl = flags_for(new)
    if sim >= TOO_CLOSE:
        fl.append(f"too-close-to-source({sim:.2f})")
    new["flags"] = ",".join(fl)
    rows.append(new)
    return new, sim


def decide(rows, verdict, ids, note=""):
    assert verdict in ("approve", "edit", "reject")
    done, blocked = [], {}
    for r in rows:
        if r["id"] not in ids:
            continue
        if verdict == "approve":
            why = gate(r)
            if why:
                blocked[r["id"]] = why
                continue
        r["decision"] = verdict
        r["status"] = {"approve": "approved", "edit": "edit", "reject": "rejected"}[verdict]
        r["decision_note"] = note
        r["decided_at"] = now()
        done.append(r["id"])
    return done, blocked


def learn(rows):
    """Turn the owner's decisions into review-order weights per theme.
    Only ordering changes. Hard rules, gates and flags are never touched."""
    by = {}
    for r in rows:
        if r.get("decision") in ("approve", "reject"):
            t = r.get("theme") or "other"
            a, n = by.get(t, (0, 0))
            by[t] = (a + (r["decision"] == "approve"), n + 1)
    weights = {}
    for t, (a, n) in by.items():
        if n >= 3:   # too few decisions says nothing
            weights[t] = round(min(1.3, max(0.7, 0.7 + 0.6 * a / n)), 2)
    reasons = {}
    for r in rows:
        if r.get("decision") == "reject" and r.get("decision_note"):
            reasons[r["decision_note"].lower()] = reasons.get(r["decision_note"].lower(), 0) + 1
    out = {"updated": now(), "theme_weight": weights, "approve_rate": {t: f"{a}/{n}" for t, (a, n) in by.items()},
           "top_reject_reasons": sorted(reasons.items(), key=lambda x: -x[1])[:5],
           "standards": "unchanged: exclusion list, reuse gates and flags are fixed in code"}
    with open(LEARNED, "w") as f:
        json.dump(out, f, indent=2)
    return out


# ---------- rendering (original concepts only) ----------

C = dict(slate="#1B1F24", graphite="#2A2F36", charcoal="#3A4049", bone="#F3EFE7", ash="#B8B3A9", ember="#C9742E")
W, H, M = 1080, 1350, 96


def _font(name, size):
    from PIL import ImageFont
    f = {"serif": "Playfair-SemiBold.ttf", "serif_it": "Playfair-MediumItalic.ttf", "sans": "Inter-Regular.ttf",
         "sans_md": "Inter-Medium.ttf", "sans_sb": "Inter-SemiBold.ttf"}[name]
    return ImageFont.truetype(os.path.join(FONTS, f), size)


def _wrap(d, text, f, width):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _block(d, x, y, text, f, fill, width, lh=1.22):
    for line in _wrap(d, text, f, width):
        d.text((x, y), line, font=f, fill=fill)
        y += int(f.size * lh)
    return y


def _fit(d, text, name, width, max_lines, start, floor=44):
    size = start
    while size > floor:
        f = _font(name, size)
        if len(_wrap(d, text, f, width)) <= max_lines:
            return f
        size -= 4
    return _font(name, floor)


def render(c, out_dir=RENDERS):
    from PIL import Image, ImageDraw
    os.makedirs(out_dir, exist_ok=True)
    im = Image.new("RGB", (W, H), C["slate"])
    d = ImageDraw.Draw(im)
    tw = W - 2 * M
    kind = c.get("render", "type")
    small = _font("sans_md", 30)

    if kind == "type":
        fs = _fit(d, c["setup"], "sans_md", tw, 4, 60)
        fp = _fit(d, c["punch"], "serif", tw, 4, 92)
        hs = len(_wrap(d, c["setup"], fs, tw)) * int(fs.size * 1.22)
        hp = len(_wrap(d, c["punch"], fp, tw)) * int(fp.size * 1.22)
        y = (H - hs - 70 - hp) // 2 - 20
        y = _block(d, M, y, c["setup"], fs, C["ash"], tw)
        d.line((M, y + 28, M + 80, y + 28), fill=C["ember"], width=4)
        _block(d, M, y + 70, c["punch"], fp, C["bone"], tw)
        if c["id"] == "MB04":
            d.rounded_rectangle((M, H - 300, W - M, H - 284), 8, fill=C["charcoal"])
            d.rounded_rectangle((M, H - 300, M + 22, H - 284), 8, fill=C["ember"])
            d.text((M, H - 270), "2%", font=small, fill=C["ash"])
        if c["id"] == "MM06":
            gy = H - 330
            for i in range(4):
                d.rounded_rectangle((M + i * 226, gy, M + i * 226 + 200, gy + 120), 10, fill=C["charcoal"])
            d.rounded_rectangle((M, gy + 150, W - M, gy + 158), 4, fill=C["graphite"])
            d.rounded_rectangle((M, gy + 150, M + 140, gy + 158), 4, fill=C["ash"])
        if c["id"] == "MP01":
            d.text((M, M + 40), "fine.", font=_font("sans_md", 44), fill=C["ash"])
            d.line((M - 6, M + 68, M + 110, M + 68), fill=C["ember"], width=5)

    elif kind == "bars":
        y = _block(d, M, M + 80, c["setup"], _fit(d, c["setup"], "serif", tw, 2, 76), C["bone"], tw) + 70
        mx = max(v for _, v in c["bars"])
        for i, (lab, v) in enumerate(c["bars"]):
            y = _block(d, M, y, lab, _font("sans_md", 38), C["ash"], tw) + 10
            bw = max(18, int((tw - 120) * v / mx))
            d.rectangle((M, y, M + bw, y + 70), fill=C["ember"] if i == 0 else C["bone"])
            d.text((M + bw + 20, y + 8), str(v), font=_font("serif", 52), fill=C["bone"])
            y += 140
        d.text((M, H - M - 30), c["punch"], font=small, fill=C["ash"])

    elif kind in ("line", "progress"):
        y0 = _block(d, M, M + 60, c["setup"], _font("serif", 70), C["bone"], tw)
        top, bot, left, right = y0 + 80, H - 330, M + 10, W - M
        d.line((left, bot, right, bot), fill=C["charcoal"], width=3)
        d.line((left, top, left, bot), fill=C["charcoal"], width=3)
        if kind == "line":
            pts, mx = c["line"], max(c["line"])
            xy = [(left + i * (right - left) / (len(pts) - 1), bot - (bot - top) * p / mx) for i, p in enumerate(pts)]
            d.line(xy, fill=C["ember"], width=8, joint="curve")
            for i, lab in enumerate(c.get("labels", [])):
                if lab:
                    tx = min(xy[i][0], right - d.textlength(lab, font=small))
                    d.text((tx, bot + 16), lab, font=small, fill=C["ash"])
            note = "Suddenly ready to reorganise my whole life"
            _block(d, int(right - 520), int(top - 10), note, _font("sans_md", 30), C["bone"], 430)
        else:
            d.line((left, bot, right, top), fill=C["charcoal"], width=6)
            d.text((right - 190, top - 46), "Expected", font=small, fill=C["ash"])
            pts = [0, .12, .06, .2, .16, .05, .14, .24, .2, .3, .27, .34]
            xy = [(left + i * (right - left) / (len(pts) - 1), bot - (bot - top) * p) for i, p in enumerate(pts)]
            d.line(xy, fill=C["ember"], width=8, joint="curve")
            for i, lab, dy in ((2, "had a cold", 22), (5, "Christmas", 22), (9, "remembered", -64)):
                d.text((xy[i][0] - 60, xy[i][1] + dy), lab, font=small, fill=C["bone"])
            d.text((right - 120, xy[-1][1] + 24), "Actual", font=small, fill=C["ember"])
        _block(d, M, H - 250, c["punch"], _font("serif_it", 50), C["bone"], tw)

    elif kind == "flow":
        f = _font("sans_md", 36)
        y = M + 30
        d.text((M, y), c["setup"], font=_font("serif", 62), fill=C["bone"])
        y += 140
        endy = H - 300
        for q in c["flow"]:
            d.rounded_rectangle((M, y, M + 460, y + 110), 14, outline=C["ash"], width=3)
            d.text((M + 28, y + 34), q, font=f, fill=C["bone"])
            d.text((M + 500, y + 34), "yes", font=small, fill=C["ash"])
            d.text((M + 500, y + 70), "no", font=small, fill=C["ash"])
            d.line((M + 580, y + 55, W - M - 120, endy), fill=C["charcoal"], width=3)
            y += 190
        d.rounded_rectangle((W - M - 520, endy, W - M, endy + 140), 18, fill=C["ember"])
        d.text((W - M - 490, endy + 44), c["punch"], font=_font("serif", 50), fill=C["slate"])

    elif kind == "venn":
        cx, cy, r = W // 2, H // 2 + 20, 330
        d.ellipse((cx - r - 14, cy - r, cx + r - 14, cy + r), outline=C["bone"], width=6)
        d.ellipse((cx - r + 14, cy - r, cx + r + 14, cy + r), outline=C["ember"], width=6)
        _block(d, M, M, c["venn"][0], _font("sans_md", 40), C["bone"], tw)
        _block(d, M, H - M - 100, c["venn"][1], _font("sans_md", 40), C["ember"], tw)
        f = _font("serif", 72)
        d.text((cx - d.textlength(c["punch"], font=f) / 2, cy - 40), c["punch"], font=f, fill=C["bone"])

    elif kind == "ui":
        y = _block(d, M, M + 120, c["setup"], _font("sans_md", 52), C["ash"], tw) + 80
        d.rounded_rectangle((M, y, M + 220, y + 120), 50, fill=C["charcoal"])
        d.text((M + 70, y + 26), c["ui"], font=_font("sans_md", 58), fill=C["bone"])
        d.text((M + 6, y + 140), "Delivered 14:02", font=_font("sans", 26), fill=C["ash"])
        _block(d, M, y + 260, c["punch"], _fit(d, c["punch"], "serif", tw, 4, 84), C["bone"], tw)

    d.text((W - M - d.textlength("moodius", font=_font("sans_sb", 26)), H - 70), "moodius",
           font=_font("sans_sb", 26), fill=C["charcoal"])
    path = os.path.join(out_dir, f"{c['id']}.png")
    im.save(path, optimize=True)
    return path


def main(argv):
    if not argv:
        print(__doc__)
        return 0
    cmd, args = argv[0], argv[1:]
    rows = load()
    if cmd == "import":
        a, dups = import_file(args[0], rows)
        save(rows)
        print(f"added {a}, skipped {dups} duplicates")
    elif cmd == "concepts":
        print(f"added {load_concepts(rows)} concepts")
        save(rows)
    elif cmd == "batch":
        n = int(args[0]) if args else 10
        todo = [r for r in rows if r["status"] in ("discovered", "reviewed", "drafted", "edit")]
        for r in sorted(todo, key=score, reverse=True)[:n]:
            g = gate(r)
            print(f"{r['id']:6} {score(r):4.1f}  {r.get('reuse_status') or '?':17} {text_of(r)[:70]}")
            if g:
                print("       blocked: " + "; ".join(g))
    elif cmd == "set":
        r = next(x for x in rows if x["id"] == args[0])
        for kv in args[1:]:
            k, v = kv.split("=", 1)
            if k not in FIELDS:
                raise SystemExit(f"unknown field {k}")
            if k == "reuse_status" and v not in REUSE:
                raise SystemExit(f"reuse_status must be one of {REUSE}")
            r[k] = v
        r["flags"] = ",".join(f for f in flags_for(r))
        if r["status"] == "discovered":
            r["status"] = "reviewed"
        save(rows)
    elif cmd == "inspire":
        new, sim = inspire(rows, *args[:4])
        save(rows)
        print(f"{new['id']} similarity to source {sim:.2f}" + ("  TOO CLOSE: rewrite" if sim >= TOO_CLOSE else ""))
    elif cmd == "decide":
        note = ""
        if "--note" in args:
            i = args.index("--note")
            note, args = args[i + 1], args[:i] + args[i + 2:]
        done, blocked = decide(rows, args[0], set(args[1:]), note)
        save(rows)
        print("done:", " ".join(done) or "-")
        for k, v in blocked.items():
            print(f"not approved {k}: " + "; ".join(v))
    elif cmd == "render":
        data = json.load(open(CONCEPTS, encoding="utf-8"))["concepts"]
        for c in data:
            if not args or c["id"] in args:
                print(render(c))
    elif cmd == "learn":
        print(json.dumps(learn(rows), indent=2))
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
