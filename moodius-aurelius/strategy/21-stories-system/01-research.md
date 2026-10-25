# What works in Stories: research (25 Oct 2026)

Builds on, and doesn't repeat: strategy/20-story-replies/01-research-sweep.md (Mosseri on sends, the 2023 stories ranking explainer, Meta's engagement-bait rules, Berger & Milkman, Upworthy tests), hook-intel/ and strategy/16-lessons-2026-10-22.md.

Every line below is marked:
- ✅ **Verified**: from Meta's own documentation, a platform statement, or a peer-reviewed study I could cite.
- 🟡 **Third-party estimate**: a vendor or analytics site, method unknown.
- ⚪ **Assumption**: my judgement, to be tested by the A/B plan (10-ab-tests.md).

## 1. Our own data (audit)

| What | Result |
|---|---|
| Metricool story analytics (brand 7224060, 1-25 Oct, fields IGST02-IGST13) | ✅ **Empty: no rows.** Same as the reach batch found. Stories can't be judged from Metricool yet. |
| Instagram API, story `replies` | ✅ Meta's docs: "Returns 0 for stories created by users in Europe or Japan." The account is run from Europe, so **story replies will always read 0 in any API-based tool.** Replies have to be counted in the app or in DMs. |
| Instagram API, other story metrics | ✅ Available: reach, views, navigation (taps forward, taps back, exits, swipe forward), shares, follows, profile visits, profile activity. Only for 24 hours unless a webhook captures them; values under 5 return an error. |
| Feed data we do have (reach batch) | ✅ Carousels drove the jump to 2,141 / 5,734 / 2,398 reach (21-23 Oct); 59 followers. Tension openers about another person beat routines. Sends track reach. |
| Story performance so far | ⚪ Unknown. The 22 quiz stories scheduled 26 Oct-7 Nov are the first real test; the tracker (09-tracker.xlsx) starts logging them. |

**So what:** the scoreboard for stories is the Instagram app plus your DMs, not Metricool. The tracker is built around that.

## 2. How Instagram treats Stories

| Finding | Status | Source | What we do |
|---|---|---|---|
| Stories rank on how likely a viewer is to tap your story, like it, or reply by message. Public profile views count a little. | ✅ | Mosseri, reported by [Social Media Today, 28 Jan 2025](https://www.socialmediatoday.com/news/instagram-stories-ranking-factors-2025/738541/) | Every night asks for a reply. Replies are the main score in the tracker. |
| "For the vast majority of creators, posting to Feed is going to be the best way to reach as many people as possible." "Think of [Stories] as a way to reach your most passionate audience." | ✅ | Mosseri, same source | Stories are for **depth with followers**, not reach. Growth still comes from carousels; stories turn viewers into regulars and repliers. The follower-conversion score is a bonus, not the goal. |
| Stories ranked by viewing history, engagement history (likes, DMs) and closeness | ✅ | Instagram explainer, May 2023 (see sweep) | A reply tonight moves us up that person's story bar tomorrow. Daily rhythm matters. |
| Story metrics include follows, profile visits, shares, navigation (exits, taps) | ✅ | [Meta, Instagram Media Insights](https://developers.facebook.com/docs/instagram-platform/reference/instagram-media/insights/) | Tracker columns match these exactly. |
| Scheduling tools can publish stories via the API (`media_type=STORIES`), max 100 API posts per 24 h | ✅ | [Meta, Content Publishing](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/content-publishing) | Reply-prompt versions keep going through Metricool. |
| No sticker (poll, quiz, slider, question, link, Add Yours) can be added through the API | ✅ | Agorapulse API limits page (sweep); Meta's publishing guide lists none | **Real stickers are by hand only.** Every interactive frame is rendered twice: `_hand` (space for the sticker) and `_auto` (reply prompt printed). |
| "Add Yours" sticker: "custom prompts and public responses… see who responds to it in their own Stories" | ✅ | Instagram via [TechCrunch, Nov 2021](https://techcrunch.com/2021/11/01/instagram-rolls-out-an-add-yours-sticker-in-stories-to-create-threads-users-can-respond-to/amp) | Used twice a month (low-effort, public). Moodius joins with a photo of a page or an object, never a face. |
| Story engagement averages ~0.48%; smaller accounts often double it; no sticker tap rates published | 🟡 | Storrito 2026 benchmarks (sweep) | Treat any "polls get X% more" claim as unproven. |

## 3. Why the formats work: behavioural science

| Mechanism | Evidence | Status | Used in |
|---|---|---|---|
| **Guess first, learn better.** Trying to answer before seeing the answer, even wrongly, improves memory for the answer. | Kornell, Hays & Bjork, J. Exp. Psychology: Learning, Memory & Cognition 35(4), 2009 ([PubMed](https://pubmed.ncbi.nlm.nih.gov/19586265/)) | ✅ | Every quiz → answer pair. The page teaches something people keep. |
| **Curiosity gap.** Curiosity rises when people notice a gap in what they know. | Loewenstein, Psychological Bulletin 116(1), 1994 | ✅ | 21:00 hook withholds, 09:00 pays off. |
| **Asking questions makes you likeable**, especially follow-up questions. | Huang, Yeomans, Brooks, Minson & Gino, J. Personality and Social Psychology 113(3), 2017 ([APS summary](https://psychologicalscience.org/news/minds-business/asking-questions-increases-likability.html)) | ✅ | Response bank: every reply to a follower ends with a follow-up question, not a full stop. |
| **Talking about yourself is rewarding.** | Tamir & Mitchell, PNAS 109(21), 2012 | ✅ | Monday "about you" nights. |
| **Closeness grows through gradual, mutual self-disclosure.** | Aron et al., Personality and Social Psychology Bulletin 23(4), 1997 (the "36 questions"; [Greater Good practice](https://ggia.berkeley.edu/practice/36_questions_for_increasing_closeness)) | ✅ | Question depth goes light → medium → deep across the week; Moodius answers deep questions first. |
| **Positive and awe content is shared more; sadness less. Tension still wins the first click.** | Berger & Milkman 2012; Robertson et al. 2023 (sweep) | ✅ | Tense hook, kind or surprising payoff. Max 1 heavy topic a week. |
| **Bait is punished.** "Tag 3 friends", "comment YES". | Meta, 2017 (sweep) | ✅ | Sends always name a kind of person ("send this to the friend who…"). |

## 4. Accounts in the brief's six areas

**Plain answer: nobody publishes story metrics.** Stories vanish after 24 hours and their numbers are private to the account owner, so there is no verified data on any competitor's story views, poll votes or reply rates. Anything claiming otherwise is a guess. I also can't open Instagram from here (it's blocked for this workspace), so I haven't watched their stories either.

What can be verified:

| Account / area | What's verifiable | Status |
|---|---|---|
| @dailyphilosopher (Stoicism) | ~1.34M followers, ~13 posts a week, short text cards and reels, Stoic quotes (CreatorDB, 6 Oct 2026). Engagement rate figure on the same page contradicts itself. | 🟡 |
| The School of Life (emotional intelligence) | 222K followers on TikTok per CreatorDB; Instagram not listed there | 🟡 |
| Daily Stoic / Ryan Holiday | Newsletter-first business; Instagram is distribution (public interviews) | 🟡 |
| Greater Good Science Center (kindness, wellbeing) | Publishes free, evidence-based practices (36 questions, gratitude letter) we can cite and adapt | ✅ |

**15-minute homework, optional (by hand, on your phone):** watch tonight's stories from 5 accounts you admire in these areas and note only three things per account: (1) first frame: question, claim or picture? (2) which sticker, if any, (3) did they answer their own question? Paste notes into `research-notes.md` and I'll fold them in. Don't follow anyone from the Moodius account just to research; use your eyes, not the follow button.

## 5. Masculinity, relationships and emotional intelligence

Researched as asked, framed for everyone (brand rule: no men-only or red-pill framing). What made it into the content:

- **Bids for connection** (Gottman): 86% vs 33% turning toward, six-year follow-up ([Gottman Institute](https://www.gottman.com/blog/turn-toward-instead-of-away/)). Lab finding reported by the institute, flagged as such on the card.
- **The liking gap** (Boothby et al., Psychological Science 2018): people underestimate how much new acquaintances like them.
- **Emotional granularity** (Kashdan, Barrett & McKnight, 2015) and **affect labelling** (Lieberman et al., 2007): naming feelings precisely helps.
- **Anxiety reappraisal** (Brooks, 2014) and **self-distancing** (Kross et al., 2014).
- **Social relationships and survival** (Holt-Lunstad et al., PLoS Medicine 2010, 148 studies).

These apply to anyone; the cards never say "men".

## 6. What we still need from Instagram Insights

To judge stories properly we need, per story, from the app (Archive → story → swipe up → Insights): reach, taps forward, taps back, exits, next story, replies, sticker taps, shares, profile visits, follows. Weekly: followers on Sunday, accounts reached, and the "Top content → Stories" view. The tracker has a column for each. Optional (yes/no in README): a free GitHub Actions job could save these automatically every few hours before stories expire, except replies, which Meta zeroes for Europe.

## Sources (web, read 25 Oct 2026)

- [Meta: Instagram Media Insights](https://developers.facebook.com/docs/instagram-platform/reference/instagram-media/insights/) · [Meta: Content Publishing](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/content-publishing)
- [Social Media Today: Instagram stories ranking factors, Jan 2025](https://www.socialmediatoday.com/news/instagram-stories-ranking-factors-2025/738541/)
- [TechCrunch: Add Yours sticker, Nov 2021](https://techcrunch.com/2021/11/01/instagram-rolls-out-an-add-yours-sticker-in-stories-to-create-threads-users-can-respond-to/amp)
- [Kornell, Hays & Bjork 2009 (PubMed)](https://pubmed.ncbi.nlm.nih.gov/19586265/) · [APS: Asking questions increases likability](https://psychologicalscience.org/news/minds-business/asking-questions-increases-likability.html) · [Greater Good: 36 questions](https://ggia.berkeley.edu/practice/36_questions_for_increasing_closeness)
- [Gottman Institute: Turn toward instead of away](https://www.gottman.com/blog/turn-toward-instead-of-away/) · [CreatorDB: dailyphilosopher](https://creatordb.app/creatorstats/dailyphilosopher/) · [CreatorDB: theschooloflife](https://creatordb.app/creatorstats/theschooloflife/)
- Study citations on each card are given in full in 02-concepts.md.
