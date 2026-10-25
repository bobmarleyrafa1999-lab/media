#!/usr/bin/env python3
"""Moodius Story templates T01-T12 (1080x1920), Pillow only. £0, runs offline.

Usage:
  python3 templates.py samples   -> ../templates/T01-hook.jpg ... (one sample per template)
  python3 templates.py sequences -> ../renders/S01/S01-e1_auto.jpg, S01-e2_hand.jpg ...
Interactive frames (sticker or reply set) render twice: _hand (clear sticker zone, post from the app)
and _auto (reply prompt printed, schedulable in Metricool). Others render once as _all.
"""
import os, sys, json
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FONTS = os.path.join(ROOT, "..", "..", "tools", "fonts")

W, H = 1080, 1920
M = 96                      # side margin
TOP = 330                   # content starts below Instagram's progress bar + name
SAFE_BOTTOM = H - 260       # keep reply bar clear

C = dict(slate="#1B1F24", graphite="#2A2F36", charcoal="#3A4049", bone="#F3EFE7", ash="#B8B3A9", ember="#C9742E",
         ink="#1B1F24", paper_ash="#6B665E")

def font(name, size):
    paths = {
        "serif": os.path.join(FONTS, "Playfair-SemiBold.ttf"),
        "serif_xb": os.path.join(FONTS, "Playfair-ExtraBold.ttf"),
        "serif_it": os.path.join(FONTS, "Playfair-MediumItalic.ttf"),
        "sans": os.path.join(FONTS, "Inter-Regular.ttf"),
        "sans_md": os.path.join(FONTS, "Inter-Medium.ttf"),
        "sans_sb": os.path.join(FONTS, "Inter-SemiBold.ttf"),
    }
    return ImageFont.truetype(paths[name], size)

PILLAR = {"HM": "The Human Mind", "FK": "Forgotten Knowledge", "RR": "The Reading Room",
          "LB": "The Living Body", "GL": "The Good Life"}
LIGHT = {"T05", "T06"}       # Bone background templates (magazine "feature" pages)


def wrap(d, text, f, width):
    lines = []
    for para in text.split("\n"):
        words, cur = para.split(), ""
        for w in words:
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) <= width:
                cur = t
            else:
                if cur:
                    lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def text_block(d, xy, text, f, fill, width, lh=1.18, tracking=0):
    x, y = xy
    if not text:
        return y
    for line in wrap(d, text, f, width):
        if tracking:
            cx = x
            for ch in line:
                d.text((cx, y), ch, font=f, fill=fill)
                cx += d.textlength(ch, font=f) + tracking
        else:
            d.text((x, y), line, font=f, fill=fill)
        y += int(f.size * lh)
    return y


def caps(d, xy, text, size, fill, tracking=4):
    return text_block(d, xy, text.upper(), font("sans_sb", size), fill, W - 2 * M, 1.3, tracking)


class Frame:
    def __init__(self, t, seq_id="", pillar="", page="", light=None):
        self.t = t
        self.light = (t in LIGHT) if light is None else light
        bg = C["bone"] if self.light else (C["graphite"] if t == "T12" else C["slate"])
        self.fg = C["ink"] if self.light else C["bone"]
        self.muted = C["paper_ash"] if self.light else C["ash"]
        self.rule = "#D9D3C7" if self.light else C["charcoal"]
        self.im = Image.new("RGB", (W, H), bg)
        self.d = ImageDraw.Draw(self.im)
        # masthead
        d = self.d
        d.rectangle([M, 196, M + 14, 210], fill=C["ember"])
        text_block(d, (M + 28, 190), "MOODIUS", font("sans_sb", 24), self.fg, 400, tracking=5)
        right = " · ".join(x for x in [PILLAR.get(pillar, ""), page] if x)
        if right:
            f = font("sans_md", 22)
            d.text((W - M - d.textlength(right.upper(), font=f) - 2 * len(right), 192), right.upper(), font=f, fill=self.muted)
        d.line([M, 240, W - M, 240], fill=self.rule, width=2)
        f = font("sans_md", 22)
        h = "@moodiusaurelius"
        d.text((W - M - d.textlength(h, font=f), SAFE_BOTTOM - 10), h, font=f, fill=self.muted)
        self.y = TOP + 60

    def kicker(self, k):
        if k:
            self.y = caps(self.d, (M, self.y), k, 28, C["ember"]) + 22

    def title(self, s, size=84, face="serif"):
        if s:
            self.y = text_block(self.d, (M, self.y), s, font(face, size), self.fg, W - 2 * M, 1.14) + 26

    def body(self, s, size=42, colour=None):
        if s:
            self.y = text_block(self.d, (M, self.y), s, font("sans", size), colour or self.fg, W - 2 * M - 20, 1.38) + 22

    def note(self, s):
        if s:
            self.d.rectangle([M, self.y + 4, M + 5, self.y + 4 + 34], fill=C["ember"])
            self.y = text_block(self.d, (M + 26, self.y), s, font("sans_md", 27), self.muted, W - 2 * M - 30, 1.42) + 20

    def footer(self, s):
        if s:
            y = SAFE_BOTTOM - 150
            self.d.line([M, y - 26, M + 120, y - 26], fill=C["ember"], width=4)
            text_block(self.d, (M, y), s, font("sans_sb", 32), C["ember"], W - 2 * M, 1.3)

    def zone(self, mode, reply, kind="box"):
        """Sticker zone. hand: left clear. auto: reply prompt panel."""
        top = max(self.y + 30, 1060)
        bottom = SAFE_BOTTOM - 190
        if mode == "hand" or not reply:
            self.y = bottom
            return
        d = self.d
        panel = "#E6E0D4" if self.light else C["graphite"]
        if self.t == "T12":
            panel = C["slate"]
        h = 250 if kind != "slider" else 240
        y0 = min(top, bottom - h)
        d.rounded_rectangle([M, y0, W - M, y0 + h], radius=28, fill=panel)
        if kind == "slider":
            ly = y0 + 140
            d.line([M + 60, ly, W - M - 60, ly], fill=C["ember"], width=6)
            for i in range(10):
                x = M + 60 + i * (W - 2 * M - 120) / 9
                d.ellipse([x - 9, ly - 9, x + 9, ly + 9], fill=C["ember"] if i in (0, 9) else self.muted)
                lab = str(i + 1)
                f = font("sans_md", 24)
                d.text((x - d.textlength(lab, font=f) / 2, ly + 22), lab, font=f, fill=self.muted)
            text_block(d, (M + 50, y0 + 36), reply, font("sans_sb", 36), self.fg, W - 2 * M - 100, 1.25)
        else:
            yy = text_block(d, (M + 50, y0 + 50), reply, font("sans_sb", 40), self.fg, W - 2 * M - 100, 1.25)
            text_block(d, (M + 50, yy + 10), "Replies go to my DMs. Nobody else sees them.", font("sans_md", 26), self.muted, W - 2 * M - 100)
        self.y = y0 + h + 30

    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.im.save(path, "JPEG", quality=90, optimize=True)


def options_block(fr, options, answer=None):
    d = fr.d
    for i, opt in enumerate(options):
        letter = "ABCD"[i]
        y = fr.y
        hit = answer is not None and i == answer
        dim = answer is not None and i != answer
        if hit:
            d.rounded_rectangle([M - 20, y - 14, W - M + 20, y + 84], radius=18, fill=C["ember"])
        col = C["bone"] if hit else (fr.rule if dim and not fr.light else (fr.muted if dim else fr.fg))
        d.text((M + 4, y - 6), letter, font=font("serif_xb", 60), fill=C["bone"] if hit else C["ember"] if not dim else fr.muted)
        text_block(d, (M + 80, y + 2), opt, font("serif_it", 50), col if not hit else C["bone"], W - 2 * M - 100, 1.1)
        fr.y = y + 112
    fr.y += 10


def two_cards(fr, left, right, lbody="", rbody=""):
    d = fr.d
    gap = 28
    cw = (W - 2 * M - gap) // 2
    y0 = fr.y
    hgt = 300 if not (lbody or rbody) else 520
    for i, (lab, txt) in enumerate([(left, lbody), (right, rbody)]):
        x = M + i * (cw + gap)
        d.rounded_rectangle([x, y0, x + cw, y0 + hgt], radius=26, fill="#E6E0D4" if fr.light else C["graphite"])
        d.text((x + 36, y0 + 26), "AB"[i], font=font("serif_xb", 64), fill=C["ember"])
        yy = text_block(d, (x + 36, y0 + 118), lab, font("serif", 44), fr.fg, cw - 70, 1.14)
        if txt:
            text_block(d, (x + 36, yy + 16), txt, font("sans", 31), fr.muted, cw - 70, 1.36)
    fr.y = y0 + hgt + 30


def stacked_cards(fr, top_lab, top_txt, bot_lab, bot_txt):
    d = fr.d
    for lab, txt, col in [(top_lab, top_txt, C["ember"]), (bot_lab, bot_txt, fr.muted)]:
        y0 = fr.y
        inner = wrap(d, txt, font("sans", 38), W - 2 * M - 80)
        hgt = 110 + len(inner) * 52 + 30
        d.rounded_rectangle([M, y0, W - M, y0 + hgt], radius=24, fill=C["graphite"])
        caps(d, (M + 40, y0 + 34), lab, 24, col)
        text_block(d, (M + 40, y0 + 92), txt, font("sans", 38), C["bone"], W - 2 * M - 80, 1.36)
        fr.y = y0 + hgt + 24


def books_motif(fr):
    d = fr.d
    x = W - M - 200
    base = 470
    for i, (w, h, col) in enumerate([(34, 190, C["slate"]), (26, 160, C["ember"]), (40, 210, C["charcoal"]), (30, 175, C["graphite"])]):
        d.rectangle([x, base - h, x + w, base], fill=col)
        x += w + 8
    d.line([W - M - 220, base + 2, W - M, base + 2], fill=C["slate"], width=4)


def kindness_motif(fr):
    d = fr.d
    cx, cy = W - M - 90, 400
    for r in (80, 56, 32):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=C["ember"], width=4)


def render(fr_spec, mode, seq=None, page="", shift=None):
    """Interactive frames sit high (sticker zone below); others are centred vertically."""
    if shift is None:
        probe = render(fr_spec, mode, seq, page, shift=0)
        interactive = bool(fr_spec.get("sticker") or fr_spec.get("reply"))
        if interactive:
            return probe
        bottom = SAFE_BOTTOM - (230 if fr_spec.get("footer") else 80)
        start = probe.start
        free = bottom - probe.y
        return render(fr_spec, mode, seq, page, shift=max(0, min(int(free * 0.42), 420)))
    t = fr_spec["t"]
    fr = Frame(t, seq["id"] if seq else "", seq["pillar"] if seq else "", page)
    if t == "T05":
        books_motif(fr)
    if t == "T06":
        kindness_motif(fr)
    if t in ("T05", "T06"):
        fr.y = TOP + 220
    fr.y += shift
    fr.start = fr.y
    s = fr_spec
    fr.kicker(s.get("kicker"))
    if t == "T12":
        fr.d.text((M - 6, fr.y - 40), "“", font=font("serif_xb", 200), fill=C["ember"])
        fr.y += 120
        fr.title(s.get("title"), 76, "serif_it")
        fr.body(s.get("body"), 42, C["ash"])
    elif t == "T01":
        fr.title(s.get("title"), 96)
        fr.body(s.get("body"), 46, C["ash"])
    elif t == "T02":
        fr.title(s.get("title"), 80)
        two_cards(fr, s.get("left", "A"), s.get("right", "B"))
        fr.body(s.get("body"))
    elif t == "T07":
        fr.title(s.get("title"), 70)
        fr.y += 12
        if s.get("body") or s.get("note"):
            stacked_cards(fr, s.get("left") or "My view", s.get("body", ""), s.get("right") or "Best case against", s.get("note", ""))
    elif t == "T08":
        fr.title(s.get("title"), 80)
        if s.get("answer") is not None:
            fr.body(s.get("body"))
            options_block(fr, s["options"], s["answer"])
            fr.note(s.get("note"))
        else:
            fr.body(s.get("body"))
            if s.get("options"):
                options_block(fr, s["options"])
    elif t == "T03":
        fr.title(s.get("title"), 78)
        fr.body(s.get("body"))
        fr.note(s.get("note"))
    else:  # T04 question, T05 book, T06 kindness, T09 slider, T10 add yours, T11 you pick
        fr.title(s.get("title"), 84)
        fr.body(s.get("body"), 42, fr.muted if t not in ("T05", "T06") else None)
        if t == "T11" and s.get("options"):
            options_block(fr, s["options"])
        if t not in ("T04", "T09", "T10") or (s.get("answer") is not None):
            fr.note(s.get("note"))
        else:
            fr.note(s.get("note"))
    interactive = bool(s.get("sticker") or s.get("reply"))
    if interactive:
        fr.zone(mode, s.get("reply"), "slider" if t == "T09" else "box")
    fr.footer(s.get("footer"))
    return fr


SAMPLES = [
 ("T01-hook", dict(t="T01", kicker="Quick one", title="You spilled coffee down your shirt before a meeting.", body="How many people noticed?")),
 ("T02-two-perspectives", dict(t="T02", kicker="Two perspectives, one dilemma", title="Your friend's business idea is bad.", left="Honest, now", right="Encourage, then ask questions", sticker="Poll", reply="Reply 'honest' or 'encourage'.")),
 ("T03-psychology-says", dict(t="T03", kicker="What psychology actually says", title="“I'm excited” beat “I'm calm”.", body="People told to say “I am excited” before singing or speaking did better than people told to say “I am calm”.", note="Brooks, J. Experimental Psychology: General, 2014.")),
 ("T04-question-box", dict(t="T04", kicker="A question worth asking yourself", title="What would you do this week if nobody would ever know?", sticker="Question box", reply="Reply with one thing.")),
 ("T05-book", dict(t="T05", kicker="Books that changed how I think", title="A 2,000-year-old handbook starts with one idea.", body="Some things are up to us. Most aren't.", note="Moodius paraphrase of Epictetus, Enchiridion 1. Free at Standard Ebooks.")),
 ("T06-kindness", dict(t="T06", kicker="A stranger's act of kindness", title="Someone you'll never see again did something you still remember.", body="Tell me in one line.", sticker="Question box", reply="Reply with one line. I'll share a few (no names).")),
 ("T07-argument-against", dict(t="T07", kicker="The argument against my own opinion", title="Rest is a skill, not a reward.", left="My view", body="Rest you plan for works better than rest you collapse into.", right="Best case against", note="Some weeks you can't choose rest. Calling it a skill can make tired people feel they're failing.")),
 ("T08-quiz", dict(t="T08", kicker="Guess", title="In the study, the typical time to build a habit was…", options=["21 days", "about 66 days", "254 days"], sticker="Quiz", reply="Reply A, B or C. Answer at 9.")),
 ("T08b-answer", dict(t="T08", kicker="Answer", title="B. About 66 days.", body="It took some people 18 days and others 254.", note="Lally et al., European J. Social Psychology, 2010.", options=["21 days", "about 66 days", "254 days"], answer=1)),
 ("T09-slider", dict(t="T09", kicker="Body check", title="Minutes outside this week. Real outside.", sticker="Emoji slider", reply="Reply with your guess in minutes.")),
 ("T10-add-yours", dict(t="T10", kicker="Add yours", title="A small thing that made today better.", body="Mine: [one small true thing].", sticker="Add Yours", reply="Reply with yours. One line.")),
 ("T11-you-pick", dict(t="T11", kicker="You pick", title="Next week, more of…", options=["a forgotten history", "how your mind works", "being kind, with evidence"], sticker="Poll", reply="Reply A, B or C.")),
 ("T12-moodius-take", dict(t="T12", kicker="Moodius take", title="You can't always calm down. You can rename it.", body="Same racing heart. Different story about it.", footer="Send this to someone with a big day this week.")),
]


def main():
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    index = []
    if what in ("samples", "all"):
        for name, spec in SAMPLES:
            for mode in (["hand", "auto"] if spec.get("reply") else ["all"]):
                p = os.path.join(ROOT, "templates", f"{name}_{mode}.jpg")
                render(spec, mode, None, "").save(p)
    if what in ("sequences", "all"):
        sys.path.insert(0, HERE)
        from sequences import S
        for seq in S:
            frames = [("e", f) for f in seq["evening"]] + [("m", f) for f in seq["morning"]]
            n = len(frames)
            for i, (part, f) in enumerate(frames, 1):
                page = f"{seq['id']} · {i}/{n}"
                modes = ["hand", "auto"] if (f.get("sticker") or f.get("reply")) else ["all"]
                # hand-only frames (placeholders to fill by hand) render once as hand
                if "[" in (f.get("title") or ""):
                    modes = ["hand"]
                for mode in modes:
                    fn = f"{seq['id']}-{i:02d}{part}_{mode}.jpg"
                    render(f, mode, seq, page).save(os.path.join(ROOT, "renders", seq["id"], fn))
                    index.append(dict(seq=seq["id"], frame=i, part="evening 21:00" if part == "e" else "morning 09:00",
                                      mode=mode, file=f"renders/{seq['id']}/{fn}", template=f["t"],
                                      sticker=f.get("sticker"), reply=f.get("reply")))
        json.dump(index, open(os.path.join(ROOT, "renders", "index.json"), "w"), indent=1, ensure_ascii=False)
    print("ok", len(index))


if __name__ == "__main__":
    main()
