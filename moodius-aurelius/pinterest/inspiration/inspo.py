#!/usr/bin/env python3
"""Moodius visual research library: Pinterest (and anything else) as art direction, never as content.

    python3 inspo.py boards                       # the 11 research boards to create (secret)
    python3 inspo.py add URL [URL ...] [--board "Existential Cinema"] [--creator NAME]
    python3 inspo.py scan                         # palette + light/contrast for every image in inbox/
    python3 inspo.py api [--board-filter WORD]    # import pins from your own boards (read-only token)
    python3 inspo.py report                       # counts per board, palette fit, missing fields

Library: library.csv next to this file. One row per reference. Images you saved by hand go in
inbox/ named <id>.jpg (or any name: scan gives them an id). The script never downloads or
republishes third-party images; `reuse` defaults to "inspiration only".

API mode needs a token with boards:read and pins:read (plus boards:read_secret and
pins:read_secret for secret boards). Token from PINTEREST_ACCESS_TOKEN or PINTEREST_TOKEN_FILE,
same as ../pins.py. It is never written anywhere.
"""
import argparse, csv, json, os, re, sys, urllib.request
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIB, INBOX = HERE / "library.csv", HERE / "inbox"
FIELDS = ["id", "added", "source_url", "pin_id", "creator", "creator_url", "board", "palette_hex",
          "palette_fit", "brightness", "contrast", "mood", "composition", "format_use", "reuse", "local_file", "notes"]

BOARDS = {
    "Masculinity in Silence": "Men alone with a feeling: backs, hands, empty rooms, no faces. For E.",
    "Existential Cinema": "Stills and frames from films about meaning and absurdity. Reference only (copyright). For D, C.",
    "Visual Philosophy": "Images that carry an idea without words. For A, F.",
    "Human Condition": "Everyday moments everyone recognises: queues, kitchens, buses. For D.",
    "The Art of Solitude": "One figure or none, a lot of space. For B, A.",
    "Vintage Photography": "Pre-1930 and public-domain photographs (museum open access). Some reusable: check the licence. For F, D.",
    "Dark Academia": "Libraries, desks, worn books, lamplight. For F, carousels.",
    "Quiet Intimacy": "Two cups, two coats, a hand on a shoulder. Closeness without romance clichés. For D, E.",
    "Brutalism and Architecture": "Concrete, stairwells, repetition, scale. For C (contrast), B.",
    "Typography and Editorial Design": "Layouts and type pairings close to Playfair + Inter. For carousels, covers.",
    "Film Stills and Moodboards": "Light, framing and colour grading references. Reference only. For all reel looks.",
}
PALETTE = {"Slate": (27, 31, 36), "Graphite": (42, 47, 54), "Charcoal": (58, 64, 73),
           "Bone": (243, 239, 231), "Ash": (184, 179, 169), "Ember": (201, 116, 46)}


def load():
    if not LIB.exists():
        return []
    with open(LIB, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def save(rows):
    with open(LIB, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})


def next_id(rows):
    n = max([int(r["id"][1:]) for r in rows if re.fullmatch(r"V\d+", r.get("id", ""))] + [0])
    return f"V{n + 1:04d}"


def pin_id(url):
    m = re.search(r"pinterest\.[a-z.]+/pin/(?:[^/]*--)?(\d+)", url)
    return m.group(1) if m else ""


def cmd_boards(_):
    print("Create these as SECRET boards on the Moodius Pinterest account, so the public profile stays on-brand:\n")
    for b, d in BOARDS.items():
        print(f"- {b}: {d}")


def cmd_add(a):
    rows = load()
    known = {r["source_url"] for r in rows}
    for url in a.urls:
        if url in known:
            print(f"skip (already in library): {url}")
            continue
        r = {"id": next_id(rows), "added": date.today().isoformat(), "source_url": url, "pin_id": pin_id(url),
             "creator": a.creator or "", "board": a.board or "", "reuse": "inspiration only"}
        rows.append(r)
        print(f"{r['id']}  {url}")
    save(rows)


def analyse(path):
    """5-colour palette, mean brightness (0-100), RMS contrast, and distance to the Moodius palette."""
    from PIL import Image, ImageStat
    im = Image.open(path).convert("RGB")
    im.thumbnail((400, 400))
    q = im.quantize(colors=5, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()[:15]
    counts = sorted(q.getcolors(), reverse=True)
    cols = [tuple(pal[i * 3:i * 3 + 3]) for _, i in counts]
    hexes = " ".join("#%02X%02X%02X" % c for c in cols)
    grey = im.convert("L")
    st = ImageStat.Stat(grey)
    bright = round(st.mean[0] / 2.55)
    contrast = round(st.stddev[0] / 2.55)
    # palette fit: share of pixels whose nearest brand colour is within a tolerant distance
    total, near = 0, 0
    for n, i in counts:
        c = tuple(pal[i * 3:i * 3 + 3])
        d = min(sum((x - y) ** 2 for x, y in zip(c, p)) ** 0.5 for p in PALETTE.values())
        total += n
        near += n if d < 60 else 0
    return hexes, round(100 * near / total), bright, contrast


def guess_mood(bright, contrast):
    if bright < 25:
        return "nocturnal, heavy" if contrast > 18 else "dim, hushed"
    if bright < 50:
        return "moody, low-key" if contrast > 18 else "muted, quiet"
    return "airy, high-key" if contrast < 18 else "crisp, daylight"


def cmd_scan(_):
    rows = load()
    by_file = {r["local_file"]: r for r in rows if r.get("local_file")}
    by_id = {r["id"]: r for r in rows}
    for p in sorted(INBOX.iterdir()):
        if p.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
            continue
        r = by_file.get(p.name) or by_id.get(p.stem)
        if not r:
            r = {"id": next_id(rows), "added": date.today().isoformat(), "reuse": "inspiration only",
                 "notes": "added from inbox: fill source_url and creator"}
            rows.append(r)
        r["local_file"] = p.name
        r["palette_hex"], fit, b, c = analyse(p)
        r["palette_fit"], r["brightness"], r["contrast"] = f"{fit}%", str(b), str(c)
        r["mood"] = r.get("mood") or guess_mood(b, c) + " (auto)"
        print(f"{r['id']}  {p.name:30s} fit {fit:3d}%  bright {b:3d}  contrast {c:3d}  {r['palette_hex']}")
    save(rows)


def api_get(token, path):
    req = urllib.request.Request("https://api.pinterest.com/v5" + path, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def paged(token, path):
    bookmark = None
    while True:
        sep = "&" if "?" in path else "?"
        page = api_get(token, f"{path}{sep}page_size=100" + (f"&bookmark={bookmark}" if bookmark else ""))
        yield from page.get("items", [])
        bookmark = page.get("bookmark")
        if not bookmark:
            return


def token():
    t = os.environ.get("PINTEREST_ACCESS_TOKEN")
    if t:
        return t
    f = Path(os.environ.get("PINTEREST_TOKEN_FILE", "common/oauth_tokens/access_token.json"))
    if f.exists():
        return json.loads(f.read_text())["access_token"]
    sys.exit("No token: set PINTEREST_ACCESS_TOKEN or PINTEREST_TOKEN_FILE (scopes boards:read pins:read).")


def cmd_api(a):
    tok, rows = token(), load()
    known = {r.get("pin_id") for r in rows}
    added = 0
    for b in paged(tok, "/boards"):
        if b["name"] not in BOARDS and not (a.board_filter and a.board_filter.lower() in b["name"].lower()):
            continue
        for p in paged(tok, f"/boards/{b['id']}/pins"):
            if p["id"] in known:
                continue
            rows.append({"id": next_id(rows), "added": date.today().isoformat(),
                         "source_url": p.get("link") or f"https://www.pinterest.com/pin/{p['id']}/",
                         "pin_id": p["id"], "board": b["name"], "reuse": "inspiration only",
                         "notes": (p.get("title") or p.get("description") or "")[:200]})
            known.add(p["id"])
            added += 1
    save(rows)
    print(f"{added} new references. Creator and composition still need a look: run `report`.")


def cmd_report(_):
    rows = load()
    print(f"{len(rows)} references")
    for b in BOARDS:
        n = sum(r.get("board") == b for r in rows)
        print(f"  {b:34s} {n}")
    other = [r for r in rows if r.get("board") not in BOARDS]
    if other:
        print(f"  {'(no or other board)':34s} {len(other)}")
    for f in ("creator", "mood", "composition", "format_use"):
        print(f"missing {f}: {sum(not r.get(f) for r in rows)}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("boards")
    p = sub.add_parser("add"); p.add_argument("urls", nargs="+"); p.add_argument("--board"); p.add_argument("--creator")
    sub.add_parser("scan")
    p = sub.add_parser("api"); p.add_argument("--board-filter")
    sub.add_parser("report")
    a = ap.parse_args()
    {"boards": cmd_boards, "add": cmd_add, "scan": cmd_scan, "api": cmd_api, "report": cmd_report}[a.cmd](a)


if __name__ == "__main__":
    main()
