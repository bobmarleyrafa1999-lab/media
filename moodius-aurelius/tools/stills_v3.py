#!/usr/bin/env python3
"""Render Moodius stills in the Phase 1 design system, with layout QC built in.

    python3 stills_v3.py spec.json out_dir

Same spec format and kinds as stills_v2.py (cover, quote, term, step, pair, signoff, story).
What v3 adds (20 Oct 2026 upload-pack QC):
  - every slide's content block is measured after drawing and placed on one optical centre,
    so the text does not jump up and down as you swipe;
  - balanced line breaks (no one-word last lines);
  - typographic quotes and apostrophes;
  - stories keep the top 250 px and bottom 300 px clear of Instagram's header and reply bar;
  - a hard check that nothing crosses the 96 px margins or the header/footer bands.
"""
import json, os, re, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from design import *

W = 1080
CENTRE = {1350: 655, 1920: 880}          # optical centre of the content block
SAFE = {1350: (190, 1350 - 200), 1920: (330, 1920 - 420)}   # content must stay inside
STORY_TOP = 250                           # stories: under Instagram's progress bar and name
STORY_BOTTOM = 300                        # stories: above the reply bar


def font(path, size):
    return ImageFont.truetype(path, size)


def smart(s):
    s = re.sub(r'(^|[\s(\[—–-])"', r'\1“', s)
    s = s.replace('"', '”')
    s = re.sub(r"(^|[\s(\[—–-])'", r"\1‘", s)
    return s.replace("'", "’")


def greedy(d, text, f, max_w):
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


def wrap(d, text, f, max_w):
    """Display type (60px+): balanced lines. Body type: full measure, but never a one-word last line."""
    text = smart(text)
    out = []
    for para in text.split("\n"):
        lines = greedy(d, para, f, max_w)
        if len(lines) > 1 and f.size < 60:
            w = max_w
            while (" " not in lines[-1]) and w > max_w * 0.6:
                w -= 8
                cand = greedy(d, para, f, w)
                if len(cand) > len(lines):
                    break
                if " " in cand[-1]:
                    lines = cand
                    break
        elif len(lines) > 1:
            lo, hi = max_w * 0.55, max_w
            for _ in range(14):
                mid = (lo + hi) / 2
                if len(greedy(d, para, f, mid)) == len(lines):
                    hi = mid
                else:
                    lo = mid
            lines = greedy(d, para, f, hi)
        out += lines
    return out


def tracked(d, xy, text, f, fill, track=0.18):
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


def frame(d, h, spec):
    m = MARGIN
    top = STORY_TOP if h > 1400 else m
    d.rectangle((m, top + 6, m + 14, top + 20), fill=EMBER)
    tracked(d, (m + 30, top), WORDMARK, font(BODY_SB, 26), BONE, 0.32)
    if spec.get("page"):
        f = font(BODY_M, 26)
        d.text((W - m - d.textlength(spec["page"], font=f), top), spec["page"], font=f, fill=ASH)
    bottom = h - (STORY_BOTTOM if h > 1400 else m) - 30
    f = font(BODY, 24)
    hx = W - m - d.textlength(HANDLE, font=f)
    d.text((hx, bottom), HANDLE, font=f, fill=ASH)
    if spec.get("cite"):
        fc = font(BODY_M, 24)
        cite = smart(spec["cite"]).upper()
        y = bottom if m + tracked_len(d, cite, fc, 0.12) + 24 < hx else bottom - 44
        tracked(d, (m, y), cite, fc, ASH, 0.12)


# ---------- content drawers: draw at y=0 on a tall scratch canvas ----------
MW = W - 2 * MARGIN


def c_cover(d, spec):
    m = MARGIN
    fk, fc, fs = font(BODY_SB, 30), font(DISPLAY, spec.get("size", 92)), font(BODY, 40)
    y = 200
    if spec.get("kicker"):
        tracked(d, (m, y - 70), smart(spec["kicker"]).upper(), fk, EMBER, 0.2)
    y = para(d, m, y, spec["claim"], fc, BONE, MW, 1.12)
    if spec.get("sub"):
        para(d, m, y + 40, spec["sub"], fs, ASH, MW, 1.35)


def c_quote(d, spec):
    m = MARGIN
    fq, fn = font(QUOTE, spec.get("size", 62)), font(BODY, 40)
    y = 300
    d.text((m - 6, y - 150), "“", font=font(DISPLAY_XB, 200), fill=EMBER)
    y = para(d, m, y, spec["quote"], fq, BONE, MW, 1.3)
    if spec.get("note"):
        d.rectangle((m, y + 30, m + 80, y + 33), fill=EMBER)
        para(d, m, y + 70, spec["note"], fn, ASH, MW, 1.4)


def c_term(d, spec):
    m = MARGIN
    ft, fg, fd = font(DISPLAY, spec.get("size", 84)), font(BODY_M, 28), font(BODY, 44)
    y = 200
    if spec.get("tag"):
        tracked(d, (m, y - 60), smart(spec["tag"]).upper(), fg, EMBER, 0.2)
    y = para(d, m, y, spec["term"], ft, BONE, MW, 1.1)
    d.rectangle((m, y + 24, W - m, y + 26), fill=CHARCOAL)
    para(d, m, y + 60, spec["definition"], fd, BONE, MW, 1.4)


def c_step(d, spec):
    m = MARGIN
    fnum, ft, fb = font(DISPLAY_XB, 170), font(DISPLAY, spec.get("size", 64)), font(BODY, 42)
    y = 200
    d.text((m - 4, y - 40), str(spec["n"]), font=fnum, fill=EMBER)
    y = para(d, m, y + 190, spec["title"], ft, BONE, MW, 1.15)
    para(d, m, y + 40, spec["body"], fb, ASH, MW, 1.4)


def c_pair(d, spec):
    m, gap = MARGIN, 48
    cw = (W - 2 * m - gap) / 2
    fh, fr, fn = font(BODY_SB, 28), font(BODY, spec.get("size", 38)), font(BODY, 36)
    rows = spec["rows"]
    hs = [max(len(wrap(d, l, fr, cw - 20)), len(wrap(d, r, fr, cw - 20))) * fr.size * 1.3 + 44 for l, r in rows]
    y = 200
    tracked(d, (m, y), smart(spec["left"]).upper(), fh, ASH, 0.18)
    tracked(d, (m + cw + gap, y), smart(spec["right"]).upper(), fh, EMBER, 0.18)
    y += 70
    d.rectangle((m + cw + gap - 4, y - 10, m + cw + gap - 2, y + sum(hs)), fill=CHARCOAL)
    for (l, r), rh in zip(rows, hs):
        d.rectangle((m, y, W - m, y + 1), fill=CHARCOAL)
        para(d, m, y + 22, l, fr, ASH, cw - 20, 1.3)
        para(d, m + cw + gap + 16, y + 22, r, fr, BONE, cw - 20, 1.3)
        y += rh
    if spec.get("note"):
        para(d, m, y + 40, spec["note"], fn, BONE, MW, 1.35)


def c_signoff(d, spec):
    m = MARGIN
    fl, fa = font(DISPLAY, spec.get("size", 76)), font(BODY_M, 38)
    y = para(d, m, 200, spec["line"], fl, BONE, MW, 1.15)
    d.rectangle((m, y + 24, m + 80, y + 27), fill=EMBER)
    if spec.get("action"):
        para(d, m, y + 60, spec["action"], fa, ASH, MW, 1.4)


STORY_STYLE = {"claim": (DISPLAY, 80, BONE, 1.15), "quote": (QUOTE, 62, BONE, 1.3),
               "body": (BODY, 44, BONE, 1.4), "small": (BODY_M, 32, ASH, 1.4)}


def c_story(d, spec):
    m = MARGIN
    y = 200
    tracked(d, (m, y - 90), smart(spec["label"]).upper(), font(BODY_SB, 30), EMBER, 0.24)
    for text, style in spec["lines"]:
        p, s, c, lh = STORY_STYLE[style]
        y = para(d, m, y, text, font(p, s), c, MW, lh) + 44


DRAW = {"cover": c_cover, "quote": c_quote, "term": c_term, "step": c_step, "pair": c_pair,
        "signoff": c_signoff, "story": c_story}


def render(spec):
    h = 1920 if spec["kind"] == "story" else 1350
    scratch = Image.new("RGB", (W, 2600), SLATE)
    DRAW[spec["kind"]](ImageDraw.Draw(scratch), spec)
    a = np.asarray(scratch).astype(int)
    rows = np.where((np.abs(a - np.array(SLATE)).sum(2) > 24).any(1))[0]
    top, bot = rows.min(), rows.max() + 1
    block = scratch.crop((0, top, W, bot))
    centre = spec.get("centre", CENTRE[h])
    y = int(round(centre - (bot - top) / 2))
    lo, hi = SAFE[h]
    if y < lo or y + (bot - top) > hi:
        raise ValueError(f"content too tall for the safe area ({bot - top}px); shorten the copy or lower 'size'")
    img = Image.new("RGB", (W, h), SLATE)
    img.paste(block, (0, y))
    d = ImageDraw.Draw(img)
    if spec["kind"] == "cover" and spec.get("swipe", True):
        f = font(BODY_M, 30)
        t = "Swipe  →"
        d.text((W - MARGIN - d.textlength(t, font=f), h - MARGIN - 110), t, font=f, fill=EMBER)
    if spec["kind"] == "signoff":
        d.text((MARGIN, h - MARGIN - 110), "Follow " + HANDLE, font=font(BODY_SB, 30), fill=EMBER)
    if spec["kind"] == "story" and spec.get("footer"):
        d.text((MARGIN, y + (bot - top) + 70), smart(spec["footer"]), font=font(BODY_M, 34), fill=EMBER)
    frame(d, h, spec)
    # margin check: nothing may cross the 96 px side margins
    a = np.asarray(img).astype(int)
    cols = np.where((np.abs(a - np.array(SLATE)).sum(2) > 60).any(0))[0]
    if cols.min() < MARGIN - 8 or cols.max() > W - MARGIN + 2:
        raise ValueError(f"text crosses the side margin ({cols.min()}..{cols.max()})")
    return img


if __name__ == "__main__":
    spec_path, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    for name, spec in json.load(open(spec_path)).items():
        out = os.path.join(out_dir, f"{name}.jpg")
        render(spec).save(out, quality=94)
        print(out)
