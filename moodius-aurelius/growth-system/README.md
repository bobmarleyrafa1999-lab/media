# Growth system (Stages 4 to 7 prototype)

The glue between the parts Moodius already has: the research library, the
reels engine, Metricool, and the comment agent. Built 25 Oct 2026 from the
master brief. Free, no accounts connected, synthetic test data only.

| file | what it does |
|---|---|
| `pillars.json` | The five pillars, weekly targets, disclaimers, banned framing and claim words. One place to change the rules. |
| `tools/brief_lint.py` | Checks a post brief before anything is drafted or queued. Blocks on: a missing part, an unknown pillar, a question that isn't 1-3 words or isn't the caption's last line, an evidence id not in the tidbit library, a missing health/history disclaimer, red-pill or miracle-cure wording, faces in automated posts, a book review of a book Surafel hasn't read, an undisclosed affiliate link. Warns on hand-read sources, long hooks, number openers and banned visuals. |
| `tools/analytics.py` | Merges Instagram's own export and `strategy/post-log.csv` into one SQLite file, then writes `dashboard.html` and `weekly.md`: rates per 1,000 reached by pillar and format, follow-up candidates, posts that produced follows, underperformers, pillar balance and the hurt/conflict cap. |
| `tools/comments.py` | Stage 5. Sorts comments into an approval queue (intent, pillar, the actual question, a matching tidbit, a DRAFT reply, a follow-up question). Crisis, sensitive, sponsorship, commercial and criticism always go to Surafel with no draft. Repeated questions become post ideas and brief skeletons. Never sends anything. |
| `tools/calendar_build.py` | Stage 6. Fills one reel-first week (12 reels, 2 carousels) from passing briefs against the pillar targets and the hurt/conflict cap. Writes a tracker CSV, a check note and a hand-off JSON for the account thread, all marked draft. |
| `experiments-proposed.csv` | Stage 7. X7-X10, each with its metric, posts per arm, minimum events and minimum gap fixed in advance. `analytics.py --experiments` reads it and calls each test by that rule. |
| `WORKFLOW.md` | The daily and weekly loop, and the steps that need Surafel. |
| `briefs/examples/` | Two passing briefs and one that breaks every rule. |
| `fixtures/` | Synthetic export, tags and comments (marked SYNTHETIC), plus four real tidbit rows. |

## Run

```
cd moodius-aurelius/growth-system
python3 tools/brief_lint.py briefs/examples/*.json --library 'fixtures/tidbits-sample.csv'
python3 tools/analytics.py --ig-export fixtures/ig-export-sample.csv \
    --tags fixtures/tags-sample.csv --out /tmp/moodius-out --week-ending 2026-10-25
python3 tools/comments.py fixtures/comments-sample.csv \
    --library fixtures/tidbits-sample.csv --out /tmp/moodius-comments
python3 tools/calendar_build.py --briefs briefs/examples --week-start 2026-11-09 \
    --library fixtures/tidbits-sample.csv --out /tmp/moodius-week
python3 -m unittest discover -s tools
```

Point `--library` at `research/library/tidbits/*.csv` once PR #9 and #11 are
merged. Python 3.9+, standard library only.

## Honest limits

- Instagram's API reports `follows` and `profile_visits` for feed posts and
  stories, not reels, so reel follow rates show as "n/a". Reel follow effects
  can only be read from account-level daily follower change.
- Rates use summed numerators over summed denominators, and only over posts
  that report both. Groups under 5 posts are labelled "lead only".
- Real exports stay out of this public repo; they live in the project files.

## Not built yet (needs Surafel's yes)

- A weekly GitHub Actions job that pulls insights with the comment agent's
  existing Instagram token.
- Comment agent topics moved to the five pillars, plus a book-request intent.
- The Friday routine running every brief through `brief_lint.py`.
