"""Highlight covers v3: hand-inked look.

Every stroke is drawn with a broad calligraphy nib (thick and thin by
direction), wobbles slightly, overshoots its ends and tapers like a pen
lifting off paper. Ink edges are roughened and speckled, and the ground
has paper grain, so nothing reads as a clean vector icon.

    python3 build_highlights.py   # square/*.png, story/*.png, preview-row.png

Fixed seed, so every rebuild draws the same "hand".
"""
import math
import pathlib
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = pathlib.Path(__file__).parent
FONT = HERE.parent / "logo-v2" / "fonts" / "Inter-Medium.ttf"
SLATE, BONE, EMBER = (27, 31, 36), (243, 239, 231), (201, 116, 46)
PX = 2160          # drawing canvas, downscaled to 1080 at the end
K = PX / 1000      # design units are 0..1000
NIB = math.radians(35)
GROW = 1.15   # icons drawn a touch larger than designed
WIDTH = 1.35  # heavier pen so strokes survive the small highlight circle


def sc(x, y):
    return ((500 + (x - 500) * GROW) * K, (500 + (y - 500) * GROW) * K)


# ---------------------------------------------------------------- pen

class Wobble:
    """Smooth hand tremor: a few slow sines with random phase."""

    def __init__(self, rnd, amp):
        self.terms = [(rnd.uniform(0.6, 2.2), rnd.uniform(0, 6.3), amp * rnd.uniform(0.4, 1.0))
                      for _ in range(3)]

    def __call__(self, t):
        return sum(a * math.sin(f * t * math.tau + p) for f, p, a in self.terms)


def densify(points, step=1.5):
    out = [points[0]]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        out += [(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n) for i in range(1, n + 1)]
    return out


def line(a, b):
    return [a, b]


def arc(cx, cy, rx, ry, a0, a1, n=90):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def quad(p0, p1, p2, n=60):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])
            for t in (i / n for i in range(n + 1))]


class Sheet:
    def __init__(self, seed):
        self.rnd = random.Random(seed)
        self.layers = {}  # colour -> L mask

    def mask(self, colour):
        if colour not in self.layers:
            self.layers[colour] = Image.new("L", (PX, PX), 0)
        return self.layers[colour]

    def stroke(self, pts, colour, width=16, wobble=2.6, overshoot=5):
        """Broad-nib stroke with tremor, overshoot and tapered ends."""
        rnd = self.rnd
        pts = densify(pts)
        # overshoot: extend both ends a little along their direction
        for end in (0, -1):
            (xa, ya), (xb, yb) = (pts[0], pts[3]) if end == 0 else (pts[-1], pts[-4])
            d = math.hypot(xa - xb, ya - yb) or 1
            o = rnd.uniform(0, overshoot)
            ext = (xa + (xa - xb) / d * o, ya + (ya - yb) / d * o)
            pts = [ext] + pts if end == 0 else pts + [ext]
        length = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))
        span = max(length / 320, 0.15)  # tremor cycles scale with stroke length
        wobble *= min(1.0, 0.35 + length / 250)
        wx, wy, ww = Wobble(rnd, wobble), Wobble(rnd, wobble), Wobble(rnd, 0.18)
        draw = ImageDraw.Draw(self.mask(colour))
        n = len(pts)
        for i, (x, y) in enumerate(pts):
            t = i / (n - 1)
            j = min(i + 1, n - 1)
            k = max(i - 1, 0)
            ang = math.atan2(pts[j][1] - pts[k][1], pts[j][0] - pts[k][0])
            nib = 0.42 + 0.58 * abs(math.sin(ang - NIB))
            taper = min(1.0, t / 0.08, (1 - t) / 0.12) ** 0.6
            r = WIDTH * width / 2 * nib * (0.55 + 0.45 * taper) * (1 + ww(t * span))
            cx, cy = sc(x + wx(t * span), y + wy(t * span))
            rr = r * K * GROW
            draw.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=255)

    def blob(self, pts, colour, wobble=3.0):
        """Filled shape with a wobbly, hand-cut edge."""
        pts = densify(pts + [pts[0]], 3)
        wx, wy = Wobble(self.rnd, wobble), Wobble(self.rnd, wobble)
        n = len(pts)
        poly = [sc(x + wx(i / n), y + wy(i / n)) for i, (x, y) in enumerate(pts)]
        ImageDraw.Draw(self.mask(colour)).polygon(poly, fill=255)

    def render(self, ground):
        rnd = self.rnd
        img = Image.new("RGB", (PX, PX), ground)
        # paper: fine grain plus soft blotches
        grain = Image.effect_noise((PX, PX), 30)
        blot = Image.effect_noise((PX // 64, PX // 64), 30).resize((PX, PX), Image.BICUBIC)
        blot = blot.filter(ImageFilter.GaussianBlur(40))
        tex = ImageChops.blend(grain, blot, 0.5).point(lambda v: int(128 + (v - 128) * 0.3))
        img = ImageChops.add(img, Image.merge("RGB", [tex] * 3), 1, -128)
        for colour, m in self.layers.items():
            # roughen edges: soften, add noise, re-threshold
            noise = Image.effect_noise((PX, PX), 70)
            m = ImageChops.add(m.filter(ImageFilter.GaussianBlur(2.2)), noise, 1, -128)
            m = m.point(lambda v: 255 if v > 128 else 0).filter(ImageFilter.GaussianBlur(0.8))
            # uneven ink: letterpress speckle where the ink didn't take
            speck = Image.effect_noise((PX // 3, PX // 3), 90).resize((PX, PX), Image.BICUBIC)
            speck = speck.point(lambda v: 0 if v > 205 else 255)
            m = ImageChops.multiply(m, speck)
            m = m.point(lambda v: int(v * rnd.uniform(0.9, 0.97)))
            img.paste(Image.new("RGB", (PX, PX), colour), (0, 0), m)
        return img.resize((1080, 1080), Image.LANCZOS)


# ---------------------------------------------------------------- icons
# Drawn in a 1000 x 1000 square; Instagram shows roughly the middle 80%.

def manifesto(s, ink, acc):
    s.stroke(line((338, 668), (352, 338)), ink, 30)
    s.stroke(line((352, 338), (498, 640)), ink, 30)
    s.stroke(line((498, 640), (650, 334)), ink, 30)
    s.stroke(line((650, 334), (662, 670)), ink, 30)
    for x in (338, 662):
        s.stroke(line((x - 34, 676), (x + 36, 672)), ink, 14)
    s.stroke(line((318, 336), (378, 340)), ink, 14)
    s.stroke(line((626, 332), (686, 336)), ink, 14)
    s.blob(arc(742, 650, 25, 23, 0, 359, 40)[:-1], acc)


def daily(s, ink, acc):
    s.blob(arc(500, 600, 118, 112, 180, 360, 60), acc)
    s.stroke(arc(500, 600, 118, 112, 185, 355), ink, 12, wobble=2)
    for ang in (-160, -128, -90, -54, -22):
        a = math.radians(ang)
        s.stroke(line((500 + 160 * math.cos(a), 600 + 160 * math.sin(a)),
                      (500 + 225 * math.cos(a), 600 + 225 * math.sin(a))), ink, 18)
    s.stroke(line((285, 606), (718, 600)), ink, 18)
    s.stroke(line((345, 664), (650, 668)), ink, 14)
    s.stroke(line((410, 718), (585, 716)), ink, 12)


def tools(s, ink, acc):
    s.stroke(arc(500, 500, 196, 192, -80, 285), ink, 18)  # left open, overlaps like a pen loop
    s.blob([(500, 352), (538, 500), (462, 500)], acc)
    s.stroke([(500, 352), (538, 500), (500, 648), (462, 500), (500, 352)], ink, 9, wobble=1.2)
    for a in (-90, 0, 90, 180):
        r = math.radians(a)
        s.stroke(line((500 + 214 * math.cos(r), 500 + 214 * math.sin(r)),
                      (500 + 250 * math.cos(r), 500 + 250 * math.sin(r))), ink, 16)
    s.blob(arc(500, 500, 13, 13, 0, 359, 20)[:-1], ink)


def discipline(s, ink, acc):
    s.stroke([(285, 700), (375, 700), (375, 610), (465, 610), (465, 520),
              (555, 520), (555, 430), (645, 430), (645, 700)], ink, 18)
    s.stroke(line((262, 704), (735, 700)), ink, 18)
    s.stroke(line((600, 432), (602, 300)), ink, 12)
    s.blob([(602, 300), (690, 322), (604, 352)], acc)


def truths(s, ink, acc):
    s.blob(quad((500, 268), (580, 380), (500, 440)) + quad((500, 440), (420, 380), (500, 268))[1:], acc)
    s.stroke(line((500, 438), (502, 478)), ink, 9)
    s.stroke([(450, 480), (447, 690)], ink, 16)
    s.stroke([(552, 482), (556, 690)], ink, 16)
    s.stroke(line((446, 482), (556, 480)), ink, 12)
    s.stroke(quad((552, 500), (566, 530), (558, 560)), ink, 10)  # wax drip
    s.stroke(quad((360, 700), (500, 724), (642, 700)), ink, 18)


def journal(s, ink, acc):
    s.stroke(quad((500, 368), (400, 320), (275, 344)) + [(272, 640)]
             + quad((272, 640), (400, 618), (500, 676))[1:], ink, 16)
    s.stroke(quad((500, 368), (600, 320), (727, 344)) + [(730, 640)]
             + quad((730, 640), (600, 618), (500, 676))[1:], ink, 16)
    s.stroke(line((500, 370), (500, 674)), ink, 12)
    for i in range(4):
        y = 420 + i * 52
        s.stroke(quad((318, y), (390, y - 12), (460, y + 6)), ink, 9, wobble=1.6)
    for i in range(2):
        y = 470 + i * 52
        s.stroke(quad((548, y + 6), (600, y - 10), (640, y)), ink, 9, wobble=1.6)
    s.blob([(570, 338), (615, 332), (615, 470), (592, 448), (570, 470)], acc)


def identity(s, ink, acc):
    s.stroke(arc(500, 450, 138, 178, -95, 268), ink, 18)
    s.stroke(arc(500, 450, 100, 136, 200, 245, 30), acc, 14)
    s.stroke(line((500, 630), (502, 690)), ink, 18)
    s.stroke(quad((392, 708), (500, 690), (610, 708)), ink, 18)


COVERS = [
    ("1-Manifesto", manifesto, EMBER, BONE, SLATE),
    ("2-Daily", daily, BONE, SLATE, EMBER),
    ("3-Tools", tools, SLATE, BONE, EMBER),
    ("4-Discipline", discipline, BONE, SLATE, EMBER),
    ("5-Truths", truths, SLATE, BONE, EMBER),
    ("6-Journal", journal, BONE, SLATE, EMBER),
    ("7-Identity", identity, SLATE, BONE, EMBER),
]


def main():
    (HERE / "square").mkdir(exist_ok=True)
    (HERE / "story").mkdir(exist_ok=True)
    tiles = []
    for i, (name, draw, ground, ink, acc) in enumerate(COVERS):
        sheet = Sheet(seed=1000 + i)
        draw(sheet, ink, acc)
        sq = sheet.render(ground)
        sq.save(HERE / "square" / f"{name}.png")
        story = Image.new("RGB", (1080, 1920), ground)
        story.paste(sq, (0, 420))
        story.save(HERE / "story" / f"{name}.png")
        tiles.append((name.split("-", 1)[1], sq))
    preview(tiles)


def preview(tiles):
    d, gap, pad = 200, 60, 60
    font = ImageFont.truetype(str(FONT), 26)
    rows = []
    for page, ink, ring in (("#FFFFFF", "#111111", "#DBDBDB"), ("#000000", "#F5F5F5", "#363636")):
        row = Image.new("RGB", (pad * 2 + len(tiles) * d + (len(tiles) - 1) * gap, d + 110), page)
        dr = ImageDraw.Draw(row)
        for i, (label, im) in enumerate(tiles):
            x = pad + i * (d + gap)
            big = im.resize((d * 4, d * 4), Image.LANCZOS)
            mask = Image.new("L", big.size, 0)
            ImageDraw.Draw(mask).ellipse((24, 24, big.size[0] - 25, big.size[1] - 25), fill=255)
            disc = Image.new("RGB", big.size, page)
            disc.paste(big, (0, 0), mask)
            ImageDraw.Draw(disc).ellipse((4, 4, big.size[0] - 5, big.size[1] - 5), outline=ring, width=8)
            row.paste(disc.resize((d, d), Image.LANCZOS), (x, 30))
            tw = dr.textlength(label, font=font)
            dr.text((x + d / 2 - tw / 2, d + 50), label, fill=ink, font=font)
        rows.append(row)
    sheet = Image.new("RGB", (rows[0].width, rows[0].height * 2))
    sheet.paste(rows[0], (0, 0))
    sheet.paste(rows[1], (0, rows[0].height))
    sheet.save(HERE / "preview-row.png")


if __name__ == "__main__":
    main()
