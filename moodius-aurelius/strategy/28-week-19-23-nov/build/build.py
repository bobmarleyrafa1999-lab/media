#!/usr/bin/env python3
"""Catch-up build for Thu 19 - Mon 23 Nov 2026 (the Fri 13 Nov weekly run never ran: usage credits).
Carousels + reel covers in grid format v2 (option C). 19 Nov carousel = Slate (16 Nov was Sand);
step 3 from 20 Nov 12:00: Sand, Slate, Olive. Post numbers continue the feed count (16 Nov 18:00 = NO. 69).
Quotes checked against the cached Standard Ebooks text in reels-engine/.sources (Long, Meditations 1 and 5).
Stories use tools/stills_v3.py kind "story". Renders to ../renders/."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "27-grid-refresh", "build"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "tools"))
import grid_v2 as g
OUT = os.path.join(HERE, "..", "renders")

C = [
 ("C70-thank-you-list", "2026-11-19 12:00", "slate", "People", 70,
  "The most powerful man in Rome opened his notebook with a *thank-you* list.",
  [("Book 1", "Before a single piece of advice to himself, Marcus Aurelius spends the first book of the Meditations naming people, one by one, and what each of them taught him."),
   ("“From my grandfather Verus I learned good morals and the government of my temper.”", "Marcus Aurelius, Meditations 1.1, tr. George Long (public domain)."),
   ("Small lessons count", "A grammar teacher, Alexander, taught him how to correct someone without making them feel small: don't point out the mistake, just use the right word yourself in your reply (1.10)."),
   ("“…not frequently nor without necessity to say to anyone, or to write in a letter, that I have no leisure.”", "From Alexander the Platonist. Meditations 1.12, tr. George Long. An emperor, reminding himself not to say he's too busy."),
   ("So, today:", "Write one line. From ___, I learned ___. Then send it to them. Most people never find out what they taught you.")],
  ("Whose name goes first?", "Send this to someone who'd be on your list. Answer below.")),
 ("C72-argued-with-his-bed", "2026-11-20 12:00", "sand", "Body", 72,
  "The emperor of Rome also argued with his *bed.*",
  [("Book 5, line one", "The most powerful man alive opens a page of his private notebook like this:"),
   ("“In the morning when thou risest unwillingly, let this thought be present—I am rising to the work of a human being.”", "Marcus Aurelius, Meditations 5.1, tr. George Long (public domain)."),
   ("Then he argues back", "He writes his own excuses into the page. “But this is more pleasant.” “But it is necessary to take rest also.” And he agrees: rest is necessary."),
   ("Not against sleep", "He doesn't shout himself out of bed. He reminds himself what he's getting up for. A reason, not a rule."),
   ("So, tonight:", "Write down the first thing you're getting up for tomorrow. Small counts: the coffee, the walk, one call.")],
  ("Snooze or up?", "Send this to the friend who sets five alarms. Answer below.")),
]

# reel covers (videoThumbnailUrl), grid v2 reel tile
R = [
 ("R010-cover-71", "slate", "Mind", 71, "*Fine* is a word that ends conversations."),
 ("F01-cover-73", "slate", "People", 73, "The friends you keep are *training* you."),
]

ASK = "Reply with one word. Answer tomorrow at 9."
S = [
 ("2026-11-18 21:00", "D39-quiz-book-one", dict(kind="story", label="Quick one", lines=[
   ("An emperor's private notebook. What fills the whole first book?", "claim"),
   ("A  complaints\nB  thank-yous", "quote"),
   ("Reply A or B. Answer tomorrow at 9.", "small")])),
 ("2026-11-19 09:00", "D40-answer-book-one", dict(kind="story", label="Answer", lines=[
   ("B. A whole book of thank-yous.", "claim"),
   ("Before any advice to himself, Marcus Aurelius names the people who shaped him, one by one: a grandfather, his mother, teachers, a brother, friends.", "body"),
   ("Meditations, Book 1.", "small")], footer="The list, at 12:00")),
 ("2026-11-19 21:00", "D41-quiz-book-five", dict(kind="story", label="Quick one", lines=[
   ("Meditations, Book 5, line one. What is the emperor writing about?", "claim"),
   ("A  war\nB  getting out of bed\nC  taxes", "quote"),
   ("Reply A, B or C. Answer tomorrow at 9.", "small")])),
 ("2026-11-20 09:00", "D42-answer-book-five", dict(kind="story", label="Answer", lines=[
   ("B. Getting out of bed.", "claim"),
   ("“In the morning when thou risest unwillingly, let this thought be present—I am rising to the work of a human being.”", "body"),
   ("Marcus Aurelius, Meditations 5.1, tr. George Long.", "small")], footer="How he argues with himself, at 12:00")),
 ("2026-11-20 21:00", "D43-vote-friday", dict(kind="story", label="You pick", lines=[
   ("More of which next week?", "claim"),
   ("A  history\nB  mind\nC  kindness", "quote"),
   ("Reply A, B or C. Most replies wins.", "small")])),
 ("2026-11-21 09:00", "D44-saturday-line", dict(kind="story", label="Saturday", lines=[
   ("One small thing for the weekend.", "claim"),
   ("Send one line to someone who taught you something this year. “From you I learned…” is enough.", "body"),
   ("From Thursday's thank-you list.", "small")])),
 ("2026-11-22 21:00", "D45-sunday-journal", dict(kind="story", label="Journal", lines=[
   ("Who made your week better?", "claim"),
   ("One name. They don't have to know. (They should, though.)", "body"),
   (ASK.replace(" Answer tomorrow at 9.", ""), "small")])),
 ("2026-11-23 09:00", "D46-monday-worry", dict(kind="story", label="Monday check-in", lines=[
   ("What's the one thing you're already worried about this week?", "claim"),
   ("Just the word. Nobody else sees your reply.", "body"),
   ("Moodius: the boiler.", "small")], footer="A chart about that, at 12:00")),
 ("2026-11-23 21:00", "D47-quiz-knowing-doing", dict(kind="story", label="Quick one", lines=[
   ("Be honest. Which list is longer?", "claim"),
   ("A  things you know you should do\nB  things you actually do", "quote"),
   ("Reply A or B. Answer tomorrow at 9.", "small")])),
 ("2026-11-24 09:00", "D48-answer-knowing-doing", dict(kind="story", label="Answer", lines=[
   ("A, for nearly everyone.", "claim"),
   ("Knowing and doing are different muscles. Most of us train only one.", "body")], footer="A chart about that, at 12:00")),
]

if __name__ == "__main__":
    import stills_v3 as sv
    os.makedirs(OUT, exist_ok=True)
    for cid, slot, ground, label, no, hook, inners, (sl, sb) in C:
        d = os.path.join(OUT, cid); os.makedirs(d, exist_ok=True)
        total = len(inners) + 2
        seed = no * 10
        g.tile(hook, ground, "carousel", label, no=no, seed=seed).save(os.path.join(d, "01.jpg"), quality=92)
        for i, (t, b) in enumerate(inners, start=2):
            g.inner(t, b, ground, i, total, seed + i, label).save(os.path.join(d, f"{i:02d}.jpg"), quality=92)
        g.inner(sl, sb, ground, total, total, seed + total, label).save(os.path.join(d, f"{total:02d}.jpg"), quality=92)
        print(cid, total, "slides", ground)
    for name, ground, label, no, hook in R:
        g.tile(hook, ground, "reel", label, no=no, seed=no * 10).save(os.path.join(OUT, name + ".jpg"), quality=92)
    # meme MP07 slide 2 (Seneca footnote)
    g.inner("“We suffer more often in imagination than in reality.”",
            "Seneca, Moral Letters 13.4, tr. Richard M. Gummere (public domain). Seneca got there first.",
            "slate", 2, 2, 742, "Mind").save(os.path.join(OUT, "MP07-02.jpg"), quality=92)
    sd = os.path.join(OUT, "stories"); os.makedirs(sd, exist_ok=True)
    for slot, k, spec in S:
        sv.render(spec).save(os.path.join(sd, k + ".jpg"), quality=94)
    json.dump([dict(slot=s, id=k, alt=" ".join(t for t, _ in v["lines"]).replace("\n", " / ")) for s, k, v in S],
              open(os.path.join(HERE, "..", "stories.json"), "w"), ensure_ascii=False, indent=1)
    print(len(S), "stories")
