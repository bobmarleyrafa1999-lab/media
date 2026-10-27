#!/usr/bin/env python3
"""Covers for the four highlights the owner created on 27 Oct 2026. 1080x1920 story frames;
Instagram crops the centre circle. Pillow only."""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS, OUT = os.path.join(ROOT, "fonts"), os.path.join(ROOT, "highlights")
SLATE, BONE, ASH, EMBER, CHAR = "#1B1F24", "#F3EFE7", "#B8B3A9", "#C9742E", "#3A4049"
W, H = 1080, 1920
CX, CY = W // 2, H // 2


def glyph_zeno(d):      # Z of the Stoa: a porch column (stoa = porch)
    f = ImageFont.truetype(os.path.join(FONTS, "Playfair-SemiBold.ttf"), 300)
    d.text((CX - d.textlength("Z", font=f) / 2, CY - 210), "Z", font=f, fill=BONE)
    d.ellipse((CX + 100, CY + 70, CX + 136, CY + 106), fill=EMBER)


def glyph_resilience(d):  # a bent line that comes back up
    d.line([(CX - 200, CY - 60), (CX - 60, CY + 80), (CX + 40, CY + 20), (CX + 200, CY - 120)], fill=BONE, width=26, joint="curve")
    d.ellipse((CX + 182, CY - 138, CX + 218, CY - 102), fill=EMBER)


def glyph_training(d):    # a plain dumbbell
    d.rectangle((CX - 150, CY - 12, CX + 150, CY + 12), fill=BONE)
    for s in (-1, 1):
        d.rounded_rectangle((CX + s * 150 - 40, CY - 90, CX + s * 150 + 40, CY + 90), 14, fill=BONE)
    d.ellipse((CX - 18, CY + 120, CX + 18, CY + 156), fill=EMBER)


def glyph_reading(d):     # an open book
    d.polygon([(CX, CY - 40), (CX - 230, CY - 100), (CX - 230, CY + 110), (CX, CY + 160)], outline=BONE, width=14)
    d.polygon([(CX, CY - 40), (CX + 230, CY - 100), (CX + 230, CY + 110), (CX, CY + 160)], outline=BONE, width=14)
    d.ellipse((CX - 18, CY - 120, CX + 18, CY - 84), fill=EMBER)


COVERS = [("1-Zeno", glyph_zeno), ("2-Resilience", glyph_resilience),
          ("3-Training-Room", glyph_training), ("4-Reading", glyph_reading)]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    row = Image.new("RGB", (4 * 300 + 50, 350), SLATE)
    for i, (name, fn) in enumerate(COVERS):
        im = Image.new("RGB", (W, H), SLATE)
        d = ImageDraw.Draw(im)
        d.ellipse((CX - 420, CY - 420, CX + 420, CY + 420), outline=CHAR, width=4)
        fn(d)
        im.save(os.path.join(OUT, name + ".png"), optimize=True)
        crop = im.crop((CX - 440, CY - 440, CX + 440, CY + 440)).resize((260, 260))
        mask = Image.new("L", (260, 260), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, 259, 259), fill=255)
        row.paste(crop, (30 + i * 300, 20), mask)
        f = ImageFont.truetype(os.path.join(FONTS, "Inter-Medium.ttf"), 24)
        label = name.split("-", 1)[1].replace("-", " ")
        ImageDraw.Draw(row).text((30 + i * 300 + 130 - ImageDraw.Draw(row).textlength(label, font=f) / 2, 295), label, font=f, fill=ASH)
    row.save(os.path.join(OUT, "preview-row.png"))
    print("ok")
