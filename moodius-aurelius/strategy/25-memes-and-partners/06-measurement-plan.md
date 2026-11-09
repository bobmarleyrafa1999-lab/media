# 30-day measurement plan: does the meme lane help?

**Dates.** Mon 23 Nov – Tue 22 Dec 2026. It starts after the 19 Nov review closes E1/E2, so those tests stay clean.
**Hypothesis (a starting guess, not a proven mix).** About 40% memes, 40% educational, 20% recommendations in the 8 weekly feed slots raises sends and saves without costing follows or trust. The two-week sample comes out at 39 / 44 / 17.
**Commercial overlay.** None during the 30 days (OBI first). After that: at most 1 commercial post per 8 feed posts, never inside a meme, measured separately.

## Baseline

Educational carousels and reels from 21 Oct–19 Nov (the daily carousel + reel period), read at the same post age. Current figures for 21–26 Oct, from Metricool per-post data:

| | Posts | Reach | Saves | Shares | (Saves + shares) per 1,000 reach |
|---|---|---|---|---|---|
| Carousels | 5 | 1,470 | 2 | 5 | 4.8 |
| Reels | 6 | 934 | 6 | 0 | 6.4 |

Per-post reach from the API runs below the account total (known since 25 Oct), so posts are only compared with posts.

## What we measure (per post, at day 7)

| Metric | Source | Note |
|---|---|---|
| **(Shares + saves) per 1,000 reach** | Metricool per post | Main metric. Shares are what a meme is for |
| Meaningful comments | Read by hand (or the comment agent once live) | 4+ words and on topic. Arguments, insults and bait replies don't count, even though they'd lift the number |
| Follows per 1,000 reach | Metricool IGPO29 | Carousels only; the API gives no follows for reels |
| Profile visits | Instagram app insights | The API no longer returns them. Screenshot on Fridays, or skip |
| Profile link taps | Metricool IGAC12 | Account level |
| Unfollows | Followers day to day; app insights | "Followers lost" returns empty for this account |
| Production time | Minutes, logged in `data/queue.csv` notes | Memes should take under 10 min of your time each |

## Fair comparison

- Same age: every post read at day 7.
- Medians per lane, not averages.
- Outliers: a post above 3× its lane median is reported on its own line and the medians are shown with and without it.
- Same slots: memes mostly sit in 12:00 carousel slots, compared with 12:00 educational carousels.
- Minimum: 8 meme posts before any verdict (the project's 30% median rule).

## Decision on 23 Dec

| Result | Then |
|---|---|
| Meme median on the main metric ≥ 1.3× educational, follows per 1,000 reach not below 0.8×, no rise in unfollows | Keep 40/40/20, try one more meme slot |
| Within ±30% | Keep memes at 2–3 a week for warmth; no change to the mix |
| Memes below 0.7×, or unfollows rise | Drop to 1 a week; review which themes you rejected and which flopped |

Also reported: which meme themes win (the `learn` command), single-image vs 2-slide (if any singles ran), and meme reels vs meme carousels (only 2 meme reels, so a lead, not a verdict).
