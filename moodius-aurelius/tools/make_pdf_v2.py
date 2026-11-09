#!/usr/bin/env python3
"""Lead-magnet PDF in the Phase 1 design: 7 Stoic Tools for When Emotions Are Loud.  python3 make_pdf_v2.py out.pdf"""
import os, sys
from reportlab.lib.pagesizes import A5
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
for name, f in [("PF", "Playfair-SemiBold.ttf"), ("PFI", "Playfair-MediumItalic.ttf"), ("PFX", "Playfair-ExtraBold.ttf"),
                ("IN", "Inter-Regular.ttf"), ("INM", "Inter-Medium.ttf"), ("INS", "Inter-SemiBold.ttf")]:
    pdfmetrics.registerFont(TTFont(name, os.path.join(D, f)))
rgb = lambda h: tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
SLATE, CHARCOAL, BONE, ASH, EMBER = rgb("1B1F24"), rgb("3A4049"), rgb("F3EFE7"), rgb("B8B3A9"), rgb("C9742E")
W, H = A5
M = 40  # margin

TOOLS = [
    ("Name the judgement", "Men are disturbed not by the things which happen, but by the opinions about the things.", "Epictetus, Enchiridion 5 (tr. Long)",
     "The feeling is real. The story that came with it is a guess. Psychologists call separating the two cognitive reappraisal, and it is linked to lower distress than pushing the feeling down.",
     "Write the event in one line. Under it, write the story you told yourself about it. Which line is the fact?"),
    ("Sort what is yours", "Of things some are in our power, and others are not.", "Epictetus, Enchiridion 1 (tr. Long)",
     "Your judgements, your effort and your actions are yours. Other people's reactions, the past and the outcome are not. Loud emotions usually come from carrying the second list.",
     "Two columns tonight: mine, not mine. Act on one thing in the first. Let the second one go on paper."),
    ("Wait before you act", "The greatest remedy for anger is delay.", "Seneca, On Anger 2.29 (tr. Basore)",
     "The first surge passes. A message sent in the surge doesn't. Waiting is not suppressing: you feel it fully, you just don't let it hold the keyboard.",
     "Next time you're angry, set a 20-minute timer before you reply, speak or decide."),
    ("Rehearse the hard day", "Begin the morning by saying to yourself: I shall meet with the busybody, the ungrateful, arrogant, deceitful, envious, unsocial.", "Marcus Aurelius, Meditations 2.1 (tr. Long)",
     "Marcus wasn't being bitter. He was preparing. Expecting friction means it doesn't ambush you, and you can choose your response in advance.",
     "Each morning, name the one person or moment most likely to test you, and decide now how you'll answer."),
    ("Shrink the imagined", "There are more things, Lucilius, likely to frighten us than there are to crush us; we suffer more often in imagination than in reality.", "Seneca, Letters 13.4 (tr. Gummere)",
     "Replaying the argument at 2am feels like solving it. It isn't. The mind keeps running the scene because it hasn't been told what you'll actually do.",
     "When the replay starts, write one sentence: \"Tomorrow I will ___.\" Then stop."),
    ("Train it by doing", "Every habit and faculty is maintained and increased by the corresponding actions.", "Epictetus, Discourses 2.18 (tr. Long)",
     "Calm is a skill, not a temperament. Every time you pause instead of react, the pause gets easier. Every time you react, so does that.",
     "Pick one trigger this week. Each time it fires, do the same small thing: breathe out, name it, choose."),
    ("Review the day", "What bad habit have you cured today? What fault have you resisted? In what respect are you better?", "Seneca, On Anger 3.36 (tr. Basore)",
     "Seneca ran this review every night, once the lamp was out. It is not self-punishment. It is noticing, so tomorrow goes a little better.",
     "Before bed, answer the three questions in a line each. Five minutes."),
]


def frame(c, page=None):
    c.setFillColorRGB(*SLATE); c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColorRGB(*EMBER); c.rect(M, H - M - 6, 6, 6, fill=1, stroke=0)
    c.setFillColorRGB(*BONE); c.setFont("INS", 8); c.drawString(M + 12, H - M - 6, "MOODIUS")
    c.setFillColorRGB(*ASH); c.setFont("IN", 7.5); c.drawRightString(W - M, M - 12, "@moodiusaurelius")
    if page: c.drawRightString(W - M, H - M - 6, page)


def para(c, text, font, size, y, colour, lead=1.4, width=W - 2 * M):
    c.setFont(font, size); c.setFillColorRGB(*colour)
    for ln in simpleSplit(text, font, size, width):
        c.drawString(M, y, ln); y -= size * lead
    return y


def rule(c, y, w=28):
    c.setStrokeColorRGB(*EMBER); c.setLineWidth(1.2); c.line(M, y, M + w, y)


def main(out):
    c = canvas.Canvas(out, pagesize=A5)
    c.setTitle("7 Stoic Tools for When Emotions Are Loud"); c.setAuthor("Moodius Aurelius")
    frame(c)
    para(c, "FREE GUIDE", "INS", 8.5, H / 2 + 120, EMBER)
    y = para(c, "7 Stoic tools for when emotions are loud", "PF", 30, H / 2 + 90, BONE, lead=1.15)
    rule(c, y - 6)
    y = para(c, "Regulate, decide and act. One tool a day for a week.", "IN", 11.5, y - 28, ASH)
    para(c, "Epictetus · Seneca · Marcus Aurelius", "INM", 8.5, M + 10, ASH)
    c.showPage()

    frame(c, "1 / 10")
    y = para(c, "Stoicism for people who feel things", "PF", 19, H - 110, BONE, lead=1.2)
    rule(c, y - 4)
    intro = ("The Stoics are remembered as people who didn't feel. Read them and you find the opposite: "
             "Seneca grieving, Marcus irritated by the people around him, Epictetus a former slave who knew fear well. "
             "What they built was not a way to stop feeling. It was a way to feel fully and still choose what to do next.")
    y = para(c, intro, "IN", 10.5, y - 26, BONE, lead=1.6)
    y = para(c, "How to use this: read one tool a day for seven days. Do the practice. Every quote has its book and section, "
                "so you can read the original.", "IN", 10.5, y - 12, ASH, lead=1.6)
    c.showPage()

    for i, (title, quote, cite, body, practice) in enumerate(TOOLS, 1):
        frame(c, f"{i + 1} / 10")
        c.setFillColorRGB(*EMBER); c.setFont("PFX", 54); c.drawString(M, H - 140, str(i))
        y = para(c, title, "PF", 20, H - 172, BONE, lead=1.2)
        y = para(c, f"“{quote}”", "PFI", 12.5, y - 16, BONE, lead=1.45)
        y = para(c, cite.upper(), "INM", 7, y - 4, ASH)
        y = para(c, body, "IN", 10, y - 20, BONE, lead=1.6)
        rule(c, y - 6)
        y = para(c, "PRACTICE", "INS", 8, y - 26, EMBER)
        para(c, practice, "IN", 10, y - 4, BONE, lead=1.6)
        c.showPage()

    frame(c, "10 / 10")
    y = para(c, "One line to keep", "PF", 20, H - 120, BONE)
    y = para(c, "“It is not this thing that disturbs you, but your own judgement about it.”", "PFI", 14, y - 16, BONE, lead=1.4)
    y = para(c, "MARCUS AURELIUS, MEDITATIONS 8.47 (TR. LONG, MODERNISED)", "INM", 7, y - 4, ASH)
    rule(c, y - 18)
    y = para(c, "Reply to the email this came with and tell me which tool you're trying first. I read every reply.", "IN", 10.5, y - 40, BONE, lead=1.6)
    para(c, "A carousel and a reel every day on Instagram: @moodiusaurelius", "INM", 9, y - 16, EMBER)
    c.showPage(); c.save()


if __name__ == "__main__":
    main(sys.argv[1])
