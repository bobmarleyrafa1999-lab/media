# 8. Testing dashboard (Phase 1 rules)

**Rules:** one experiment at a time, two variants, at least 10 posts per variant, primary metrics **sends per reach** and **saves per reach**. No claims of significance; results are reported as "A ahead on X of 10 posts, medians a vs b".

## Queue (`experiments.csv`)
| ID | Question | A | B | Primary metric | When |
|---|---|---|---|---|---|
| X1 | Cover: claim vs question | "You don't have X. You have Y." | "Why do you X?" | saves/reach | 26 Oct → about 15 Nov (10 carousels each, alternate days) |
| X2 | Reel length | 12–15s | 18–20s | sends/reach | next |
| X3 | CTA | save | send | matching rate | then |
| X4 | Caption length | under 60 words | 150–250 words | saves/reach, comments | then |
The 30-day cadence test itself (1 carousel + 1 reel a day) is judged on 19 Nov: median sends/reach and saves/reach by format, follower growth, against Week 2's baseline (followers 3→4, reels 115–143 views).

## Metrics
| Metric | Definition |
|---|---|
| Sends per reach | shares ÷ reach |
| Saves per reach | saves ÷ reach |
| Comments per reach | comments ÷ reach |
| Follows | follows attributed to the post (Instagram app insights) |
| Reel watch | average watch time ÷ length, 3-second view rate |

## The Sheet
Tab "tracker" is the calendar with metric columns. Add tab "summary" with three pivots: by format (median sends/reach, saves/reach), by experiment arm, by week. `post-log.csv` holds the raw history from Week 2 on.

## Claude does (automatic)
- Every Friday: pulls metrics, computes the two rates, updates `post-log.csv` and `experiments.csv`, assigns next week's posts to the running experiment's arms, and reports status.

## You do (by hand)
- Paste the weekly numbers Claude lists into the Sheet (until Claude has direct Sheets write access).
- Read the Friday reply. Nothing to decide unless an experiment finishes.
