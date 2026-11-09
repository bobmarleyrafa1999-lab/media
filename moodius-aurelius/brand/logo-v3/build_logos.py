"""Moodius Aurelius logo options v3: warm, approachable, in the current page shades.

Same outputs as logo-v2 (outlined SVG + PNG avatar, dark/light lockups,
320px circle preview, comparison.png) with a warm earth palette and motifs
taken from the Stoics: the Stoa (the painted porch the school is named
after), the olive branch, the arch of a reading room.

    python3 build_logos.py

Reuses the type helpers in ../logo-v2/build_logos.py.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "logo-v2"))
import build_logos as v2  # noqa: E402
from build_logos import IN_SB, PF_IT, PF_SB, PF_XB, svg, text, width  # noqa: E402

# Surafel's current page shades (Phase 1), mapped onto the warm motifs.
SLATE, GRAPHITE, CHARCOAL = "#1B1F24", "#2A2F36", "#3A4049"
BONE, ASH, EMBER = "#F3EFE7", "#B8B3A9", "#C9742E"
C = {
    "walnut": SLATE,       # dark ground
    "olive_d": GRAPHITE,   # second dark ground
    "olive": CHARCOAL,
    "sage": ASH,
    "terracotta": EMBER,   # the warm pop
    "ochre": ASH,
    "clay": ASH,
    "parchment": BONE,     # light ground
    "ink": SLATE,
}
TAG = "STOICISM FOR PEOPLE WHO FEEL THINGS"


# ---------------------------------------------------------------- shapes

def stoa(cx, base, w, colours, roof, step=None):
    """Flat Stoa: pediment, lintel, four painted columns, two steps."""
    s = w / 600
    h_col = 300 * s
    col_w = 62 * s
    gap = (w - 4 * col_w - 60 * s) / 3
    x0 = cx - w / 2 + 30 * s
    top = base - 40 * s - h_col
    out = []
    for i in range(4):
        x = x0 + i * (col_w + gap)
        out.append(f'<rect x="{x:.1f}" y="{top:.1f}" width="{col_w:.1f}" height="{h_col:.1f}" '
                   f'rx="{6*s:.1f}" fill="{colours[i % len(colours)]}"/>')
    lin = top - 46 * s
    out.append(f'<rect x="{cx - w/2:.1f}" y="{lin:.1f}" width="{w:.1f}" height="{38*s:.1f}" rx="{6*s:.1f}" fill="{roof}"/>')
    pk = lin - 120 * s
    out.append(f'<path d="M{cx - w/2 - 10*s:.1f} {lin - 10*s:.1f} L{cx:.1f} {pk:.1f} '
               f'L{cx + w/2 + 10*s:.1f} {lin - 10*s:.1f} Z" fill="{roof}" stroke="{roof}" '
               f'stroke-width="{12*s:.1f}" stroke-linejoin="round"/>')
    step = step or roof
    out.append(f'<rect x="{cx - w/2:.1f}" y="{base - 32*s:.1f}" width="{w:.1f}" height="{14*s:.1f}" rx="{5*s:.1f}" fill="{step}"/>')
    out.append(f'<rect x="{cx - w/2 - 30*s:.1f}" y="{base - 12*s:.1f}" width="{w + 60*s:.1f}" height="{14*s:.1f}" rx="{5*s:.1f}" fill="{step}"/>')
    return "".join(out)


def leaf(x, y, length, angle, fill):
    """Olive leaf: a pointed ellipse from (x, y) along angle (degrees)."""
    L, Wd = length, length * 0.30
    d = (f"M0 0 C{L*0.30:.1f} {-Wd:.1f} {L*0.75:.1f} {-Wd*0.8:.1f} {L:.1f} 0 "
         f"C{L*0.75:.1f} {Wd*0.8:.1f} {L*0.30:.1f} {Wd:.1f} 0 0 Z")
    return f'<path transform="translate({x:.1f} {y:.1f}) rotate({angle})" d="{d}" fill="{fill}"/>'


def sprig(x, y, scale, stem, leaves, berry=None):
    """Olive sprig rising to the upper right from (x, y)."""
    s = scale
    out = [f'<path d="M{x:.1f} {y:.1f} Q{x + 60*s:.1f} {y - 40*s:.1f} {x + 150*s:.1f} {y - 170*s:.1f}" '
           f'fill="none" stroke="{stem}" stroke-width="{9*s:.1f}" stroke-linecap="round"/>']
    spots = [(0.22, -150, 1), (0.40, -10, 1), (0.58, -135, 0.95), (0.74, 5, 0.9), (0.90, -115, 0.85)]
    for t, ang, k in spots:
        # point on the quadratic stem
        px = (1 - t) ** 2 * x + 2 * (1 - t) * t * (x + 60 * s) + t * t * (x + 150 * s)
        py = (1 - t) ** 2 * y + 2 * (1 - t) * t * (y - 40 * s) + t * t * (y - 170 * s)
        out.append(leaf(px, py, 96 * s * k, ang, leaves))
    out.append(leaf(x + 150 * s, y - 170 * s, 90 * s, -62, leaves))
    if berry:
        out.append(f'<circle cx="{x + 92*s:.1f}" cy="{y - 64*s:.1f}" r="{15*s:.1f}" fill="{berry}"/>')
    return "".join(out)


def arch(cx, base, w, h, stroke, sw, fill="none"):
    r = w / 2
    d = (f"M{cx - r:.1f} {base:.1f} L{cx - r:.1f} {base - h + r:.1f} "
         f"A{r:.1f} {r:.1f} 0 0 1 {cx + r:.1f} {base - h + r:.1f} L{cx + r:.1f} {base:.1f}")
    if fill != "none":
        d += " Z"
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>'


# ---------------------------------------------------------------- A Painted Porch
# The Stoics are named after the Stoa Poikile, the painted porch in Athens.
# Four columns, each a different earth pigment.

PAINT = [EMBER, BONE, ASH, EMBER]
PAINT_LIGHT = [EMBER, CHARCOAL, ASH, EMBER]


def a_mark(dark=True):
    roof = C["parchment"] if dark else C["walnut"]
    body = stoa(540, 790, 600, PAINT if dark else PAINT_LIGHT, roof)
    return svg(1080, 1080, body, C["walnut"] if dark else C["parchment"])


def a_lockup(dark=True):
    W, H = 2000, 640
    fg = C["parchment"] if dark else C["walnut"]
    sub = C["ochre"] if dark else C["terracotta"]
    body = stoa(400, 470, 330, PAINT if dark else PAINT_LIGHT, fg)
    t, _ = text(PF_SB, "Moodius Aurelius", 136, 680, 330, fg, "start")
    tag, _ = text(IN_SB, TAG, 30, 684, 410, sub, "start", tracking=0.26)
    return svg(W, H, body + t + tag, C["walnut"] if dark else C["parchment"])


# ---------------------------------------------------------------- B Olive & Ink
# Italic serif set like a signature, with an olive sprig (Athena's tree,
# the tree of Athens where the Stoa stood).

def b_mark(dark=True):
    bg = C["olive_d"] if dark else C["parchment"]
    fg = C["parchment"] if dark else C["olive_d"]
    leaves = C["sage"] if dark else C["olive"]
    size = 640
    m, w = text(PF_IT, "M", size, 0, 0, fg, "start")
    base = 540 + PF_IT.cap * size / PF_IT.upm / 2 + 10
    m, _ = text(PF_IT, "M", size, 540 - w / 2 - 110, base, fg, "start")
    body = sprig(700, 830, 1.15, leaves, leaves, C["terracotta"]) + m
    return svg(1080, 1080, body, bg)


def b_lockup(dark=True):
    W, H = 2000, 640
    bg = C["olive_d"] if dark else C["parchment"]
    fg = C["parchment"] if dark else C["olive_d"]
    leaves = C["sage"] if dark else C["olive"]
    sub = C["clay"] if dark else C["terracotta"]
    t, w = text(PF_IT, "Moodius Aurelius", 176, W / 2 - 70, 350, fg)
    body = sprig(W / 2 + w / 2 - 10, 330, 0.75, leaves, leaves, C["terracotta"]) + t
    tag, _ = text(IN_SB, TAG, 32, W / 2, 470, sub, tracking=0.30)
    return svg(W, H, body + tag, bg)


# ---------------------------------------------------------------- C Ember Point
# The current "M." kept, warmed: walnut ground, parchment M, terracotta point.
# The easiest change for people who already know the page.

def c_mark(dark=True):
    fg = C["parchment"] if dark else C["walnut"]
    size = 640
    _, w = text(PF_XB, "M", size, 0, 0, fg, "start")
    r, gap = 46, 22
    x0 = 540 - (w + gap + 2 * r) / 2
    base = 540 + PF_XB.cap * size / PF_XB.upm / 2
    m, _ = text(PF_XB, "M", size, x0, base, fg, "start")
    body = m + f'<circle cx="{x0 + w + gap + r:.1f}" cy="{base - r:.1f}" r="{r}" fill="{C["terracotta"]}"/>'
    return svg(1080, 1080, body, C["walnut"] if dark else C["parchment"])


def c_lockup(dark=True):
    W, H = 2000, 640
    fg = C["parchment"] if dark else C["walnut"]
    sub = C["sage"] if dark else C["olive"]
    word = "Moodius Aurelius"
    size = 190
    w = width(PF_XB, word, size, 0.005)
    r = 15
    x0 = (W - (w + 12 + 2 * r)) / 2
    t, _ = text(PF_XB, word, size, x0, 345, fg, "start", 0.005)
    tag, _ = text(IN_SB, TAG, 34, W / 2, 470, sub, tracking=0.32)
    body = t + f'<circle cx="{x0 + w + 12 + r:.1f}" cy="{345 - r:.1f}" r="{r}" fill="{C["terracotta"]}"/>' + tag
    return svg(W, H, body, C["walnut"] if dark else C["parchment"])


# ---------------------------------------------------------------- D Reading Room
# An arch, like a porch opening or a library window, framing the M.
# Soft terracotta ground: the friendliest of the four.

def d_mark(dark=True):
    bg = C["terracotta"] if dark else C["parchment"]
    fg = C["parchment"] if dark else C["terracotta"]
    inner = C["walnut"]
    body = arch(540, 880, 560, 700, fg, 26, fill=fg if dark else C["clay"])
    msize = 420
    body += text(PF_XB, "M", msize, 540, 760, inner if dark else C["walnut"])[0]
    body += f'<rect x="{540 - 300}" y="866" width="600" height="26" rx="13" fill="{fg if dark else C["terracotta"]}"/>'
    return svg(1080, 1080, body, bg)


def d_lockup(dark=True):
    W, H = 2000, 640
    bg = C["walnut"] if dark else C["parchment"]
    fg = C["parchment"] if dark else C["walnut"]
    body = arch(400, 500, 250, 330, C["terracotta"], 0, fill=C["terracotta"])
    body += text(PF_XB, "M", 190, 400, 455, C["parchment"])[0]
    body += f'<rect x="{400 - 150}" y="494" width="300" height="14" rx="7" fill="{C["ochre"]}"/>'
    t1, w1 = text(PF_SB, "Moodius ", 138, 600, 330, fg, "start")
    t2, _ = text(PF_IT, "Aurelius", 138, 600 + w1, 330, C["terracotta"] if not dark else C["clay"], "start")
    tag, _ = text(IN_SB, TAG, 30, 604, 410, C["sage"] if dark else C["olive"], "start", tracking=0.26)
    return svg(W, H, body + t1 + t2 + tag, bg)


v2.OPTIONS = {
    "A-painted-porch": (a_mark, a_lockup),
    "B-olive-and-ink": (b_mark, b_lockup),
    "C-ember-point": (c_mark, c_lockup),
    "D-reading-room": (d_mark, d_lockup),
}
v2.HERE, v2.SVG_DIR, v2.PNG_DIR = HERE, HERE / "svg", HERE / "png"

if __name__ == "__main__":
    v2.main()
