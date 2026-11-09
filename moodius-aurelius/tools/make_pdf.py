#!/usr/bin/env python3
"""Build the free lead-magnet PDF: 7 Ancient Rules for Young Men.  python3 make_pdf.py out.pdf"""
import sys
from reportlab.lib.pagesizes import A5
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

F = "/usr/share/fonts/truetype/freefont/"
pdfmetrics.registerFont(TTFont("S", F + "FreeSerif.ttf"))
pdfmetrics.registerFont(TTFont("SB", F + "FreeSerifBold.ttf"))
pdfmetrics.registerFont(TTFont("SI", F + "FreeSerifItalic.ttf"))
STONE, CREAM, GOLD, MUTED = (0.106, 0.114, 0.122), (0.93, 0.90, 0.84), (0.79, 0.66, 0.42), (0.63, 0.60, 0.54)
W, H = A5

RULES = [
    ("Know what is yours", "Some things are up to us, and some are not.", "Epictetus, Enchiridion 1",
     "Your judgements, your effort and your character are yours. Other people's opinions, the past and the outcome are not. Most anxiety comes from carrying the second list.",
     "Write two columns tonight: what's mine, what isn't. Put down everything in the second one."),
    ("Examine your life", "The unexamined life is not worth living.", "Plato, Apology 38a",
     "Socrates chose death over a life without questions. Purpose doesn't arrive. You find it by asking, honestly and often, what you are living for.",
     "Ask yourself one question every morning: what would make today worth having lived?"),
    ("Build your character by doing", "We become just by doing just acts, temperate by doing temperate acts, brave by doing brave acts.", "Aristotle, Nicomachean Ethics II.1",
     "You are not waiting to discover who you are. You are deciding it, one act at a time. Character is a habit.",
     "Pick one virtue for this week (courage, honesty, self-control) and do one act of it every day."),
    ("Use your suffering", "It is difficulties that show what men are.", "Epictetus, Discourses 1.24",
     "Pain is not proof that your life has gone wrong. It is the training ground. Viktor Frankl, who survived Auschwitz, wrote that suffering stops being suffering the moment it finds a meaning.",
     "Name the hardest thing in your life right now. Then write what it could be training in you."),
    ("Love your fate", "Do not seek to have events happen as you want them to, but instead want them to happen as they do happen, and your life will go well.", "Epictetus, Enchiridion 8",
     "Amor fati is not giving up. It is saying yes to the life in front of you, including the parts you didn't choose, and making something of them.",
     "When something goes wrong this week, say out loud: 'Good. Now what can I do with this?'"),
    ("Choose your circle", "Associate with those who will make a better man of you.", "Seneca, Letter 7",
     "You become the people you spend your evenings with. Seneca told his friend to welcome those he could improve too, because men learn while they teach.",
     "Message one person this week who makes you better. Tell them so."),
    ("See the beauty", "Dwell on the beauty of life. Watch the stars, and see yourself running with them.", "Marcus Aurelius, Meditations 7.47",
     "The emperor of Rome, at war and surrounded by plague, still told himself to look up. A good man is not a grim man.",
     "Once a day, stop for one minute and notice something beautiful. Don't photograph it."),
]


def bg(c):
    c.setFillColorRGB(*STONE); c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColorRGB(*GOLD); c.setFont("SB", 11); c.drawCentredString(W / 2, H - 40, "M · A")
    c.setStrokeColorRGB(*GOLD); c.setLineWidth(0.6); c.line(W / 2 - 30, H - 47, W / 2 + 30, H - 47)
    c.setFillColorRGB(*MUTED); c.setFont("S", 8); c.drawCentredString(W / 2, 28, "@moodiusaurelius")


def para(c, text, font, size, y, colour, lead=1.35, width=W - 90):
    c.setFont(font, size); c.setFillColorRGB(*colour)
    for ln in simpleSplit(text, font, size, width):
        c.drawCentredString(W / 2, y, ln); y -= size * lead
    return y


def main(out):
    c = canvas.Canvas(out, pagesize=A5)
    c.setTitle("7 Ancient Rules for Young Men"); c.setAuthor("Moodius Aurelius")
    bg(c)
    y = para(c, "7 Ancient Rules", "SB", 30, H / 2 + 90, CREAM)
    y = para(c, "for young men who want a life that means something", "SI", 15, y - 6, CREAM)
    para(c, "Epictetus · Plato · Aristotle · Seneca · Marcus Aurelius", "S", 10, y - 30, GOLD)
    c.showPage()
    bg(c)
    y = para(c, "Why this exists", "SB", 18, H - 110, CREAM)
    intro = ("Most of what young men are sold online is either rage or comfort. The ancients offered something better: "
             "a purpose worth living for, a way to make meaning out of suffering, and the strength to love the life you actually have. "
             "These seven rules are the core of it. Read one a day for a week. Do the practice. Then start again.")
    para(c, intro, "S", 12, y - 14, CREAM, lead=1.5)
    c.showPage()
    for i, (title, quote, cite, body, practice) in enumerate(RULES, 1):
        bg(c)
        c.setFillColorRGB(*GOLD); c.setFont("S", 10); c.drawCentredString(W / 2, H - 80, f"RULE {i}")
        y = para(c, title, "SB", 22, H - 112, CREAM)
        y = para(c, f"“{quote}”", "SI", 14, y - 16, CREAM, lead=1.4)
        y = para(c, cite, "S", 10, y - 4, GOLD)
        y = para(c, body, "S", 11.5, y - 22, CREAM, lead=1.5)
        c.setStrokeColorRGB(*GOLD); c.line(W / 2 - 20, y - 8, W / 2 + 20, y - 8)
        y = para(c, "Practice", "SB", 11, y - 30, GOLD)
        para(c, practice, "S", 11.5, y - 4, CREAM, lead=1.5)
        c.showPage()
    bg(c)
    y = para(c, "Every night", "SB", 20, H - 110, CREAM)
    y = para(c, "“I examine my entire day and go back over what I've done and said, hiding nothing from myself.”", "SI", 14, y - 14, CREAM, lead=1.4)
    y = para(c, "Seneca, On Anger 3.36", "S", 10, y - 4, GOLD)
    y = para(c, "Before bed: What did I do well? Where did I fall short? What will I do differently tomorrow?", "S", 12, y - 22, CREAM, lead=1.5)
    para(c, "Three posts a day on Instagram: @moodiusaurelius", "S", 11, y - 40, GOLD)
    c.showPage(); c.save()


if __name__ == "__main__":
    main(sys.argv[1])
