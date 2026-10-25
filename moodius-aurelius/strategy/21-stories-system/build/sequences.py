"""The 15 strongest Story sequences, fully written (25 Oct 2026).

Each sequence = an evening set (21:00, hook + sticker) and a morning set (09:00, payoff + Moodius take).
Every interactive frame renders twice:
  *_hand.jpg  clear sticker zone: post from the Instagram app and add the sticker named in `sticker`
  *_auto.jpg  reply prompt printed in the zone: can be scheduled in Metricool (the API can't add stickers)
Frames marked with the template id (see templates.py).

"Moodius take" lines are drafts in the page's voice. Change anything that isn't true for you before it goes out.
"""

def F(t, kicker="", title="", body="", note="", sticker=None, reply=None, options=None, answer=None,
      footer="", left="", right="", alt=None):
    return dict(t=t, kicker=kicker, title=title, body=body, note=note, sticker=sticker, reply=reply,
                options=options, answer=answer, footer=footer, left=left, right=right, alt=alt)

S = []

S.append(dict(id="S01", concept="C01", pillar="HM", format="PS", name="The spotlight",
 why="Universal embarrassment + a quiz you can get wrong + a relieving, slightly funny payoff. Tension hook, kind payoff (rule 3).",
 evening=[
  F("T01", "Quick one", "You spilled coffee down your shirt before a meeting.", "How many people noticed?"),
  F("T08", "Guess", "In the study, what share of the room noticed the embarrassing T-shirt?",
    options=["about half", "about a quarter", "nearly everyone"],
    sticker="Quiz sticker: A about half / B about a quarter / C nearly everyone. Mark B correct.",
    reply="Reply A, B or C. Answer tomorrow at 9."),
 ],
 morning=[
  F("T08", "Answer", "B. About a quarter.", "Students wearing an embarrassing T-shirt guessed about half the room noticed. Around a quarter did.",
    note="Gilovich, Medvec & Savitsky, J. Personality and Social Psychology, 2000.",
    options=["about half", "about a quarter", "nearly everyone"], answer=1),
  F("T12", "Moodius take", "The spotlight is mostly in your head.", "Which is good news, and mildly insulting.",
    footer="Send this to the friend who still talks about the thing from 2019."),
 ]))

S.append(dict(id="S02", concept="C36", pillar="HM", format="QA", name="Up to you?",
 why="Epictetus arc week (12-15 Nov). Turns the oldest Stoic idea into a 2-second sort the viewer does on their own worry.",
 evening=[
  F("T01", "A question worth asking yourself", "One thing worrying you right now.", "Hold it in your head. Don't tell me what it is."),
  F("T02", "Sort it", "Is it up to you?", left="Up to me", right="Not up to me",
    sticker="Poll sticker: Up to me / Not up to me.", reply="Reply 'mine' or 'not mine'."),
 ],
 morning=[
  F("T03", "What a 2,000-year-old handbook says", "Epictetus splits the world in two.",
    "Up to us: our judgements and choices. Not up to us: other people, reputation, outcomes.",
    note="Moodius paraphrase of Epictetus, Enchiridion 1. Free at Standard Ebooks."),
  F("T12", "Moodius take", "Most worries are half and half.", "Do your half. Put the other half down for the night.",
    footer="Send this to someone carrying a worry that isn't theirs."),
  F("T04", "Your turn", "What's the part that IS up to you?",
    sticker="Question box: 'The part that's up to me is…'", reply="Reply with one sentence. I read every one."),
 ]))

S.append(dict(id="S03", concept="C14", pillar="GL", format="PS", name="Look at the bird",
 why="Relationships research framed for everyone. A tiny, memorable behaviour (the 'bid') with a strong number and a sendable CTA.",
 evening=[
  F("T01", "Quick one", "Your friend says “look at that bird”.", "You're halfway through a message."),
  F("T02", "Be honest", "What do you actually do?", left="Look at the bird", right="Keep typing",
    sticker="Poll sticker: Look at the bird / Keep typing.", reply="Reply 'bird' or 'typing'."),
 ],
 morning=[
  F("T03", "What psychology actually says", "It's never about the bird.",
    "John Gottman calls these moments 'bids'. Couples still together six years after his newlywed study had turned toward bids 86% of the time. Couples who divorced: 33%.",
    note="The Gottman Institute. Lab finding reported in his books, not a journal paper. Works for friendships too."),
  F("T12", "Moodius take", "Look at the bird.", "Then finish the message. It'll wait. The person might not.",
    footer="Send this to the person who always shows you birds."),
 ]))

S.append(dict(id="S04", concept="C09", pillar="HM", format="PS", name="Calm down or get excited",
 why="Practical, counter-intuitive, tested. People choose 'calm' and are surprised; the payoff is a tool they can use tomorrow.",
 evening=[
  F("T01", "Before something scary", "Heart racing. Big moment in five minutes.", "What do you tell yourself?"),
  F("T02", "Pick one", "Which works better?", left="“Calm down.”", right="“I'm excited.”",
    sticker="Poll sticker: Calm down / I'm excited.", reply="Reply 'calm' or 'excited'. Answer at 9."),
 ],
 morning=[
  F("T03", "What psychology actually says", "“I'm excited” won.",
    "People told to say “I am excited” before singing or speaking in public did better than people told to say “I am calm”.",
    note="Brooks, J. Experimental Psychology: General, 2014."),
  F("T12", "Moodius take", "You can't always calm down. You can rename it.", "Same racing heart. Different story about it.",
    footer="Send this to someone with a big day this week."),
  F("T04", "Your turn", "What's the scary thing on your calendar?",
    sticker="Question box: 'This week I'm nervous about…'", reply="Reply with one word. I'll be rooting for you."),
 ]))

S.append(dict(id="S05", concept="C46", pillar="HM", format="AA", name="Closure (argued against)",
 why="The 'argument against my own opinion' format: Moodius takes a stance, steelmans the other side and invites disagreement. Builds trust and long replies.",
 evening=[
  F("T07", "The argument against my own opinion", "You don't need closure from someone who hurt you.",
    left="My view", right="Best case against",
    body="Waiting for an apology can keep you tied to them for years.",
    note="Some conversations really do repair things. Refusing to ask can be its own kind of pride."),
  F("T02", "Your call", "Who wins?", left="My view", right="The case against",
    sticker="Poll sticker: Your view / The case against.", reply="Reply 'view' or 'against'."),
  F("T04", "Change my mind", "What would change my mind?",
    sticker="Question box: 'Change my mind…'", reply="Reply and argue with me. Politely."),
 ],
 morning=[
  F("T12", "Where I've landed (for now)", "Ask once. Then stop waiting.",
    "Asking isn't the trap. Waiting is. Thank you to everyone who argued with me.",
    footer="Tonight: one you'll disagree with even more."),
 ]))

S.append(dict(id="S06", concept="C44", pillar="GL", format="SK", name="A stranger's kindness",
 why="Positive, shareable, collects real stories (question-box answers show no names). Backed by a 2023 kindness study.",
 evening=[
  F("T06", "A stranger's act of kindness", "Someone you'll never see again did something you still remember.",
    "Tell me in one line."),
  F("T04", "One line", "What did they do?",
    sticker="Question box: 'A stranger once…'", reply="Reply with one line. I'll share a few (no names)."),
 ],
 morning=[
  F("T06", "You told me", "[Share 3 question-box answers here, by hand.]",
    "Question-box answers show no names. Never share a DM without asking first.",
    note="Hand-posted frame. In the scheduled version, use the frame below instead."),
  F("T03", "What psychology actually says", "Small kindness lands bigger than you think.",
    "People who did a small kind act for a stranger underestimated how much it meant to them.",
    note="Kumar & Epley, J. Experimental Psychology: General, 2023."),
  F("T12", "Moodius take", "Pass one on today.", "Reply 'done' tomorrow. No details needed.",
    footer="Send this to the kindest stranger-talker you know."),
 ]))

S.append(dict(id="S07", concept="C49", pillar="FK", format="FG", name="Vienna, 1847",
 why="Forgotten history with a gasp-level answer and a moral about ego, not about the past. Awe/surprise travel (Berger & Milkman).",
 evening=[
  F("T01", "Forgotten, guess it", "Vienna, 1847. A doctor asked colleagues to do one thing.", "Deaths fell. They mocked him."),
  F("T08", "Guess", "What did he ask them to do?", options=["wash their hands", "open the windows", "wear masks"],
    sticker="Quiz sticker: A wash their hands / B open the windows / C wear masks. Mark A correct.",
    reply="Reply A, B or C. Answer at 9."),
 ],
 morning=[
  F("T08", "Answer", "A. Wash their hands.",
    "Ignaz Semmelweis had doctors wash in chlorinated lime. Deaths from childbed fever fell sharply. Many colleagues rejected it anyway.",
    note="Encyclopaedia Britannica, 'Ignaz Semmelweis'. History, not medical advice.",
    options=["wash their hands", "open the windows", "wear masks"], answer=0),
  F("T04", "A question worth asking yourself", "What good idea did you resist because of who said it?",
    sticker="Question box", reply="Reply with one word. Mine: going to bed earlier."),
 ]))

S.append(dict(id="S08", concept="C22", pillar="LB", format="BC", name="The awe walk",
 why="Living Body without fitness clichés: a free, 15-minute practice with a delightful detail (the selfies shrank).",
 evening=[
  F("T01", "The Living Body", "Older adults took one 15-minute 'awe walk' a week for 8 weeks.", "Something odd happened to their photos."),
  F("T08", "Guess", "What changed?", options=["more selfies", "they got smaller in the frame", "nothing"],
    sticker="Quiz sticker: A more selfies / B they got smaller in the frame / C nothing. Mark B correct.",
    reply="Reply A, B or C. Answer at 9."),
 ],
 morning=[
  F("T08", "Answer", "B. More sky, less self.",
    "Awe walkers also reported more joy and warmer feelings toward others than people on ordinary walks.",
    note="Sturm et al., Emotion, 2022. Small study.", options=["more selfies", "they got smaller in the frame", "nothing"], answer=1),
  F("T09", "Body check", "When did something last make you feel small, in a good way?",
    sticker="Emoji slider 🏢 → 🌌: 'How much awe this week?'", reply="Reply with a number from 1 to 10."),
  F("T12", "Moodius take", "Fifteen minutes. No podcast.", "Look up more than you look down.",
    footer="Send this to someone who needs a walk."),
 ]))

S.append(dict(id="S09", concept="C30", pillar="GL", format="TP", name="The bad business idea",
 why="'Two perspectives, one dilemma': everyone has faced it, both sides are defensible, so the poll splits and replies get long.",
 evening=[
  F("T01", "Two perspectives, one dilemma", "Your friend's business idea is bad.", "They ask what you think."),
  F("T02", "Your move", "What do you say?", left="Honest, now", right="Encourage, then ask questions",
    sticker="Poll sticker: Honest now / Encourage + questions.", reply="Reply 'honest' or 'encourage'."),
 ],
 morning=[
  F("T07", "Both sides", "Honest vs encouraging.", left="Honest now", right="Encourage first",
    body="Saves them money and months.", note="They may need to find it out themselves, and keep you as a friend."),
  F("T12", "Moodius take", "Ask three good questions before one verdict.",
    "Marcus thought kindness only counts when it's genuine, not a performance. Fake encouragement is a performance. (Meditations 11.18, paraphrase)"),
  F("T04", "Your turn", "The kindest honest thing anyone ever told you?",
    sticker="Question box", reply="Reply with one line."),
 ]))

S.append(dict(id="S10", concept="C16", pillar="HM", format="MR", name="The 21-day myth",
 why="'Myth or replicated': flatters curiosity, corrects a famous number with a real one, and comforts people who are struggling with a habit.",
 evening=[
  F("T01", "Myth or replicated?", "“A new habit takes 21 days.”", "You've heard it. Is it true?"),
  F("T08", "Guess", "In the study, the typical time to automatic was…", options=["21 days", "about 66 days", "254 days"],
    sticker="Quiz sticker: A 21 days / B about 66 days / C 254 days. Mark B correct.",
    reply="Reply A, B or C. Answer at 9."),
 ],
 morning=[
  F("T08", "Answer", "B. About 66 days.", "The middle of the range. It took some people 18 days and others 254.",
    note="Lally et al., European J. Social Psychology, 2010.", options=["21 days", "about 66 days", "254 days"], answer=1),
  F("T12", "Moodius take", "If it's day 22 and still feels like work…", "…you're not broken. You're average. Keep going.",
    footer="Send this to someone on day 22."),
  F("T09", "Your turn", "What habit are you on day 'some' of?",
    sticker="Emoji slider 🐢 → 🚀: 'How automatic is it yet?'", reply="Reply with the habit, one word."),
 ]))

S.append(dict(id="S11", concept="C39", pillar="RR", format="BK", name="The book that changed you",
 why="Audience-led Reading Room: answers become next week's content (with consent), and the page learns what its readers read.",
 evening=[
  F("T05", "Books that changed how I think", "One book that changed how you think.", "Title only. No essays. (Okay, a short essay.)"),
  F("T04", "Title only", "Which book?", sticker="Question box: 'The book that changed how I think'",
    reply="Reply with the title. I'll share the list tomorrow."),
 ],
 morning=[
  F("T05", "You told me", "[Share 5 question-box answers by hand.]", "Answers from the question box show no names.",
    note="Hand-posted frame. Scheduled version: skip to the next frame."),
  F("T05", "Moodius's pick", "[HIS PICK: only a book you've read.]", "[One line on what it changed.]",
    note="Fill in before posting. Never review a book you haven't read."),
  F("T12", "Moodius take", "The best book is the one you argue with.",
    footer="Send this to the friend who lends books and never gets them back."),
 ]))

S.append(dict(id="S12", concept="C25", pillar="HM", format="UQ", name="Envy as a map",
 why="'An uncomfortable question' done gently: private reflection first, then a reframe that makes an ugly feeling useful.",
 evening=[
  F("T01", "An uncomfortable question", "Who do you envy?", "Don't answer. Just notice how fast a name came."),
  F("T04", "Anonymous", "What do they have that you want?",
    sticker="Question box: 'What does your envy want?' (answers show no names)", reply="Reply with the thing, not the person."),
 ],
 morning=[
  F("T12", "Moodius take", "Envy is rude but useful.", "It points at something you want and haven't admitted yet."),
  F("T02", "The real question", "Do you want their life, or one thing in it?", left="Their life", right="One thing in it",
    sticker="Poll sticker: Their life / One thing in it.", reply="Reply 'life' or 'one thing'."),
 ]))

S.append(dict(id="S13", concept="C06", pillar="GL", format="PS", name="The note you keep not writing",
 why="Gratitude with a twist (people underestimate the impact). Ends in an action, measured by a one-word 'sent' reply.",
 evening=[
  F("T01", "Quick one", "You write someone a thank-you note.", "How happy will they be, really?"),
  F("T08", "Guess", "Compared with your guess, they'll be…", options=["a bit happy", "as happy as you'd guess", "happier than you'd guess"],
    sticker="Quiz sticker: A a bit happy / B as you'd guess / C happier than you'd guess. Mark C correct.",
    reply="Reply A, B or C. Answer at 9."),
 ],
 morning=[
  F("T08", "Answer", "C. Happier than you'd guess.",
    "Writers of gratitude letters underestimated how surprised and happy recipients would feel, and overestimated the awkwardness.",
    note="Kumar & Epley, Psychological Science, 2018.", options=["a bit happy", "as happy as you'd guess", "happier than you'd guess"], answer=2),
  F("T04", "Your turn", "Who has done more for you than you've told them?",
    sticker="Question box: first name only, or just 'got one'", reply="Reply with a first name. That's your note."),
  F("T12", "Moodius take", "Three lines is enough.", "What they did. What it changed. Thank you.",
    footer="Reply 'sent' when you've sent it."),
 ]))

S.append(dict(id="S14", concept="C50", pillar="FK", format="FG", name="Nightingale's chart",
 why="Overturns a cliché (the lamp) with a nerdy, empowering fact. Shareable to 'the friend who loves a chart'.",
 evening=[
  F("T01", "Forgotten, guess it", "Florence Nightingale's most powerful tool wasn't a lamp.", "What was it?"),
  F("T08", "Guess", "Her secret weapon:", options=["a chart", "a letter to the Queen", "a scalpel"],
    sticker="Quiz sticker: A a chart / B a letter to the Queen / C a scalpel. Mark A correct.",
    reply="Reply A, B or C. Answer at 9."),
 ],
 morning=[
  F("T08", "Answer", "A. A chart.",
    "Her diagrams showed more soldiers in the Crimean War died of preventable disease than of wounds, and helped push hospital reform.",
    note="Encyclopaedia Britannica, 'Florence Nightingale'.", options=["a chart", "a letter to the Queen", "a scalpel"], answer=0),
  F("T12", "Moodius take", "A nurse out-argued generals with a graph.", "Kindness sometimes looks like homework.",
    footer="Send this to someone who loves a good chart."),
 ]))

S.append(dict(id="S15", concept="C21", pillar="LB", format="BC", name="120 minutes",
 why="A slider people answer honestly, a concrete number to aim for, and a soft, non-preachy nudge outside. Weekend slot.",
 evening=[
  F("T01", "Body check", "Minutes outside this week.", "Real outside. The car park doesn't count."),
  F("T09", "Honest guess", "How many?", sticker="Emoji slider 🏢 → 🌳: 'Minutes in nature this week'",
    reply="Reply with your guess in minutes."),
 ],
 morning=[
  F("T03", "What psychology actually says", "The number in one big survey: 120.",
    "Among about 20,000 people in England, those who spent at least 120 minutes a week in nature were more likely to report good health and wellbeing.",
    note="White et al., Scientific Reports, 2019. Linked, not proven to cause it."),
  F("T12", "Moodius take", "That's 17 minutes a day.", "A park bench counts. So does a tree you walk past slowly.",
    footer="Send this to the friend who'd come with you."),
 ]))

assert len(S) == 15
