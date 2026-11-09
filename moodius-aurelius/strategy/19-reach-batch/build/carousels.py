#!/usr/bin/env python3
"""Slide specs for the 19-reach-batch carousels and stories (render with tools/stills_v3.py)."""
import json, os

FK, GL, HM = "Forgotten Knowledge", "The Good Life", "The Human Mind"
NOT_ADVICE = "History, not medical advice. Some traditional remedies are toxic."

C = {
 "C1-tu-youyou": [
  dict(kind="cover", kicker=FK, claim="A Nobel Prize was hiding in a 1,600-year-old first-aid book.", sub="The clue was one boring detail.", size=84),
  dict(kind="term", tag="China, 4th century", term="Ge Hong’s handbook", definition="For fevers: soak a handful of qinghao (sweet wormwood) in water, wring out the juice, drink it.", cite="Ge Hong, Zhouhou Beiji Fang"),
  dict(kind="term", tag="Beijing, 1970s", term="Tu Youyou reads it", definition="Her team was hunting a malaria drug. Their hot extracts kept failing. Then she noticed the recipe never said boil."),
  dict(kind="term", tag="The detail", term="Cold water.", definition="Heat was destroying the active compound. Low-temperature extraction worked. The result was artemisinin, now a frontline malaria drug.", cite="Tu Youyou, Nature Medicine 17 (2011)"),
  dict(kind="term", tag="2015", term="The Nobel Prize", definition="Tu Youyou won the Nobel Prize in Physiology or Medicine. The footnote that mattered was 1,600 years old."),
  dict(kind="signoff", line="Somebody wrote it down. Somebody read it twice.", action="Modern artemisinin is purified and dosed. Wormwood juice is not a malaria treatment. History, not medical advice.", size=70),
 ],
 "C2-confucius-not-yet": [
  dict(kind="cover", kicker=GL, claim="A student told Confucius he’d mastered kindness.", sub="Confucius’s review was brutal. And weirdly hopeful."),
  dict(kind="quote", quote="What I do not wish men to do to me, I also wish not to do to men.", note="Tsze-kung, his student, feeling pretty good about himself.", cite="Analects V.11 · tr. James Legge"),
  dict(kind="quote", quote="Ts’ze, you have not attained to that.", note="The Master. Unimpressed.", cite="Analects V.11 · tr. James Legge", size=72),
  dict(kind="term", tag="Why it isn’t mean", term="Not yet isn’t never.", definition="He didn’t say the idea was wrong. He said living it is harder than saying it. The most hopeful put-down in history."),
  dict(kind="term", tag="Try it this week", term="One quiet proof", definition="Do one thing for someone that you’d want done for you. Don’t announce it. That’s the gap between saying it and doing it."),
  dict(kind="signoff", line="Nobody’s there yet. That’s the fun part.", action="Tag the friend who says “I’m basically a saint.”"),
 ],
 "C3-goat-first": [
  dict(kind="cover", kicker=FK, claim="Medieval Seville’s best doctor tested surgery on a goat first.", sub="Respect to the goat.", size=84),
  dict(kind="term", tag="Seville, 12th century", term="Ibn Zuhr (Avenzoar)", definition="Before anyone tried a tracheotomy on a person, he performed one on a goat to show it could be done safely.", cite="Karamanou et al., JBUON 20(4), 2015"),
  dict(kind="term", tag="Córdoba, 10th century", term="al-Zahrawi", definition="Wrote a thirty-volume medical encyclopedia and drew the surgical tools he used, probably the first drawings of their kind.", cite="Manaf, Hektoen International, 2015"),
  dict(kind="term", tag="Málaga, 13th century", term="Ibn al-Baytar", definition="A botanist who listed about 1,400 simple medicines from plants, animals and minerals.", cite="Cabo-González, Folia Orientalia 56, 2019"),
  dict(kind="term", tag="What they shared", term="Test it. Draw it. Write it down.", definition="Three habits that sound a lot like modern science. Al-Andalus had them a thousand years ago."),
  dict(kind="signoff", line="Curiosity, plus one very patient goat.", action=NOT_ADVICE),
 ],
 "C4-always-pays": [
  dict(kind="cover", kicker=GL, claim="The friend who always pays might be the happiest one at the table.", sub="There’s data on this. Sort of.", size=84),
  dict(kind="term", tag="136 countries", term="Spending on others", definition="People who had spent money on others in the past month reported more wellbeing in 120 of 136 countries. Linked, not proven to cause it.", cite="Aknin et al., J Pers Soc Psychol, 2013"),
  dict(kind="term", tag="One small experiment", term="Their £5, your £5", definition="In a study of 46 people, those told to spend money on someone else ended the day happier than those who spent it on themselves. Later studies found smaller effects.", cite="Dunn, Aknin & Norton, Science, 2008"),
  dict(kind="term", tag="Cheap experiment", term="£3, one person, no post", definition="Buy the coffee. Don’t mention it. Notice how the rest of the day feels."),
  dict(kind="signoff", line="Generous isn’t a personality. It’s a habit you can start on Monday.", action="Tag the friend who always pays. It’s your round.", size=70),
 ],
 "C5-cheering-up-list": [
  dict(kind="cover", kicker=HM, claim="Bad mood? An emperor’s fix: think about other people.", sub="Not their faults. Their best bits."),
  dict(kind="quote", quote="When thou wishest to delight thyself, think of the virtues of those who live with thee; for instance, the activity of one, and the modesty of another, and the liberality of a third", note="Marcus Aurelius, in his private notes.", cite="Meditations 6.48 · tr. George Long", size=56),
  dict(kind="term", tag="Why it works", term="Flip the search", definition="A bad mood goes looking for what’s wrong, including in people. Marcus sends it looking for what’s right instead. (Moodius’s reading.)"),
  dict(kind="step", n=1, title="Pick four people", body="Someone you live with, work with, text, or haven’t seen in years."),
  dict(kind="step", n=2, title="One good quality each", body="The one who’s always on time. The one who’s funny at funerals."),
  dict(kind="step", n=3, title="Tell one of them", body="A short message. No reason needed. Watch their day change. Then yours."),
  dict(kind="signoff", line="The quickest mood lift is noticing someone.", action="Tag the person you’d list first."),
 ],
 "C6-timbuktu-tree": [
  dict(kind="cover", kicker=FK, claim="A medical book in Timbuktu names a tree nobody can find.", sub="The knowledge survived. The plant went missing.", size=84),
  dict(kind="term", tag="Mali, 17th-18th century", term="Handbooks of cures", definition="Timbuktu scholars wrote down diagnoses and remedies using plants, animals and minerals, alongside prayers.", cite="The Met, record 736515"),
  dict(kind="term", tag="The puzzle", term="One name, no tree", definition="Entries name local trees in Bambara and other local languages. Some, like a tree called Ṣukuru, scholars still can’t identify.", cite="HMML, Medical Texts From Timbuktu"),
  dict(kind="term", tag="2011 survey", term="100,000+ manuscripts", definition="Kept in at least 408 private family libraries in Mali.", cite="The Met, record 736515"),
  dict(kind="signoff", line="Somewhere, a tree has a reputation it doesn’t know about.", action=NOT_ADVICE, size=70),
 ],
}

S = {
 "S1a-quiz-cold-water": dict(kind="story", label="Quick quiz", lines=[
   ("A Nobel Prize came out of a 4th-century recipe.", "claim"),
   ("Everyone else missed one detail in it. What was it?", "body"),
   ("Reply with your guess. Answer tomorrow at 9.", "small")]),
 "S1b-answer-cold-water": dict(kind="story", label="Answer", lines=[
   ("Cold water.", "claim"),
   ("The old recipe never said boil. Heat was destroying the medicine. Full story at 12:00.", "body"),
   ("Tu Youyou, Nature Medicine, 2011. History, not medical advice.", "small")]),
 "S2a-quiz-goat": dict(kind="story", label="Quick quiz", lines=[
   ("Seville, 1100s. A doctor wants to try a new throat surgery.", "claim"),
   ("Who did he test it on first?", "body"),
   ("Reply with your guess. Answer tomorrow at 9.", "small")]),
 "S2b-answer-goat": dict(kind="story", label="Answer", lines=[
   ("A goat.", "claim"),
   ("Ibn Zuhr proved the operation was safe before trying it on people. Full story at 12:00.", "body"),
   ("Karamanou et al., JBUON, 2015. History, not medical advice.", "small")]),
}

# Abstract cover motif: one big Charcoal figure tied to the story (no faces, no statues).
MOTIF = {"C1-tu-youyou": "1,600", "C2-confucius-not-yet": "not yet", "C3-goat-first": "1100s",
         "C4-always-pays": "£3", "C5-cheering-up-list": "6.48", "C6-timbuktu-tree": "408"}

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = {}
    for name, slides in C.items():
        for i, s in enumerate(slides, 1):
            s = dict(s); s["page"] = f"{i}/{len(slides)}"
            out[f"{name}/{i:02d}"] = s
    out.update({f"stories/{k}": v for k, v in S.items()})
    json.dump(out, open(os.path.join(here, "stills-spec.json"), "w"), ensure_ascii=False, indent=1)
    print(len(out), "slides")
