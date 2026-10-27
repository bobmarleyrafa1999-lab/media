#!/usr/bin/env python3
"""Moodius grid refresh (27 Oct 2026): post templates v2 and profile-grid mock-ups.

    python3 grid_v2.py mocks        # 3 options x (end state + 3-step transition) -> ../mocks
    python3 grid_v2.py samples      # full carousel + reel cover samples per option -> ../renders
    python3 grid_v2.py cover --option A --index 7 --kind carousel --label "Mind" --no 15 \
        --hook "Someone will *annoy* you today." --out x.png

Format v2, shared by every option:
  - bigger headline that fills the tile, so it still reads at grid size;
  - a pillar label (Mind / Body / People + post number) instead of the repeated wordmark;
  - one key word underlined with a hand-drawn Ember brush stroke (mark it with *stars* in the hook);
  - a thin inset frame, so every tile reads as one series of cards;
  - fine paper grain on every ground (hand-made texture, never a gradient).

Colour is chosen by the post's ORDER (cycle[n % len]), never by its grid position, so the pattern
survives every new post. Brand rules kept: no statues, gold, marble, gradients or AI stock.
"""
import argparse, os, re, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FONTS = os.path.join(ROOT, "fonts")
DISPLAY = os.path.join(FONTS, "Playfair-SemiBold.ttf")
ITALIC = os.path.join(FONTS, "Playfair-MediumItalic.ttf")
BODY = os.path.join(FONTS, "Inter-Regular.otf")
BODY_M = os.path.join(FONTS, "Inter-Medium.otf")
BODY_SB = os.path.join(FONTS, "Inter-SemiBold.otf")
HANDLE = "@moodiusaurelius"


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# Core palette (approved) + two warm additions for option C
SLATE, GRAPHITE, CHARCOAL = rgb("1B1F24"), rgb("2A2F36"), rgb("3A4049")
BONE, ASH, EMBER = rgb("F3EFE7"), rgb("B8B3A9"), rgb("C9742E")
OLIVE, SAND = rgb("4A4C37"), rgb("E4D9C4")

# ground -> background, ink (headline), accent (stroke, label square), quiet (label, handle), frame
GROUNDS = {
    "slate": dict(bg=SLATE, ink=BONE, accent=EMBER, quiet=ASH, frame=rgb("2E333B")),
    "bone": dict(bg=BONE, ink=SLATE, accent=EMBER, quiet=rgb("6E6A62"), frame=rgb("DCD5C8")),
    "ember": dict(bg=EMBER, ink=SLATE, accent=SLATE, quiet=rgb("3A2614"), frame=rgb("B5662A")),
    "olive": dict(bg=OLIVE, ink=BONE, accent=rgb("D98A45"), quiet=rgb("C9C3AE"), frame=rgb("5A5C46")),
    "sand": dict(bg=SAND, ink=SLATE, accent=EMBER, quiet=rgb("6E6656"), frame=rgb("CFC3AB")),
}

# Each option: end-state cycle, and the one new ground step 2 introduces on every other carousel.
OPTIONS = {
    "A": dict(name="Paper and ink", cycle=["bone", "slate"], step2="bone",
              blurb="Checkerboard: carousels on Bone paper, reels on Slate. Calm, editorial."),
    "B": dict(name="Ember thread", cycle=["bone", "slate", "ember", "slate"], step2="bone",
              blurb="Bone and Slate, with an Ember tile every 4th post that draws a diagonal line."),
    "C": dict(name="Three columns", cycle=["sand", "slate", "olive"], step2="sand",
              blurb="Sand, Slate and a new warm Olive in 3 repeating colours: one column each."),
}

W = 1080
SIZES = {"carousel": 1350, "reel": 1920}
SIDE = 112                       # text margin (grid crops 34 px off each side of a 4:5 post)
INSET = 52                       # frame inset


def font(p, s):
    return ImageFont.truetype(p, s)


def smart(s):
    s = re.sub(r'(^|[\s(\[—–-])"', r'\1“', s)
    s = s.replace('"', '”')
    s = re.sub(r"(^|[\s(\[—–-])'", r"\1‘", s)
    return s.replace("'", "’")


def grain(img, seed, amount=5.0):
    """Paper grain: fine noise plus a few faint fibres. No gradient, no vignette."""
    rng = np.random.default_rng(seed)
    a = np.asarray(img).astype(np.float32)
    h, w = a.shape[:2]
    n = rng.normal(0, amount, (h, w, 1))
    # slightly coarser mottling, upscaled from a small field
    small = rng.normal(0, amount * 0.6, (h // 6 + 1, w // 6 + 1)).astype(np.float32)
    mott = np.asarray(Image.fromarray(small).resize((w, h), Image.BILINEAR))[..., None]
    a = a + n + mott
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(out, "RGBA")
    base = np.asarray(img)[h // 2, 10].tolist()
    lum = sum(base) / 3
    tone = (0, 0, 0, 10) if lum > 128 else (255, 255, 255, 7)
    for _ in range(70):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        ang, ln = rng.uniform(0, np.pi), rng.uniform(20, 70)
        pts = [(x + np.cos(ang) * t + rng.normal(0, 1.2), y + np.sin(ang) * t + rng.normal(0, 1.2))
               for t in np.linspace(0, ln, 6)]
        d.line(pts, fill=tone, width=1)
    return out


def brush(d, x0, x1, y, color, seed, weight=11):
    """Hand-drawn underline: tapered, slightly wavy, three jittered passes."""
    rng = np.random.default_rng(seed)
    x0 -= 6
    x1 += 10
    n = 40
    xs = np.linspace(x0, x1, n)
    lift = rng.uniform(-6, 2)                     # stroke rises a touch to the right
    wave = rng.uniform(1.5, 3.0)
    ph = rng.uniform(0, 6.28)
    for p in range(3):
        jy = rng.normal(0, 1.2)
        for i in range(n - 1):
            t = i / (n - 1)
            taper = np.sin(np.pi * min(1, t * 1.15 + 0.04)) ** 0.6
            wdt = max(2, weight * taper * (0.85 + 0.25 * p / 2) + rng.normal(0, 0.8))
            ya = y + lift * t + wave * np.sin(ph + t * 5) + jy
            yb = y + lift * (t + 1 / n) + wave * np.sin(ph + (t + 1 / n) * 5) + jy
            d.line([(xs[i], ya), (xs[i + 1], yb)], fill=color, width=int(round(wdt)))


def layout(d, text, f, max_w):
    """Split into lines; returns list of lists of (word, marked)."""
    words = []
    for tok in re.findall(r"\*[^*]+\*\S*|\S+", text):
        if tok.startswith("*"):
            inner_, tail = tok[1:].split("*", 1)
            parts = inner_.split()
            parts[-1] += tail
            for w in parts:
                words.append((w, True))
        else:
            words.append((tok, False))
    lines, cur = [], []
    for w in words:
        cand = " ".join(x for x, _ in cur + [w])
        if cur and d.textlength(cand, font=f) > max_w:
            lines.append(cur)
            cur = [w]
        else:
            cur.append(w)
    lines.append(cur)
    # avoid a one-word last line when it can be balanced
    if len(lines) > 1 and len(lines[-1]) == 1 and len(lines[-2]) > 2:
        lines[-1].insert(0, lines[-2].pop())
    return lines


def headline(d, hook, top, g, seed, max_w, size, kind):
    hook = smart(hook)
    for s in range(size, 52, -4):
        f = font(DISPLAY, s)
        lines = layout(d, hook, f, max_w)
        if len(lines) <= (5 if kind == "reel" else 4):
            break
    lh = f.size * 1.14
    ascent = f.getmetrics()[0]
    y = top
    marks, words = [], []
    for ln in lines:
        x = SIDE
        run = None
        for i, (w, m) in enumerate(ln):
            txt = w + (" " if i < len(ln) - 1 else "")
            wl = d.textlength(w.rstrip(".,:;?!"), font=f) if m else d.textlength(w, font=f)
            if m:
                run = (run[0] if run else x, x + wl)
            elif run:
                marks.append((run, y)); run = None
            words.append((x, y, w))
            x += d.textlength(txt, font=f)
        if run:
            marks.append((run, y))
        y += lh
    # the stroke goes down first, just under the baseline, so descenders sit on top of it
    for k, ((a, b), ly) in enumerate(marks):
        brush(d, a, b, ly + ascent + f.size * 0.13, g["accent"], seed + k, weight=max(8, f.size // 9))
    for x, wy, w in words:
        d.text((x, wy), w, font=f, fill=g["ink"])
    return y


def tile(hook, ground="slate", kind="carousel", label="Mind", no=None, seed=1, sub=None,
         size=None, swipe=True):
    """One grid cover (carousel slide 1 or reel cover) in format v2."""
    g = GROUNDS[ground]
    h = SIZES[kind]
    img = grain(Image.new("RGB", (W, h), g["bg"]), seed)
    d = ImageDraw.Draw(img)
    band = (0, h) if kind == "carousel" else (240, 1680)      # what the 3:4 grid shows
    # frame
    fy0, fy1 = band[0] + INSET, band[1] - INSET
    d.rectangle((INSET, fy0, W - INSET, fy1), outline=g["frame"], width=3)
    # label
    ly = fy0 + 64
    d.rectangle((SIDE, ly + 8, SIDE + 14, ly + 22), fill=g["accent"])
    lab = label.upper() + (f"  ·  NO. {no}" if no else "")
    x = SIDE + 32
    fl = font(BODY_SB, 27)
    for ch in lab:
        d.text((x, ly), ch, font=fl, fill=g["quiet"])
        x += d.textlength(ch, font=fl) + 27 * 0.2
    # headline, placed in the upper-middle of the visible band
    top = band[0] + (300 if kind == "carousel" else 330)
    y = headline(d, hook, top, g, seed, W - 2 * SIDE, size or (104 if kind == "carousel" else 110), kind)
    if sub:
        fs = font(BODY, 40)
        y += 34
        for ln in layout(d, smart(sub), fs, W - 2 * SIDE):
            d.text((SIDE, y), " ".join(w for w, _ in ln), font=fs, fill=g["quiet"])
            y += 54
    # footer
    fy = fy1 - 64 - 26
    d.text((SIDE, fy), HANDLE, font=font(BODY, 26), fill=g["quiet"])
    if kind == "carousel" and swipe:
        t = "Swipe  →"
        fsw = font(BODY_M, 28)
        d.text((W - SIDE - d.textlength(t, font=fsw), fy - 2), t, font=fsw, fill=g["accent"])
    return img


def inner(title, body, ground, n, total, seed, label="Mind"):
    """Inner carousel slide in format v2 (same frame, quieter type)."""
    g = GROUNDS[ground]
    img = grain(Image.new("RGB", (W, 1350), g["bg"]), seed)
    d = ImageDraw.Draw(img)
    d.rectangle((INSET, INSET, W - INSET, 1350 - INSET), outline=g["frame"], width=3)
    ly = INSET + 64
    d.rectangle((SIDE, ly + 8, SIDE + 14, ly + 22), fill=g["accent"])
    fl = font(BODY_SB, 27)
    d.text((SIDE + 32, ly), label.upper(), font=fl, fill=g["quiet"])
    pg = f"{n}/{total}"
    d.text((W - SIDE - d.textlength(pg, font=fl), ly), pg, font=fl, fill=g["quiet"])
    y = headline(d, title, 330, g, seed, W - 2 * SIDE, 76, "carousel")
    fb = font(BODY, 42)
    y += 40
    for ln in layout(d, smart(body), fb, W - 2 * SIDE):
        d.text((SIDE, y), " ".join(w for w, _ in ln), font=fb, fill=g["ink"] if ground != "ember" else SLATE)
        y += 60
    d.text((SIDE, 1350 - INSET - 90), HANDLE, font=font(BODY, 26), fill=g["quiet"])
    return img


# ---------------------------------------------------------------- old look (for the transition mock)
def old_tile(hook, kind="carousel", seed=1):
    h = SIZES[kind]
    img = Image.new("RGB", (W, h), SLATE)
    d = ImageDraw.Draw(img)
    top = 0 if kind == "carousel" else 240
    m = 96
    d.rectangle((m, top + m + 6, m + 14, top + m + 20), fill=EMBER)
    x = m + 30
    for ch in "MOODIUS":
        d.text((x, top + m), ch, font=font(BODY_SB, 26), fill=BONE)
        x += d.textlength(ch, font=font(BODY_SB, 26)) + 26 * 0.32
    f = font(DISPLAY, 78)
    y = top + 420
    for ln in layout(d, smart(hook.replace("*", "")), f, W - 2 * m):
        d.text((m, y), " ".join(w for w, _ in ln), font=f, fill=BONE)
        y += 90
    d.rectangle((m, y + 24, m + 80, y + 27), fill=EMBER)
    d.text((m, top + (1350 if kind == "carousel" else 1440) - m - 30), HANDLE, font=font(BODY, 24), fill=ASH)
    return img


# ---------------------------------------------------------------- grid mock
def grid_crop(img, kind):
    """What the profile grid shows: a 3:4 crop."""
    if kind == "carousel":
        cw = int(1350 * 3 / 4)
        x = (W - cw) // 2
        return img.crop((x, 0, x + cw, 1350))
    return img.crop((0, 240, W, 1680))


def mock(tiles, cols=3, tw=360, gap=4, title=None):
    th = int(tw * 4 / 3)
    rows = (len(tiles) + cols - 1) // cols
    head = 70 if title else 0
    out = Image.new("RGB", (cols * tw + (cols - 1) * gap, head + rows * th + (rows - 1) * gap), (255, 255, 255))
    d = ImageDraw.Draw(out)
    if title:
        d.text((16, 20), title, font=font(BODY_SB, 26), fill=SLATE)
    for i, (img, kind) in enumerate(tiles):
        t = grid_crop(img, kind).resize((tw, th), Image.LANCZOS)
        out.paste(t, ((i % cols) * (tw + gap), head + (i // cols) * (th + gap)))
        if kind == "reel":
            px, py = (i % cols) * (tw + gap) + tw - 30, head + (i // cols) * (th + gap) + 14
            dd = ImageDraw.Draw(out)
            dd.polygon([(px, py), (px, py + 18), (px + 15, py + 9)], fill=(255, 255, 255))
    return out


# Sample posts, newest first. Real hooks from the queue and recent posts; reels marked.
POSTS = [
    ("You can forgive them and still not *let them back in.*", "reel", "People"),
    ("Three short books you can read *free* tonight.", "carousel", "Mind"),
    ("Knowing vs *doing*: a short honest chart.", "carousel", "Mind"),
    ("Someone will *annoy* you today. Decide now.", "reel", "People"),
    ("Strong body, *quiet* mind.", "carousel", "Body"),
    ("Being busy is the most respectable way to *avoid yourself.*", "carousel", "Mind"),
    ("You checked their profile again. Here's *what it cost.*", "reel", "People"),
    ("Nobody taught you how to call a friend *for no reason.*", "carousel", "People"),
    ("The friends you keep are *training* you for something.", "carousel", "People"),
    ("You rehearse the lie in the *shower* first.", "reel", "Mind"),
    ("Is discipline self-respect or *self-punishment?*", "carousel", "Body"),
    ("When did you last say what you felt, *out loud?*", "carousel", "People"),
]
OLD = [
    "Nobody tells you grief comes back in the supermarket.",
    "People I've said “I'm fine” to:",
    "You drive past a place you used to be someone else in.",
]


def ground_for(option, n, step, kind):
    """Ground of the post n places into a step (n counts from the newest post of the step)."""
    o = OPTIONS[option]
    if step == 1:
        return "slate"
    if step == 2:
        return o["step2"] if (kind == "carousel" and n % 2 == 0) else "slate"
    return o["cycle"][n % len(o["cycle"])]


def end_state(option):
    tiles = []
    for i, (hook, kind, lab) in enumerate(POSTS):
        # n counts from the oldest post so the pattern is anchored the way it will be published
        n = len(POSTS) - 1 - i
        g = OPTIONS[option]["cycle"][n % len(OPTIONS[option]["cycle"])]
        tiles.append((tile(hook, g, kind, lab, no=40 - i, seed=100 + i), kind))
    return tiles


def transition(option):
    """Top row = step 3, then step 2, step 1, bottom row = today's look."""
    tiles = []
    steps = [3, 3, 3, 2, 2, 2, 1, 1, 1]
    for i, step in enumerate(steps):
        hook, kind, lab = POSTS[i]
        n = len(steps) - 1 - i
        g = ground_for(option, n, step, kind)
        tiles.append((tile(hook, g, kind, lab, no=40 - i, seed=200 + i), kind))
    for j, h in enumerate(OLD):
        tiles.append((old_tile(h, "carousel", seed=j), "carousel"))
    return tiles


def cmd_mocks(out):
    os.makedirs(out, exist_ok=True)
    for k, o in OPTIONS.items():
        m = mock(end_state(k), title=f"Option {k} · {o['name']} · how the top 12 look from 16 Nov")
        m.save(os.path.join(out, f"option-{k}-end-state.png"), optimize=True)
        m = mock(transition(k), title=f"Option {k} · bottom row today → top row 16 Nov")
        m.save(os.path.join(out, f"option-{k}-transition.png"), optimize=True)
        print("mock", k)


SAMPLE = dict(
    hook="Being busy is the most respectable way to *avoid yourself.*",
    slides=[("Busy is *allowed.*", "Nobody asks a busy person how they are. That is the point of it."),
            ("The test", "If the diary emptied tomorrow, what would you have to sit with?"),
            ("An old idea", "Seneca's point, in our words: life feels short when we spend it on things we never chose. (Moodius paraphrase of On the Shortness of Life.)"),
            ("So, today:", "Leave one gap in the day on purpose. Ten minutes, no phone. Busy or brave?")],
)


def cmd_samples(out):
    os.makedirs(out, exist_ok=True)
    for k, o in OPTIONS.items():
        g = o["cycle"][0]
        d = os.path.join(out, f"option-{k}")
        os.makedirs(d, exist_ok=True)
        tile(SAMPLE["hook"], g, "carousel", "Mind", no=41, seed=7).save(os.path.join(d, "carousel-01.png"))
        for i, (t, b) in enumerate(SAMPLE["slides"], start=2):
            inner(t, b, g, i, len(SAMPLE["slides"]) + 1, seed=7 + i).save(os.path.join(d, f"carousel-{i:02d}.png"))
        for gname in sorted(set(o["cycle"])):
            tile("You can forgive them and still not *let them back in.*", gname, "reel", "People", no=42,
                 seed=9).save(os.path.join(d, f"reel-cover-{gname}.png"))
        print("samples", k)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["mocks", "samples", "cover"])
    ap.add_argument("--option", default="A")
    ap.add_argument("--index", type=int, default=0, help="post number since the step-3 anchor")
    ap.add_argument("--kind", default="carousel", choices=["carousel", "reel"])
    ap.add_argument("--ground", help="override the ground the pattern would choose")
    ap.add_argument("--label", default="Mind")
    ap.add_argument("--no", type=int)
    ap.add_argument("--hook")
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.cmd == "mocks":
        cmd_mocks(a.out or os.path.join(ROOT, "mocks"))
    elif a.cmd == "samples":
        cmd_samples(a.out or os.path.join(ROOT, "renders"))
    else:
        cyc = OPTIONS[a.option]["cycle"]
        g = a.ground or cyc[a.index % len(cyc)]
        tile(a.hook, g, a.kind, a.label, a.no, seed=a.index).save(a.out)
        print(a.out, g)


if __name__ == "__main__":
    main()
