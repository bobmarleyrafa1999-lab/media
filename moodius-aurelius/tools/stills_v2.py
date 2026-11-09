#!/usr/bin/env python3
"""Render Moodius stills in the Phase 1 design system (flat Slate, Bone, one Ember accent).

    python3 stills_v2.py spec.json out_dir

spec.json: {"name": {"kind": ..., ...}, ...}. Every kind takes optional "page" ("2/7") and "cite"
(printed in small caps, bottom left). Carousel kinds are 1080x1350; "story" is 1080x1920.

  cover    kicker, claim, [sub], [swipe=true]          claim cover / Quiet Truth card
  quote    quote, [note]                               pull quote
  term     term, [tag], definition                     term card
  step     n, title, body                              numbered step
  pair     left, right, rows: [[l, r], ...], [note]    pair slide (two columns)
  signoff  line, [action]                              sign-off
  story    label, lines: [[text, "claim|quote|body|small"]], [footer]
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
from design import *

W = 1080


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, f, max_w):
    out = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split(" "):
            cand = f"{cur} {word}".strip()
            if cur and d.textlength(cand, font=f) > max_w:
                out.append(cur)
                cur = word
            else:
                cur = cand
        out.append(cur)
    return out


def tracked(d, xy, text, f, fill, track=0.18):
    """Draw caps with letter-spacing; returns the width drawn."""
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + f.size * track
    return x - xy[0]


def tracked_len(d, text, f, track=0.18):
    return sum(d.textlength(ch, font=f) + f.size * track for ch in text)


def para(d, x, y, text, f, fill, max_w, lh=1.25):
    for ln in wrap(d, text, f, max_w):
        d.text((x, y), ln, font=f, fill=fill)
        y += f.size * lh
    return y


def para_h(d, text, f, max_w, lh=1.25):
    return len(wrap(d, text, f, max_w)) * f.size * lh


def frame(d, h, spec):
    m = MARGIN
    d.rectangle((m, m + 6, m + 14, m + 20), fill=EMBER)
    tracked(d, (m + 30, m), WORDMARK, font(BODY_SB, 26), BONE, 0.32)
    if spec.get("page"):
        f = font(BODY_M, 26)
        d.text((W - m - d.textlength(spec["page"], font=f), m), spec["page"], font=f, fill=ASH)
    bottom = h - (260 if h > 1400 else m) - 30   # stories keep clear of Instagram's reply bar
    f = font(BODY, 24)
    hx = W - m - d.textlength(HANDLE, font=f)
    d.text((hx, bottom), HANDLE, font=f, fill=ASH)
    if spec.get("cite"):
        fc = font(BODY_M, 24)
        y = bottom if m + tracked_len(d, spec["cite"].upper(), fc, 0.12) + 24 < hx else bottom - 44
        tracked(d, (m, y), spec["cite"].upper(), fc, ASH, 0.12)


def canvas(h):
    img = Image.new("RGB", (W, h), SLATE)
    return img, ImageDraw.Draw(img)


def cover(spec, h=1350):
    img, d = canvas(h)
    m, mw = MARGIN, W - 2 * MARGIN
    fk, fc, fs = font(BODY_SB, 30), font(DISPLAY, spec.get("size", 92)), font(BODY, 40)
    blocks = para_h(d, spec["claim"], fc, mw, 1.12) + (para_h(d, spec["sub"], fs, mw, 1.35) + 40 if spec.get("sub") else 0)
    y = (h - blocks) / 2 - 20
    if spec.get("kicker"):
        tracked(d, (m, y - 70), spec["kicker"].upper(), fk, EMBER, 0.2)
    y = para(d, m, y, spec["claim"], fc, BONE, mw, 1.12)
    if spec.get("sub"):
        para(d, m, y + 40, spec["sub"], fs, ASH, mw, 1.35)
    if spec.get("swipe", True):
        f = font(BODY_M, 30)
        t = "Swipe  →"
        d.text((W - m - d.textlength(t, font=f), h - m - 110), t, font=f, fill=EMBER)
    frame(d, h, spec)
    return img


def quote(spec, h=1350):
    img, d = canvas(h)
    m, mw = MARGIN, W - 2 * MARGIN
    fq, fn = font(QUOTE, spec.get("size", 62)), font(BODY, 40)
    total = para_h(d, spec["quote"], fq, mw, 1.3) + (para_h(d, spec["note"], fn, mw, 1.4) + 70 if spec.get("note") else 0)
    y = (h - total) / 2
    d.text((m - 6, y - 150), "“", font=font(DISPLAY_XB, 200), fill=EMBER)
    y = para(d, m, y, spec["quote"], fq, BONE, mw, 1.3)
    if spec.get("note"):
        d.rectangle((m, y + 30, m + 80, y + 33), fill=EMBER)
        para(d, m, y + 70, spec["note"], fn, ASH, mw, 1.4)
    frame(d, h, spec)
    return img


def term(spec, h=1350):
    img, d = canvas(h)
    m, mw = MARGIN, W - 2 * MARGIN
    ft, fg, fd = font(DISPLAY, 84), font(BODY_M, 28), font(BODY, 44)
    total = para_h(d, spec["term"], ft, mw, 1.1) + 60 + para_h(d, spec["definition"], fd, mw, 1.4)
    y = (h - total) / 2
    if spec.get("tag"):
        tracked(d, (m, y - 60), spec["tag"].upper(), fg, EMBER, 0.2)
    y = para(d, m, y, spec["term"], ft, BONE, mw, 1.1)
    d.rectangle((m, y + 24, W - m, y + 26), fill=CHARCOAL)
    para(d, m, y + 60, spec["definition"], fd, BONE, mw, 1.4)
    frame(d, h, spec)
    return img


def step(spec, h=1350):
    img, d = canvas(h)
    m, mw = MARGIN, W - 2 * MARGIN
    fnum, ft, fb = font(DISPLAY_XB, 170), font(DISPLAY, 64), font(BODY, 42)
    total = 190 + para_h(d, spec["title"], ft, mw, 1.15) + 40 + para_h(d, spec["body"], fb, mw, 1.4)
    y = (h - total) / 2
    d.text((m - 4, y - 40), str(spec["n"]), font=fnum, fill=EMBER)
    y = para(d, m, y + 190, spec["title"], ft, BONE, mw, 1.15)
    para(d, m, y + 40, spec["body"], fb, ASH, mw, 1.4)
    frame(d, h, spec)
    return img


def pair(spec, h=1350):
    img, d = canvas(h)
    m = MARGIN
    gap = 48
    cw = (W - 2 * m - gap) / 2
    fh, fr, fn = font(BODY_SB, 28), font(BODY, 38), font(BODY, 36)
    rows = spec["rows"]
    heights = [max(para_h(d, l, fr, cw - 20, 1.3), para_h(d, r, fr, cw - 20, 1.3)) + 44 for l, r in rows]
    total = 80 + sum(heights) + (para_h(d, spec["note"], fn, W - 2 * m) + 40 if spec.get("note") else 0)
    y = max(m + 120, (h - total) / 2)
    tracked(d, (m, y), spec["left"].upper(), fh, ASH, 0.18)
    tracked(d, (m + cw + gap, y), spec["right"].upper(), fh, EMBER, 0.18)
    y += 70
    d.rectangle((m + cw + gap - 4, y - 10, m + cw + gap - 2, y + sum(heights)), fill=CHARCOAL)
    for (l, r), rh in zip(rows, heights):
        d.rectangle((m, y, W - m, y + 1), fill=CHARCOAL)
        para(d, m, y + 22, l, fr, ASH, cw - 20, 1.3)
        para(d, m + cw + gap + 16, y + 22, r, fr, BONE, cw - 20, 1.3)
        y += rh
    if spec.get("note"):
        para(d, m, y + 40, spec["note"], fn, BONE, W - 2 * m, 1.35)
    frame(d, h, spec)
    return img


def signoff(spec, h=1350):
    img, d = canvas(h)
    m, mw = MARGIN, W - 2 * MARGIN
    fl, fa = font(DISPLAY, 76), font(BODY_M, 38)
    total = para_h(d, spec["line"], fl, mw, 1.15) + 60 + (para_h(d, spec["action"], fa, mw, 1.4) if spec.get("action") else 0)
    y = (h - total) / 2
    y = para(d, m, y, spec["line"], fl, BONE, mw, 1.15)
    d.rectangle((m, y + 24, m + 80, y + 27), fill=EMBER)
    if spec.get("action"):
        para(d, m, y + 60, spec["action"], fa, ASH, mw, 1.4)
    f = font(BODY_SB, 30)
    t = "Follow " + HANDLE
    d.text((m, h - m - 110), t, font=f, fill=EMBER)
    frame(d, h, spec)
    return img


STORY_STYLE = {"claim": (DISPLAY, 80, BONE, 1.15), "quote": (QUOTE, 62, BONE, 1.3),
               "body": (BODY, 44, BONE, 1.4), "small": (BODY_M, 32, ASH, 1.4)}


def story(spec, h=1920):
    img, d = canvas(h)
    m, mw = MARGIN, W - 2 * MARGIN
    items = []
    for text, style in spec["lines"]:
        p, s, c, lh = STORY_STYLE[style]
        f = font(p, s)
        items.append((text, f, c, lh, para_h(d, text, f, mw, lh)))
    total = sum(i[4] for i in items) + 44 * (len(items) - 1)
    y = (h - total) / 2 - 120          # leave room under the text for a sticker
    tracked(d, (m, y - 90), spec["label"].upper(), font(BODY_SB, 30), EMBER, 0.24)
    for text, f, c, lh, ih in items:
        para(d, m, y, text, f, c, mw, lh)
        y += ih + 44
    if spec.get("footer"):
        d.text((m, h - 480), spec["footer"], font=font(BODY_M, 34), fill=EMBER)
    frame(d, h, spec)
    return img


KINDS = {"cover": cover, "quote": quote, "term": term, "step": step, "pair": pair,
         "signoff": signoff, "story": story}

if __name__ == "__main__":
    spec_path, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    for name, spec in json.load(open(spec_path)).items():
        img = KINDS[spec["kind"]](spec)
        out = os.path.join(out_dir, f"{name}.jpg")
        img.save(out, quality=92)
        print(out)
