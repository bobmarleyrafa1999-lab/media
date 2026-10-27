# Implementation plan (27 Oct 2026)

## What existed before
* `growth-system/tools/analytics.py` (PR #12, unmerged): plain Python + SQLite, reads an Instagram CSV export and the 90-day tracker, writes a dashboard and weekly note. It stays as it is; this tracker is a separate folder so the two can't break each other.
* Metricool (paid) holds account and post data from 3 Oct 2026. Stories return no rows through Metricool's analytics connector.
* Meta's API hosts are blocked from Claude's containers, so anything that talks to Meta runs on your Mac.

## Built in this version (v0.1)
1. **Storage:** SQLite with raw-file archive, long-format account and content snapshots, tags, experiments, forecast log, collection log.
2. **Import:** CSV templates; Instagram / Meta Business Suite / Metricool CSV exports via header aliases; Metricool connector JSON.
3. **Metrics:** daily, weekly, monthly changes; growth %; engagement by reach; saves, shares and attributed follows per 1,000 reached; follows per production hour; bot-wave check; freshness and completeness.
4. **Content analysis:** format, pillar, hook, CTA and posting hour comparisons with n, medians, bootstrap ranges, viral outliers separated, "lead only" under 5 posts.
5. **Forecasts:** no-growth, recent-drift and weekly seasonal-naive baselines; statsmodels damped ETS and ARIMA(0,1,1) only from 56 days; rolling-origin backtests with MAE and interval coverage; simpler model kept unless 10% better. Assumption-based scenarios with milestones and a posting-frequency explorer.
6. **Weekly report** and **Streamlit dashboard** (local only).
7. **Optional Meta API collector** with retries, token redaction and logs; launchd schedule template.

## Not built yet (and why)
* **Stories:** neither Metricool's connector nor the API keeps story metrics after 24 hours. Capturing them needs the daily collector running, or Meta's story_insights webhook (needs a public server, so skipped).
* **Statistical 30/60/90-day forecasts:** switched off until there are enough days of follower totals (about 72 days for 30-day forecasts). The code turns them on automatically.
* **Reel retention curves:** Meta's API gives average watch time and total watch time, not the curve. Retention % and 3-second view rate come from Metricool.
* **Ads:** no ads have run, so paid columns are empty. They are stored separately when they appear.

## Exact remaining steps for you
1. Install on your Mac (docs/SETUP-MAC.md).
2. Tell Claude your growth goal and today's follower count.
3. Optional: Meta API setup (docs/META-API-SETUP.md) if you want daily collection without copying numbers.
