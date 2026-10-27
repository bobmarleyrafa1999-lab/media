# Getting your numbers in

Pick one route. Every route keeps the original file in `data/raw/` and never imports the same file twice. Leave a cell **empty** when you don't have a number. Empty means "not available", while 0 means "really zero".

## Route A: Meta Business Suite export (free, official, posts and reels)
1. On a computer, go to **business.facebook.com** and pick the Moodius page.
2. Left menu: **Insights** > **Content**.
3. Set the date range (for example the last 28 days) and make sure Instagram is selected.
4. Click **Export data** > choose **CSV** > **Generate**. Save the file.
5. In Terminal (in the growth-tracker folder, with `.venv` active):
   `python -m moodius_growth import-content ~/Downloads/THE-FILE.csv --source ig_export`

The importer prints `unknown_columns`. Those columns are kept in the raw file but not used. If `reach` or `media_id` is in that list, send Claude just the header row (no numbers needed) and the alias list gets updated. Meta renames these buttons from time to time; if yours look different, say what you see.

## Route B: Metricool CSV (posts and reels)
1. In Metricool: **Analytics** > **Instagram**, set the date range.
2. Scroll to the **Posts** list, then the **Reels** list. Each has a download (↓ / CSV) button above it.
3. Import each file:
   `python -m moodius_growth import-content posts.csv --source metricool_csv --format carousel`
   `python -m moodius_growth import-content reels.csv --source metricool_csv --format reel`
   (`--format` is only used when the file has no type column.)

Metricool's **account** numbers (followers, reach per day) are easiest through the template below.

## Route C: the templates (anything the exports miss, about 2 minutes a week)

### templates/account_daily.csv: one row per day
| Column | Where to find it (Instagram app > Professional dashboard, or Metricool Analytics) |
|---|---|
| date | YYYY-MM-DD |
| followers_total | Follower count shown on your profile that day |
| following_total | Following count |
| follows / unfollows | Insights > Followers > Follows / Unfollows for that day (leave empty if not shown; Meta hides it under 100 followers) |
| reach | Insights > Accounts reached for that one day |
| views | Insights > Views for that day |
| accounts_engaged | Insights > Accounts engaged |
| profile_visits | Insights > Profile activity > Profile visits |
| link_taps | Insights > Profile activity > External link taps |
| story_reach | Leave empty unless you have it |
| scope | `organic` (no ads running). Use `organic+paid` if the number includes an ad. |
| reporting_tz | `Europe/London` for numbers from the app on your phone in the UK; `Europe/Madrid` for Metricool |

Copy the file, fill rows, then: `python -m moodius_growth import-account my-week.csv`

If the app only gives a 7-day total, don't put it on one day. Leave the daily cells empty and note the weekly total in Claude's thread instead. A total spread across days would be invented.

### templates/content_snapshot.csv: one row per post per check
Fill `media_id` (the post link works), `format`, `published_at` (UK time), and whatever metrics you have. Each import is a dated snapshot; the latest one per post is used, and older ones are kept for history.

### templates/content_tags.csv: your labels (the bit no export has)
`pillar` (Mind / Body / People), `topic`, `hook_type` (e.g. tension, curiosity, contrast, list, question), `cta` (send this, save this, question, none), `duration_s` (reels), `production_minutes`, `experiment_id`, `arm`. Use the same `media_id` as the post rows.
`python -m moodius_growth import-tags my-tags.csv`

### templates/experiments.csv
Already holds E1-E3 from the 90-day plan. `python -m moodius_growth import-experiments templates/experiments.csv`

## Time zones
Everything is shown in UK time. Metricool's daily account numbers use Madrid days (one hour ahead of the UK all year), so its "day" runs 23:00-23:00 UK. Those rows are marked `Europe/Madrid` and can't be re-cut into UK days, so they are labelled rather than shifted. Post times are converted exactly.
