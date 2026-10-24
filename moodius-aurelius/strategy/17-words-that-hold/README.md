# 17. Words that hold: what makes people keep watching, like and follow (24 Oct 2026)

What this answers: which words and sentence shapes in @moodiusaurelius posts go with people staying past 3 seconds, watching longer, liking and following; which words other creators' outlier videos use; why each one works according to published psychology and neuroscience; and how to rewrite the next week of hooks.

Sources used:
- **Own posts.** Metricool brand 7224060, pulled 24 Oct 2026: 15 reels and 8 feed posts published 6-23 Oct. Table: `own-posts-2026-10-24.csv`. Script: `tools/own_word_patterns.py`.
- **Other creators.** The hook-intel database from 22 Oct (`hook-intel/data/hookintel.db`, PR #5): 168 on-topic short videos from Stoic, psychology and Jung channels that have a views-vs-creator-median "outlier ratio". Script: `tools/creator_keyword_lift.py`, output `creator-keyword-lift-2026-10-24.txt`.
- **Research.** 21 peer-reviewed papers, listed at the end with DOI links. Each mechanism below names the paper it comes from. Where a link from the paper to Instagram behaviour is my inference, it says so.

## How much to trust this

- 15 reels and about 14 followers. Every "own data" number is a median of 2-10 posts. Treat them as leads to test, not findings.
- Metricool counts far fewer views than Instagram shows, so use the numbers as relative (post vs post), not absolute.
- The three newest reels (21-23 Oct, Slate/Bone look, about 22-30% 3-second rate) all held fewer people than the older stone-look reels (25-47%). Some of that drop may be the new look or the first frame, not the words. The X5 hook test from 2 Nov is what can separate the two.
- Creator data are mostly YouTube Shorts titles, not Instagram reels, and "outlier ratio" is views divided by that creator's own median. A word group used by 2 creators can be one channel's style. The table lists how many creators each group spans.
- No study here measured Instagram reels. The papers explain mechanisms (why a word grabs attention or feels rewarding); they don't promise a number on this account.

## The short version

1. **Open on another person or a scene the viewer is in, in the second person.** "Someone disrespected you today?", "You can't make everyone like you", "Not every insult deserves a reply". Own reels with a person or conflict in the hook: median 43% past 3s vs 29% for the rest. Mechanism: self-reference and social threat.
2. **Ask a question, then make the viewer wait for the second half of the answer.** The one reel that did this ("Someone disrespected you today?" then "if it's true... if it's false...") was watched 16.5s on average; every other reel sat at 2.5-5.7s. A question mark on its own did nothing for other creators (0.89x). The wait is what works. Mechanism: the curiosity gap and reward anticipation.
3. **Set up the obvious reading, then overturn it.** "It's not what happened that hurts. It's the story you tell about it." (43%), "You don't have a discipline problem. You have a self-trust problem." (the only post that brought follows: 5). Creators' "secret / truth / real / actually" titles: 1.97x across 9 creators. Mechanism: prediction error.
4. **Put two things the viewer thought were one side by side.** "X vs Y", "hurts more than". Highest lift in the creator set (5.8x, 4 creators, small n). Mechanism: prediction error plus a ruling on a fight the viewer has with themself.
5. **Use plain pain words, then pay off with relief or awe.** Hurt, lonely, ignored, replay, 2am. Creators' pain-word titles: 1.81x across 17 creators, and the three biggest outliers in the set are all about loneliness (75x, 28x, 23x, three different channels). But sadness gets watched more than it gets shared, so the last beat needs relief or awe if you want sends.
6. **Stop opening with a list, a thinker's name, or a self-help noun.** Number or list openers: 27% vs 35%. Thinker name first: 25% vs 33%. Motivation / busy / rules / things: 29% vs 37%, and the two worst reels on the account (reach 20 and 23). Keep Marcus, Seneca and Epictetus on line 2, where they prove the point instead of opening it.

## 1. What your own posts say

Reels only (carousels have no hold data). "With" is the median of reels whose on-screen hook contains the pattern, "without" is the median of the rest.

| Word pattern in the hook | Reels | Past 3s, with vs without | Avg watch (s), with vs without | Reach, with vs without |
|---|---|---|---|---|
| Another person or a conflict (someone, insult, argument, everyone, angry) | 5 | **43.1% vs 29.4%** | 5.0 vs 4.2 | 117 vs 124 |
| A question mark | 2 | 41.2% vs 29.7% | **10.4 vs 4.3** | 113 vs 122 |
| Second person (you, your) | 7 | 34.7% vs 29.8% | 4.4 vs 4.2 | 141 vs 115 |
| Two-beat turn (short line, full stop, short line) | 5 | 31.8% vs 29.4% | 4.3 vs 4.3 | 114 vs 122 |
| Negation (not, isn't, can't, didn't) | 10 | 30.8% vs 30.3% | 4.3 vs 4.3 | 124 vs 117 |
| Abstract self-help noun (motivation, busy, rules, signs, things) | 6 | 29.4% vs 37.0% | 4.3 vs 4.3 | 118 vs 121 |
| Number or list | 4 | 27.2% vs 34.7% | 4.2 vs 4.4 | 156 vs 117 |
| Thinker's name first | 3 | 25.2% vs 33.2% | 4.3 vs 4.3 | 122 vs 119 |

Likes, saves, shares and follows:
- **Most likes:** "You can't make everyone like you." (11). People like what they'd say about themselves.
- **Most shares and saves:** "Some things are up to you. Most aren't." (4 shares, 2 saves): a short rule the viewer can hand to someone else.
- **Only follows:** the self-trust carousel (5 follows from 342 reach). It's the clearest "you think it's X, it's Y" reframe on the account, followed by a 7-day plan. That promises more to come, which is what a follow is.
- **Exception to rule 1:** "They got away with it. You didn't." is an other-person hook but held only 23.7%. On frame 0 "You didn't" reads two ways (you didn't get away with it? you didn't cheat?). An ambiguous first line makes the brain work before it gets curious. Keep the first line readable in one pass.
- Negation alone does nothing. "Not every insult..." works because of the insult, not the "not".

## 2. What other creators' outlier hooks say

168 on-topic hooks (median outlier ratio 1.08x). "Lift" is the median outlier ratio of hooks containing the words. Only groups with 3+ hooks shown. Full list: `creator-keyword-lift-2026-10-24.txt`.

| Words in the hook | Hooks | Creators | Median outlier, with vs without | Real examples from the set (outlier) |
|---|---|---|---|---|
| vs, more than | 4 | 4 | **5.79x vs 1.06x** | "Being Ignored Hurts MORE Than Being Hated" (6.2x), "Depression vs Responsibility" (5.3x) |
| psychological, brain, therapist | 6 | 6 | 2.33x vs 1.08x | "The psychological cost of being available" (9.5x), "The Job of a Therapist" (4.5x) |
| secret, truth, real, actually | 12 | 9 | 1.97x vs 1.00x | "The Secret to Never Getting Upset" (5.8x), "The Real Cure for the Loneliness Epidemic" (28.1x) |
| why you (keep) | 7 | 2 | 1.82x vs 1.07x | "Why You Keep Giving Your Heart to the Wrong People" (3.2x) |
| hurt, pain, lonely, ignored, broken | 26 | 17 | 1.81x vs 1.03x | "The Deepest Pain of a Broken Heart" (9.8x), "How Modern Life Created a Loneliness Epidemic" (74.5x) |
| stop, never, don't | 14 | 10 | 1.70x vs 1.02x | "Stop doing these five things according to the Stoics" (15.8x), "Stop Taking It Personally" (4.0x) |
| silence, quiet | 6 | 4 | 1.60x vs 1.07x | "Why The Quietest Person In The Room Always Wins" (1.5x) |
| cost, still | 4 | 3 | 1.48x vs 1.07x | "You Have Free Time. Why Does It Still Feel Like Work?" (7.3x) |
| thinker's name | 46 | 9 | 1.29x vs 1.03x | "What Marcus Aurelius Teaches About Waking Up Early" (7.2x) |
| why | 35 | 15 | 1.19x vs 1.07x | |
| you, your | 54 | 18 | 1.00x vs 1.13x | |
| number or list | 21 | 7 | 1.00x vs 1.08x | |
| question mark | 12 | 8 | 0.89x vs 1.08x | |

Two things line up across both data sets. "You" on its own does nothing, and neither does a question mark or a list. What lifts is **what the "you" is put into**: a cost, a contrast, a pain, a correction or a hidden reason.

**Left out on purpose** (high outliers, off-brand or manipulative): "What Happens To Manipulators The Day You Go Cold", "The 4-Second Silence Trick That Exposes Anyone", "Machiavelli's Law Of Armed Boundaries", "Loneliness KILLS More Than Smoking!" (a contested statistic in capitals). The mechanism behind them (threat, power over others) gets attention, but it turns the viewer against other people, which is the opposite of the positioning.

## 3. Ranked patterns, with the mechanism behind each

Ranked by strength of evidence on this account first, other creators second.

### 1. The other-person scene, in the second person
**Words:** someone, they, people, everyone, your [mother / boss / friend], today, again.
**Evidence:** own 43% vs 29% past 3s (5 reels); creators "people / someone" 1.14x (weak alone).
**Mechanism.** Information framed as being about the self is processed more deeply and remembered better than the same information about others (the self-reference effect: Rogers, Kuiper & Kirker 1977; meta-analysis of 129 studies, Symons & Johnson 1997). It runs through the cortical midline structures (Northoff et al. 2006). A threat from another person adds a negativity weight: bad events get more attention and processing than good ones of the same size (Baumeister et al. 2001). In a field test, question headlines that referred to the reader ("Is *your* boss...") got more clicks than statements; in one of the two studies they also beat questions that didn't refer to the reader (Lai & Farbrot 2014).
**Rule.** Frame 0 names a person and something they did to "you", in under 10 words. "Someone" beats "people"; a scene ("left you on read") beats a category ("toxic people").

### 2. The question with a delayed second half
**Words:** a question in line 1, then "if... / if...", "two answers", "only one of them".
**Evidence:** own 16.5s average watch vs 2.5-5.7s for every other reel (n=1); question mark alone 0.89x for creators.
**Mechanism.** Curiosity rises when people notice a gap between what they know and what they want to know, and it's strongest when the gap feels small enough to close soon (Loewenstein 1994). Curiosity about an answer activates reward areas (the caudate) and improves memory for the answer (Kang et al. 2009). High-curiosity states also improve memory for things shown while waiting, through the midbrain dopamine circuit and the hippocampus (Gruber, Gelman & Ranganath 2014). The anticipation phase is itself rewarding: the nucleus accumbens responds to the expectation of a reward, before the reward arrives (Knutson et al. 2001). The second branch is what holds people; the question just opens the gap.
**Rule.** Use a question only when the answer has two parts and the second part comes after second 6. Pay off both, every time. A gap that doesn't close teaches people to swipe next time (this last point is our rule, not a finding).

### 3. The overturned expectation ("It's not X. It's Y.")
**Words:** isn't, actually, really, the real, the truth about, you don't have a ___ problem.
**Evidence:** own "It's the story you tell" 43%; self-trust carousel the only follows (5); creators "secret / truth / real / actually" 1.97x, 9 creators.
**Mechanism.** Dopamine neurons fire most to outcomes that differ from what was predicted: the reward prediction error (Schultz, Dayan & Montague 1997). Attention follows the same logic. Gaze goes to what is surprising in the Bayesian sense, the input that most changes what the viewer expected (Itti & Baldi 2009). Line 1 sets the prediction ("you're lazy"); line 2 breaks it ("you're avoiding a feeling").
**Follow link (inference).** A follow is a bet that future posts will keep paying. A reframe that changes how someone sees their own week is the clearest sign this account will keep doing that. On this account it's the only post shape that has brought follows so far.
**Rule.** Line 1 says what the viewer already believes, in their words. Line 2 replaces it within 3 seconds.

### 4. X vs Y: two things that felt like one
**Words:** vs, or, more than, hurts more than, only one of them, the difference between.
**Evidence:** creators 5.79x (4 hooks, 4 creators, small n); own "regulating, not suppressing" 29.7% (opened as a list, so the test isn't clean).
**Mechanism.** The same prediction error as pattern 3, plus a promise to settle a question the viewer is already asking themself ("is this rest or avoidance?"). The answer updates a belief about the self, which is the self-reference effect again.
**Rule.** Both words must be things the viewer has felt (grief vs self-pity, rest vs avoidance, alone vs lonely), never two kinds of people.

### 5. Plain pain words, with a relief or awe payoff
**Words:** hurt, lonely, ignored, replay, 2am, left out, the story you tell.
**Evidence:** creators 1.81x across 17 creators; the 3 biggest outliers are all about loneliness; own "hurts" reel 43%.
**Mechanism.** In 105,000 headline variants tested on 370 million impressions at Upworthy, each extra negative word raised click-through by about 2.3%, and sadness words had the clearest effect of the four emotions tested (Robertson et al. 2023). But in a study of which New York Times articles got emailed, sadness made sharing *less* likely, while high-arousal emotions such as awe, anger and anxiety made it more likely (Berger & Milkman 2012). So pain words earn the watch; the share needs a lift at the end. Naming a feeling also helps the viewer: putting feelings into words reduced amygdala response in an fMRI study (Lieberman et al. 2007), which fits the positioning.
**Rule.** Name the hurt in line 1, but end on relief, awe or a small action. Your reels get almost no sends (0 on the three newest), and this is the most likely fix.

### 6. The correction ("Stop ___")
**Words:** stop, never, not every, don't.
**Evidence:** creators 1.70x across 10 creators ("Stop doing these five things according to the Stoics", 15.8x); own "Not every insult deserves a reply" 43% and a share.
**Mechanism.** A correction implies the viewer is losing something now, and losses weigh more than gains (Baumeister et al. 2001).
**Rule.** Correct a habit, never a person or a group. "Stop explaining yourself" is fine; "Stop being weak" is a pep talk and fails rule 6 of doc 16.

### 7. Generic "you" that states a shared truth
**Words:** "you" in the sense of "anyone": "You can't make everyone like you."
**Evidence:** most likes on the account (11).
**Mechanism.** People use generic "you" to turn a personal hurt into a general lesson, and it helps them make meaning of negative experiences (Orvell, Kross & Gelman 2017). A viewer reads it as something true of them and of everyone, which is easy to like and easy to send.
**Contrast.** Accusing "you" ("Motivation isn't coming. ... Neither should you.") reached 20. Generic "you" includes the viewer; accusing "you" corners them.

### Weak or negative
- **Number or list first** (own 27% vs 35%; creators 1.00x). A number tells the viewer how long they'll be there and nothing about why. Put the list after a conflict line.
- **Thinker's name first** (own 25% vs 33%; creators 1.29x, mostly Jung channels). Authority is a reason to believe, not a reason to stay. Use the name on line 2.
- **Abstract self-help nouns** (motivation, productivity, rules, habits). Own 29% vs 37% and the two worst reels.

## 4. Likes and follows: what the research says about the social side

- **Likes beget likes.** Teenagers in an fMRI study liked photos more when they already showed many likes, and seeing popular photos raised activity in the nucleus accumbens (Sherman et al. 2016). In a 14,000-person music market, showing download counts made popular songs more popular and made success less predictable (Salganik, Dodds & Watts 2006). The honest use: reply to comments in the first hour so the first ones are real conversations (already on your weekly list). Never buy likes or use engagement pods.
- **Talking about yourself feels rewarding.** Disclosing information about oneself activated the mesolimbic dopamine system, and people gave up money to do it (Tamir & Mitchell 2012). That supports the house rule of ending every post on a 1-3 word question about the viewer's own life ("Which one?", "Sound familiar?"), with Moodius answering first in the pinned comment.
- **Shared posts are posts about the self and others.** Articles that later went viral raised activity in brain regions for self-related thinking and for thinking about other people (Scholz et al. 2017). A post gets sent when it says something about the viewer *and* someone they know: "Send this to someone who..." only works when the reel already made the viewer think of that person.
- **Moral and emotional words spread, mostly within a side.** Each moral-emotional word in a tweet raised retweets by about 20%, mostly within the poster's own political group (Brady et al. 2017). That's how outrage accounts grow. Use moral-emotional words about the viewer's own conduct (shame, pride, fair, cruel), never against a group. This keeps the brand off the young-men / red-pill track.

## 5. Keyword bank

**Use (with the mechanism):**

| Word or frame | Mechanism | House version |
|---|---|---|
| someone ___ you | self-reference + social threat | "Someone left you on read." |
| again | recognition: a scene the viewer has lived more than once | "You replayed it again." |
| 2am, tonight, today | puts the scene in the viewer's own day | "It's 2am and you're winning the argument." |
| isn't ___. It's ___. | prediction error | "You're not lazy. You're avoiding a feeling." |
| you don't have a ___ problem | prediction error, aimed at the self | "You don't have a confidence problem." |
| ___ vs ___ / or | two-option gap | "Rest or avoidance?" |
| hurts more than | contrast + pain word | "Being ignored hurts more than being hated." |
| the quiet cost of | hidden cost (9.5x in the creator set) | "The quiet cost of always being available." |
| why you keep ___ | names a repeating pattern the viewer is in | "Why you keep apologising first." |
| actually, really, the real | promises an update to a belief | "What Epictetus actually meant." |
| stop ___ (a habit) | correction, loss weight | "Stop explaining yourself to people committed to misreading you." |
| lonely, ignored, left out | sadness words (clicks) | "Lonely at a full table." |
| only one of them | two-branch wait | "Two people skip the gym. Only one is resting." |

**Retire as openers:** numbers ("3", "5"), "rules", "signs", "things", "motivation", "productivity", "discipline" (unless reframed as a feeling), a thinker's name, "Did you know", "Save this".

**Never (dark patterns):** fake urgency ("before it's deleted"), "wait for the end" when the end doesn't pay, rage-bait about a group, "Comment YES if...", made-up numbers or studies, manipulation framed as a skill ("exposes anyone", "go cold").

## 6. Rewrites for the queue, 26 Oct to 1 Nov

These are suggestions only. Nothing in Metricool has been changed. Every caption still ends on a 1-3 word question.

| Slot | Now | Suggested frame 0 | Pattern | Last line |
|---|---|---|---|---|
| Mon 26, 12:00 carousel | You're not lazy. You're avoiding a feeling. | **Keep.** Add a scene on card 1 above it: "You opened that email four times." | 3 + 1 | Which feeling? |
| Mon 26, 18:00 reel | Likes are a vote from people who gave your post half a second... | "You checked the likes again." then "Those votes took half a second. Yours took your whole life." | 1 + 3 | Whose vote counts? |
| Tue 27, 12:00 carousel | How to stop rehearsing disasters that never come. | "You've lived this disaster ten times tonight. It hasn't happened once." | 1 + 5 | Sound familiar? |
| Tue 27, 18:00 reel | Being alone isn't the problem. Being alone when you didn't choose it is. | **Keep.** Loneliness is the strongest topic in the creator set. Line 2 needs to land by second 3. | 3 + 5 | Chosen or not? |
| Wed 28, 12:00 carousel | Do less, better: the Stoic answer to burnout. | "The quiet cost of saying yes to everything." | hidden cost | What's one no? |
| Wed 28, 18:00 reel | Gregor Samsa turns into an insect overnight, and his first real panic is that he's late... | "He woke up as an insect. His first worry? Being late for work." | 2 + 3 | Relatable? |
| Thu 29, 12:00 carousel | Why one comment ruins your whole day. | "Ten kind comments. One cruel one. Guess which you replayed." | 1 + 5 | Which one stuck? |
| Thu 29, 18:00 reel | Nobody warns you that the early version of a better life looks a bit ridiculous... | "Leaving at eleven looks ridiculous. For about a month." | 3 | Worth it? |
| Fri 30, 12:00 carousel | Who you let close becomes who you are. | "Listen to how you talk after an hour with them." | 1 | Who's rubbing off? |
| Fri 30, 17:00 reel | If anger was the only feeling that was safe to show growing up... | "Your anger is carrying something heavier." | 3 + 5 | What's underneath? |
| Sat 31, 12:00 carousel | Stop explaining your philosophy. Show it. | **Keep.** It's a correction aimed at a habit. | 6 | Show or tell? |
| Sat 31, 18:00 reel | There's a version of independence that's really just fear with good posture... | "You don't reach out, so you can't be turned down." then "That's not independence. That's fear with good posture." | 1 + 3 | Sound familiar? |
| Sun 1, 12:00 carousel | The two horses pulling your mind. | "Two horses are pulling your mind. Only one listens." | 2 + 4 | Which one wins? |
| Sun 1, 18:00 reel | In a 2014 study (Wilson et al., Science), many people left alone with their thoughts for 15 minutes chose... | "People chose an electric shock over 15 minutes alone with their thoughts." Citation moves to line 2. | 3 + 5 | Could you? |

The Gregor Samsa, two-horses and Wilson rewrites put the story first and the source second. The source stays in the reel and the caption, as the quote rules require.

### Hook-intel drafts HI01-HI05: which variant fits these findings

| Script | Best fit | Why |
|---|---|---|
| HI01 | B: "Someone insulted you today. Here's what Epictetus trained for." | Other person + second person first, thinker on line 2 (patterns 1, 3) |
| HI02 | A: 'Is being "too sensitive" a flaw, or is it information?' | Question about a told fact with a two-option answer (patterns 2, 4) |
| HI03 | A: "You were lonely at a full table, and nobody noticed." | Loneliness + a scene the viewer is in (patterns 1, 5) |
| HI04 | A: "You answer every message within a minute. Here's the cost." | Hidden cost in the second person (the 9.5x creator hook) |
| HI05 | C: "Two people skip the gym tonight. Only one is resting." | Two-branch wait (pattern 2), the shape of the 16.5s reel |

## 7. What to test next

- **X5 (from 2 Nov, 18:00 reels)** already tests situation vs curiosity hooks. Log which of patterns 1-6 each reel uses, in the `hook_type` column of `post-log.csv`, so the 19 Nov review can rerun both scripts on more posts.
- **Sends test.** For two weeks, end other-person reels on relief or awe instead of a "send this" line, and compare sends per reach with the 21-23 Oct reels (0 sends).
- **Frame-0 readability.** After "They got away with it. You didn't.", check every frame 0 reads one way in a single pass, at phone size.
- **Follows.** Every follow so far came from a reframe carousel that promised a 7-day plan. Try a reframe reel that ends on "Part 1 of 3" before the Epictetus arc (12-15 Nov), and compare follows per reach.

## References

All links go to the DOI or an open copy.

1. Baumeister, R. F., Bratslavsky, E., Finkenauer, C., & Vohs, K. D. (2001). Bad is stronger than good. *Review of General Psychology*, 5(4), 323-370. https://doi.org/10.1037/1089-2680.5.4.323
2. Berger, J., & Milkman, K. L. (2012). What makes online content viral? *Journal of Marketing Research*, 49(2), 192-205. https://doi.org/10.1509/jmr.10.0353
3. Brady, W. J., Wills, J. A., Jost, J. T., Tucker, J. A., & Van Bavel, J. J. (2017). Emotion shapes the diffusion of moralized content in social networks. *PNAS*, 114(28), 7313-7318. https://doi.org/10.1073/pnas.1618923114
4. Gruber, M. J., Gelman, B. D., & Ranganath, C. (2014). States of curiosity modulate hippocampus-dependent learning via the dopaminergic circuit. *Neuron*, 84(2), 486-496. https://doi.org/10.1016/j.neuron.2014.08.060
5. Itti, L., & Baldi, P. (2009). Bayesian surprise attracts human attention. *Vision Research*, 49(10), 1295-1306. https://doi.org/10.1016/j.visres.2008.09.007
6. Kang, M. J., Hsu, M., Krajbich, I. M., Loewenstein, G., McClure, S. M., Wang, J. T., & Camerer, C. F. (2009). The wick in the candle of learning: Epistemic curiosity activates reward circuitry and enhances memory. *Psychological Science*, 20(8), 963-973. https://doi.org/10.1111/j.1467-9280.2009.02402.x
7. Kidd, C., & Hayden, B. Y. (2015). The psychology and neuroscience of curiosity. *Neuron*, 88(3), 449-460. https://doi.org/10.1016/j.neuron.2015.09.010
8. Knutson, B., Adams, C. M., Fong, G. W., & Hommer, D. (2001). Anticipation of increasing monetary reward selectively recruits nucleus accumbens. *Journal of Neuroscience*, 21(16), RC159. https://doi.org/10.1523/JNEUROSCI.21-16-j0002.2001
9. Lai, L., & Farbrot, A. (2014). What makes you click? The effect of question headlines on readership in computer-mediated communication. *Social Influence*, 9(4), 289-299. https://doi.org/10.1080/15534510.2013.847859
10. Lieberman, M. D., Eisenberger, N. I., Crockett, M. J., Tom, S. M., Pfeifer, J. H., & Way, B. M. (2007). Putting feelings into words: Affect labeling disrupts amygdala activity in response to affective stimuli. *Psychological Science*, 18(5), 421-428. https://doi.org/10.1111/j.1467-9280.2007.01916.x
11. Loewenstein, G. (1994). The psychology of curiosity: A review and reinterpretation. *Psychological Bulletin*, 116(1), 75-98. https://doi.org/10.1037/0033-2909.116.1.75
12. Northoff, G., Heinzel, A., de Greck, M., Bermpohl, F., Dobrowolny, H., & Panksepp, J. (2006). Self-referential processing in our brain: A meta-analysis of imaging studies on the self. *NeuroImage*, 31(1), 440-457. https://doi.org/10.1016/j.neuroimage.2005.12.002
13. Orvell, A., Kross, E., & Gelman, S. A. (2017). How "you" makes meaning. *Science*, 355(6331), 1299-1302. https://doi.org/10.1126/science.aaj2014
14. Robertson, C. E., Pröllochs, N., Schwarzenegger, K., Pärnamets, P., Van Bavel, J. J., & Feuerriegel, S. (2023). Negativity drives online news consumption. *Nature Human Behaviour*, 7, 812-822. https://doi.org/10.1038/s41562-023-01538-4
15. Rogers, T. B., Kuiper, N. A., & Kirker, W. S. (1977). Self-reference and the encoding of personal information. *Journal of Personality and Social Psychology*, 35(9), 677-688. https://doi.org/10.1037/0022-3514.35.9.677
16. Salganik, M. J., Dodds, P. S., & Watts, D. J. (2006). Experimental study of inequality and unpredictability in an artificial cultural market. *Science*, 311(5762), 854-856. https://doi.org/10.1126/science.1121066
17. Scholz, C., Baek, E. C., O'Donnell, M. B., Kim, H. S., Cappella, J. N., & Falk, E. B. (2017). A neural model of valuation and information virality. *PNAS*, 114(11), 2881-2886. https://doi.org/10.1073/pnas.1615259114
18. Schultz, W., Dayan, P., & Montague, P. R. (1997). A neural substrate of prediction and reward. *Science*, 275(5306), 1593-1599. https://doi.org/10.1126/science.275.5306.1593
19. Sherman, L. E., Payton, A. A., Hernandez, L. M., Greenfield, P. M., & Dapretto, M. (2016). The power of the like in adolescence: Effects of peer influence on neural and behavioral responses to social media. *Psychological Science*, 27(7), 1027-1035. https://doi.org/10.1177/0956797616645673
20. Symons, C. S., & Johnson, B. T. (1997). The self-reference effect in memory: A meta-analysis. *Psychological Bulletin*, 121(3), 371-394. https://doi.org/10.1037/0033-2909.121.3.371
21. Tamir, D. I., & Mitchell, J. P. (2012). Disclosing information about the self is intrinsically rewarding. *PNAS*, 109(21), 8038-8043. https://doi.org/10.1073/pnas.1202129109

Lai & Farbrot figures checked against the British Psychological Society's summary; Robertson et al. figures against Nieman Lab's report of the paper. The container can't reach OpenAlex or Semantic Scholar, so the other papers were not re-read for this doc; they are standard, widely cited papers, and the claims made here are the ones in their abstracts.

## Rerun

```
python3 tools/own_word_patterns.py            # edit the R list from a fresh Metricool pull first
python3 -I tools/creator_keyword_lift.py path/to/hook-intel/data/hookintel.db
```
