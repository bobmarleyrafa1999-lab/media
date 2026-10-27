# Weekly growth report: 21 Sep to 27 Sep 2026

> **DEMO DATA. Synthetic numbers for testing, not @moodiusaurelius.**

_Reporting days follow Europe/London. Sources: demo. Generated 27 Oct 2026 12:23 (UK time on your Mac)._

## 1. What changed

| | This week | Previous week | Change |
|---|---|---|---|
| Followers at end | 1,293 | 1,221 | +72 |
| Net follower change | 72 | 42 | +30 |
| Follower growth % | +5.9% | +3.6% | |
| Reach-days (sum of daily reach; not unique people) | 11,367 | 9,510 | +1,857 |
| Views | 15,916 | 13,317 | +2,599 |
| Net followers per 1,000 reach-days (proxy) | 6.3 | 4.4 | |
| Insights follows / unfollows (days reported) | 77 / 5 (7/7 d) | 52 / 10 (7/7 d) | |
| Profile visits | 225 (7/7 d) | 187 | |
| Link taps | 4 (6/7 d) | 9 | |
| Posts published (feed + reels) | 11 | | |

Follower totals and the Insights 'follows' count are different measures: totals come from the account's follower count, follows/unfollows from Meta's daily Insights, which can lag and miss days. Growth % uses totals.

## 2. Evidence and plausible explanations

**Formats, posts at least 3 days old, last 28 days (organic only).** Medians, not averages; 80% range is a bootstrap interval for the median. Fewer than 5 posts = lead only.

| Format | n | Median reach (80% range) | Typical median (no outliers) | Viral outliers | Median engagement by reach | Saves / 1k | Shares / 1k | Follows / 1k (n) | Reel avg watch | Reel 3 s view rate |
|---|---|---|---|---|---|---|---|---|---|---|
| carousel | 25 | 423 (358-441) | 398 | 1 | 5.1% | 11.6 | 5.8 | 3.5 (25) | - | - |
| reel | 14 | 162 (151-225) | 162 | 0 | 4.9% | 3.8 | 4.5 | n/a (0) | 5.2 s | 34% |

Reels have no per-post follows in Meta's API, so reel 'Follows / 1k' is n/a, not 0.

**This week's posts, by reach** (young posts are still collecting):

| Published (UK) | Format | First line | Reach | Eng. by reach | Shares / 1k | Follows | Age at collection |
|---|---|---|---|---|---|---|---|
| Mon 21 Sep 12:00 | carousel | DEMO carousel 21 Sep: list hook about Body | 233 | 3.4% | 4.3 | 0 | 6.8 d |
| Tue 22 Sep 12:00 | carousel | DEMO carousel 22 Sep: conflict hook about Body | 1,302 | 4.8% | 5.4 | 6 | 5.8 d |
| Tue 22 Sep 18:00 | reel | DEMO reel 22 Sep: story hook about Mind | 91 | 6.6% | 0.0 | n/a | 5.6 d |
| Wed 23 Sep 12:00 | carousel | DEMO carousel 23 Sep: story hook about People | 503 | 6.0% | 9.9 | 5 | 4.8 d |
| Thu 24 Sep 12:00 | carousel | DEMO carousel 24 Sep: story hook about Body | 374 | 4.8% | 2.7 | 2 | 3.8 d |
| Thu 24 Sep 18:00 | reel | DEMO reel 24 Sep: list hook about Body | 127 | 5.5% | 0.0 | n/a | 3.6 d |
| Fri 25 Sep 12:00 | carousel | DEMO carousel 25 Sep: conflict hook about People | 618 | 4.7% | 4.9 | 2 | 2.8 d |
| Fri 25 Sep 18:00 | reel | DEMO reel 25 Sep: conflict hook about Mind | 192 | 4.2% | 5.2 | n/a | 2.6 d |
| Sat 26 Sep 12:00 | carousel | DEMO carousel 26 Sep: question hook about Mind | 169 | 6.5% | 0.0 | 0 | 1.8 d |
| Sun 27 Sep 12:00 | carousel | DEMO carousel 27 Sep: list hook about Body | 209 | 6.7% | 4.8 | 1 | 0.8 d |
| Sun 27 Sep 18:00 | reel | DEMO reel 27 Sep: story hook about Body | 34 | 8.8% | 0.0 | n/a | 0.6 d |

- **Carousels vs reels:** carousel median reach 423 vs reel 162 (2.6x, n=25 vs 14). Plausible reasons: carousels get saved and resurfaced, and the carousel topics differed from reel topics. This is observational, not proof the format causes it.
- **Top post this week:** "DEMO carousel 22 Sep: conflict hook about Body" (carousel, reach 1,302).

## 3. Three actions for this week (in order)

1. **Keep the daily carousel as the main growth format.** Its median reach is 2.6x the reel median over the last 28 days. Keep reels at the planned count rather than adding more until a reel beats the carousel median.
2. **Fix the first 3 seconds of reels.** Only 34% of reel views pass 3 s (median). Open on the other person or the conflict, and make line two pay off the hook by second 3.
3. **Make a follow-up to "DEMO carousel 23 Sep: story hook about People".** It has the best attributed follows per 1,000 reached (9.9) of posts with 100+ reach. One post is a lead, not proof: treat it as a repeat test.

## 4. One controlled experiment

**D1 (running)**

- Hypothesis: DEMO: conflict openers earn more shares than question openers
- Variable: carousel opener
- Primary metric: shares per 1k reach
- Observation window: 7 days per post, run 2026-09-01 to 2026-09-28
- Decision rule: Pick the arm whose median is >=30% higher after 8 posts each; else no winner

Progress so far:

| arm | n | median_shares_per_1k | median_reach |
|---|---|---|---|
| A | 14 | 5.1 | 428.0 |
| B | 14 | 3.7 | 366.0 |

## 5. Forecast vs actual

Nothing to score yet: this is the first logged week. This report's forecasts are saved and will be scored next week.

**Statistical forecast status:** 30 days: 1,509 followers on 27 Oct (80% range 1,446-1,600, model drift_28, backtest MAE 44.5); 60 days: 1,910 followers on 26 Nov (80% range 1,943-2,067, model drift_7, backtest MAE 104.1); 90 days: 2,219 followers on 26 Dec (80% range 2,266-2,476, model drift_7, backtest MAE 158.7)

Where the point sits outside its 80% range, the model has been consistently too low or too high in past backtests; the range (built from those past errors) is the better guide.

7-day-ahead backtests so far: no_growth MAE 48.3 followers over 19 origins; drift_7 MAE 14.5 followers over 19 origins; drift_28 MAE 12.6 followers over 19 origins; seasonal_naive_7 MAE 14.5 followers over 19 origins; ets_damped MAE 13.0 followers over 19 origins; arima_011_drift MAE 13.0 followers over 19 origins.

**Assumption-based scenarios from 1,293 followers** (projections, not forecasts):

| Scenario | Reach / day | Net followers per 1k reach | +30 d | +60 d | +90 d | 1k | 5k | 10k | 25k | 50k |
|---|---|---|---|---|---|---|---|---|---|---|
| conservative | 1,349 | 4.9 | 1,463 | 1,630 | 1,794 | already reached | not within 180 d | not within 180 d | not within 180 d | not within 180 d |
| base | 1,301 | 5.5 | 1,492 | 1,690 | 1,885 | already reached | not within 180 d | not within 180 d | not within 180 d | not within 180 d |
| optimistic | 1,498 | 6.3 | 1,584 | 1,903 | 2,252 | already reached | not within 180 d | not within 180 d | not within 180 d | not within 180 d |

- *conservative*: Reach falls back to the typical posting-day level of the last 28 days (the recent carousel lift fades), no reach growth, 2% of followers leave each month. Reach basis: median daily reach over the last 28 days (28 posting days with data). Conversion basis: pooled net followers per 1,000 reached over the same days (proxy).
- *base*: Reach stays at the 14-day typical level, conversion stays at the 14-day pooled rate, 1% monthly churn. No growth in reach is assumed. Reach basis: median daily reach over the last 14 days (14 posting days with data). Conversion basis: pooled net followers per 1,000 reached over the same days (proxy).
- *optimistic*: Reach holds at the last-7-day typical level and then grows 10% a month (an assumption, not measured), 0.5% monthly churn. Reach basis: median daily reach over the last 7 days (7 posting days with data). Conversion basis: pooled net followers per 1,000 reached over the same days (proxy).

Days 91-180 are exploratory. None of these assume viral spikes repeat; they use medians.

## 6. Data quality

| Source | Last collected (UTC) | Age | Status |
|---|---|---|---|
| demo | 2026-09-28T07:00:00+00:00 | 701.4 h | old |

Not available in the last 28 days: story_reach. Shown as n/a, never as 0.

Metricool reports account days on Madrid time (one hour ahead of the UK all year), so a 'day' runs 23:00-23:00 UK. Post times are converted to UK time exactly.
