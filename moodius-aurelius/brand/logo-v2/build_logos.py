"""Moodius Aurelius logo options v2 (earthy blue + green).

Builds four logo directions as outlined SVG (no font files needed to open them)
and PNG renders: avatar mark, dark lockup, light lockup, plus a 320px circle
preview of each avatar so legibility can be judged at Instagram size.

    python3 build_logos.py            # writes svg/, png/, comparison.png

Needs: fonttools, uharfbuzz, cairosvg, Pillow. Fonts live in ./fonts (OFL).
"""
import io
import math
import pathlib

import cairosvg
import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).parent
FONTS = HERE / "fonts"
SVG_DIR = HERE / "svg"
PNG_DIR = HERE / "png"

# Earthy blue + green palette. Bone stays as the light ground so the
# family still sits next to the existing Phase 1 posts.
C = {
    "ink": "#0F2229",        # Ink Petrol, darkest ground
    "spruce": "#163A31",     # Deep Spruce
    "pine": "#2A5A46",       # Pine
    "harbour": "#24506B",    # Harbour Blue
    "verdigris": "#45B096",  # Verdigris, the pop accent on dark
    "verdigris_d": "#2B7F6B",  # Verdigris for light grounds
    "lichen": "#B3D3A0",     # Lichen, light green
    "mist": "#AFCFE0",       # Mist Blue
    "bone": "#F3EFE7",
}


class Face:
    def __init__(self, filename):
        path = FONTS / filename
        self.tt = TTFont(path)
        self.glyphs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()
        self.upm = self.tt["head"].unitsPerEm
        self.cap = self.tt["OS/2"].sCapHeight
        blob = hb.Blob.from_file_path(str(path))
        self.hb = hb.Font(hb.Face(blob))

    def shape(self, text, tracking=0.0):
        """Kerned glyph run: [(glyph name, x in font units)], total advance."""
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hb, buf, {"kern": True, "liga": False})
        run, x = [], 0
        track = tracking * self.upm
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            run.append((self.order[info.codepoint], x + pos.x_offset, pos.x_advance))
            x += pos.x_advance + track
        return run, x - track


PF_XB = Face("Playfair-ExtraBold.ttf")
PF_SB = Face("Playfair-SemiBold.ttf")
PF_IT = Face("Playfair-MediumItalic.ttf")
IN_MD = Face("Inter-Medium.ttf")
IN_SB = Face("Inter-SemiBold.ttf")


def glyph_d(face, name, matrix):
    pen = SVGPathPen(face.glyphs)
    face.glyphs[name].draw(TransformPen(pen, matrix))
    return pen.getCommands()


def text(face, s, size, x, y, fill, anchor="middle", tracking=0.0):
    """Outlined text with baseline at y. Returns (svg, width_px)."""
    run, adv = face.shape(s, tracking)
    k = size / face.upm
    w = adv * k
    x0 = {"start": x, "middle": x - w / 2, "end": x - w}[anchor]
    d = "".join(glyph_d(face, g, (k, 0, 0, -k, x0 + gx * k, y)) for g, gx, _ in run)
    return f'<path fill="{fill}" d="{d}"/>', w


def width(face, s, size, tracking=0.0):
    return face.shape(s, tracking)[1] * size / face.upm


def arc_text(face, s, size, cx, cy, radius, fill, bottom=False, tracking=0.0):
    """Text set on a circle. Top arc reads clockwise with letters pointing out;
    bottom arc reads left to right with letters pointing in (both upright)."""
    run, adv = face.shape(s, tracking)
    k = size / face.upm
    total = adv * k
    parts = []
    for g, gx, ga in run:
        mid = (gx + ga / 2) * k - total / 2  # arc distance of glyph centre
        half = ga * k / 2
        if not bottom:
            th = mid / radius
            px, py = cx + radius * math.sin(th), cy - radius * math.cos(th)
            rot = th
        else:
            th = math.pi - mid / radius
            px, py = cx + radius * math.sin(th), cy - radius * math.cos(th)
            rot = th - math.pi
        cs, sn = math.cos(rot), math.sin(rot)
        # local glyph coords: lx = k*u - half, ly = -k*v ; rotate then move
        a, b = k * cs, k * sn
        c, d = k * sn, -k * cs
        e = px - cs * half
        f = py - sn * half
        parts.append(glyph_d(face, g, (a, b, c, d, e, f)))
    return f'<path fill="{fill}" d="{"".join(parts)}"/>'


def svg(w, h, body, bg=None):
    rect = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}">{rect}{body}</svg>')


# ---------------------------------------------------------------- option A
# "Verdigris Point": the current M. evolved. Heavier serif M, period in
# verdigris; wordmark is the full name ending on the same point.

def a_mark(dark=True):
    fg = C["bone"] if dark else C["ink"]
    dot = C["verdigris"] if dark else C["verdigris_d"]
    size = 640
    m, w = text(PF_XB, "M", size, 0, 0, fg, "start")
    r = 44
    gap = 22
    total = w + gap + 2 * r
    x0 = 540 - total / 2
    capy = 540 + PF_XB.cap * size / PF_XB.upm / 2
    m, _ = text(PF_XB, "M", size, x0, capy, fg, "start")
    body = m + f'<circle cx="{x0 + w + gap + r:.1f}" cy="{capy - r:.1f}" r="{r}" fill="{dot}"/>'
    return svg(1080, 1080, body, C["ink"] if dark else C["bone"])


def a_lockup(dark=True):
    fg = C["bone"] if dark else C["ink"]
    dot = C["verdigris"] if dark else C["verdigris_d"]
    sub = C["lichen"] if dark else C["pine"]
    W, H = 2000, 640
    size = 190
    word = "Moodius Aurelius"
    w = width(PF_XB, word, size, 0.005)
    r = 15
    x0 = (W - (w + 12 + 2 * r)) / 2
    base = 345
    t, _ = text(PF_XB, word, size, x0, base, fg, "start", 0.005)
    tag, _ = text(IN_SB, "STOICISM FOR PEOPLE WHO FEEL THINGS", 34, W / 2, 470, sub, tracking=0.32)
    body = t + f'<circle cx="{x0 + w + 12 + r:.1f}" cy="{base - r:.1f}" r="{r}" fill="{dot}"/>' + tag
    return svg(W, H, body, C["ink"] if dark else C["bone"])


# ---------------------------------------------------------------- option B
# "Spruce Stack": two-line serif, roman MOODIUS over italic Aurelius in
# lichen. Avatar is an upright M with an italic a tucked into it.

def b_mark(dark=True):
    fg = C["bone"] if dark else C["spruce"]
    acc = C["lichen"] if dark else C["pine"]
    sizeM, sizeA = 600, 460
    wm = width(PF_SB, "M", sizeM)
    wa = width(PF_IT, "a", sizeA)
    overlap = 40
    total = wm + wa - overlap
    x0 = 540 - total / 2
    base = 540 + PF_SB.cap * sizeM / PF_SB.upm / 2
    m, _ = text(PF_SB, "M", sizeM, x0, base, fg, "start")
    a, _ = text(PF_IT, "a", sizeA, x0 + wm - overlap, base, acc, "start")
    return svg(1080, 1080, m + a, C["spruce"] if dark else C["bone"])


def b_lockup(dark=True):
    fg = C["bone"] if dark else C["spruce"]
    acc = C["lichen"] if dark else C["pine"]
    W, H = 2000, 640
    top, _ = text(PF_SB, "MOODIUS", 168, W / 2, 300, fg, tracking=0.16)
    bot, _ = text(PF_IT, "Aurelius", 178, W / 2, 485, acc)
    return svg(W, H, top + bot, C["spruce"] if dark else C["bone"])


# ---------------------------------------------------------------- option C
# "Harbour Seal": a roundel. Name set around a ring, M at the centre,
# verdigris points either side. Works as a stamp on every post.

def seal(cx, cy, R, fg, ring, acc, fill=None):
    body = ""
    if fill:
        body += f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="{fill}"/>'
    s = R / 420  # designed at R = 420
    body += f'<circle cx="{cx}" cy="{cy}" r="{R - 8*s:.1f}" fill="none" stroke="{ring}" stroke-width="{7*s:.1f}"/>'
    body += f'<circle cx="{cx}" cy="{cy}" r="{R - 132*s:.1f}" fill="none" stroke="{ring}" stroke-width="{3.5*s:.1f}"/>'
    tsize = 76 * s
    capr = IN_SB.cap * tsize / IN_SB.upm
    mid = R - 70 * s
    body += arc_text(IN_SB, "MOODIUS", tsize, cx, cy, mid - capr / 2, fg, tracking=0.30)
    body += arc_text(IN_SB, "AURELIUS", tsize, cx, cy, mid + capr / 2, fg, bottom=True, tracking=0.30)
    for side in (-1, 1):
        body += f'<circle cx="{cx + side*mid:.1f}" cy="{cy}" r="{11*s:.1f}" fill="{acc}"/>'
    msize = 330 * s
    m, _ = text(PF_XB, "M", msize, cx, cy + PF_XB.cap * msize / PF_XB.upm / 2, fg)
    return body + m


def c_mark(dark=True):
    if dark:
        body = seal(540, 540, 470, C["bone"], C["mist"], C["verdigris"])
        return svg(1080, 1080, body, C["harbour"])
    body = seal(540, 540, 470, C["harbour"], C["harbour"], C["verdigris_d"])
    return svg(1080, 1080, body, C["bone"])


def c_lockup(dark=True):
    W, H = 2000, 640
    if dark:
        fg, ring, acc, bg, sub = C["bone"], C["mist"], C["verdigris"], C["harbour"], C["mist"]
    else:
        fg, ring, acc, bg, sub = C["harbour"], C["harbour"], C["verdigris_d"], C["bone"], C["pine"]
    body = seal(420, 320, 230, fg, ring, acc)
    t, _ = text(PF_SB, "Moodius Aurelius", 132, 740, 330, fg, "start")
    tag, _ = text(IN_SB, "STOICISM FOR PEOPLE WHO FEEL THINGS", 30, 744, 410, sub, "start", tracking=0.26)
    return svg(W, H, body + t + tag, bg)


# ---------------------------------------------------------------- option D
# "Horizon": a disc split into harbour blue (what you can't control) over
# pine green (the ground you stand on), M standing on the horizon line.

def horizon(cx, cy, R, top, bottom, line, fg):
    s = R / 400
    body = (f'<clipPath id="hz{int(cx)}{int(cy)}"><circle cx="{cx}" cy="{cy}" r="{R}"/></clipPath>'
            f'<g clip-path="url(#hz{int(cx)}{int(cy)})">'
            f'<rect x="{cx-R}" y="{cy-R}" width="{2*R}" height="{R + 70*s:.1f}" fill="{top}"/>'
            f'<rect x="{cx-R}" y="{cy + 70*s:.1f}" width="{2*R}" height="{R}" fill="{bottom}"/>'
            f'<rect x="{cx-R}" y="{cy + 66*s:.1f}" width="{2*R}" height="{8*s:.1f}" fill="{line}"/></g>')
    msize = 420 * s
    m, _ = text(PF_XB, "M", msize, cx, cy + 66 * s, fg)
    return body + m


def d_mark(dark=True):
    bg = C["ink"] if dark else C["bone"]
    # avatar: the split runs edge to edge so Instagram's circle crop is the disc
    if dark:
        s = 470 / 400
        msize = 420 * s
        m, _ = text(PF_XB, "M", msize, 540, 540 + 66 * s, C["bone"])
        body = (f'<rect width="1080" height="{540 + 70*s:.1f}" fill="{C["harbour"]}"/>'
                f'<rect y="{540 + 70*s:.1f}" width="1080" height="1080" fill="{C["pine"]}"/>'
                f'<rect y="{540 + 66*s:.1f}" width="1080" height="{8*s:.1f}" fill="{C["lichen"]}"/>' + m)
        return svg(1080, 1080, body)
    body = horizon(540, 540, 470, C["harbour"], C["pine"], C["lichen"], C["bone"])
    return svg(1080, 1080, body, bg)


def d_lockup(dark=True):
    W, H = 2000, 640
    bg = C["ink"] if dark else C["bone"]
    fg = C["bone"] if dark else C["ink"]
    acc = C["lichen"] if dark else C["pine"]
    body = horizon(390, 320, 220, C["harbour"], C["pine"], C["lichen"], C["bone"])
    t1, w1 = text(PF_SB, "Moodius ", 140, 690, 330, fg, "start")
    t2, _ = text(PF_IT, "Aurelius", 140, 690 + w1, 330, acc, "start")
    tag, _ = text(IN_SB, "STOICISM FOR PEOPLE WHO FEEL THINGS", 30, 694, 410, acc, "start", tracking=0.26)
    return svg(W, H, body + t1 + t2 + tag, bg)


OPTIONS = {
    "A-verdigris-point": (a_mark, a_lockup),
    "B-spruce-stack": (b_mark, b_lockup),
    "C-harbour-seal": (c_mark, c_lockup),
    "D-horizon": (d_mark, d_lockup),
}


def png(svg_text, out, width_px=None):
    data = cairosvg.svg2png(bytestring=svg_text.encode(), output_width=width_px)
    out.write_bytes(data)
    return Image.open(io.BytesIO(data)).convert("RGB")


def circle_preview(img, px):
    """Instagram-style circular crop at px diameter on white feed ground."""
    big = img.resize((px * 4, px * 4), Image.LANCZOS)
    mask = Image.new("L", big.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, big.size[0] - 1, big.size[1] - 1), fill=255)
    ground = Image.new("RGB", big.size, "white")
    ground.paste(big, (0, 0), mask)
    return ground.resize((px, px), Image.LANCZOS)


def main():
    SVG_DIR.mkdir(exist_ok=True)
    PNG_DIR.mkdir(exist_ok=True)
    renders = {}
    for key, (mark, lockup) in OPTIONS.items():
        files = {
            "avatar": mark(True),
            "avatar-light": mark(False),
            "lockup-dark": lockup(True),
            "lockup-light": lockup(False),
        }
        imgs = {}
        for name, s in files.items():
            (SVG_DIR / f"{key}-{name}.svg").write_text(s)
            imgs[name] = png(s, PNG_DIR / f"{key}-{name}.png")
        circle_preview(imgs["avatar"], 320).save(PNG_DIR / f"{key}-avatar-320-circle.png")
        renders[key] = imgs
    comparison(renders)


def comparison(renders):
    """One sheet: per option, dark lockup, light lockup, 320 + 110 px avatars."""
    W, row_h, pad = 2600, 560, 40
    sheet = Image.new("RGB", (W, pad + row_h * len(renders)), "#E9E6DF")
    draw = ImageDraw.Draw(sheet)
    label = ImageFont.truetype(str(FONTS / "Inter-SemiBold.ttf"), 34)
    for i, (key, imgs) in enumerate(renders.items()):
        y = pad + i * row_h
        draw.text((pad, y), key.replace("-", " ", 1).replace("-", " ").title(), fill="#1B1F24", font=label)
        y += 56
        for j, name in enumerate(("lockup-dark", "lockup-light")):
            im = imgs[name].resize((1000, 320), Image.LANCZOS)
            sheet.paste(im, (pad + j * 1030, y))
        sheet.paste(circle_preview(imgs["avatar"], 320), (pad + 2070, y))
        sheet.paste(circle_preview(imgs["avatar"], 110), (pad + 2070 + 340, y + 210))
    sheet.save(HERE / "comparison.png", optimize=True)


if __name__ == "__main__":
    main()
