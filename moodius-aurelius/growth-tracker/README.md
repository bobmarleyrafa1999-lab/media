# Moodius growth tracker

Tracks, explains and forecasts the growth of @moodiusaurelius. Runs only on your Mac, uses free tools, and needs no Claude to run.

**What you get each week:** a one-page report (what changed, the evidence, three actions, one experiment, forecast vs actual) and a local dashboard with Overview, Content, Forecasts, Experiments and Data quality tabs.

## Start here

| I want to... | Read |
|---|---|
| Install it on my Mac (once, about 15 minutes) | [docs/SETUP-MAC.md](docs/SETUP-MAC.md) |
| Add this week's numbers (about 5 minutes) | [docs/IMPORT-GUIDE.md](docs/IMPORT-GUIDE.md) |
| Connect Meta's official API instead of copying numbers (optional) | [docs/META-API-SETUP.md](docs/META-API-SETUP.md) |
| Know what each number means and what's not available | [docs/METRICS.md](docs/METRICS.md) |
| See why these libraries and versions are safe to install | [docs/LIBRARY-CHECKS.md](docs/LIBRARY-CHECKS.md) |
| See the plan and what's still to build | [docs/PLAN.md](docs/PLAN.md) |

## The weekly routine (Monday, 10 minutes)

1. Import the week's numbers (or let the optional API collector do it).
2. `python3 -m moodius_growth report` and read section 3: your three actions.
3. `streamlit run app.py` if you want to look closer.

## Ground rules built into the code

* Raw files are kept unchanged in `data/raw/`; nothing is imported twice.
* Missing numbers stay missing (n/a). They are never turned into 0.
* Follower totals and Meta's "follows" are kept apart. Post reach is never added up and called unique reach.
* Forecasts only appear when the history supports them, with backtested error in followers. Otherwise you get clearly labelled scenarios.
* Demo data lives in a separate file (`data/demo.sqlite`) and the dashboard shows a red banner when you look at it.
* Real data, tokens and logs are in `data/` and `logs/`, which git ignores. The dashboard only listens on your own Mac.

## Files

```
moodius_growth/   the Python package (db, importers, metrics, forecast, report, meta_api, cli)
app.py            the dashboard
templates/        CSV import templates + experiments
scenarios.json    the assumptions behind the projections (edit freely)
schedule/         optional daily collection on your Mac (launchd)
demo/             synthetic demo data builder
tests/            python3 -m unittest discover -s tests
```
