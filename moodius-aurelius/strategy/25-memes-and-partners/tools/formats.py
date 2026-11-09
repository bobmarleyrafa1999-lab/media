#!/usr/bin/env python3
"""Moodius meme formats inspired by saved finds: text post, whiteboard table, hand-lettered sign, sketch scene.
Originals only. Uses meme_queue's pens (clean / Rough.js) and house palette. Needs Node.js for the sketched shapes.

  python3 tools/formats.py            # renders/formats/MT01.png ...
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import meme_queue as mq

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(mq.RENDERS, "formats")

C, W, H, M = mq.C, mq.W, mq.H, mq.M
FONTS = mq.FONTS   # Caveat (OFL) and Permanent Marker (Apache-2.0), licences beside them


def hand(size, weight=600):
    f = ImageFont.truetype(os.path.join(FONTS, "Caveat.ttf"), size)
    f.set_variation_by_axes([weight])
    return f


def marker(size):
    return ImageFont.truetype(os.path.join(FONTS, "PermanentMarker-Regular.ttf"), size)


def canvas():
    im = Image.new("RGB", (W, H), C["slate"])
    return im, ImageDraw.Draw(im)


def sign_off(d):
    f = mq._font("sans_sb", 26)
    d.text((W - M - d.textlength("moodius", font=f), H - 70), "moodius", font=f, fill=C["charcoal"])


def text_post(mid, text):
    im, d = canvas()
    f = mq._fit(d, text, "sans", W - 2 * M - 60, 7, 64, 44)
    lines = mq._wrap(d, text, f, W - 2 * M - 60)
    th = len(lines) * int(f.size * 1.32)
    ch = 150 + th + 60
    y0 = (H - ch) // 2
    d.rounded_rectangle((M - 30, y0, W - M + 30, y0 + ch), 28, fill=C["graphite"])
    # avatar: ember disc with a serif m (the page's own mark, no person)
    d.ellipse((M, y0 + 36, M + 84, y0 + 120), fill=C["ember"])
    fm = mq._font("serif", 52)
    d.text((M + 42 - d.textlength("m", font=fm) / 2, y0 + 44), "m", font=fm, fill=C["slate"])
    d.text((M + 108, y0 + 42), "Moodius", font=mq._font("sans_sb", 36), fill=C["bone"])
    d.text((M + 108, y0 + 86), "@moodiusaurelius", font=mq._font("sans", 30), fill=C["ash"])
    y = y0 + 150
    for ln in lines:
        d.text((M, y), ln, font=f, fill=C["bone"])
        y += int(f.size * 1.32)
    sign_off(d)
    return save(im, mid)


def whiteboard(mid, title, cols, rows, foot):
    im, d = canvas()
    pen = mq.RoughPen(d, mid)
    d.text((M, M - 10), title, font=hand(84, 700), fill=C["bone"])
    top, left, right = M + 150, M - 20, W - M + 20
    labw = 230
    colw = (right - left - labw) / len(cols)
    hy = top + 70
    for i, c in enumerate(cols):
        x = left + labw + i * colw + 14
        d.text((x, top - 6), c, font=hand(62, 700), fill=C["ember"] if i == len(cols) - 1 else C["ash"])
    pen.line((left, hy, right, hy), fill=C["bone"], width=4)
    pen.line((left + labw - 10, hy - 80, left + labw - 10, H - 300), fill=C["bone"], width=4)
    rh = (H - 300 - hy - 20) / len(rows)
    for r, (lab, *cells) in enumerate(rows):
        y = hy + 26 + r * rh
        mq._block(d, left, y, lab, hand(58, 700), C["bone"], labw - 20, 0.95)
        for i, cell in enumerate(cells):
            x = left + labw + i * colw + 14
            mq._block(d, x, y, cell, hand(54, 500), C["ember"] if i == len(cells) - 1 else C["bone"], colw - 24, 0.95)
        if r < len(rows) - 1:
            pen.line((left, y + rh - 26, right, y + rh - 26), fill=C["charcoal"], width=2)
    mq._block(d, M, H - 250, foot, mq._font("serif_it", 46), C["bone"], W - 2 * M)
    sign_off(d)
    return save(im, mid)


def sign(mid, lines, foot):
    im, d = canvas()
    pen = mq.RoughPen(d, mid)
    x0, y0, x1, y1 = 170, 170, W - 170, H - 330
    d.rectangle((x0 + 6, y0 + 6, x1 - 6, y1 - 6), fill=C["bone"])
    pen.rect((x0, y0, x1, y1), outline=C["ash"], width=5)
    tw = x1 - x0 - 110
    def fit(t, size):
        while size > 40 and max(d.textlength(w, font=marker(size)) for w in t.split()) > tw:
            size -= 4
        return size
    laid = []
    for text, colour, size in lines:
        size = fit(text, size)
        laid.append((mq._wrap(d, text, marker(size), tw), colour, size))
    total = sum(len(ls) * int(sz * 1.18) + 40 for ls, _, sz in laid) - 40
    y = (y0 + y1 - total) // 2
    for ls, colour, size in laid:
        for ln in ls:
            d.text((x0 + 55, y), ln, font=marker(size), fill=C[colour])
            y += int(size * 1.18)
        y += 40
    mq._block(d, M, H - 250, foot, mq._font("serif_it", 46), C["bone"], W - 2 * M)
    sign_off(d)
    return save(im, mid)


def sketch_sandwich(mid, setup, punch):
    im, d = canvas()
    pen = mq.RoughPen(d, mid)
    mq._block(d, M, M + 20, setup, hand(80, 700), C["bone"], W - 2 * M, 1.0)
    cx, cy = W // 2, 800
    # night window with moon, then plate and sandwich on the counter
    pen.rect((W - M - 320, 300, W - M, 600), outline=C["ash"], width=4)
    pen.line((W - M - 160, 300, W - M - 160, 600), fill=C["ash"], width=3)
    pen.ellipse((W - M - 270, 350, W - M - 190, 430), outline=C["bone"], width=5)
    d.text((M, 330), "01:07", font=hand(96, 700), fill=C["ember"])
    pen.ellipse((cx - 400, cy + 70, cx + 400, cy + 260), outline=C["ash"], width=6)
    pen.rect((cx - 280, cy - 70, cx + 280, cy - 10), fill=C["ash"], outline=C["bone"], width=5)
    pen.rect((cx - 265, cy - 10, cx + 265, cy + 50), fill=C["ember"], outline=C["ember"], width=5)
    pen.rect((cx - 280, cy + 50, cx + 280, cy + 110), fill=C["ash"], outline=C["bone"], width=5)
    pen.line((M - 40, cy + 300, W - M + 40, cy + 290), fill=C["charcoal"], width=5)
    mq._block(d, M, H - 240, punch, mq._font("serif", 72), C["bone"], W - 2 * M)
    sign_off(d)
    return save(im, mid)


def save(im, mid):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, mid + ".png")
    im.save(p, optimize=True)
    return p


if __name__ == "__main__":
    print(text_post("MT01", "Nobody prepares for a conversation quite like someone who is never going to have it."))
    print(text_post("MT02", "Marcus Aurelius wrote a whole book reminding himself to stay calm, and probably never meant anyone else to read it. Most relatable thing an emperor has ever done."))
    print(text_post("MT03", "The Stoics practised imagining losing everything. My phone runs the same drill every evening at 3%."))
    print(whiteboard("MW01", "Getting through a bad day",
                     ["65 AD", "2009", "Now"],
                     [("Say it", "Write a friend a long letter", "Post a vague status", "Story, deleted after 4 min"),
                      ("Get advice", "Ask a philosopher", "Ask a forum", "Read the comments"),
                      ("Calm down", "Long walk", "Long drive", "Long scroll")],
                     "Seneca's letters to Lucilius were the first option. They're still in print."))
    print(sign("MS01", [("I'M NOT OVERTHINKING.", "slate", 92), ("I'M DRAFTING.", "ember", 92)],
               "Nineteen versions. None of them sent."))
    print(sketch_sandwich("MD01", "Where every \"from Monday\" plan is made:", "The 1 a.m. sandwich."))
