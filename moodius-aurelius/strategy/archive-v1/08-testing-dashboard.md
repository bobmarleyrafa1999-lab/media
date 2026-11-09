# 8. A/B testing system and performance dashboard

## Metrics (all from Metricool, pulled 72h after posting so posts are comparable)
| Metric | Definition | Primary for |
|---|---|---|
| Views | Plays (reels) / impressions (images) | slot tests |
| Reach | Unique accounts | carousel vs reel |
| 3s hold | Metricool "3-second view rate" | hooks |
| Watch % | avg watch time ÷ duration | reel length, story reels |
| Save rate | saves ÷ reach | carousels, practices |
| Share rate | shares ÷ reach | memes, F1 |
| Comment rate | comments ÷ reach | captions, questions |
| Engagement rate | (likes + comments + saves + shares) ÷ reach | overall |
| Follow conversion | follows from the post ÷ reach (read in the Instagram app if Metricool lacks it) | growth |

**Baseline (Week 2, D):** reel views 115–143 at good slots, 3s hold 25–48% (median ≈ 41%), avg watch 2.5–5.9s, interactions 1–9.

## Experiments, first 30 days
Run at most two reel experiments at once, in different slots, so they don't contaminate each other.
| ID | Question | Arms | Where | Primary metric | Weeks |
|---|---|---|---|---|---|
| E6 | Does 15:00 beat the old 10:00 and match 12/18? | 15:00 vs 12:00/18:00 | all reels | views at 72h | 3–4 (running) |
| E2 | Carousel vs reel in the third slot | carousel (Tue/Thu/Sun 15:00, Sun 18:00) vs reels in the same slots in Week 3 | 15:00 | reach, then save+share rate | 4–6 |
| E1 | Confrontational vs curiosity hook | "You keep…" vs "The emperor of Rome wrote one rule…" | F1 reels, 12:00, alternate days | 3s hold | 5 |
| E3 | Short vs long caption | < 60 words vs 150–250 words | F1/F6 reels at 18:00, alternate days | save rate, comment rate | 5 |
| E5 | Minimalist vs illustrated | dark stone vs public-domain classical art (Met Open Access / Wikimedia, CC0) behind text | reels at 18:00 | 3s hold, reach | 6 |
| E7 | CTA type | send vs save vs follow | all reels, rotating | matching rate (shares / saves / follows) | 6 |
| E4 | Carousel length | 5 vs 8 slides | carousels | save rate | 5–8 |

## Decision rules (no fake significance)
- **Unit = one post.** Pair posts by slot and weekday; compare each pair.
- **Minimum 6 pairs** before saying anything. Report the median of each arm and the number of pairs won.
- **"Directional"** = one arm wins ≥ 5 of 6 or ≥ 8 of 10 pairs. Act on it cautiously, keep testing. (Sign test p ≈ 0.11–0.22: not significant.)
- **"Winner"** = ≥ 9 of 10 pairs (two-sided sign test p ≈ 0.02) **and** the gap holds in the second half of the test.
- **Stop early** only when one arm is worse on every pair after 6 (likely harmful).
- At our size (~130 views/reel), percentages swing a lot. Never compare one post to one post.
- Log every result, including nulls, in `experiments.csv`.

## Dashboard layout (Google Sheets: import `post-log.csv` and `experiments.csv`)
**Tab 1 · Weekly scorecard**: followers (start/end, % growth), posts published / planned, median views, median 3s hold, total saves, shares, comments, link clicks, email signups.
**Tab 2 · Post log**: one row per asset (schema in `07`), conditional formatting: green above the 4-week median, red below.
**Tab 3 · Format leaderboard**: pivot by format_code → count, median reach, median 3s hold, median save rate, median share rate. Sorted by the format's primary metric.
**Tab 4 · Hook types**: pivot by hook_type → median 3s hold.
**Tab 5 · Slots**: pivot by slot × weekday → median views (heatmap).
**Tab 6 · Experiments**: ID, status, pairs run, pairs won A/B, medians A/B, call (none / directional / winner), date, next action.

## Weekly review (Friday routine, 10 lines max in the thread)
1. Scorecard numbers vs last week.
2. Top 3 and bottom 3 posts and why (format, hook, slot).
3. Experiment status changes.
4. Next week's mix change (if any) with the rule that triggered it.
