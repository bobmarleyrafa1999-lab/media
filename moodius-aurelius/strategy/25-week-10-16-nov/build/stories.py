#!/usr/bin/env python3
"""Story specs for 9-16 Nov 2026 (render with tools/stills_v3.py). 21:00 question -> 09:00 answer/morning line.
No new quotes: facts repeat verified carousel content."""
import json, os
ASK = "Reply with one word. Answer tomorrow at 9."
S = [
 ("2026-11-09 09:00", "D23-monday-dread", dict(kind="story", label="Monday check-in", lines=[
   ("What's the one thing this week you're already dreading?", "claim"),
   ("Just the word. Nobody else sees your reply.", "body"),
   ("Moodius: the Thursday call.", "small")], footer="Tonight: a quick quiz")),
 ("2026-11-09 21:00", "D24-quiz-old-place", dict(kind="story", label="Quick one", lines=[
   ("You drive past somewhere you used to live.", "claim"),
   ("Afterwards you mostly feel:", "body"),
   ("A  warmer\nB  worse", "quote"),
   (ASK.replace("one word", "A or B"), "small")])),
 ("2026-11-10 09:00", "D25-answer-old-place", dict(kind="story", label="Answer", lines=[
   ("If you said A, so did the research.", "claim"),
   ("People asked to write about a nostalgic memory came out feeling more connected to others and surer of who they were.", "body"),
   ("Wildschut et al., J. Personality and Social Psychology, 2006.", "small")], footer="Why it still stings, at 12:00")),
 ("2026-11-10 21:00", "D26-poll-deep-dive", dict(kind="story", label="You pick the next deep dive", lines=[
   ("Septima Clark or Arthur Ashe?", "claim"),
   ("Clark: the teacher behind the civil-rights citizenship schools. Ashe: the champion who used his platform off the court.", "body"),
   ("Tap the poll, or reply with a name.", "small")], footer="Epictetus deep dive lands Sunday")),
 ("2026-11-11 09:00", "D27-before-you-send", dict(kind="story", label="Wednesday", lines=[
   ("Before you send it today.", "claim"),
   ("Write the message. Read it as the person receiving it. Then decide.", "body"),
   ("Votes from last night still open.", "small")], footer="Why, at 12:00")),
 ("2026-11-11 21:00", "D28-which-emotion", dict(kind="story", label="Journal", lines=[
   ("Which emotion visited most this week?", "claim"),
   ("One word. Nobody else sees your reply.", "body"),
   (ASK, "small")])),
 ("2026-11-12 09:00", "D29-it-had-a-reason", dict(kind="story", label="Morning", lines=[
   ("Whatever you named last night had a reason to come.", "claim"),
   ("Today, when it shows up, ask what it wants before you argue with it.", "body")],
   footer="18:00: a new series. The slave who taught an emperor.")),
 ("2026-11-12 21:00", "D30-forgive-today", dict(kind="story", label="Journal", lines=[
   ("What did you forgive today?", "claim"),
   ("Big or tiny. The driver counts.", "body"),
   (ASK, "small")])),
 ("2026-11-13 09:00", "D31-quiz-sailors", dict(kind="story", label="Friday quiz", lines=[
   ("In 1747 a ship's doctor tested six remedies on twelve sick sailors.", "claim"),
   ("Which one worked?", "body"),
   ("A  cider\nB  oranges and lemons\nC  seawater", "quote"),
   ("Reply A, B or C. Answer at 12:00.", "small")])),
 ("2026-11-13 21:00", "D32-vote-friday", dict(kind="story", label="You pick", lines=[
   ("Next Friday's forgotten history. Which field?", "claim"),
   ("A  medicine\nB  astronomy\nC  food", "quote"),
   ("Reply A, B or C. Most replies wins.", "small")])),
 ("2026-11-14 09:00", "D33-part-three", dict(kind="story", label="Saturday", lines=[
   ("Part 3 of 3 lands at 12:00.", "claim"),
   ("A three-step test for how free you are. Guess the steps before you watch.", "body")],
   footer="Reel at 12:00")),
 ("2026-11-14 21:00", "D34-today-taught", dict(kind="story", label="Journal", lines=[
   ("What did today teach you?", "claim"),
   ("One line. It doesn't have to be profound.", "body"),
   (ASK, "small")])),
 ("2026-11-15 09:00", "D35-sunday-deep-dive", dict(kind="story", label="Sunday", lines=[
   ("Born enslaved. Banished from Rome.", "claim"),
   ("The full Epictetus story, ten slides, at 12:00. Read it slowly.", "body")],
   footer="Carousel at 12:00")),
 ("2026-11-15 21:00", "D36-differently-tomorrow", dict(kind="story", label="Journal", lines=[
   ("What will you do differently tomorrow?", "claim"),
   ("One sentence. Write it where you'll see it at 7am.", "body"),
   (ASK, "small")])),
 ("2026-11-16 09:00", "D37-monday-anger", dict(kind="story", label="Monday", lines=[
   ("Your anger costs you more than what caused it.", "claim"),
   ("The emperor's ledger, at 12:00. Until then: count the minutes.", "body")],
   footer="Carousel at 12:00")),
 ("2026-11-16 21:00", "D38-who-needs-message", dict(kind="story", label="Journal", lines=[
   ("Who needs a message from you?", "claim"),
   ("Not the reply you owe. The one nobody's expecting.", "body"),
   (ASK, "small")])),
]
if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    json.dump({k: v for _, k, v in S}, open(os.path.join(here, "stories-spec.json"), "w"), ensure_ascii=False, indent=1)
    json.dump([dict(slot=s, id=k, type="STORY", alt=" ".join(t for t, _ in v["lines"]).replace("\n", " / ")) for s, k, v in S],
              open(os.path.join(here, "..", "stories.json"), "w"), ensure_ascii=False, indent=1)
    print(len(S), "stories")
