"""Upload pack content, 20 Oct - 1 Nov 2026 (Phase 1). Used by build.py.

Captions carry at most 5 hashtags: Instagram has capped hashtags at 5 per post since Dec 2025.
Quotes are in public-domain translations (Long, Gummere, Basore, Higginson, Jowett, Ross, Ludovici),
lightly modernised (thee/thou -> you) where noted in the citation.
"""

# ---------------------------------------------------------------- stories (stills_v3 "story")

def daily(label, quote, note, cite):
    return {"kind": "story", "label": label, "cite": cite,
            "lines": [[quote, "quote"], [note, "body"]]}


def journal(q, extra="Reply to this story. I read every one."):
    return {"kind": "story", "label": "Journal", "lines": [[q, "claim"], [extra, "small"]]}


STORIES = {
    "2026-10-21": (
        daily("Daily", "“Every habit and faculty is maintained and increased by the corresponding actions.”",
              "Keep one small promise today. That is the action.", "Epictetus · Discourses 2.18 · Long"),
        journal("What did you avoid today, and why?")),
    "2026-10-22": (
        daily("Daily", "“Begin the morning by saying to yourself: I shall meet with the busybody, the ungrateful, arrogant, deceitful, envious, unsocial.”",
              "Not cynicism. Preparation. Today won’t surprise you.", "Marcus Aurelius · Meditations 2.1 · Long"),
        journal("What feeling did you name today?")),
    "2026-10-23": (
        daily("Daily", "“We suffer more often in imagination than in reality.”",
              "If you replayed it at 2am, this one is for you.", "Seneca · Letters 13.4 · Gummere"),
        journal("Who were you kind to today?")),
    "2026-10-24": (
        daily("Daily", "“I conceal nothing from myself, I omit nothing.”",
              "Tonight: five minutes, the day in order. Honest, not harsh.", "Seneca · On Anger 3.36 · Basore"),
        journal("What hurt today? Is it endurable?")),
    "2026-10-25": (
        daily("Daily", "“Look within. Within is the fountain of good, and it will ever bubble up, if you will ever dig.”",
              "Sunday. Whatever you’re looking for this week, start there.", "Marcus Aurelius · Meditations 7.59 · Long"),
        journal("What did you notice today that was beautiful?")),
    "2026-10-26": (
        daily("Daily", "“Remember how long you have been putting off these things.”",
              "Monday. Pick the one thing. Two minutes. Start.", "Marcus Aurelius · Meditations 2.4 · Long"),
        journal("Where did you lose your temper today, even inside?")),
    "2026-10-27": (
        daily("Manifesto", "“Let not future things disturb you, for you will come to them, if it shall be necessary, having with you the same reason which now you use for present things.”",
              "Tomorrow gets the same you. That is enough.", "Marcus Aurelius · Meditations 7.8 · Long"),
        journal("What are you pretending not to know?")),
    "2026-10-28": (
        daily("Daily", "“Occupy yourself with few things, says the philosopher, if you would be tranquil.”",
              "Drop one unnecessary thing today. Notice that nothing breaks.", "Marcus Aurelius · Meditations 4.24 · Long"),
        journal("Who do you miss? Text them tonight.", "Then reply to this story with “done”.")),
    "2026-10-29": (
        daily("Tools", "“If you once gain time and respite, you will more easily command yourself.”",
              "The tool: wait an hour before you answer anything that stings.", "Epictetus · Enchiridion 20 · Higginson"),
        journal("What are you quietly proud of today?")),
    "2026-10-30": (
        daily("Discipline", "“His friend is another self.”",
              "Choose the people you’d be glad to become.", "Aristotle · Nicomachean Ethics IX.4 · Ross"),
        journal("What did fear decide for you this week?")),
    "2026-10-31": (
        daily("Truths", "“Sheep don’t throw up the grass to show the shepherds how much they have eaten; but, inwardly digesting their food, they outwardly produce wool and milk.”",
              "Don’t explain your philosophy. Show it.", "Epictetus · Enchiridion 46 · Higginson"),
        journal("What did your body need today that you ignored?")),
    "2026-11-01": (
        daily("Identity", "“The human charioteer drives his in a pair; and one of them is noble and of noble breed, and the other is ignoble.”",
              "Two horses, one driver. If today feels like a tug of war, that’s why.", "Plato · Phaedrus 246b · Jowett"),
        journal("Who made you better this week?")),
}

# ---------------------------------------------------------------- carousels written for 25 Oct - 1 Nov

C25 = {  # Week 3 carousel, quotes moved to public-domain translations
    "01": {"kind": "cover", "kicker": "For heavy weeks", "claim": "5 ancient lines for when life gets heavy."},
    "02": {"kind": "quote", "quote": "I judge you unfortunate because you have never been unfortunate; you have passed through life without an antagonist; no one will know what you can do, not even yourself.",
           "note": "The easy life never finds out who you are.", "cite": "Seneca · On Providence 4.3 · Basore", "size": 58},
    "03": {"kind": "quote", "quote": "Nothing happens to any man which he is not formed by nature to bear.",
           "note": "Others have carried this exact weight. You can too.", "cite": "Marcus Aurelius · Meditations 5.18 · Long"},
    "04": {"kind": "quote", "quote": "What do you think that Hercules would have been if there had not been such a lion, and hydra, and stag, and boar?",
           "note": "No monsters, no hero. Your problems are the plot.", "cite": "Epictetus · Discourses 1.6 · Long"},
    "05": {"kind": "quote", "quote": "What does not destroy me, makes me stronger.",
           "note": "Overused because it’s true. But only if you let it work on you.", "cite": "Nietzsche · Twilight of the Idols, Maxims 8 · Ludovici"},
    "06": {"kind": "quote", "quote": "He who suffers before it is necessary, suffers more than is necessary.",
           "note": "Most of the weight is tomorrow’s. Put it down until tomorrow.", "cite": "Seneca · Letters 98.8 · Gummere"},
    "07": {"kind": "signoff", "line": "Which one do you need this week?", "action": "Save this. Send it to someone who’s going through it."},
}

C26 = {  # Mon 26 Oct, F1 Reframe, procrastination
    "01": {"kind": "cover", "kicker": "Reframe", "claim": "You’re not lazy.\nYou’re avoiding a feeling."},
    "02": {"kind": "term", "tag": "The real issue", "term": "Avoidance",
           "definition": "Putting off a task to escape the feeling it brings: doubt, boredom, fear of doing it badly. Psychologists link procrastination to short-term mood repair, not laziness."},
    "03": {"kind": "quote", "quote": "Remember how long you have been putting off these things, and how often you have received an opportunity from the gods, and yet do not use it.",
           "note": "Marcus wrote this to himself. Even an emperor put things off.", "cite": "Marcus Aurelius · Meditations 2.4 · Long"},
    "04": {"kind": "step", "n": 1, "title": "Name the feeling", "body": "Before you open the task, finish the sentence: “I’m avoiding this because I feel…”"},
    "05": {"kind": "step", "n": 2, "title": "Shrink the start", "body": "Two minutes. Open the file, write one line. The feeling is loudest just before you begin."},
    "06": {"kind": "step", "n": 3, "title": "Bring the feeling with you", "body": "You don’t need to feel ready. Do the two minutes with the feeling still in the room."},
    "07": {"kind": "signoff", "line": "Lazy people don’t feel this bad about it.", "action": "Save this for the next thing you keep putting off."},
}

C27 = {  # Tue 27 Oct, F3 Mechanism, anxiety about tomorrow
    "01": {"kind": "cover", "kicker": "Mechanism", "claim": "How to stop rehearsing disasters that never come."},
    "02": {"kind": "term", "tag": "The mechanism", "term": "Catastrophising",
           "definition": "Your mind runs the worst case on repeat because rehearsing feels like preparing. It isn’t. It’s living the bad day in advance, often more than once."},
    "03": {"kind": "quote", "quote": "Let not future things disturb you, for you will come to them, if it shall be necessary, having with you the same reason which now you use for present things.",
           "note": "You’ll meet tomorrow with the same mind that got you through today.", "cite": "Marcus Aurelius · Meditations 7.8 · Long"},
    "04": {"kind": "step", "n": 1, "title": "Ask for the next action", "body": "Is there one thing you can do about it now? Do it or put it in the calendar. If there isn’t, the rehearsal is just noise."},
    "05": {"kind": "step", "n": 2, "title": "Come back to the room", "body": "Say: “I’ll deal with that when it’s here, with what I’ll have then.” Then name three things you can see."},
    "06": {"kind": "signoff", "line": "You’ve handled every day so far.\nTomorrow gets the same you.", "action": "Save this for the night it starts again."},
}

C28 = {  # Wed 28 Oct, F2 Ancient line, modern situation, overwhelm
    "01": {"kind": "cover", "kicker": "Ancient line, modern situation", "claim": "Do less, better: the Stoic answer to burnout.",
           "sub": "Forty tabs open, nothing finished? Marcus had a question for that."},
    "02": {"kind": "quote", "quote": "The greatest part of what we say and do being unnecessary, if a man takes this away, he will have more leisure and less uneasiness.",
           "note": "Burnout often isn’t too much work. It’s too much unnecessary work.", "cite": "Marcus Aurelius · Meditations 4.24 · Long"},
    "03": {"kind": "pair", "left": "Today", "right": "Marcus’s question", "rows": [
        ["Saying yes to every request", "Is this necessary, or just asked?"],
        ["Answering messages all evening", "Necessary now, or necessary at all?"],
        ["Ten goals for this month", "Which one, done well, makes the rest easier?"]]},
    "04": {"kind": "step", "n": 1, "title": "Cut one thing today", "body": "Ask of each task: “Is this necessary?” Drop one that isn’t. Notice that nothing breaks."},
    "05": {"kind": "signoff", "line": "Fewer things, done properly.\nThat’s the whole method.", "action": "Send this to someone running on empty."},
}

C29 = {  # Thu 29 Oct, F8 Two-column comparison, criticism
    "01": {"kind": "cover", "kicker": "Two columns", "claim": "Why one comment ruins your whole day.",
           "sub": "Ninety-nine kind ones, one sharp one. Guess which you replay."},
    "02": {"kind": "pair", "left": "Reacting", "right": "Responding", "rows": [
        ["Reread it ten times", "Read it once, then close the app"],
        ["“They think I’m useless”", "“They said one thing about one post”"],
        ["Reply in the first minute", "Wait an hour, then decide if it needs a reply"]],
        "note": "Psychologists call it negativity bias: the mind gives a threat more weight than praise."},
    "03": {"kind": "pair", "left": "What happened", "right": "What you added", "rows": [
        ["Eleven words from a stranger", "A verdict on your whole worth"],
        ["One bad review", "“I should quit”"],
        ["A friend’s short reply", "“They’re angry with me”"]],
        "note": "“It is your own opinion which provokes you.”", "cite": "Epictetus · Enchiridion 20 · Higginson"},
    "04": {"kind": "step", "n": 1, "title": "Buy time", "body": "Epictetus: gain time and respite, and you will more easily command yourself. Don’t reply today."},
    "05": {"kind": "signoff", "line": "The comment took them ten seconds.\nDon’t give it your day.", "action": "Send this to someone rereading one right now."},
}

C30 = {  # Fri 30 Oct, F10 Myth vs text, friendship
    "01": {"kind": "cover", "kicker": "Myth vs text", "claim": "“You are who you are, whoever you’re around.”",
           "sub": "Aristotle disagreed."},
    "02": {"kind": "quote", "quote": "They are thought to become better too by their activities and by improving each other; for from each other they take the mould of the characteristics they approve.",
           "note": "We take the shape of the people we admire.", "cite": "Aristotle · Nicomachean Ethics IX.12 · Ross", "size": 58},
    "03": {"kind": "term", "tag": "Why the myth spread", "term": "The self-made story",
           "definition": "It feels stronger to believe character is built alone. But moods, habits and standards are social. Research links them to the people we spend time with."},
    "04": {"kind": "quote", "quote": "He is related to his friend as to himself, for his friend is another self.",
           "note": "Pick friends you’d be glad to become.", "cite": "Aristotle · Nicomachean Ethics IX.4 · Ross"},
    "05": {"kind": "signoff", "line": "Who you let close becomes who you are.", "action": "Send this to the friend who makes you better."},
}

C31 = {  # Sat 31 Oct, F9 Journal prompt set, talk vs action
    "01": {"kind": "cover", "kicker": "Journal prompts", "claim": "Stop explaining your philosophy. Show it.",
           "sub": "Five questions for tonight."},
    "02": {"kind": "step", "n": 1, "title": "Where did my actions match what I say I believe today?",
           "body": "Epictetus: don’t talk about your principles. Act on them.", "cite": "Enchiridion 46 · Higginson", "size": 56},
    "03": {"kind": "step", "n": 2, "title": "What did I explain that I could have simply done?",
           "body": "Sheep don’t show the shepherd the grass. They make wool.", "cite": "Enchiridion 46 · Higginson", "size": 56},
    "04": {"kind": "step", "n": 3, "title": "Who saw my values today without me naming them?",
           "body": "“No longer talk at all about the kind of man that a good man ought to be, but be such.”", "cite": "Meditations 10.16 · Long", "size": 56},
    "05": {"kind": "step", "n": 4, "title": "What did I promise this week that I haven’t started?",
           "body": "“Philosophy teaches us to act, not to speak.”", "cite": "Seneca · Letters 20.2 · Gummere", "size": 56},
    "06": {"kind": "step", "n": 5, "title": "What would someone learn about me by watching, not listening?",
           "body": "Your calendar and your reactions are your real philosophy.", "size": 56},
    "07": {"kind": "signoff", "line": "Talk less about it.\nLet it show.", "action": "Answer one in the comments. Keep the rest for tonight."},
}

C01 = {  # Sun 1 Nov, F7 Protocol, emotion vs reason
    "01": {"kind": "cover", "kicker": "The protocol", "claim": "The two horses pulling your mind.",
           "sub": "Plato’s oldest picture of emotion, as a six-step practice."},
    "02": {"kind": "quote", "quote": "The human charioteer drives his in a pair; and one of them is noble and of noble breed, and the other is ignoble and of ignoble breed; and the driving of them of necessity gives a great deal of trouble to him.",
           "note": "One horse wants the good. One wants it now. You hold the reins.", "cite": "Plato · Phaedrus 246b · Jowett", "size": 54},
    "03": {"kind": "term", "tag": "The rule", "term": "Steer, don’t shoot the horse",
           "definition": "The wild horse isn’t the enemy. It’s energy. Plato’s charioteer doesn’t get rid of it; he trains it. Feelings work the same way."},
    "04": {"kind": "step", "n": 1, "title": "Notice the pull", "body": "A craving, a flash of anger, the urge to text them. Say it: “The wild horse is pulling.”"},
    "05": {"kind": "step", "n": 2, "title": "Name what it wants", "body": "Relief, revenge, comfort, attention? One word is enough."},
    "06": {"kind": "step", "n": 3, "title": "Ask the other horse", "body": "What would the version of you that you respect do in the next ten minutes?"},
    "07": {"kind": "step", "n": 4, "title": "Shorten the reins", "body": "Put distance in: stand up, leave the room, wait ten minutes before you act."},
    "08": {"kind": "step", "n": 5, "title": "Give the energy a job", "body": "A walk, a workout, a hard honest conversation instead of a sharp one."},
    "09": {"kind": "step", "n": 6, "title": "Review at night", "body": "Which horse won today? No verdict, just notes for tomorrow."},
    "10": {"kind": "signoff", "line": "You’re not the horses.\nYou’re the one holding the reins.", "action": "Save this. Tell me which step you’ll try first."},
}

NEW_CAROUSELS = {"2026-10-25": C25, "2026-10-26": C26, "2026-10-27": C27, "2026-10-28": C28,
                 "2026-10-29": C29, "2026-10-30": C30, "2026-10-31": C31, "2026-11-01": C01}
# 21-24 Oct reuse strategy/phase1-first-five/carousels.json (p1..p4), re-rendered with stills_v3.
OLD_OVERRIDES = {"p2-06": {"line": "You can’t control their mood.\nYou can be ready for it."},
                 "p4-10": {"line": "Five minutes. Every night.\nHonest, not harsh."}}
OLD_CAROUSELS = {"2026-10-21": "p1", "2026-10-22": "p2", "2026-10-23": "p3", "2026-10-24": "p4"}

# ---------------------------------------------------------------- reels re-rendered with reels_v2 (fixed)

REELS_V2 = {
    "2026-10-21": ("p5-regulating", {"style": "dawn", "seed": 5151, "segments": [
        ["Three signs you’re regulating, not suppressing.", 2.8, True],
        ["1. You can name the feeling.", 2.2, False],
        ["2. You feel it, then choose\nwhat to do.", 2.4, False],
        ["3. It passes instead of\nleaking out later.", 2.4, False],
        ["“It is not this thing that disturbs you, but your own judgement about it.”", 3.8, "quote"],
        ["Marcus Aurelius · Meditations 8.47 · Long", 1.8, "cite"],
        ["Feel it. Then decide.", 2.0, True]]}),
    "2026-10-22": ("reel-32-ask-for-help", {"style": "march", "seed": 3203, "segments": [
        ["Asking for help isn’t weak.", 2.6, True],
        ["The emperor of Rome wrote this to himself:", 2.4, False],
        ["“Be not ashamed to be helped; for it is your business to do your duty like a soldier in the assault on a town.”", 4.6, "quote"],
        ["Marcus Aurelius · Meditations 7.7 · Long", 2.0, "cite"],
        ["If you’re limping, lean on someone. Then keep climbing.", 3.2, True],
        ["Send this to someone who’s struggling in silence.", 2.8, False]]}),
    "2026-10-23": ("reel-35-do-wrong", {"style": "battle", "seed": 3536, "segments": [
        ["They got away with it. You didn’t.", 2.8, True],
        ["Socrates was asked: would you rather do wrong, or suffer it?", 2.8, False],
        ["“If I must choose between them, I would rather suffer than do.”", 3.4, "quote"],
        ["Plato · Gorgias 469c · Jowett", 1.8, "cite"],
        ["Whoever cheats you has to live with a cheat. You don’t. Stay clean.", 3.4, False],
        ["Send this to someone who got burned.", 2.6, False]]}),
    "2026-10-24": ("reel-38-love-your-people", {"style": "elegy", "seed": 3869, "segments": [
        ["You didn’t choose your family. Or your city. Or your time.", 3.4, True],
        ["Marcus Aurelius didn’t either. He wrote:", 2.4, False],
        ["“The men among whom you have received your portion, love them, but do it truly, sincerely.”", 4.2, "quote"],
        ["Marcus Aurelius · Meditations 6.39 · Long", 1.8, "cite"],
        ["Stop wishing for a different hand. Play this one with love.", 3.2, True],
        ["Send this to the people you’re stuck with.", 2.6, False]]}),
    "2026-10-25": ("reel-40-dig-within", {"style": "dawn", "seed": 4081, "segments": [
        ["You’re looking for it everywhere but here.", 2.8, True],
        ["Marcus Aurelius pointed inward:", 2.2, False],
        ["“Look within. Within is the fountain of good, and it will ever bubble up, if you will ever dig.”", 4.2, "quote"],
        ["Marcus Aurelius · Meditations 7.59 · Long", 1.8, "cite"],
        ["The person you’re looking for is a decision away.", 3.0, True],
        ["Follow for one line a day.", 2.2, False]]}),
}
# 26 Oct - 1 Nov: reels-engine renders, A versions, unchanged (they passed QC).
ENGINE_REELS = {"2026-10-26": "R001-opinion-of-others", "2026-10-27": "R003-phone-on-and-quiet",
                "2026-10-28": "R002-kafka-train", "2026-10-29": "R004-first-year-embarrassing",
                "2026-10-30": "R006-whats-under-the-anger", "2026-10-31": "R005-go-first",
                "2026-11-01": "R007-five-minutes-no-phone"}

# ---------------------------------------------------------------- captions
# (caption, first comment, alt text). Engine reels and unchanged posts take their caption from the
# Metricool queue; TAGS overrides the hashtag line (max 5).

CAPTIONS = {
    ("2026-10-21", "carousel"): None,
    ("2026-10-22", "reel"): (
        "Asking for help isn't weak.\n\nMarcus Aurelius, Meditations 7.7 (Long): \"Be not ashamed to be helped; for it is your business to do your duty like a soldier in the assault on a town.\" The emperor of Rome wrote that to himself. If you're limping, lean on someone. Then keep climbing.\n\nSend this to someone who's struggling in silence.",
        "The rest of Meditations 7.7: \"How then, if being lame you cannot mount up on the battlements alone, but with the help of another it is possible?\"\n\nWho's one person you could ask for help this week? 👇",
        "Text reel: Be not ashamed to be helped. Marcus Aurelius, Meditations 7.7, Long translation."),
    ("2026-10-23", "reel"): (
        "They got away with it. You didn't.\n\nPlato, Gorgias 469c (Jowett). Asked whether he would rather do wrong or suffer it, Socrates answers: \"If I must choose between them, I would rather suffer than do.\" Whoever cheated you has to live with a cheat. You don't. Staying clean is the win, even when it doesn't feel like one.\n\nSend this to someone who got burned.",
        "Marcus Aurelius, Meditations 9.4 (Long): \"He who does wrong does wrong against himself.\"\n\nHave you ever been glad, later, that you didn't get even? 👇",
        "Text reel: I would rather suffer than do wrong. Plato, Gorgias 469c, Jowett translation."),
    ("2026-10-24", "reel"): (
        "You didn't choose your family. Or your city. Or your time.\n\nMarcus Aurelius, Meditations 6.39 (Long): \"Adapt yourself to the things with which your lot has been cast: and the men among whom you have received your portion, love them, but do it truly, sincerely.\" He didn't choose his either. Amor fati starts with the people in your kitchen. Stop wishing for a different hand. Play this one with love.\n\nSend this to the people you're stuck with.",
        "Meditations 6.48 (Long): \"When you wish to delight yourself, think of the virtues of those who live with you.\"\n\nWho's one person you were given rather than chose, and what's one good thing about them? 👇",
        "Text reel: love the people you have received your portion among. Marcus Aurelius, Meditations 6.39, Long translation."),
    ("2026-10-25", "reel"): (
        "You're looking for it everywhere but here.\n\nMarcus Aurelius, Meditations 7.59 (Long): \"Look within. Within is the fountain of good, and it will ever bubble up, if you will ever dig.\" The person you want to become isn't in a course, a new city or someone else's approval. It's a decision, and you can make it today.\n\nFollow for one line a day.",
        "Plato, Phaedrus 279b (Jowett), Socrates' prayer: \"Give me beauty in the inward soul; and may the outward and inward man be at one.\"\n\nWhat's one good thing in you that you've been underusing? 👇",
        "Text reel: Look within, within is the fountain of good. Marcus Aurelius, Meditations 7.59, Long translation."),
    ("2026-10-25", "carousel"): (
        "5 ancient lines for when life gets heavy.\n\nSeneca, Marcus Aurelius, Epictetus and Nietzsche on what hard seasons are for. Swipe, pick the one you need, and carry it into Monday.\n\nSave this. Send it to someone who's going through it.",
        "Which one do you need this week? Just the number 👇",
        "Seven-slide carousel: five lines on hardship from Seneca, Marcus Aurelius, Epictetus and Nietzsche, public-domain translations."),
    ("2026-10-26", "carousel"): (
        "You're not lazy. You're avoiding a feeling.\n\nMost procrastination isn't a time problem. Psychologists link it to mood repair: you put the task off to escape how it makes you feel (doubt, boredom, fear of doing it badly). Marcus caught himself at it too. Meditations 2.4 (Long): \"Remember how long you have been putting off these things.\"\n\nName the feeling. Shrink the start to two minutes. Bring the feeling with you.\n\nSave this for the next thing you keep putting off.",
        "What's the feeling behind the thing you're putting off right now? One word is enough 👇",
        "Seven-slide carousel: procrastination as avoiding a feeling, Marcus Aurelius Meditations 2.4, three steps."),
    ("2026-10-27", "carousel"): (
        "How to stop rehearsing disasters that never come.\n\nYour mind runs the worst case on repeat because rehearsing feels like preparing. It isn't. It's living the bad day in advance, often more than once. Marcus Aurelius, Meditations 7.8 (Long): you will meet future things \"having with you the same reason which now you use for present things.\"\n\nAsk for the next action. If there isn't one, come back to the room.\n\nSave this for the night it starts again.",
        "What's the disaster your mind rehearses most? You don't have to explain it, one word is fine 👇",
        "Six-slide carousel: catastrophising, Marcus Aurelius Meditations 7.8, two steps to stop rehearsing."),
    ("2026-10-28", "carousel"): (
        "Do less, better: the Stoic answer to burnout.\n\nMarcus Aurelius, Meditations 4.24 (Long): \"The greatest part of what we say and do being unnecessary, if a man takes this away, he will have more leisure and less uneasiness.\" Burnout often isn't too much work. It's too much unnecessary work.\n\nOne question for every task today: is this necessary?\n\nSend this to someone running on empty.",
        "What's one thing you could drop this week that nobody would notice? 👇",
        "Five-slide carousel: Marcus Aurelius Meditations 4.24 on doing fewer things, with a today-versus-Marcus comparison."),
    ("2026-10-29", "carousel"): (
        "Why one comment ruins your whole day.\n\nNinety-nine kind ones, one sharp one, and you replay the sharp one. Psychologists call it negativity bias: the mind gives a threat more weight than praise. Epictetus, Enchiridion 20 (Higginson): \"It is your own opinion which provokes you.\" The comment took ten seconds. The story you add to it takes the day.\n\nBuy time. Don't reply today.\n\nSend this to someone rereading one right now.",
        "Which column do you live in more often, reacting or responding? Be honest 👇",
        "Five-slide carousel: reacting versus responding to criticism, Epictetus Enchiridion 20."),
    ("2026-10-30", "carousel"): (
        "Who you let close becomes who you are.\n\nThe myth: you are who you are, whoever you're around. Aristotle disagreed. Nicomachean Ethics IX.12 (Ross): friends \"take the mould of the characteristics they approve\" from each other. And IX.4: \"his friend is another self.\"\n\nPick friends you'd be glad to become.\n\nSend this to the friend who makes you better.",
        "Who's one person who made you better just by being around them? 👇",
        "Five-slide carousel: Aristotle, Nicomachean Ethics IX.4 and IX.12, on friends shaping character."),
    ("2026-10-31", "carousel"): (
        "Stop explaining your philosophy. Show it.\n\nEpictetus, Enchiridion 46 (Higginson): sheep don't throw up the grass to show the shepherd how much they've eaten; they digest it and produce wool and milk. Five questions for tonight's journal, each tied to a line from Epictetus, Marcus or Seneca.\n\nAnswer one in the comments. Keep the rest for tonight.",
        "Pick one of the five and answer it here. Short is fine 👇",
        "Seven-slide carousel: five journal prompts on acting rather than talking, Epictetus Enchiridion 46, Marcus Meditations 10.16, Seneca Letters 20.2."),
    ("2026-11-01", "carousel"): (
        "The two horses pulling your mind.\n\nPlato, Phaedrus 246b (Jowett): the soul as a charioteer with two horses, \"one of them is noble and of noble breed, and the other is ignoble.\" The wild horse isn't the enemy. It's energy. You don't get rid of it, you train it.\n\nSix steps: notice the pull, name what it wants, ask the other horse, shorten the reins, give the energy a job, review at night.\n\nSave this. Tell me which step you'll try first.",
        "Which horse wins more often in your week, and when? 👇",
        "Ten-slide carousel: Plato's charioteer from Phaedrus 246b as a six-step practice for strong emotions."),
}

TAGS = {
    ("2026-10-21", "carousel"): "#stoicism #selftrust #discipline #habits #psychology",
    ("2026-10-21", "reel"): "#stoicism #emotionalregulation #marcusaurelius #emotions #psychology",
    ("2026-10-22", "carousel"): "#stoicism #marcusaurelius #boundaries #emotionalregulation #psychology",
    ("2026-10-22", "reel"): "#stoicism #marcusaurelius #askingforhelp #mentalhealth #emotions",
    ("2026-10-23", "carousel"): "#stoicism #overthinking #rumination #seneca #psychology",
    ("2026-10-23", "reel"): "#plato #socrates #stoicism #justice #letitgo",
    ("2026-10-24", "carousel"): "#stoicism #seneca #journaling #eveningroutine #selfreflection",
    ("2026-10-24", "reel"): "#amorfati #marcusaurelius #stoicism #family #relationships",
    ("2026-10-25", "carousel"): "#stoicism #resilience #seneca #hardtimes #meaning",
    ("2026-10-25", "reel"): "#stoicism #marcusaurelius #selfworth #innerpeace #selfawareness",
    ("2026-10-26", "carousel"): "#stoicism #procrastination #marcusaurelius #emotions #psychology",
    ("2026-10-27", "carousel"): "#stoicism #anxiety #overthinking #marcusaurelius #psychology",
    ("2026-10-28", "carousel"): "#stoicism #burnout #marcusaurelius #focus #lessismore",
    ("2026-10-29", "carousel"): "#stoicism #epictetus #criticism #emotionalregulation #psychology",
    ("2026-10-30", "carousel"): "#aristotle #friendship #philosophy #character #stoicism",
    ("2026-10-31", "carousel"): "#stoicism #journaling #epictetus #journalprompts #selfreflection",
    ("2026-11-01", "carousel"): "#plato #philosophy #emotions #selfcontrol #stoicism",
}
