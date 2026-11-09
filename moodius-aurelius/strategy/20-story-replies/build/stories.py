#!/usr/bin/env python3
"""Story specs for 26 Oct - 7 Nov 2026 (render with tools/stills_v3.py).

Pattern: 21:00 hook question with a one-word reply -> 09:00 answer -> 12:00 carousel on the same story.
Stories carry no new quotes: any quote shown is copied from an already-verified carousel.
"""
import json, os

ASK = "Reply with one word. Answer tomorrow at 9."
NOT_ADVICE = "History, not medical advice."

# slot, replaces (Metricool id or None), spec
S = [
 ("2026-10-26 09:00", "402026011", "D01-monday-putting-off", dict(kind="story", label="Monday check-in", lines=[
   ("What are you putting off today?", "claim"),
   ("Just the word. Nobody else sees your reply.", "body"),
   ("I’ll go first: the dentist. Every year.", "small")],
   footer="Why we do it, at 12:00")),
 ("2026-10-26 21:00", "402026240", "D02-quiz-dreaded", dict(kind="story", label="Be honest", lines=[
   ("Everything you dreaded this year.", "claim"),
   ("How much of it actually happened?", "body"),
   ("A  most of it\nB  hardly any", "quote"),
   (ASK.replace("one word", "A or B"), "small")])),
 ("2026-10-27 09:00", "402026274", "D03-answer-dreaded", dict(kind="story", label="Answer", lines=[
   ("If you said B, the data agrees.", "claim"),
   ("People with anxiety logged their worries for weeks. 91% never came true.", "body"),
   ("LaFreniere & Newman, Behavior Therapy, 2020. Small study, 29 people.", "small")],
   footer="What Marcus did about it, at 12:00")),
 ("2026-10-28 21:00", "402026718", "D04-quiz-99-kind", dict(kind="story", label="Quick one", lines=[
   ("99 kind comments. 1 mean one.", "claim"),
   ("Which one are you still thinking about at bedtime?", "body"),
   ("Reply “the 1” or “the 99”. Answer tomorrow at 9.", "small")])),
 ("2026-10-29 09:00", "402026761", "D05-answer-99-kind", dict(kind="story", label="Answer", lines=[
   ("The 1. You’re normal.", "claim"),
   ("Psychologists call it “bad is stronger than good”: one sting outweighs a lot of kindness.", "body"),
   ("Baumeister et al., Review of General Psychology, 2001.", "small")],
   footer="How to turn the volume down, at 12:00")),
 ("2026-10-29 21:00", "402026941", "D06-quiz-friend-texted", dict(kind="story", label="Think of one person", lines=[
   ("The friend you’ve texted most this month.", "claim"),
   ("Are you more like them than a year ago?", "body"),
   ("Reply yes or no. Or send this to them and ask.", "small")])),
 ("2026-10-30 09:00", "402026980", "D07-answer-friend-texted", dict(kind="story", label="Answer", lines=[
   ("Aristotle would say yes.", "claim"),
   ("He thought good friends improve each other just by spending time together.", "body"),
   ("Moodius paraphrase of Nicomachean Ethics, Book IX.", "small")],
   footer="Choose them well, at 12:00")),
 ("2026-10-30 21:00", "402027189", "D08-quiz-confucius", dict(kind="story", label="Guess", lines=[
   ("A student tells Confucius: “I’ve mastered kindness.”", "claim"),
   ("What does Confucius say?", "body"),
   ("A  “Well done.”\nB  “Not yet.”", "quote"),
   (ASK.replace("one word", "A or B"), "small")])),
 ("2026-10-31 09:00", "402027253", "D09-answer-confucius", dict(kind="story", label="Answer", lines=[
   ("B. Brutal. Weirdly hopeful.", "claim"),
   ("“Ts’ze, you have not attained to that.”", "quote"),
   ("Analects V.11, tr. James Legge.", "small")],
   footer="Why “not yet” isn’t never, at 12:00")),
 ("2026-11-01 21:00", "402027761", "D10-quiz-who-paid", dict(kind="story", label="Dinner’s over", lines=[
   ("Who’s happier walking home?", "claim"),
   ("A  the friend who paid\nB  the friend who didn’t", "quote"),
   (ASK.replace("one word", "A or B"), "small")])),
 ("2026-11-02 09:00", None, "D11-answer-who-paid", dict(kind="story", label="Answer", lines=[
   ("Maybe A.", "claim"),
   ("In 120 of 136 countries, people who’d spent on others lately reported more wellbeing.", "body"),
   ("Aknin et al., 2013. Linked, not proven to cause it.", "small")],
   footer="The cheap experiment, at 12:00")),
 ("2026-11-02 21:00", None, "D12-quiz-emperor-mood", dict(kind="story", label="Guess", lines=[
   ("A Roman emperor’s fix for a bad mood.", "claim"),
   ("A  wine\nB  a list of his friends’ best bits", "quote"),
   (ASK.replace("one word", "A or B"), "small")])),
 ("2026-11-03 09:00", None, "D13-answer-emperor-mood", dict(kind="story", label="Answer", lines=[
   ("B. Very wholesome. Slightly annoying.", "claim"),
   ("Marcus Aurelius thought about the good qualities of the people around him.", "body"),
   ("Meditations 6.48.", "small")],
   footer="Try his list, at 12:00")),
 ("2026-11-03 21:00", None, "D14-quiz-timbuktu", dict(kind="story", label="Guess", lines=[
   ("A medical book in Timbuktu names a tree.", "claim"),
   ("Where can you see one today?", "body"),
   ("A  a park in Mali\nB  nobody knows which tree it is", "quote"),
   (ASK.replace("one word", "A or B"), "small")])),
 ("2026-11-04 09:00", None, "D15-answer-timbuktu", dict(kind="story", label="Answer", lines=[
   ("B. Still a mystery.", "claim"),
   ("Scholars still can’t identify some trees named in Timbuktu’s handbooks.", "body"),
   (NOT_ADVICE, "small")],
   footer="The library behind it, at 12:00")),
 ("2026-11-04 21:00", None, "D16-quiz-li-shizhen", dict(kind="story", label="Guess", lines=[
   ("How long did Li Shizhen spend writing one book of medicines?", "claim"),
   ("A  2 years\nB  27 years", "quote"),
   (ASK.replace("one word", "A or B"), "small")])),
 ("2026-11-05 09:00", None, "D17-answer-li-shizhen", dict(kind="story", label="Answer", lines=[
   ("27 years.", "claim"),
   ("UNESCO now lists his Bencao Gangmu as world heritage. Your unfinished project has time.", "body"),
   ("UNESCO Silk Roads. " + NOT_ADVICE, "small")])),
 ("2026-11-05 21:00", None, "D18-ask-thank-you", dict(kind="story", label="One word", lines=[
   ("Something a friend did this year that you never thanked them for.", "claim"),
   ("Reply with one word. Then go and thank them.", "body"),
   ("I’ll check tomorrow. Gently.", "small")])),
 ("2026-11-06 09:00", None, "D19-answer-thank-you", dict(kind="story", label="Did you?", lines=[
   ("Sent the thank-you? Reply “done”.", "claim"),
   ("In one study, writing and delivering a thank-you letter gave the biggest happiness boost of five exercises. It faded after a month, so repeat.", "body"),
   ("Seligman et al., American Psychologist, 2005.", "small")])),
 ("2026-11-06 21:00", None, "D20-quiz-ebers", dict(kind="story", label="Guess", lines=[
   ("Egypt’s Ebers Papyrus, c. 1550 BCE, one of the oldest medical books.", "claim"),
   ("Where is it kept today?", "body"),
   ("A  Cairo\nB  Leipzig", "quote"),
   (ASK.replace("one word", "A or B"), "small")])),
 ("2026-11-07 09:00", None, "D21-answer-ebers", dict(kind="story", label="Answer", lines=[
   ("B. Leipzig, Germany.", "claim"),
   ("Around 700 remedies, 3,500 years old, living in a university library. It has seen things.", "body"),
   ("Encyclopaedia Britannica. " + NOT_ADVICE, "small")],
   footer="The friend who always pays, at 18:00")),
 ("2026-11-07 21:00", None, "D22-vote-next", dict(kind="story", label="You pick", lines=[
   ("Two weeks of stories. Which do you want more of?", "claim"),
   ("A  forgotten history\nB  how your mind works\nC  being kind, with evidence", "quote"),
   ("Reply A, B or C. Most replies wins next week.", "small")])),
]

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    json.dump({k: v for _, _, k, v in S}, open(os.path.join(here, "stills-spec.json"), "w"), ensure_ascii=False, indent=1)
    json.dump([dict(slot=s, replaces=r, id=k, type="STORY", alt=" ".join(t for t, _ in v["lines"]).replace("\n", " / "))
               for s, r, k, v in S], open(os.path.join(here, "..", "stories.json"), "w"), ensure_ascii=False, indent=1)
