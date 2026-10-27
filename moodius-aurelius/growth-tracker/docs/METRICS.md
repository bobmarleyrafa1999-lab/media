# What each number means, and what's available

Sources checked 27 Oct 2026: Meta's Instagram Platform docs (Insights, IG User Insights, IG Media Insights, the Jan 2025 "views" change) and Metricool's list of available Instagram fields.

## Formulas
| Measure | Formula | Notes |
|---|---|---|
| Net follower change | follower total at end − total at start | From totals, not from Insights "follows". |
| Follower growth % | net change ÷ followers at start × 100 | Start = total at the end of the day before the period. Unreliable under ~50 followers. |
| Engagement by reach | (likes + comments + saves + shares) ÷ reach × 100 | n/a if any part is missing. Comments can include your own pinned comment. |
| Saves / shares / follows per 1,000 reached | metric ÷ reach × 1,000 | Groups use pooled sums (Σmetric ÷ Σreach), not an average of ratios. |
| Follows per production hour | attributed follows ÷ (production minutes ÷ 60) | Needs `production_minutes` in your tags. |
| Net followers per 1,000 reach-days | net change ÷ Σ daily reach × 1,000 | **Proxy.** Mixes every source of followers with every format's reach. |
| Reach-days | Σ daily account reach | **Not unique reach.** One person on two days counts twice. |

## Availability by source
✅ available · ⚠️ with limits · ❌ not available (shown as n/a, never 0)

| Metric | Meta API (account) | Meta API (post) | Metricool connector | Notes |
|---|---|---|---|---|
| Follower total | ✅ `followers_count` field | | ✅ | A live count; snapshot it daily. |
| Follows / unfollows | ⚠️ `follows_and_unfollows`, needs ≥100 followers | | ⚠️ Followers gained/lost | Can differ from total changes (lag, deleted accounts, timing). |
| Reach | ✅ daily, estimated | ✅ feed, reels, stories | ✅ | Account reach per day is unique for that day only. |
| Views | ✅ (marked "in development") | ✅ | ✅ | Replaced impressions/plays from April 2025. |
| Profile visits | ❌ at account level in the current metric list | ⚠️ feed + stories only | ❌ (field deprecated) | Enter from the app weekly. |
| Link taps | ✅ `profile_links_taps` | | ❌ (deprecated) | |
| Likes, comments, saves, shares | ✅ | ✅ | ✅ | |
| Follows from a post | | ⚠️ feed + stories only, **not reels** | ⚠️ feed posts | Reel follows can only be judged from account totals. |
| Reel avg / total watch time | | ✅ `ig_reels_avg_watch_time`, `ig_reels_video_view_total_time` | ✅ | Retention curve: not in the API. |
| Reel 3 s view rate / skip rate | | ⚠️ `reels_skip_rate` "in development" | ✅ view rate, retention % | |
| Story reach, replies, navigation | | ⚠️ only for 24 h; values under 5 error | ❌ returned no rows | Replies are 0 for European accounts. Completion proxy = 1 − exits ÷ reach (when collected in time). |
| Paid vs organic | ⚠️ non-`total_*` metrics are organic only | ⚠️ | ⚠️ reach paid / spend fields | No ads have run; the paid columns are empty. |

Other limits from Meta's docs: data can lag up to 48 hours; posts' metrics are kept for 2 years; carousel slides (album children) have no insights of their own; missing data comes back empty, not as 0.

## Comparing formats fairly
* Reels: reach, views, watch time, 3-second view rate, shares and saves per 1k.
* Carousels and images: reach, saves and shares per 1k, attributed follows per 1k.
* Stories: reach, replies, completion proxy. Never against feed reach.
* Only posts at least 3 days old are compared (younger posts are still collecting reach); the dashboard lets you change this.
* Viral outliers (above Q3 + 3×IQR of their own format) are listed separately, and "typical" medians leave them out.
* Fewer than 5 posts in a group = "lead only": worth a test, not a conclusion.
