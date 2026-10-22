# Pillar: Freedom (civil liberties, history, decolonising the mind)

Draft, 22 Oct 2026. Nothing scheduled.

## How it sits inside the brand
"Stoicism for people who feel things" stays the positioning. This pillar adds the half of Stoicism the page hasn't used yet: **freedom**. The Stoics' central question was who is free, and the teacher who answered it best, Epictetus, was born enslaved. Inner freedom (what the page already does: feelings, habits, attention) and outer freedom (rights, history, the voices who won them) become one thread:

> The mind is the first place anyone gets colonised, and the last place they get free.

That's the series line (Moodius words). Series name **Free Minds**, filed under the existing Truths and Identity highlights. A separate "Freedom" highlight can be decided at the 19 Nov review if the pillar earns it.

**Share of the mix:** about 1 reel a week and 1 carousel every other week (roughly 15%). The Stoic and psychology core stays at 80% or more. The content-mix thread has been asked to leave room.

**Voices:** weighted to the 20th century as asked (Baldwin, Lorde, hooks, Frankl, Biko, King, Hamer, Lewis, Jordan, Malcolm X after 1964, Bukowski sparingly). Older public-domain voices (Douglass, Du Bois, Thoreau, Mill, the Stoics) carry the long quotes, because they are free to quote. See `02-roster.csv` for each person, why they fit and what to avoid.

## Guardrails
1. **Every post ends inside the viewer's own life.** History is the mirror, not the topic: each reel lands on a feeling, a habit or a question. No party politics, elections, living politicians or current-conflict takes.
2. **Ethical screen for voices.** No one tied to mass killing, executions, state repression or open hatred of a group. "Use with care" voices get one line, not a series. Living people are skipped by default (an anonymous brand shouldn't speak for them).
3. **Quotes only from `quotes.csv`.** Public-domain lines must pass `tools/verify_quotes.py`. Copyrighted lines: one short sentence, full credit (person, work, year), never edited, never in an ad. Anything longer becomes "Idea: … · Moodius words". Wikiquote and quote sites are for discovery, never the source.
4. **Label every claim** with the existing tiers: historical fact (date + source), philosophical, Moodius opinion. No invented numbers. "Hundreds of thousands", not a precise crowd figure, unless a dated source is cited.
5. **Dignity rule for images.** Portraits, crowds, places, documents, hands, books. No images of violence, injury or bodies, and no chains as decoration. Archive photos go through the engine's Slate tint like everything else, so the palette holds. No statues, marble or gold still applies, including busts of Marcus.
6. **No selling on this pillar.** CTA is send, save or comment. A real person's name or face never appears next to the journal, the shop or the guide (estates of King, Malcolm X and others enforce name and likeness rights).
7. **Own the tension.** The account is named after an emperor whose empire ran on slavery. Say so once, plainly, early in the series; it makes everything else credible.
8. **Speak with, not for.** No "we" for experiences that aren't the brand's. Let the quoted voice carry the weight; Moodius adds the question.
9. **Hashtags:** #philosophy #history #stoicism #civilrights #mentalfreedom. Don't borrow movement hashtags for reach.
10. **Comments will run hotter.** Surafel's rule set: don't argue in comments, pin a source reply, hide slurs. The draft-only reply queue (community-agent) gets a "Free Minds" tone note before it sees these.

## 10 hooks
All 12 words or fewer, each tied to a verified or flagged line in `quotes.csv`.

| # | Hook | Built on |
|---|---|---|
| H1 | The Stoic who taught freedom best was born enslaved. | Epictetus, Discourses 4.1 (Q11) |
| H2 | He was forbidden to read. So reading became the plan. | Douglass, Narrative ch. 6 (Q01, Q02) |
| H3 | Bob Marley sang it. Garvey said it first. | Garvey 1937-38 (Q14) + Epictetus (Q11) |
| H4 | Seeing yourself only through their eyes has a name. | Du Bois, Souls ch. 1 (Q06) |
| H5 | Nothing changes until someone looks straight at it. | Baldwin 1962 (Q15) |
| H6 | Your silence has never once protected you. | Lorde 1977 (Q17) |
| H7 | Looking after yourself was never the selfish part. | Lorde 1988 (Q18) |
| H8 | They took everything except how he chose to meet it. | Frankl (Q20) |
| H9 | An emperor wrote "equal freedom of speech" as a lesson he learned. | Meditations 1.14 (Q09) |
| H10 | The most dangerous colony is the one in your head. | Biko 1971 (Q21) + Ngũgĩ's idea, paraphrased |

## 5 reel concepts
Card timings follow the engine's reading-speed rule. Each reel runs 15-18 seconds (the reel-first plan wants 12-18 s, hook on frame 1 and on the cover). Visual commands use `tools/fetch_archive.py` (or the GitHub Action); every image's credit line goes at the end of the caption.

### L01 None but ourselves (Garvey → Epictetus)
- hook: "Bob Marley sang it. Garvey said it first." (2.4s)
- quote: "“…none but ourselves can free the mind.”" (2.6s)
- cite: "Marcus Garvey, The Black Man, July 1938" (1.6s)
- quote: "“He is free who lives as he wishes to live.”" (2.6s)
- cite: "Epictetus, Discourses 4.1 · tr. George Long" (1.6s)
- body: "Nobody can hand you that freedom. So nobody gets to keep it from you." (3.2s, Moodius)
- cta: "Send this to someone still asking permission." (2.2s)
- **Visual:** Garvey portrait. `--source loc --query "Marcus Garvey" --tag garvey`; if nothing passes, Slate + grain. **No Marley audio or lyrics** (copyrighted); naming him is fine.
- **Labels:** historical (Garvey speech, dated), philosophical (Epictetus), Moodius opinion. Check Garvey wording in The Black Man before render.

### L02 Faced (Baldwin, March on Washington)
- hook: "Nothing changes until someone looks straight at it." (2.5s)
- quote: "“Not everything that is faced can be changed, but nothing can be changed until it is faced.”" (4.4s)
- cite: "James Baldwin, New York Times Book Review, 14 Jan 1962" (1.8s)
- body: "A year later, hundreds of thousands faced it together in Washington." (3.0s)
- body: "Yours is smaller. The conversation you keep walking around." (2.8s)
- cta: "Save this for the day you finally have it." (2.2s)
- **Visual:** Warren K. Leffler, "Civil Rights March on Washington, D.C.", 28 Aug 1963, LoC item 2013648812, rights advisory "No known restrictions on publication" (checked). `--source loc --query "march on washington Leffler" --tag march`.
- **Labels:** historical, Baldwin quote (copyrighted, one line, credited), Moodius.

### L03 Forbidden to read (Douglass)
- hook: "He was forbidden to read. So reading became the plan." (2.6s)
- body: "His owner said learning would make him unmanageable." (2.6s)
- quote: "“What he most dreaded, that I most desired.”" (2.4s)
- quote: "“From that moment, I understood the pathway from slavery to freedom.”" (3.2s)
- cite: "Frederick Douglass, Narrative, ch. 6 (1845)" (1.6s)
- body: "Notice what someone works hard to keep you from. Start there." (3.0s, Moodius)
- cta: "Send to the friend who's teaching themselves something." (2.2s)
- **Visual:** Douglass portrait. `--source loc --query "Frederick Douglass portrait" --tag douglass` (LoC item 2011649219 is a candidate; the tool confirms its advisory). The owner's slur stays out of the reel; the paraphrase carries it.
- **Labels:** historical / autobiographical, Moodius. Public domain, verified word for word.

### L04 Not the selfish part (Lorde)
- hook: "Looking after yourself was never the selfish part." (2.4s)
- quote: "“Caring for myself is not self-indulgence, it is self-preservation, and that is an act of political warfare.”" (4.8s)
- cite: "Audre Lorde, A Burst of Light (1988)" (1.6s)
- body: "She wrote it while ill, still working." (2.2s)
- body: "Rest that lets you keep going isn't quitting." (2.4s, Moodius)
- cta: "Send to the one who never stops." (2.0s)
- **Visual:** no open-licence Lorde portrait found, so own footage: `desk` or `window-rain` from footage/README.md. The quote is kept whole (the guardrail against turning it into a spa slogan).
- **Labels:** Lorde quote (copyrighted, one line), biographical fact (she wrote A Burst of Light while living with cancer), Moodius.

### L05 Changed his mind (Malcolm X → Marcus)
- hook: "He changed his mind in public. That took real nerve." (2.5s)
- body: "In 1964 Malcolm X broke with the group that made him famous." (3.0s)
- quote: "“I'm for truth, no matter who tells it.”" (2.2s)
- cite: "Malcolm X, The Autobiography of Malcolm X (1965)" (1.6s)
- quote: "“If any man is able to convince me … I will gladly change”" (3.0s)
- cite: "Marcus Aurelius, Meditations 6.21 · tr. George Long" (1.6s)
- cta: "Save this for the next argument you're losing." (2.2s)
- **Visual:** Marion S. Trikosko, U.S. News & World Report, 1964 (LoC). `--source loc --query "Malcolm X Trikosko" --tag malcolm`. Check the Autobiography wording before render.
- **Labels:** historical, Malcolm X (copyrighted, one line, post-1964), philosophical (Marcus, verified), Moodius.

## Before any of this renders
1. Engine: accept `"translation": "original (public domain)"` for English-language public-domain sources (owned by the reels-engine thread).
2. Run the Action (or the tool on the Mac) for the four LoC searches above and drop the images into `reels-engine/footage/`.
3. Check the four "check wording" lines (Garvey, Baldwin 1953, Malcolm X, Morrison) against the books.
4. Surafel picks which concepts go forward. Then the account thread schedules them.
