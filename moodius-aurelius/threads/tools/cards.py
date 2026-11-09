"""Threads visuals for Moodius: profile picture and 4:5 post cards.

    python3 cards.py avatar            -> threads/profile/*.png
    python3 cards.py posts PLAN.json   -> threads/posts/cards/<date>.png
    python3 cards.py sheet PLAN.json   -> threads/posts/cards/_contact-sheet.png

Phase 1 rules: flat Slate ground, Bone type, one Ember accent; no statues, gold,
marble or gradients. Playfair for the claim, Inter for labels and citations.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "tools"))
from design import (SLATE, GRAPHITE, CHARCOAL, BONE, ASH, EMBER,  # noqa: E402
                    DISPLAY, QUOTE, BODY, BODY_SB, HANDLE, WORDMARK)

W, H = 1080, 1350
M = 96


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(text, f, width):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if f.getlength(trial) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(text, path, width, max_h, start, floor, lead):
    """Largest size (start..floor) whose wrapped block fits max_h."""
    for size in range(start, floor - 1, -2):
        f = font(path, size)
        lines = wrap(text, f, width)
        if len(lines) * size * lead <= max_h:
            return f, lines, size
    f = font(path, floor)
    return f, wrap(text, f, width), floor


def tracked(d, xy, text, f, fill, tracking):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill)
        x += f.getlength(ch) + tracking
    return x


# ---------- profile picture ----------
def avatar(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    S = 1080
    # A: monogram M with an Ember full stop (main)
    im = Image.new("RGB", (S, S), SLATE)
    d = ImageDraw.Draw(im)
    f = font(DISPLAY, 560)
    l, t, r, b = d.textbbox((0, 0), "M", font=f)
    gw, gh = r - l, b - t
    dot = 64
    x = (S - (gw + 26 + dot)) / 2 - l
    y = (S - gh) / 2 - t - 10
    d.text((x, y), "M", font=f, fill=BONE)
    dx = x + l + gw + 26
    dy = y + t + gh - dot
    d.ellipse([dx, dy, dx + dot, dy + dot], fill=EMBER)
    im.save(os.path.join(out_dir, "avatar-A-monogram.png"))

    # B: wordmark with Ember rule (alternative)
    im = Image.new("RGB", (S, S), SLATE)
    d = ImageDraw.Draw(im)
    f = font(BODY_SB, 92)
    track = 22
    tw = sum(f.getlength(c) for c in WORDMARK) + track * (len(WORDMARK) - 1)
    tracked(d, ((S - tw) / 2, S / 2 - 70), WORDMARK, f, BONE, track)
    d.rectangle([S / 2 - 60, S / 2 + 70, S / 2 + 60, S / 2 + 78], fill=EMBER)
    im.save(os.path.join(out_dir, "avatar-B-wordmark.png"))

    # preview: both at real size inside a circle mask, on light and dark feeds
    prev = Image.new("RGB", (900, 420), BONE)
    pd = ImageDraw.Draw(prev)
    prev.paste((24, 24, 24), [450, 0, 900, 420])
    lab = font(BODY, 22)
    for i, name in enumerate(["avatar-A-monogram.png", "avatar-B-wordmark.png"]):
        src = Image.open(os.path.join(out_dir, name))
        for j, (ox, col) in enumerate([(40, (40, 40, 40)), (490, (230, 230, 230))]):
            for k, size in enumerate([160, 44]):
                a = src.resize((size, size), Image.LANCZOS)
                mask = Image.new("L", (size, size), 0)
                ImageDraw.Draw(mask).ellipse([0, 0, size, size], fill=255)
                px = ox + i * 200 + (0 if k == 0 else 58)
                py = 60 if k == 0 else 260
                prev.paste(a, (px, py), mask)
            pd.text((ox + i * 200, 330), "A main" if i == 0 else "B alt", font=lab, fill=col)
    prev.save(os.path.join(out_dir, "_preview-in-feed.png"))


# ---------- post cards ----------
def card(p, out):
    im = Image.new("RGB", (W, H), SLATE)
    d = ImageDraw.Draw(im)
    label = font(BODY_SB, 26)
    tracked(d, (M, M), WORDMARK, label, ASH, 8)
    d.rectangle([M, M + 58, M + 72, M + 64], fill=EMBER)

    width = W - 2 * M
    top, bottom = M + 150, H - M - 210
    if "card_quote" in p:
        text, path, start, floor, lead = "“" + p["card_quote"] + "”", QUOTE, 74, 46, 1.32
    else:
        text, path, start, floor, lead = p["card_claim"], DISPLAY, 96, 56, 1.22
    text = text.replace("'", "\u2019")
    f, lines, size = fit(text, path, width, bottom - top, start, floor, lead)
    block = len(lines) * size * lead
    y = top + (bottom - top - block) / 2
    for ln in lines:
        d.text((M, y), ln, font=f, fill=BONE)
        y += size * lead

    cite_f = font(BODY, 28)
    cy = H - M - 130
    for ln in wrap(p["card_cite"], cite_f, width):
        d.text((M, cy), ln, font=cite_f, fill=ASH)
        cy += 40
    d.line([M, H - M - 20, W - M, H - M - 20], fill=CHARCOAL, width=2)
    d.text((M, H - M + 2), HANDLE, font=font(BODY, 24), fill=ASH)
    tag = p.get("topic", "")
    tf = font(BODY, 24)
    d.text((W - M - tf.getlength(tag), H - M + 2), tag, font=tf, fill=ASH)
    im.save(out, optimize=True)


def posts(plan, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    data = json.load(open(plan))
    made = []
    for p in data["posts"]:
        if "card" in p:
            out = os.path.join(out_dir, p["card"])
            card(p, out)
            made.append(out)
        assert len(p["text"]) <= 500, (p["date"], p["time"], len(p["text"]))
    return made


def sheet(plan, out_dir):
    data = json.load(open(plan))
    files = [os.path.join(out_dir, p["card"]) for p in data["posts"] if "card" in p]
    tw, th, cols = 270, 338, 4
    rows = (len(files) + cols - 1) // cols
    sh = Image.new("RGB", (cols * (tw + 20) + 20, rows * (th + 50) + 20), GRAPHITE)
    sd = ImageDraw.Draw(sh)
    lab = font(BODY, 18)
    for i, fp in enumerate(files):
        x = 20 + (i % cols) * (tw + 20)
        y = 20 + (i // cols) * (th + 50)
        sh.paste(Image.open(fp).resize((tw, th), Image.LANCZOS), (x, y))
        sd.text((x, y + th + 10), os.path.basename(fp)[:-4] + " 12:30", font=lab, fill=ASH)
    sh.save(os.path.join(out_dir, "_contact-sheet.png"))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "avatar":
        avatar(os.path.join(ROOT, "profile"))
    else:
        plan = sys.argv[2]
        out = os.path.join(ROOT, "posts", "cards")
        if cmd == "posts":
            print("\n".join(posts(plan, out)))
        sheet(plan, out)
