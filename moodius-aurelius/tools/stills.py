#!/usr/bin/env python3
"""Render still images in the Moodius Aurelius style from a JSON spec.

    python3 stills.py spec.json out_dir

spec.json: {"name": {"kind": "story|cover|slide|meme", ...fields}, ...}
  story  1080x1920  label, lines (list of [text, "quote|body|cite|small"]), footer
  cover  1080x1920  glyph, word            (highlight cover; keep art inside the centre circle)
  slide  1080x1350  label, lines, footer   (carousel slide / feed post)
  meme   1080x1350  panels: [[setup, punch], ...], cite
"""
import json, os, random, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONTS = "/usr/share/fonts/truetype/freefont/"
SERIF, SERIFB, SERIFI = FONTS + "FreeSerif.ttf", FONTS + "FreeSerifBold.ttf", FONTS + "FreeSerifItalic.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
STONE, CREAM, GOLD, MUTED = (27, 29, 31), (237, 230, 214), (201, 168, 106), (160, 152, 138)
HANDLE = "@moodiusaurelius"
STYLES = {  # font, size, colour, line spacing, gap after
    "quote": (SERIFI, 70, CREAM, 1.28, 36),
    "big": (SERIFB, 84, CREAM, 1.22, 40),
    "body": (SERIF, 54, CREAM, 1.32, 30),
    "cite": (SERIF, 42, GOLD, 1.3, 40),
    "small": (SANS, 34, MUTED, 1.35, 20),
}


def background(w, h, seed):
    rnd = random.Random(seed)
    img = Image.new("RGB", (w, h), STONE)
    noise = Image.effect_noise((w // 2, h // 2), 26).resize((w, h)).filter(ImageFilter.GaussianBlur(2))
    img = Image.blend(img, Image.merge("RGB", [noise] * 3), 0.10)
    vig = Image.new("L", (w, h), 0)
    ImageDraw.Draw(vig).ellipse((-w * 0.25, -h * 0.15, w * 1.25, h * 1.15), fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(w // 5))
    dark = Image.new("RGB", (w, h), (8, 9, 10))
    img = Image.composite(img, dark, vig)
    # faint diagonal veins, like marble
    d = ImageDraw.Draw(img)
    for _ in range(5):
        x, y = rnd.randint(-200, w), rnd.randint(0, h)
        pts = [(x + i * 40, y + rnd.randint(-30, 30) + i * rnd.choice([18, 24, 30])) for i in range(40)]
        d.line(pts, fill=(44, 46, 48), width=2)
    return img.filter(ImageFilter.GaussianBlur(0.6))


def wrap(draw, text, font, max_w):
    out = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split(" "):
            cand = f"{cur} {word}".strip()
            if cur and draw.textlength(cand, font=font) > max_w:
                out.append(cur)
                cur = word
            else:
                cur = cand
        out.append(cur)
    return out


def block(draw, lines, w, max_w):
    """Lay out [(text, style)] and return [(x, y, line, font, colour)] centred on 0."""
    items, y = [], 0
    for text, style in lines:
        path, size, colour, ls, gap = STYLES[style]
        font = ImageFont.truetype(path, size)
        for ln in wrap(draw, text, font, max_w):
            tw = draw.textlength(ln, font=font)
            items.append(((w - tw) / 2, y, ln, font, colour))
            y += size * ls
        y += gap
    return items, y


def frame(img, label=None, footer=None, top=200):
    w, h = img.size
    d = ImageDraw.Draw(img)
    mono = ImageFont.truetype(SERIFB, 44)
    d.text(((w - d.textlength("M · A", font=mono)) / 2, top), "M · A", font=mono, fill=GOLD)
    d.line(((w / 2 - 100, top + 70), (w / 2 + 100, top + 70)), fill=GOLD, width=2)
    if label:
        f = ImageFont.truetype(SANS, 30)
        spaced = " ".join(label.upper())
        d.text(((w - d.textlength(spaced, font=f)) / 2, top + 100), spaced, font=f, fill=MUTED)
    f = ImageFont.truetype(SANS, 36)
    d.text(((w - d.textlength(HANDLE, font=f)) / 2, h - top - 40), HANDLE, font=f, fill=(*CREAM,))
    if footer:
        f = ImageFont.truetype(SANS, 34)
        d.text(((w - d.textlength(footer, font=f)) / 2, h - top - 120), footer, font=f, fill=GOLD)


def text_card(spec, w, h, seed, top):
    img = background(w, h, seed)
    d = ImageDraw.Draw(img)
    items, total = block(d, [tuple(x) for x in spec["lines"]], w, w - 200)
    y0 = (h - total) / 2 + spec.get("nudge", 0)
    for x, y, ln, font, colour in items:
        d.text((x + 2, y0 + y + 3), ln, font=font, fill=(0, 0, 0))
        d.text((x, y0 + y), ln, font=font, fill=colour)
    frame(img, spec.get("label"), spec.get("footer"), top)
    return img


def cover(spec, seed):
    w, h = 1080, 1920
    img = background(w, h, seed)
    d = ImageDraw.Draw(img)
    cx, cy, r = w / 2, h / 2, 330
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=GOLD, width=6)
    g = ImageFont.truetype(SERIFB, spec.get("size", 300))
    bb = d.textbbox((0, 0), spec["glyph"], font=g)
    d.text((cx - (bb[0] + bb[2]) / 2, cy - (bb[1] + bb[3]) / 2 - 30), spec["glyph"], font=g, fill=GOLD)
    f = ImageFont.truetype(SANS, 44)
    word = " ".join(spec["word"].upper())
    d.text((cx - d.textlength(word, font=f) / 2, cy + r - 130), word, font=f, fill=CREAM)
    return img


def meme(spec, seed):
    w, h = 1080, 1350
    img = Image.new("RGB", (w, h), (245, 241, 232))
    d = ImageDraw.Draw(img)
    y = spec.get("top", 360)
    for setup, punch in spec["panels"]:
        for text, path, size, colour in ((setup, SANS, 46, (40, 40, 40)), (punch, SERIFI, 60, (20, 20, 20))):
            font = ImageFont.truetype(path, size)
            for ln in wrap(d, text, font, w - 160):
                d.text((80, y), ln, font=font, fill=colour)
                y += size * 1.3
            y += 30
        y += 40
    f = ImageFont.truetype(SERIF, 38)
    d.text((80, y), spec["cite"], font=f, fill=(140, 110, 60))
    f = ImageFont.truetype(SANS, 32)
    d.text((80, h - 110), HANDLE, font=f, fill=(120, 120, 120))
    return img


def render(name, spec, out_dir, seed):
    kind = spec["kind"]
    if kind == "story":
        img = text_card(spec, 1080, 1920, seed, top=230)
    elif kind == "slide":
        img = text_card(spec, 1080, 1350, seed, top=90)
    elif kind == "cover":
        img = cover(spec, seed)
    elif kind == "meme":
        img = meme(spec, seed)
    else:
        raise SystemExit(f"unknown kind {kind}")
    out = os.path.join(out_dir, f"{name}.jpg")
    img.save(out, quality=92)
    print(out)


if __name__ == "__main__":
    spec_path, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    with open(spec_path) as f:
        specs = json.load(f)
    for i, (name, spec) in enumerate(specs.items()):
        render(name, spec, out_dir, 100 + i)
