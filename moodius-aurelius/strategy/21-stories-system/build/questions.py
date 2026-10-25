"""100 conversation questions (25 Oct 2026). 20 per pillar.

depth: light (one tap / one word), medium (one line), deep (a real answer; use sparingly, max 2 a week)
sticker: poll | slider | box (question box) | quiz | addyours
Every question is answerable in under 30 seconds. None asks for names, faces, locations or anything that identifies a third party.
Moodius answers deep questions first in a follow-up frame (self-disclosure invites self-disclosure: Aron et al., 1997).
"""

Q = {
 "HM": [  # The Human Mind
  ("What's a feeling you've never had a good word for?", "box", "medium"),
  ("Which do you replay more: what you said, or what you didn't say?", "poll", "light"),
  ("What's something you believed at 18 that you'd argue against now?", "box", "deep"),
  ("When you're stressed, do you go quiet or get busy?", "poll", "light"),
  ("What's the most useful thing you've ever been told about your own mind?", "box", "deep"),
  ("How loud is your inner critic today?", "slider", "light"),
  ("If your inner critic were a houseguest, what would it complain about first?", "box", "medium"),
  ("What do you do in the first ten minutes after something goes wrong?", "box", "medium"),
  ("Do you decide faster when you're tired or when you're rested?", "poll", "light"),
  ("What's a worry you've had for years that never came true?", "box", "deep"),
  ("Which is harder: asking for help or accepting it?", "poll", "light"),
  ("What would you stop doing if nobody would notice?", "box", "medium"),
  ("How much of today were you actually present for?", "slider", "light"),
  ("What's a compliment you've never managed to believe?", "box", "deep"),
  ("Are you more patient with strangers or with people you love?", "poll", "light"),
  ("What does 'calm' feel like in your body?", "box", "medium"),
  ("Name a mistake you're glad you made.", "box", "deep"),
  ("When did you last change your mind about a person?", "box", "medium"),
  ("Overthinker or underthinker?", "poll", "light"),
  ("What's one thing you'd tell yourself last Monday?", "box", "medium"),
 ],
 "FK": [  # Forgotten Knowledge
  ("Which century would you visit for one day, just to listen?", "box", "light"),
  ("Guess: the Ebers Papyrus, one of the oldest medical books known. 500 or 3,500 years old?", "quiz", "light"),
  ("Whose idea do you think history forgot to credit?", "box", "medium"),
  ("Would you rather read a lost library or meet its librarian?", "poll", "light"),
  ("What's a family remedy you grew up with? (History, not advice.)", "box", "medium"),
  ("Which old invention do you secretly think was better than its replacement?", "box", "light"),
  ("Do you trust an old idea more or less because it's old?", "poll", "medium"),
  ("What's something your grandparents knew that nobody taught you?", "box", "deep"),
  ("Handwritten letters: lost art or overrated?", "poll", "light"),
  ("Which historical figure would be terrible at Instagram?", "box", "light"),
  ("Would you have believed the doctor who said 'wash your hands' in 1847?", "poll", "medium"),
  ("What's a piece of history you only learned as an adult?", "box", "medium"),
  ("Map or diary: which tells you more about the past?", "poll", "light"),
  ("If you could save one book from a fire, which?", "box", "medium"),
  ("Which language would you learn just to read one old book?", "box", "light"),
  ("Do you think people in 2526 will laugh at our medicine or our manners?", "poll", "light"),
  ("Name a place you'd like to know the full history of.", "box", "light"),
  ("Which is more impressive: building a pyramid or keeping a library alive for 500 years?", "poll", "medium"),
  ("What would you want a historian to say about ordinary people in 2026?", "box", "deep"),
  ("Whose knowledge gets ignored because of who they are?", "box", "deep"),
 ],
 "RR": [  # The Reading Room
  ("One book that changed how you think. Title only.", "box", "medium"),
  ("Paper, screen or audio?", "poll", "light"),
  ("Which book did you abandon and feel guilty about?", "box", "light"),
  ("A sentence you've reread more than five times?", "box", "deep"),
  ("Do you underline in books, or is that a crime?", "poll", "light"),
  ("Which book would you give a friend having a hard year?", "box", "medium"),
  ("Fiction or non-fiction: which taught you more about people?", "poll", "medium"),
  ("What are you reading right now? (Cereal box counts.)", "box", "light"),
  ("Which book did school ruin for you?", "box", "light"),
  ("How many pages a day, honestly?", "slider", "light"),
  ("A book you disagreed with but couldn't stop thinking about?", "box", "deep"),
  ("Do you finish every book you start?", "poll", "light"),
  ("Which character would make a good friend? Which a terrible one?", "box", "medium"),
  ("Short books or long books?", "poll", "light"),
  ("What's a book you'd reread at 80?", "box", "deep"),
  ("Where do you read best?", "box", "light"),
  ("Old classic or new release for your next read?", "poll", "light"),
  ("Which idea from a book do you actually use every week?", "box", "deep"),
  ("Have you ever read a book because someone you liked loved it?", "poll", "medium"),
  ("Recommend one book in three words.", "box", "medium"),
 ],
 "LB": [  # The Living Body
  ("How rested are you, honestly?", "slider", "light"),
  ("Where does stress show up first in your body?", "box", "medium"),
  ("Morning walk or evening walk?", "poll", "light"),
  ("Minutes outside today?", "slider", "light"),
  ("What helps you fall asleep that nobody would guess?", "box", "medium"),
  ("When did you last move just because it felt good?", "box", "medium"),
  ("Gym, walk, dance in the kitchen, or none of your business?", "poll", "light"),
  ("How many glasses of water so far? Be honest.", "slider", "light"),
  ("What does your body need more of this week?", "box", "medium"),
  ("Phone in the bedroom: yes or no?", "poll", "light"),
  ("Breathe in for four, out for six. Did you just do it?", "poll", "light"),
  ("What's your favourite boring meal?", "box", "light"),
  ("Do you rest before you're tired or after you collapse?", "poll", "medium"),
  ("What's one thing you do for your body that's actually for your mind?", "box", "deep"),
  ("Stairs or lift?", "poll", "light"),
  ("When did you last feel awe outdoors?", "box", "medium"),
  ("How tense are your shoulders right now? (Now drop them.)", "slider", "light"),
  ("Cold shower: discipline or punishment?", "poll", "light"),
  ("What would you do with a free hour that's only for your body?", "box", "medium"),
  ("What's a sign you're running on empty?", "box", "deep"),
 ],
 "GL": [  # The Good Life
  ("Who would you call at 3am?", "poll", "deep"),
  ("A stranger's kindness you still remember?", "box", "medium"),
  ("Who has done more for you than you've told them?", "box", "deep"),
  ("Small thing that made today better?", "addyours", "light"),
  ("Lend money to a friend, or give it?", "poll", "medium"),
  ("Who taught you to be kind, without saying a word?", "box", "deep"),
  ("Being nice and being kind: same thing?", "poll", "medium"),
  ("What's a tiny tradition you'd keep forever?", "box", "medium"),
  ("Would you rather be admired or trusted?", "poll", "medium"),
  ("What's the best advice you ignored and later took?", "box", "deep"),
  ("Do you talk to strangers in queues?", "poll", "light"),
  ("When did you last compliment someone out loud?", "slider", "light"),
  ("Busy or full: which describes your week?", "poll", "light"),
  ("Who in your life makes ordinary things funny?", "box", "medium"),
  ("What does a good Sunday look like?", "box", "light"),
  ("What would you do differently if you knew nobody was judging?", "box", "deep"),
  ("What's a kindness that cost you nothing but mattered a lot?", "box", "medium"),
  ("Friends who challenge you or friends who comfort you?", "poll", "medium"),
  ("What's enough, for you?", "box", "deep"),
  ("Send this to the friend who… (finish the sentence)", "box", "light"),
 ],
}

def rows():
    from concepts import PILLARS
    n = 0
    for p, items in Q.items():
        for q, sticker, depth in items:
            n += 1
            yield dict(id=f"Q{n:03d}", pillar=p, pillar_name=PILLARS[p], question=q, sticker=sticker, depth=depth,
                       reply_fallback={"poll": "Reply with your pick.", "slider": "Reply with a number 1-10.",
                                       "box": "Reply with one line.", "quiz": "Reply with your guess.",
                                       "addyours": "Reply with yours."}[sticker])

if __name__ == "__main__":
    r = list(rows()); assert len(r) == 100, len(r); print(len(r))
