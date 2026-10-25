---
description: Turn Substack + Instagram numbers into an evidence-based editorial review (weekly, or day 30/60/90)
argument-hint: weekly | day30 | day60 | day90
---
Run a **$ARGUMENTS** review.
1. Inputs: Substack post stats and subscriber CSV exports Surafel drops in `moodius-aurelius/substack/data/imports/`, Instagram numbers via the Metricool connector (getAnalyticsDataByMetrics) for the essay-package posts, and `moodius-aurelius/substack/data/metrics.csv`.
2. Append one row per essay to `metrics.csv` (columns in its header). Compute: subscribers per 1,000 views, open rate, read-through where Substack shows it, restacks+shares+comments per 1,000 views, IG saves and sends per reach, IG→Substack link clicks and subscribers with source Instagram, and returning readers by pillar (opened ≥3 of last 4).
3. Re-score `relevance` in `editorial.csv` only where at least 3 essays in a pillar give a clear signal; note the change and the numbers behind it; rebuild with `build_db.py`.
4. Write `moodius-aurelius/substack/reviews/<date>-$ARGUMENTS.md`: what worked, what didn't, one experiment for next period (one at a time), and for day90 the paid-tier gate check. Ignore follower counts and likes as decision inputs.
