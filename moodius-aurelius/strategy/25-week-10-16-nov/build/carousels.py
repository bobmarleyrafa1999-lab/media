#!/usr/bin/env python3
"""Carousels for 10-16 Nov 2026 in grid format v2 (option C, picked 8 Nov). Step 1 (to 12 Nov): Slate.
Step 2 (13-19 Nov): every other carousel on Sand. Renders to ../renders/<id>/NN.jpg.
Post numbers continue the feed count (53 feed posts published by 8 Nov; PC4 54, PL04 55)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "27-grid-refresh", "build"))
import grid_v2 as g

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "renders")

# id, slot, ground, label, post no, hook (*word* = brush underline), inner slides (title, body), signoff (title, body)
C = [
 ("W1-old-place", "2026-11-10 12:00", "slate", "Mind", 56,
  "You drive past a place you used to be *someone else* in.",
  [("The sting has a name.", "Nostalgia. Not sadness, not quite happiness: both at once, aimed at a version of you that doesn't exist any more."),
   ("What the research found", "In 2006, psychologists asked people to write about a nostalgic memory. Afterwards they felt more connected to others, surer of who they were, and more positive. Nostalgia did work, not damage. (Wildschut et al., J. Personality and Social Psychology, 2006.)"),
   ("Why it hurts anyway", "You're not grieving the place. You're meeting the person who stood there and noticing how far you've walked. Distance is the evidence of change."),
   ("So, next time:", "Don't drive faster. Say the year out loud. Name one thing that version of you got right. Then keep going.")],
  ("Which place?", "Send this to the friend who still takes the long way past it. Answer below.")),
 ("W2-call-for-no-reason", "2026-11-12 12:00", "slate", "People", 60,
  "Nobody taught you how to call a friend *for no reason.*",
  [("The excuse", "You need an occasion. A birthday, a favour, bad news. Without one, the call feels like an intrusion, so you don't make it."),
   ("What the research found", "In 13 experiments (about 5,900 people), those who sent a short, unprompted message underestimated how glad the other person was to get it. The surprise was most of the gift. (Liu et al., J. Personality and Social Psychology, 2022.)"),
   ("Why we get it wrong", "You judge the message by how awkward it feels to send. They judge it by the fact that you thought of them."),
   ("So, today:", "One name. The sentence you'd say if you bumped into them. Send it before the occasion shows up.")],
  ("Who's the name?", "Send this to the friend you only text on birthdays. Answer below.")),
 ("W3-twelve-sailors", "2026-11-13 12:00", "sand", "Body", 62,
  "In 1747 a ship's doctor split twelve *sick* sailors into pairs.",
  [("The disease", "Scurvy. On long voyages it killed sailors by the thousand: bleeding gums, old wounds reopening, exhaustion. Nobody agreed on the cause."),
   ("The experiment", "James Lind, surgeon on HMS Salisbury, gave each pair a different remedy: cider, vinegar, seawater, a spice paste, dilute acid, and two oranges and a lemon a day."),
   ("The result", "The citrus pair were fit for duty within a week. Lind published it in 1753. It is one of the earliest controlled trials on record."),
   ("The slow part", "The Royal Navy made lemon juice standard issue in 1795. Forty-two years after the book. The evidence was never the problem."),
   ("What it's for", "Most of us already own the answer to the thing we keep struggling with. The gap is rarely knowledge. Historical interest only, not medical advice.")],
  ("Evidence or habit?", "Send this to the friend who's read the book twice and changed nothing. Answer below.")),
 ("W4-epictetus-deep-dive", "2026-11-15 12:00", "slate", "Mind", 66,
  "Born enslaved. Banished from Rome. The *freest* man in the empire.",
  [("Hierapolis, about AD 50", "A boy is born into slavery in a Greek city in what is now Turkey. We don't know the name he was given. Epictetus just means \"acquired\"."),
   ("Nero's court", "He is owned by Epaphroditus, Nero's secretary and himself a former slave. Epictetus walks with a limp. One ancient writer says a master broke his leg; another says he was lame from childhood. Nobody knows."),
   ("A slave at a philosophy lecture", "Still enslaved, he is allowed to study under Musonius Rufus, the leading Stoic teacher in Rome. The lessons were about what a person can and can't control. He had unusual data."),
   ("Freed, then thrown out", "After Nero's death he is freed and teaches in Rome. Around AD 90 the emperor Domitian banishes philosophers from the city. He moves to Nicopolis, a small town in western Greece, and opens a school."),
   ("\"He is free who lives as he wishes to live; who is neither subject to compulsion nor to hindrance, nor to force.\"", "Epictetus, Discourses 4.1, tr. George Long (public domain)."),
   ("He wrote nothing down", "Everything we have was taken down by a student, Arrian, who later became a Roman consul. Eight books of lectures, of which four survive, plus a pocket handbook: the Enchiridion."),
   ("\"It is you who know yourself, how much you are worth to yourself, and at what price you sell yourself; for men sell themselves at various prices.\"", "Epictetus, Discourses 1.2, tr. George Long (public domain)."),
   ("The emperor's teacher", "Decades after his death, Marcus Aurelius thanked a friend for lending him \"the discourses of Epictetus\" (Meditations 1.7). The most powerful man alive learned Stoicism from a former slave's lecture notes."),
   ("The lamp", "Lucian tells a story: after Epictetus died, around AD 135, a collector paid 3,000 drachmas for his clay lamp, as if the light had come from the lamp. The point of the story is that it hadn't.")],
  ("Who should the next deep dive be?", "Comment a name. Send this to the friend who's waiting to feel free until something changes.")),
 ("W5-anger-ledger", "2026-11-16 12:00", "sand", "Mind", 68,
  "Your anger costs you more than *what caused it.*",
  [("The maths", "The remark took four seconds. You've now spent forty minutes on it: the reply you didn't send, the replay in the shower, the version where you win."),
   ("An emperor's ledger", "Marcus Aurelius listed ten things to tell himself when someone wronged him. Number eight reads like an accountant's note."),
   ("\"Consider how much more pain is brought on us by the anger and vexation caused by such acts than by the acts themselves, at which we are angry and vexed.\"", "Marcus Aurelius, Meditations 11.18, tr. George Long (public domain)."),
   ("Not: don't feel it", "He isn't asking you to be unbothered. He's asking you to count. The original act was theirs. Every minute since has been billed to you."),
   ("So, today:", "When it flares, name the two costs out loud: what they did, and what it's costing you now. Then ask which bill you want to keep paying.")],
  ("Which cost?", "Send this to the friend who's still composing the comeback. Answer below.")),
]

if __name__ == "__main__":
    for cid, slot, ground, label, no, hook, inners, (sl, sb) in C:
        d = os.path.join(OUT, cid); os.makedirs(d, exist_ok=True)
        total = len(inners) + 2
        seed = no * 10
        g.tile(hook, ground, "carousel", label, no=no, seed=seed).save(os.path.join(d, "01.jpg"), quality=92)
        for i, (t, b) in enumerate(inners, start=2):
            g.inner(t, b, ground, i, total, seed + i, label).save(os.path.join(d, f"{i:02d}.jpg"), quality=92)
        g.inner(sl, sb, ground, total, total, seed + total, label).save(os.path.join(d, f"{total:02d}.jpg"), quality=92)
        print(cid, total, "slides", ground)
