#!/usr/bin/env python3
"""Moodius grid patterns: grid-safe covers that land in a planned profile-grid pattern.

    python3 grid_patterns.py mock   [--pattern checker|diagonal|horizon|all] [--from 2026-11-03] [--out DIR]
    python3 grid_patterns.py ledger [--pattern checker] [--from 2026-11-02] [--out DIR]
    python3 grid_patterns.py cover  --pattern checker --index 7 --hook "..." [--kind REEL] [--series "Quiet Truths"] --out x.jpg

Draft tool, 22 Oct 2026. Nothing here schedules or uploads anything.

Why it works: Instagram fills the grid newest-first, three tiles a row, and every new post pushes
all the others one place along. So a pattern that depends on the *order* of posts survives every
new post, while a pattern that depends on fixed *positions* (puzzle grids, row themes) breaks the
moment one post is missed. With 3 columns, a repeating cycle of length 2 draws a checkerboard,
length 3 draws vertical stripes and length 4 draws diagonals. The ground of post n is
cycle[n % len(cycle)], where n counts published posts since the anchor (2 Nov 2026 12:00).
Archiving an *older* post never moves the newer ones, so clear-outs don't break the top rows.

Covers are 1080x1920 (reel) with every word inside the centre 1080x1440 band, which is the 3:4
crop the profile grid shows since 2025. Carousel covers use the same band at 1080x1350.
"""
import argparse, csv, os, re, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from design import SLATE, GRAPHITE, CHARCOAL, BONE, ASH, EMBER, DISPLAY, BODY_M, BODY_SB, MARGIN, HANDLE  # noqa: E402

TRACKER = os.path.join(PROJECT, "strategy", "calendar-30-day-tracker.csv")
OUT = os.path.join(PROJECT, "strategy", "grid-patterns")
W, H = 1080, 1920
BAND = (240, 1680)          # 3:4 grid crop of a 9:16 reel


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# logo-v2 palette (brand/logo-v2/README.md), used only by the "horizon" pattern
INK_PETROL, DEEP_SPRUCE, PINE = rgb("0F2229"), rgb("163A31"), rgb("2A5A46")
HARBOUR, VERDIGRIS, VERDIGRIS_LT, LICHEN, MIST = rgb("24506B"), rgb("45B096"), rgb("2B7F6B"), rgb("B3D3A0"), rgb("AFCFE0")

# ground: background, hook colour, accent (rule + kicker dot), quiet colour (kicker, handle)
GROUNDS = {
    "slate": (SLATE, BONE, EMBER, ASH),
    "bone": (BONE, SLATE, EMBER, rgb("6E6A62")),
    "ember": (EMBER, SLATE, SLATE, rgb("3A2614")),
    "graphite": (GRAPHITE, BONE, EMBER, ASH),
    "petrol": (INK_PETROL, BONE, VERDIGRIS, MIST),
    "bone-v": (BONE, INK_PETROL, VERDIGRIS_LT, rgb("4F6B66")),
    "spruce": (DEEP_SPRUCE, BONE, LICHEN, LICHEN),
}

PATTERNS = {
    "checker": {"cycle": ["bone", "slate"],
                "name": "Checkerboard", "palette": "current"},
    "diagonal": {"cycle": ["bone", "slate", "ember", "slate"],
                 "name": "Ember diagonal", "palette": "current"},
    "horizon": {"cycle": ["bone-v", "petrol"],
                "name": "Horizon checkerboard", "palette": "logo-v2"},
}


def luminance(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in c)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    if len(lines) > 1 and len(lines[-1].split()) == 1:  # no one-word last line (engine rule 1.1)
        prev = lines[-2].split()
        lines[-2], lines[-1] = " ".join(prev[:-1]), prev[-1] + " " + lines[-1]
    return lines


def series_label(fmt):
    """'R1/B Quiet Truths' -> 'QUIET TRUTHS'; 'F2 Ancient line, modern situation' -> 'ANCIENT LINE, MODERN SITUATION'."""
    label = re.sub(r"^(R\d|F\d+|[A-F])(/[A-F])?\s+", "", fmt.strip())
    label = label.replace("text-led reel (reels-engine)", "Text reel").replace(" reel", "").replace(" carousel", "")
    return label.upper()[:34]


def cover(ground, hook, kind="REEL", series="", size=(W, H)):
    """One grid-safe cover. All text sits inside the 3:4 band so the grid shows all of it."""
    bg, fg, accent, quiet = GROUNDS[ground]
    w, h = size
    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)
    top = (h - w * 4 // 3) // 2 if h > w * 4 // 3 else 0      # top of the 3:4 band
    bot = top + min(h, w * 4 // 3)
    m = MARGIN + (w - h * 3 // 4) // 2 if h < w * 4 // 3 else MARGIN   # 4:5 carousel loses its sides in the 3:4 crop
    fs = 104 if len(hook) < 48 else 92 if len(hook) < 70 else 80
    font = ImageFont.truetype(DISPLAY, fs)
    lines = wrap(d, hook, font, w - 2 * m)
    lh = int(fs * 1.16)
    block = lh * len(lines)
    y = top + (bot - top - block) // 2 - 20
    kick = ImageFont.truetype(BODY_SB, 30)
    d.rectangle([m, top + 150, m + 14, top + 164], fill=accent)
    d.text((m + 30, top + 140), ("MOODIUS" + ("  ·  " + series if series else "")), font=kick, fill=quiet)
    for i, ln in enumerate(lines):
        d.text((m, y + i * lh), ln, font=font, fill=fg)
    d.rectangle([m, y + block + 34, m + 120, y + block + 40], fill=accent)
    small = ImageFont.truetype(BODY_M, 30)
    d.text((m, bot - 160), HANDLE, font=small, fill=quiet)
    if kind == "CAROUSEL":
        d.text((w - m - d.textlength("Swipe →", font=small), bot - 160), "Swipe →", font=small, fill=quiet)
    return img


def upcoming(start, n=None):
    rows = [r for r in csv.DictReader(open(TRACKER, encoding="utf-8"))
            if r["type"] in ("REEL", "CAROUSEL") and r["date"] >= start]
    rows.sort(key=lambda r: (r["date"], r["time_madrid"]))
    return rows[:n] if n else rows


def hook_of(r):
    h = r["hook_or_prompt"].strip()
    if h.startswith("(Free Minds"):
        return "Nothing changes until someone looks straight at it."  # liberation/03-pillar.md concept 2, pick pending
    h = h.split(" (reel-")[0].split(" (Week")[0].replace("... / ...", " ")
    return h


def anchor_index(date, anchor="2026-11-02"):
    return len(upcoming(anchor)) - len(upcoming(date))


def mock(pattern, start, out):
    """Profile as it would look after the 12 posts from `start`: newest top-left, 3 x 4 tiles at 3:4."""
    p = PATTERNS[pattern]
    rows = upcoming(start, 12)
    first = anchor_index(start)
    tw, th, gap = 360, 480, 4
    sheet = Image.new("RGB", (3 * tw + 2 * gap, 4 * th + 3 * gap), (255, 255, 255))
    covers = []
    for k, r in enumerate(rows):
        n = first + k
        g = p["cycle"][n % len(p["cycle"])]
        size = (W, H) if r["type"] == "REEL" else (1080, 1350)
        img = cover(g, hook_of(r), r["type"], series_label(r["format"]), size)
        covers.append((r, g, img))
    for pos, (r, g, img) in enumerate(reversed(covers)):         # newest first
        w, h = img.size
        ch = w * 4 // 3 if h >= w * 4 // 3 else h
        cw = ch * 3 // 4
        crop = img.crop(((w - cw) // 2, (h - ch) // 2, (w + cw) // 2, (h + ch) // 2)).resize((tw, th), Image.LANCZOS)
        dr = ImageDraw.Draw(crop)
        _, fg, _, _ = GROUNDS[g]
        icon = (255, 255, 255) if luminance(GROUNDS[g][0]) < 0.4 else (40, 40, 40)
        if r["type"] == "REEL":   # small play mark like Instagram's reel badge
            dr.polygon([(tw - 30, 14), (tw - 30, 34), (tw - 13, 24)], fill=icon)
        else:                      # carousel badge
            dr.rectangle([tw - 30, 16, tw - 16, 30], outline=icon, width=2)
            dr.rectangle([tw - 26, 12, tw - 12, 26], outline=icon, width=2)
        sheet.paste(crop, ((pos % 3) * (tw + gap), (pos // 3) * (th + gap)))
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, f"mock-{pattern}.png")
    sheet.save(path, optimize=True)
    # one full-size cover per ground so the type can be judged at 100%
    for r, g, img in covers[:len(p["cycle"])]:
        img.convert("RGB").save(os.path.join(out, f"cover-{pattern}-{g}.jpg"), quality=90)
    return path, [(r["date"], r["time_madrid"], r["type"], g, hook_of(r)) for r, g, _ in covers]


def ledger(pattern, start, out):
    """Which ground each upcoming post gets. The routine renders covers from this file."""
    p = PATTERNS[pattern]
    path = os.path.join(out, f"grid-ledger-{pattern}.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh)
        wr.writerow(["n", "date", "time_madrid", "type", "ground", "hook", "published"])
        for n, r in enumerate(upcoming(start)):
            wr.writerow([n, r["date"], r["time_madrid"], r["type"], p["cycle"][n % len(p["cycle"])], hook_of(r), ""])
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["mock", "ledger", "cover", "contrast"])
    ap.add_argument("--pattern", default="all")
    ap.add_argument("--from", dest="start", default="2026-11-03")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--index", type=int, default=0)
    ap.add_argument("--hook", default="")
    ap.add_argument("--kind", default="REEL")
    ap.add_argument("--series", default="")
    a = ap.parse_args()
    names = list(PATTERNS) if a.pattern == "all" else [a.pattern]
    if a.cmd == "contrast":
        for g, (bg, fg, acc, quiet) in GROUNDS.items():
            print(f"{g:9s} hook {contrast(bg, fg):5.2f}  accent {contrast(bg, acc):5.2f}  quiet {contrast(bg, quiet):5.2f}")
    elif a.cmd == "mock":
        for n in names:
            path, rows = mock(n, a.start, a.out)
            print(path)
            for row in rows:
                print("  ", *row)
    elif a.cmd == "ledger":
        for n in names:
            print(ledger(n, "2026-11-02" if a.start == "2026-11-03" else a.start, a.out))
    else:
        p = PATTERNS[names[0]]
        g = p["cycle"][a.index % len(p["cycle"])]
        size = (W, H) if a.kind == "REEL" else (1080, 1350)
        cover(g, a.hook, a.kind, a.series, size).save(a.out, quality=92)
        print(a.out, g)


if __name__ == "__main__":
    main()
