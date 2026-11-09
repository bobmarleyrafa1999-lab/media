"""Instagram highlight covers v2 for Moodius Aurelius.

One cover per highlight, each with its own icon, alternating light (Bone)
and dark (Slate) grounds so the row reads as seven separate circles.
Manifesto leads on Ember. Current page shades only.

    python3 build_highlights.py   # covers/*.png + *.svg, preview-row.png

Reuses the type helpers in ../logo-v2/build_logos.py.
"""
import io
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "logo-v2"))
import cairosvg  # noqa: E402
from build_logos import FONTS, PF_XB, text  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

SLATE, CHARCOAL, BONE, ASH, EMBER = "#1B1F24", "#3A4049", "#F3EFE7", "#B8B3A9", "#C9742E"
W, H, CX, CY = 1080, 1920, 540, 960
SW = 30  # stroke width, thick enough to survive the 64px highlight circle


def line(d, colour, sw=SW):
    return (f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def manifesto(fg, acc):
    size = 430
    _, w = text(PF_XB, "M", size, 0, 0, fg, "start")
    r, gap = 34, 16
    x0 = CX - (w + gap + 2 * r) / 2
    base = CY + PF_XB.cap * size / PF_XB.upm / 2
    m, _ = text(PF_XB, "M", size, x0, base, fg, "start")
    return m + f'<circle cx="{x0 + w + gap + r:.1f}" cy="{base - r:.1f}" r="{r}" fill="{acc}"/>'


def daily(fg, acc):
    y = 1050
    out = f'<path d="M{CX - 130} {y} A130 130 0 0 1 {CX + 130} {y} Z" fill="{acc}"/>'
    for ang in (-150, -115, -90, -65, -30):
        import math
        a = math.radians(ang)
        x1, y1 = CX + 175 * math.cos(a), y + 175 * math.sin(a)
        x2, y2 = CX + 235 * math.cos(a), y + 235 * math.sin(a)
        out += line(f"M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}", fg)
    out += line(f"M{CX - 230} {y} L{CX + 230} {y}", fg)
    out += line(f"M{CX - 140} {y + 70} L{CX + 140} {y + 70}", fg)
    return out


def tools(fg, acc):
    out = f'<circle cx="{CX}" cy="{CY}" r="200" fill="none" stroke="{fg}" stroke-width="{SW}"/>'
    out += f'<path d="M{CX} {CY - 150} L{CX + 46} {CY} L{CX - 46} {CY} Z" fill="{acc}"/>'
    out += f'<path d="M{CX} {CY + 150} L{CX + 46} {CY} L{CX - 46} {CY} Z" fill="{fg}"/>'
    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        out += line(f"M{CX + dx*200} {CY + dy*200} L{CX + dx*240} {CY + dy*240}", fg, 22)
    return out


def discipline(fg, acc):
    base, step, w = 1140, 115, 130
    x0 = CX - 1.5 * w
    out = ""
    for i in range(3):
        h = step * (i + 1)
        colour = acc if i == 2 else fg
        out += f'<rect x="{x0 + i*w + 8}" y="{base - h}" width="{w - 16}" height="{h}" rx="12" fill="{colour}"/>'
    out += line(f"M{x0 - 40} {base + 40} L{x0 + 3*w + 40} {base + 40}", fg)
    return out


def truths(fg, acc):
    out = (f'<path d="M{CX} 760 C{CX + 75} 860 {CX + 85} 950 {CX} 985 '
           f'C{CX - 85} 950 {CX - 75} 860 {CX} 760 Z" fill="{acc}"/>')
    out += line(f"M{CX} 985 L{CX} 1020", fg, 14)
    out += f'<rect x="{CX - 55}" y="1020" width="110" height="150" rx="12" fill="{fg}"/>'
    out += f'<rect x="{CX - 130}" y="1170" width="260" height="26" rx="13" fill="{fg}"/>'
    return out


def journal(fg, acc):
    out = line(f"M{CX} 880 Q{CX - 100} 820 {CX - 225} 845 L{CX - 225} 1105 "
               f"Q{CX - 100} 1080 {CX} 1140 Z", fg)
    out += line(f"M{CX} 880 Q{CX + 100} 820 {CX + 225} 845 L{CX + 225} 1105 "
                f"Q{CX + 100} 1080 {CX} 1140 Z", fg)
    out += f'<path d="M{CX + 70} 842 L{CX + 120} 836 L{CX + 120} 1000 L{CX + 95} 975 L{CX + 70} 1000 Z" fill="{acc}"/>'
    for i in range(3):
        y = 930 + i * 55
        out += line(f"M{CX - 170} {y} Q{CX - 100} {y - 10} {CX - 50} {y + 8}", fg, 16)
    return out


def identity(fg, acc):
    out = f'<ellipse cx="{CX}" cy="925" rx="150" ry="190" fill="none" stroke="{fg}" stroke-width="{SW}"/>'
    out += line(f"M{CX - 80} 880 A100 120 0 0 1 {CX - 20} 790", acc, 22)
    out += line(f"M{CX} 1115 L{CX} 1170", fg)
    out += f'<rect x="{CX - 110}" y="1165" width="220" height="28" rx="14" fill="{fg}"/>'
    return out


# name, draw, ground, icon colour, accent
COVERS = [
    ("1-manifesto", "Manifesto", manifesto, EMBER, BONE, SLATE),
    ("2-daily", "Daily", daily, BONE, SLATE, EMBER),
    ("3-tools", "Tools", tools, SLATE, BONE, EMBER),
    ("4-discipline", "Discipline", discipline, BONE, SLATE, EMBER),
    ("5-truths", "Truths", truths, SLATE, BONE, EMBER),
    ("6-journal", "Journal", journal, BONE, SLATE, EMBER),
    ("7-identity", "Identity", identity, SLATE, BONE, EMBER),
]


def main():
    out = HERE / "covers"
    out.mkdir(exist_ok=True)
    imgs = []
    for slug, label, draw, ground, fg, acc in COVERS:
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
               f'<rect width="{W}" height="{H}" fill="{ground}"/>{draw(fg, acc)}</svg>')
        (out / f"{slug}.svg").write_text(svg)
        data = cairosvg.svg2png(bytestring=svg.encode())
        im = Image.open(io.BytesIO(data)).convert("RGB")
        im.save(out / f"{slug}.png")
        imgs.append((label, im))
    preview(imgs)


def preview(imgs):
    """The highlight row as it shows on the profile, light and dark mode."""
    d, gap, pad = 200, 60, 60
    font = ImageFont.truetype(str(FONTS / "Inter-Medium.ttf"), 26)
    rows = []
    for page, ink, ring in (("#FFFFFF", "#111111", "#DBDBDB"), ("#000000", "#F5F5F5", "#363636")):
        row = Image.new("RGB", (pad * 2 + len(imgs) * d + (len(imgs) - 1) * gap, d + 110), page)
        dr = ImageDraw.Draw(row)
        for i, (label, im) in enumerate(imgs):
            x = pad + i * (d + gap)
            sq = im.crop((0, CY - 540, 1080, CY + 540)).resize((d * 4, d * 4), Image.LANCZOS)
            mask = Image.new("L", sq.size, 0)
            ImageDraw.Draw(mask).ellipse((24, 24, sq.size[0] - 25, sq.size[1] - 25), fill=255)
            disc = Image.new("RGB", sq.size, page)
            disc.paste(sq, (0, 0), mask)
            dd = ImageDraw.Draw(disc)
            dd.ellipse((4, 4, sq.size[0] - 5, sq.size[1] - 5), outline=ring, width=8)
            row.paste(disc.resize((d, d), Image.LANCZOS), (x, 30))
            tw = dr.textlength(label, font=font)
            dr.text((x + d / 2 - tw / 2, d + 50), label, fill=ink, font=font)
        rows.append(row)
    sheet = Image.new("RGB", (rows[0].width, sum(r.height for r in rows)))
    sheet.paste(rows[0], (0, 0))
    sheet.paste(rows[1], (0, rows[0].height))
    sheet.save(HERE / "preview-row.png")


if __name__ == "__main__":
    main()
