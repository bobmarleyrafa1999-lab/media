#!/usr/bin/env python3
"""Builds the Moodius journals from their YAML source.

    python3 build_journal.py                          # The Unexamined Self: digital A5 + print A4
    python3 build_journal.py content/seven-day-guide.yaml --out out/guide.pdf --edition digital

Digital edition: A5, Bone paper, type-in fields over every writing area, clickable contents,
bookmarks. Print edition: A4, white paper, no fields, ink-light part openers.
Fonts and palette come from the shared Moodius design system (tools/fonts, strategy/05).
"""
import argparse, os, re, sys
import yaml
from reportlab.lib.pagesizes import A4, A5
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color, HexColor

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIRS = [os.path.join(HERE, "fonts"), "/mnt/project-files/moodius-aurelius/tools/fonts"]
FONTS = [("PF", "Playfair-SemiBold.ttf"), ("PFI", "Playfair-MediumItalic.ttf"), ("PFX", "Playfair-ExtraBold.ttf"),
         ("IN", "Inter-Regular.ttf"), ("INM", "Inter-Medium.ttf"), ("INS", "Inter-SemiBold.ttf")]
for name, f in FONTS:
    path = next((os.path.join(d, f) for d in FONT_DIRS if os.path.exists(os.path.join(d, f))), None)
    if not path:
        sys.exit(f"font {f} not found in {FONT_DIRS}")
    pdfmetrics.registerFont(TTFont(name, path))

SLATE, GRAPHITE, CHARCOAL = HexColor("#1B1F24"), HexColor("#2A2F36"), HexColor("#3A4049")
BONE, ASH, EMBER = HexColor("#F3EFE7"), HexColor("#B8B3A9"), HexColor("#C9742E")
MUTED, RULE, PANEL, EMBER_INK = HexColor("#59606A"), HexColor("#D2CBBE"), HexColor("#EAE4D8"), HexColor("#98521B")
WHITE = HexColor("#FFFFFF")
ROMAN = ["", "I", "II", "III", "IV", "V", "VI"]


def smart(t):
    """Typographic quotes and apostrophes for print."""
    t = re.sub(r'(^|[\s(\[])"', "\\1\u201c", str(t))
    t = t.replace('"', "\u201d")
    t = re.sub(r"(^|[\s(\[])'", "\\1\u2018", t)
    return t.replace("'", "\u2019")


class Book:
    def __init__(self, doc, edition, path):
        self.doc, self.edition = doc, edition
        self.digital = edition == "digital"
        self.W, self.H = (A5 if self.digital else A4)
        self.k = self.W / A5[0]                # scale factor: 1.0 for A5, ~1.41 for A4
        self.M = 42 * self.k                   # margin
        self.paper = BONE if self.digital else WHITE
        self.c = canvas.Canvas(path, pagesize=(self.W, self.H))
        m = doc["meta"]
        self.c.setTitle(f"{m['title']}: {m['subtitle']}")
        self.c.setAuthor(m["author"])
        self.c.setSubject(m["subtitle"])
        self.c.setCreator("Moodius Aurelius")
        self.page = 0
        self.fields = 0
        self.toc = []        # (level, label, page, key)

    # ---- primitives -------------------------------------------------------
    def s(self, v):
        return v * self.k

    def new_page(self, dark=False, folio=True):
        if self.page:
            self.c.showPage()
        self.page += 1
        c = self.c
        c.bookmarkPage(f"p{self.page}")
        c.setFillColor(SLATE if dark else self.paper)
        c.rect(0, 0, self.W, self.H, fill=1, stroke=0)
        self.dark = dark
        if folio and not dark:
            c.setFont("IN", self.s(7))
            c.setFillColor(MUTED)
            c.drawString(self.M, self.s(24), self.doc["meta"]["title"])
            c.drawRightString(self.W - self.M, self.s(24), str(self.page))
        self.y = self.H - self.M

    def ink(self):
        return BONE if self.dark else SLATE

    def text(self, txt, font, size, colour=None, lead=1.45, width=None, x=None, gap_after=0):
        """Draw wrapped paragraphs; blank lines in txt separate paragraphs. Returns new y."""
        c = self.c
        size, width = self.s(size), width or (self.W - 2 * self.M)
        x = self.M if x is None else x
        c.setFont(font, size)
        c.setFillColor(colour or self.ink())
        paras = [smart(p.strip()) for p in str(txt).strip().split("\n\n")]
        for i, p in enumerate(paras):
            for line in simpleSplit(" ".join(p.split()), font, size, width):
                if self.y - size < self.s(40):
                    self.new_page()
                    c.setFont(font, size); c.setFillColor(colour or self.ink())
                self.y -= size * lead
                c.drawString(x, self.y, line)
            if i < len(paras) - 1:
                self.y -= size * 0.6
        self.y -= self.s(gap_after)
        return self.y

    def height_of(self, txt, font, size, lead=1.45, width=None):
        width = width or (self.W - 2 * self.M)
        n = 0
        paras = [p.strip() for p in str(txt).strip().split("\n\n")]
        for p in paras:
            n += len(simpleSplit(" ".join(p.split()), font, self.s(size), width))
        return n * self.s(size) * lead + (len(paras) - 1) * self.s(size) * 0.6

    def kicker(self, label, colour=None, gap=10):
        self.c.setFont("INS", self.s(7))
        self.c.setFillColor(colour or (EMBER if self.dark else EMBER_INK))
        self.y -= self.s(7)
        self.c.drawString(self.M, self.y, " ".join(label.upper()))
        self.y -= self.s(gap)

    def rule(self, w=28, gap=12):
        self.c.setStrokeColor(EMBER)
        self.c.setLineWidth(self.s(1.2))
        self.c.line(self.M, self.y, self.M + self.s(w), self.y)
        self.y -= self.s(gap)

    def wordmark(self, colour=None):
        c = self.c
        c.setFillColor(EMBER)
        c.rect(self.M, self.H - self.M - self.s(6), self.s(6), self.s(6), fill=1, stroke=0)
        c.setFillColor(colour or self.ink())
        c.setFont("INS", self.s(7.5))
        c.drawString(self.M + self.s(12), self.H - self.M - self.s(6), "M O O D I U S")

    def lines(self, top, bottom, name=None, gap=17):
        """Ruled writing lines between top and bottom (y coords), with an optional fillable field."""
        c = self.c
        gap = self.s(gap)
        c.setStrokeColor(RULE)
        c.setLineWidth(0.5)
        y = top - gap
        while y > bottom:
            c.line(self.M, y, self.W - self.M, y)
            y -= gap
        if self.digital and name and top - bottom > gap:
            self.fields += 1
            c.acroForm.textfield(
                name=f"{name}", tooltip="Type here", x=self.M, y=bottom, width=self.W - 2 * self.M, height=top - bottom,
                fontName="Helvetica", fontSize=9.5, textColor=SLATE, fillColor=Color(0, 0, 0, 0), borderWidth=0,
                borderColor=Color(0, 0, 0, 0), fieldFlags="multiline", forceBorder=False,
            )

    def link_to(self, page_no, x1, y1, x2, y2):
        self.c.linkAbsolute("", f"p{page_no}", (x1, y1, x2, y2))

    def mark(self, key, label, level=0):
        self.c.addOutlineEntry(label, f"p{self.page}", level=level, closed=level == 0)
        self.toc.append((level, label, self.page, key))

    # ---- pages -------------------------------------------------------------
    def cover(self):
        m = self.doc["meta"]
        self.new_page(dark=True, folio=False)
        self.c.addOutlineEntry("Cover", "p1", level=0)
        c = self.c
        c.setFillColor(HexColor("#15181C"))
        c.rect(0, 0, self.s(14), self.H, fill=1, stroke=0)
        self.wordmark(BONE)
        y = self.H * 0.46
        c.setFillColor(EMBER)
        c.setFont("PFX", self.s(64))
        c.drawString(self.M, y + self.s(70), m.get("cover_numeral", "30"))
        c.setFillColor(BONE)
        c.setFont("PF", self.s(34))
        for i, line in enumerate(m.get("cover_lines", [m["title"]])):
            c.drawString(self.M, y - i * self.s(38), line)
        y -= (len(m.get("cover_lines", [m["title"]])) - 1) * self.s(38) + self.s(26)
        c.setStrokeColor(EMBER); c.setLineWidth(self.s(1.4)); c.line(self.M, y, self.M + self.s(32), y)
        c.setFillColor(ASH); c.setFont("INM", self.s(9.5))
        c.drawString(self.M, y - self.s(20), m["subtitle"])
        c.setFont("IN", self.s(7.5))
        c.drawString(self.M, self.M, m["author"].upper().replace("", " ").strip())
        c.drawRightString(self.W - self.M, self.M, m["edition"])

    def title_page(self):
        d, m = self.doc, self.doc["meta"]
        self.new_page(folio=False)
        self.wordmark()
        self.y = self.H * 0.62
        self.text(m["title"], "PF", 24, lead=1.15)
        self.y -= self.s(8); self.rule(gap=16)
        self.text(m["subtitle"], "INM", 10, MUTED)
        if d.get("epigraph"):
            e = d["epigraph"]
            self.y = self.H * 0.32
            self.text(e["text"], "PFI", 12, lead=1.4, width=self.W - 2 * self.M - self.s(40))
            self.y -= self.s(6)
            self.text(e["cite"].upper(), "INM", 6.5, MUTED)
        self.c.setFont("IN", self.s(6.5)); self.c.setFillColor(MUTED)
        notice = m.get("notice", f"© 2026 Moodius Aurelius. For your personal use. Please don't share or resell this file. {m['edition']}.")
        yy = self.M + self.s(14)
        for line in reversed(simpleSplit(notice, "IN", self.s(6.5), self.W - 2 * self.M)):
            self.c.drawString(self.M, yy, line); yy += self.s(9)

    def contents(self, toc_pages):
        self.new_page()
        self.mark("contents", "Contents")
        self.kicker("Contents", gap=18)
        for level, label, page, key in toc_pages:
            if key in ("contents",):
                continue
            size = 9.5 if level == 0 else 8
            font = "INS" if level == 0 else "IN"
            if level == 0:
                self.y -= self.s(5)
            if self.y < self.s(60):
                self.new_page()
            self.y -= self.s(size * 1.55)
            self.c.setFont(font, self.s(size)); self.c.setFillColor(SLATE)
            x = self.M + (self.s(12) if level else 0)
            self.c.drawString(x, self.y, label)
            self.c.drawRightString(self.W - self.M, self.y, str(page))
            if page:
                self.link_to(page, x, self.y - 2, self.W - self.M, self.y + self.s(size))

    def prose_page(self, key, heading, body, level=0):
        self.new_page()
        self.mark(key, heading, level)
        self.wordmark()
        self.y = self.H - self.M - self.s(40)
        self.text(heading, "PF", 18, lead=1.2, gap_after=4)
        self.rule(gap=10)
        self.text(body, "IN", 9, lead=1.55)

    def part_opener(self, part):
        self.new_page(dark=self.digital, folio=not self.digital)
        self.mark(f"part{part['n']}", f"Part {ROMAN[part['n']]}: {part['title']}")
        c = self.c
        c.setFillColor(EMBER); c.setFont("PFX", self.s(96))
        c.drawString(self.M, self.H * 0.55, ROMAN[part["n"]])
        self.y = self.H * 0.55 - self.s(30)
        self.kicker(f"Part {ROMAN[part['n']]}", gap=12)
        self.text(part["title"], "PF", 26, lead=1.15, gap_after=6)
        self.rule(gap=10)
        self.text(part["intro"], "IN", 10, ASH if self.dark else MUTED, lead=1.55, width=self.W - 2 * self.M - self.s(30))
        days = [d for d in self.doc["days"] if d["part"] == part["n"]]
        if days:
            self.c.setFont("INM", self.s(7.5)); self.c.setFillColor(ASH if self.dark else MUTED)
            self.c.drawString(self.M, self.M, f"Days {days[0]['n']}–{days[-1]['n']}")

    def day(self, d):
        part = next(p for p in self.doc["parts"] if p["n"] == d["part"])
        c = self.c
        # Page 1: reading
        self.new_page()
        self.mark(f"day{d['n']}", f"Day {d['n']}: {d['title']}", level=1)
        c.setFillColor(EMBER); c.setFont("PFX", self.s(40))
        c.drawRightString(self.W - self.M, self.H - self.M - self.s(34), f"{d['n']:02d}")
        multi = len(self.doc["parts"]) > 1
        self.kicker(f"Day {d['n']} · Part {ROMAN[part['n']]} · {part['title']}" if multi else f"Day {d['n']} of {len(self.doc['days'])}", gap=14)
        self.text(d["title"], "PF", 19, lead=1.15, width=self.W - 2 * self.M - self.s(70), gap_after=8)
        q = d["quote"]
        self.text(q["text"], "PFI", 10.5, lead=1.42, width=self.W - 2 * self.M - self.s(16), gap_after=3)
        self.c.setFont("INM", self.s(6.3)); self.c.setFillColor(MUTED)
        self.y -= self.s(8)
        tag = "VERBATIM" if q["kind"] == "verbatim" else "PARAPHRASE"
        self.c.drawString(self.M, self.y, f"{q['cite'].upper()}  ·  {tag}")
        self.y -= self.s(14)
        self.rule(gap=4)
        ev = d["evidence"]
        ev_h = self.height_of(ev["note"], "IN", 7.2, 1.45, self.W - 2 * self.M - self.s(20)) + self.s(30)
        body_h = self.height_of(d["reading"], "IN", 9, 1.55)
        if self.y - body_h - ev_h < self.s(44):
            # Too long for one page at this size: tighten the reading slightly rather than spill.
            self.text(d["reading"], "IN", 8.5, lead=1.5)
        else:
            self.text(d["reading"], "IN", 9, lead=1.55)
        self.evidence_box(ev)
        # Page 2: questions
        self.new_page()
        self.kicker(f"Day {d['n']} · Questions", gap=10)
        top, bottom = self.y, self.s(44)
        slot = (top - bottom) / len(d["prompts"])
        for i, p in enumerate(d["prompts"]):
            self.y = top - i * slot
            self.c.setFont("PF", self.s(10)); self.c.setFillColor(EMBER_INK)
            self.c.drawString(self.M, self.y - self.s(11), f"{i + 1}")
            self.text(p, "INM", 9, lead=1.4, x=self.M + self.s(14), width=self.W - 2 * self.M - self.s(14))
            self.lines(self.y - self.s(2), top - (i + 1) * slot + self.s(6), name=f"d{d['n']:02d}_q{i + 1}")
        # Page 3: exercise + tonight
        self.new_page()
        ex = d["exercise"]
        self.kicker(f"Day {d['n']} · Exercise", gap=10)
        self.text(ex["name"], "PF", 14, lead=1.2, gap_after=4)
        self.text(ex["steps"], "IN", 8.8, lead=1.5, gap_after=4)
        tonight_h = self.s(62)
        self.lines(self.y, self.s(44) + tonight_h, name=f"d{d['n']:02d}_exercise")
        self.y = self.s(44) + tonight_h - self.s(6)
        self.c.setStrokeColor(EMBER); self.c.setLineWidth(self.s(0.8))
        self.c.line(self.M, self.y, self.W - self.M, self.y)
        self.y -= self.s(4)
        self.kicker("Tonight", gap=2)
        self.text(d["tonight"], "INM", 8.5, lead=1.4)
        self.lines(self.y, self.s(44), name=f"d{d['n']:02d}_tonight", gap=15)

    def evidence_box(self, ev):
        c = self.c
        w = self.W - 2 * self.M
        h = self.height_of(ev["note"], "IN", 7.2, 1.45, w - self.s(20)) + self.s(30)
        top = max(self.y - self.s(6), self.s(44) + h)
        if top - h < self.s(40):
            self.new_page(); top = self.y
        c.setFillColor(PANEL if self.digital else HexColor("#F2EFE9"))
        c.rect(self.M, top - h, w, h, fill=1, stroke=0)
        c.setFillColor(EMBER); c.rect(self.M, top - h, self.s(2), h, fill=1, stroke=0)
        self.y = top - self.s(6)
        c.setFont("INS", self.s(6.3)); c.setFillColor(EMBER_INK)
        self.y -= self.s(7)
        c.drawString(self.M + self.s(10), self.y, f"EVIDENCE  ·  {ev['tier'].upper()}")
        self.y -= self.s(3)
        self.text(ev["note"], "IN", 7.2, SLATE, lead=1.45, x=self.M + self.s(10), width=w - self.s(20))
        self.y = top - h - self.s(6)

    def review(self, part):
        r = self.doc["review"]
        self.new_page()
        self.mark(f"review{part['n']}", f"Review: Part {ROMAN[part['n']]}", level=1)
        self.kicker(f"{r['heading']} · Part {ROMAN[part['n']]} · {part['title']}", gap=10)
        prompts = r["prompts"] + [r["scale"]]
        top, bottom = self.y, self.s(44)
        slot = (top - bottom) / len(prompts)
        for i, p in enumerate(prompts):
            self.y = top - i * slot
            self.text(p, "INM", 9, lead=1.4)
            self.lines(self.y - self.s(2), top - (i + 1) * slot + self.s(6), name=f"review{part['n']}_{i + 1}")

    def vocabulary(self):
        v = self.doc["vocabulary"]
        self.prose_page("vocabulary", v["heading"], v["intro"])
        self.y -= self.s(10)
        col_w = (self.W - 2 * self.M) / 2
        groups = v["groups"]
        for i in range(0, len(groups), 2):
            row_top = self.y
            heights = []
            for j, g in enumerate(groups[i:i + 2]):
                self.y = row_top
                x = self.M + j * col_w
                self.c.setFont("INS", self.s(7)); self.c.setFillColor(EMBER_INK)
                self.y -= self.s(9)
                self.c.drawString(x, self.y, g["name"].upper())
                self.y -= self.s(2)
                self.text(", ".join(g["words"]), "IN", 8.2, lead=1.5, x=x, width=col_w - self.s(12))
                heights.append(self.y)
            self.y = min(heights) - self.s(10)

    def values(self):
        v = self.doc["values"]
        self.prose_page("values", v["heading"], v["intro"])
        self.y -= self.s(10)
        words = v["words"]
        cols = 3
        col_w = (self.W - 2 * self.M) / cols
        per = -(-len(words) // cols)
        start = self.y
        for ci in range(cols):
            self.y = start
            for w in words[ci * per:(ci + 1) * per]:
                self.y -= self.s(14)
                self.c.setStrokeColor(RULE); self.c.setLineWidth(0.6)
                self.c.rect(self.M + ci * col_w, self.y - self.s(1), self.s(7), self.s(7), fill=0, stroke=1)
                self.c.setFont("IN", self.s(8.5)); self.c.setFillColor(SLATE)
                self.c.drawString(self.M + ci * col_w + self.s(12), self.y, w)

    def references(self):
        refs = self.doc["references"]
        self.new_page()
        self.mark("references", "References")
        self.wordmark()
        self.y = self.H - self.M - self.s(40)
        self.text("References", "PF", 18, lead=1.2, gap_after=4)
        self.rule(gap=8)
        for key in sorted(refs, key=lambda k: refs[k].lower()):
            self.text(refs[key], "IN", 7, lead=1.4, gap_after=3)

    def closing(self):
        m = self.doc["meta"]
        self.new_page(dark=True, folio=False)
        self.wordmark(BONE)
        self.y = self.H * 0.55
        for p in m.get("closing", []):
            self.text(p, "IN", 9.5, BONE, lead=1.55, width=self.W - 2 * self.M - self.s(20), gap_after=6)
        self.c.setFillColor(ASH); self.c.setFont("IN", self.s(7.5))
        self.c.drawString(self.M, self.M, "@moodiusaurelius")

    def notes(self, n=2):
        for i in range(n):
            self.new_page()
            if i == 0:
                self.mark("notes", "Notes")
            self.kicker("Notes", gap=6)
            self.lines(self.y, self.s(44), name=f"notes_{i + 1}")

    # ---- whole book ----------------------------------------------------------
    def build(self, toc_pages=None):
        d = self.doc
        self.cover()
        self.title_page()
        if d.get("contents", True):
            self.contents(toc_pages or self.toc_estimate())
        for i, f in enumerate(d.get("front", [])):
            self.prose_page(f"front{i}", f["heading"], f["body"])
        for part in d["parts"]:
            if d.get("part_openers", True):
                self.part_opener(part)
            for day in [x for x in d["days"] if x["part"] == part["n"]]:
                self.day(day)
            if d.get("review"):
                self.review(part)
        if d.get("vocabulary"):
            self.vocabulary()
        if d.get("values"):
            self.values()
        if d.get("references"):
            self.references()
        self.notes(d.get("notes_pages", 2))
        self.closing()
        self.c.save()
        return self.toc

    def toc_estimate(self):
        return [(0, "…", 0, "x")] * (len(self.doc["parts"]) * 7 + len(self.doc.get("front", [])) + 6)


def build(src, out, edition):
    doc = yaml.safe_load(open(src, encoding="utf-8"))
    # Two passes: the first finds page numbers, the second prints them in the contents.
    tmp = out + ".tmp"
    toc = Book(doc, edition, tmp).build()
    for _ in range(3):
        book = Book(doc, edition, tmp)
        new = book.build(toc)
        if [t[2] for t in new] == [t[2] for t in toc]:
            break
        toc = new
    os.replace(tmp, out)
    return book.page, book.fields


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src", nargs="?", default=os.path.join(HERE, "content", "the-unexamined-self.yaml"))
    ap.add_argument("--out", help="output PDF (single edition)")
    ap.add_argument("--edition", choices=["digital", "print"], default=None)
    a = ap.parse_args()
    if a.out:
        pages, fields = build(a.src, a.out, a.edition or "digital")
        print(f"{a.out}: {pages} pages, {fields} type-in fields")
    else:
        os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
        for ed, name in [("digital", "The-Unexamined-Self-A5-digital.pdf"), ("print", "The-Unexamined-Self-A4-print.pdf")]:
            out = os.path.join(HERE, "out", name)
            pages, fields = build(a.src, out, ed)
            print(f"{out}: {pages} pages, {fields} type-in fields")
