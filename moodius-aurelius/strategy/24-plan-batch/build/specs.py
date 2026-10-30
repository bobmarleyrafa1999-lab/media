#!/usr/bin/env python3
"""Slide specs for the 90-day-plan batch built Fri 30 Oct 2026 (render with tools/stills_v3.py).

Posts: PC1 Franklin (Thu 5 Nov 12:00), PC2 gratitude letter (Fri 6 Nov 12:00), PC3 metta (Sat 7 Nov 12:00),
PC4 Onesimus (Mon 9 Nov 12:00); stories PS1 (Sun 8 Nov 09:00), PS2 Sunday Journal (Sun 8 Nov 21:00).
Every quote was checked on 30 Oct against the edition named on the slide (see ../sources.md).
"""
import json, os

OB, SG, OI, FK = "One Book, One Idea, One Action", "Small Good Thing", "Old Idea", "Forgotten Knowledge"
FR = "Franklin, Autobiography ch. IX · Standard Ebooks"
MS = "Metta Sutta, Sutta Nipata I.8 · tr. V. Fausböll, 1881"

C = {
 "PC1-franklin-chart": [
  dict(kind="cover", kicker=OB, claim="Benjamin Franklin kept a chart of his own faults.", sub="It didn’t go well. That was the point.", size=84),
  dict(kind="term", tag="Philadelphia, 1720s", term="A young printer with a plan", definition="Franklin decided to work on his character on purpose, one trait at a time, and to keep score."),
  dict(kind="term", tag="The list", term="Thirteen virtues", definition="Temperance, Silence, Order, Resolution, Frugality, Industry, Sincerity, Justice, Moderation, Cleanliness, Tranquillity, Chastity, Humility.", cite=FR),
  dict(kind="term", tag="The method (Moodius paraphrase)", term="One black dot per slip", definition="A little book, a page per virtue, a column per day. One virtue got his full attention each week, so all thirteen fitted in thirteen weeks."),
  dict(kind="quote", quote="I was surprised to find myself so much fuller of faults than I had imagined; but I had the satisfaction of seeing them diminish.", note="Franklin, on his first pages of dots.", cite=FR, size=58),
  dict(kind="term", tag="The one that beat him", term="Order", definition="“My scheme of Order gave me the most trouble.” He admits it never quite stuck. He kept the book anyway.", cite=FR),
  dict(kind="step", n=1, title="One trait. One week.", body="One dot per slip. Count on Sunday. The goal isn’t a clean page. It’s noticing."),
  dict(kind="signoff", line="Watching a habit is the first thing that changes it.", action="Researched introduction: no personal review yet. The Autobiography is free to read. Which virtue first?", size=70),
 ],
 "PC2-thank-you-note": [
  dict(kind="cover", kicker=SG, claim="You think a thank-you note would be awkward.", sub="The person getting it disagrees.", size=84),
  dict(kind="term", tag="Chicago, 2018", term="Letters of thanks", definition="Psychologists asked people to write a short note of gratitude to someone who had mattered to them, then guess how it would land.", cite="Kumar & Epley, Psychological Science, 2018"),
  dict(kind="term", tag="The guess", term="“They’ll find it awkward.”", definition="Writers expected the recipient to feel more awkward, and less surprised and happy, than the recipients reported feeling."),
  dict(kind="term", tag="Why we don’t send it", term="We grade the wording.", definition="Writers worried about getting the words right. Recipients cared about the warmth. (Moodius’s reading of the study.)"),
  dict(kind="step", n=1, title="Three lines. One person. Today.", body="What they did. What it changed. That you’re grateful. Send it before you edit it."),
  dict(kind="signoff", line="The thank-you you keep not sending is probably welcome.", action="Send this to the friend you’ve been meaning to thank. Who’s owed one?", size=70),
 ],
 "PC3-metta": [
  dict(kind="cover", kicker=OI, claim="A 2,500-year-old practice for the person who annoys you.", sub="Not forgiveness. Something quieter.", size=80),
  dict(kind="term", tag="India, about 5th century BCE", term="The Metta Sutta", definition="A short Buddhist text on goodwill. It covers everyone: seen and unseen, near and far, and the people you would rather skip.", cite=MS),
  dict(kind="quote", quote="As a mother at the risk of her life watches over her own child, her only child, so also let every one cultivate a boundless (friendly) mind towards all beings.", note="Verse 148.", cite=MS, size=54),
  dict(kind="quote", quote="Let no one deceive another, let him not despise (another) in any place, … let him not out of anger or resentment wish harm to another.", note="Verse 147.", cite=MS, size=54),
  dict(kind="term", tag="What it asks (Moodius’s reading)", term="Wish them well. Quietly.", definition="Not liking them. Not agreeing. A short private wish that they go well. It’s called a practice because you repeat it, badly, until it’s less bad."),
  dict(kind="term", tag="What research says", term="Loving-kindness meditation", definition="A 2015 review of 24 studies (1,759 people) found medium gains in daily positive mood. Many studies were small or at risk of bias. Linked, not proven.", cite="Zeng et al., Frontiers in Psychology, 2015"),
  dict(kind="signoff", line="Pick one person. Thirty seconds. Nobody has to know.", action="Send this to the friend who’s still annoyed about last week. Who’s yours?", size=70),
 ],
 "PC4-onesimus": [
  dict(kind="cover", kicker=FK, claim="In 1721 Boston, an enslaved man explained how to stop smallpox.", sub="Few listened. The numbers did.", size=78),
  dict(kind="term", tag="Boston, 1716", term="Onesimus", definition="A West African man enslaved by the minister Cotton Mather. He described a procedure from home: a little matter from a smallpox sore, scratched into the skin, and the person was protected.", cite="Mather, letter to the Royal Society, 1716"),
  dict(kind="term", tag="1721", term="The epidemic", definition="Smallpox hit Boston. The doctor Zabdiel Boylston tried the method Onesimus had described. Most of the town’s doctors and press were furious."),
  dict(kind="term", tag="The count", term="About 2% vs about 14%", definition="Of roughly 280 people inoculated, about six died. Of the thousands who caught smallpox the usual way, about one in seven did.", cite="Boylston, J R Soc Med, 2012"),
  dict(kind="term", tag="The part that gets left out", term="Whose knowledge it was", definition="The method was common in West Africa and in Asia long before Boston. Onesimus tried to buy his freedom in 1716. History books named the minister."),
  dict(kind="signoff", line="The expert in the room isn’t always the one being asked.", action="History, not medical advice: inoculation of this kind was risky and is no longer used. Would you have listened?", size=66),
 ],
}

S = {
 "PS1-granua-fact": dict(kind="story", label="Sunday fact", lines=[
   ("Marcus Aurelius wrote Book 1 of the Meditations in an army camp.", "claim"),
   ("The last line of the book says where: “Among the Quadi at the Granua”, a frontier war on the Danube.", "body"),
   ("No audience. No performance. That’s why it still reads like a real person.", "small")],
   footer="The diary carousel is on the grid at 12:00"),
 "PS2-journal-enough": dict(kind="story", label="Sunday journal", lines=[
   ("What would “enough” look like?", "claim"),
   ("Money, work, people, rest. Pick one and describe the day you’d stop pushing.", "body"),
   ("Add your answer below if you like. Nobody else sees it.", "small")],
   footer="Journal · Sunday 8 Nov"),
}

if __name__ == "__main__":
    out = {}
    for name, slides in C.items():
        n = len(slides)
        for i, s in enumerate(slides, 1):
            s = dict(s); s["page"] = f"{i}/{n}"
            out[f"{name}-{i:02d}"] = s
    out.update(S)
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "stills-spec.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(len(out), "slides")
