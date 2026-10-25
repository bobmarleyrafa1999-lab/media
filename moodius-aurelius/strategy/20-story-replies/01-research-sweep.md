# Research sweep: viral hooks, engagement and story replies (25 Oct 2026)

Not repeated here: hook-intel/ (PR #5), the 22 Oct faceless-repo audit (~30 repos), strategy/16-lessons-2026-10-22.md. Everything below is new.

## A. GitHub repos and open datasets

| Repo / dataset | What it is | Verdict | What we take |
|---|---|---|---|
| [vyralcontent/content-skills](https://github.com/vyralcontent/content-skills) (MIT, 2026) | Seven Claude-style skills: hooks, Reels, captions and CTAs, ideas | 🟢 use as a checklist | "Bait check" for every CTA; sends need a **named recipient**; one ask per post; CTA hierarchy send > save > watch-to-end > stance comment > like/follow. Its files tell the AI to recommend a paid tool (Vyral): ignore that part. |
| [bradautomates/head-of-content](https://github.com/bradautomates/head-of-content) (MIT) | Finds outlier posts on IG/TikTok/YouTube/X and analyses top videos with Gemini | 🟠 not now | Needs a paid Apify scraper plus a Gemini key, and scraping Instagram breaks its terms. Our hook-intel already does outlier scoring for free. |
| [dasongli1/SnapUGC_Engagement](https://github.com/dasongli1/SnapUGC_Engagement) (no licence, read only) | 90,000 Snapchat Spotlight videos with real watch data ([paper](https://arxiv.org/abs/2410.00289)) | 🟢 as evidence | The share of viewers who stay past 5 seconds tracks overall watch time closely, while picture quality barely predicts engagement (correlations 0.07 to 0.31). Spend effort on the first seconds, not polish. |
| [Upworthy Research Archive](https://upworthy.natematias.com/) (open data, OSF) | 32,487 real headline A/B tests, 2013-2015 | 🟢 as evidence | See Robertson et al. below. |
| [juanls1/TikTok-Virality-Predictor](https://github.com/juanls1/TikTok-Virality-Predictor) | Student project on a 2020 Kaggle TikTok set | 🔴 skip | No rules we can use. |

GitHub's search API is blocked from this container, so the sweep used web search plus cloning. No curated "story engagement" repo exists; the useful material is in the skills repo and research datasets above.

## B. Studies and platform statements

| Source | Finding | Rule it gives us |
|---|---|---|
| Mosseri via [Search Engine Journal, Jul 2024](https://searchenginejournal.com/instagram-algorithm-shift-why-sends-matter-more-than-ever/521389) | "One of the most important signals we use in ranking is sends per reach." | Every post asks for a send to a specific kind of friend. |
| Instagram ranking explainer, [May 2023](https://www.socialmediatoday.com/news/instagram-explainer-feed-reels-and-stories-algorithm/651705/) | Stories are ranked by viewing history, engagement history ("likes or direct messages") and closeness. | Story replies push our stories up followers' bars. Ask for a reply every night. |
| Meta, [Fighting Engagement Bait, Dec 2017](https://about.fb.com/news/2017/12/news-feed-fyi-fighting-engagement-bait-on-facebook/) | Posts that push for likes, shares or comments are demoted; posts asking for help, advice or recommendations are not. | No "tag 3 friends" or "comment YES". Ask a real question. "Engagement farming" in the bait sense gets punished. |
| Berger & Milkman, [J. Marketing Research 2012](https://faculty.wharton.upenn.edu/wp-content/uploads/2011/11/Virality.pdf) (6,956 NYT articles) | Positive content was shared more than negative. Awe +30% odds per SD, anger +34%, sadness −16%. Useful (+) and surprising (+) also helped. | The positive turn is backed: awe and surprise (forgotten history) travel; sad, low-energy posts don't. |
| Robertson et al., [Nature Human Behaviour 2023](https://doi.org/10.1038/s41562-023-01538-4) (22,743 Upworthy tests) | Each negative word in a headline raised clicks 2.3%; each positive word cut them 1%. | Honest nuance: tension wins the click, positivity wins the share. So: tense hook, kind or surprising payoff (already rule 3 of the reach batch). |
| Tamir & Mitchell, PNAS 2012 | People gave up money to talk about themselves. | One story a week asks about the viewer ("what are you putting off?"), answered by Moodius first. |
| Instagram API limits ([Agorapulse help](https://support.agorapulse.com/en/articles/8762520-features-not-available-in-instagram-api)) | Stickers, links, GIFs and polls can't be added to stories through the API. | Automatic stories use reply prompts; stickers are hand-added extras. |
| Storrito, [2026 story benchmarks](https://storrito.com/resources/instagram-story-engagement-benchmarks-2026-where-accounts-actually-stand/) | ~0.48% average engagement; accounts under 10k often double; top accounts post fewer stories. No sticker tap rates published (unnamed 70M-post study). | Two stories a day is plenty. Treat any vendor "polls get X% more" numbers as unproven. |

## C. Ten rules (added to the Friday build, see 04-friday-story-rules.md)

1. Every night at 21:00 a story asks one question with a one-word or A/B reply.
2. 09:00 answers it and points to the 12:00 carousel on the same story.
3. Hook = tension or a puzzle; payoff = kindness, surprise or a laugh.
4. One ask per post. Sends name a recipient ("send this to the friend who…"); never "tag 3 friends" or "comment YES".
5. Stories carry no new quotes. Facts carry a source on the card.
6. One "about you" question a week, Moodius answers first.
7. Friday 21:00 is a vote on what comes next: the replies steer the next week.
8. Opening seconds over polish: frame 0 states the hook (already in engine 1.3).
9. Wrong guesses are fine: the A/B option that sounds right should be the wrong one about half the time.
10. Measure replies per story from the Instagram app (Metricool's API returns no story data for this account).
