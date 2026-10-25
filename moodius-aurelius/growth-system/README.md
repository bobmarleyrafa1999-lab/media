# Growth system (Stages 4 to 7 prototype)

The glue between the parts Moodius already has: the research library, the
reels engine, Metricool, and the comment agent. Built 25 Oct 2026 from the
master brief. Free, no accounts connected, synthetic test data only.

| file | what it does |
|---|---|
| `pillars.json` | The three approved pillars (Mind 40%, Body 25%, People 35%), the six series and their rules, evidence labels, the medical-history line, tone caps, banned framing and claim words. One place to change the rules. Mirrors `strategy/22-90-day-plan/three-pillars.json`. |
| `tools/brief_lint.py` | Checks a post brief before anything is drafted or queued. Blocks on: a missing part, an unknown pillar or series (or a series used outside its pillars and formats), a Body post with no evidence label or with a dose, a book post with no label, a film post with no title/year/director, an Old Idea post with no named tradition and text, a question that isn't 1-3 words or isn't the caption's last line, an evidence id not in the tidbit library, a missing medical-history disclaimer, red-pill or miracle-cure wording, faces in automated posts, a book review of a book Surafel hasn't read, an undisclosed affiliate link. Warns on hand-read sources, long hooks, number openers and banned visuals. |
| `tools/analytics.py` | Merges the 90-day plan's `tracker.csv`, Instagram's own export and `strategy/post-log.csv` into one SQLite file, then writes `dashboard.html` and `weekly.md`: rates per 1,000 reached by pillar and format, follow-up candidates, posts that produced follows, underperformers, pillar balance against the shares, the hurt cap and the 2-in-3 opener rule. |
| `tools/comments.py` | Stage 5. Sorts comments into an approval queue (intent, pillar, the actual question, a matching tidbit, a DRAFT reply, a follow-up question). Crisis, sensitive, sponsorship, commercial and criticism always go to Surafel with no draft. Repeated questions become post ideas and brief skeletons. Never sends anything. |
| `tools/calendar_build.py` | Stage 6. Fills one week of feed slots from passing briefs. Until 22 Nov it uses a 12:00 carousel and an 18:00 reel each day (reach-batch addendum). From 23 Nov it uses the approved standard week: 5 carousels Mon-Fri 12:00 and reels Tue/Thu 18:00 and Fri 17:00 (story nights are made by hand). Targets are pillar share x slots; at most 4 hurt openers; at least 2 in 3 curiosity or appreciation openers. Writes a tracker CSV, a check note and a hand-off JSON for the account thread, all marked draft. |
| `experiments.csv` | Stage 7. E1-E3 from the 90-day plan plus two queued proposals (E4 closing-question type, E5 series label, each needing Surafel's OK). `analytics.py --experiments` calls each by the plan's rule: a lead only when both arms have enough posts, one median is 30% higher, and its reach median isn't 30% lower. |
| `WORKFLOW.md` | The daily and weekly loop, and the steps that need Surafel. |
| `briefs/examples/` | Two passing briefs and one that breaks every rule. |
| `fixtures/` | Synthetic export, tags and comments (marked SYNTHETIC), plus four real tidbit rows. |

## Run

```
cd moodius-aurelius/growth-system
python3 tools/brief_lint.py briefs/examples/*.json --library 'fixtures/tidbits-sample.csv'
python3 tools/analytics.py --ig-export fixtures/ig-export-sample.csv \
    --tags fixtures/tags-sample.csv --experiments experiments.csv \
    --out /tmp/moodius-out --week-ending 2026-10-25
# real log: --tracker ../strategy/22-90-day-plan/tracker.csv
python3 tools/comments.py fixtures/comments-sample.csv \
    --library fixtures/tidbits-sample.csv --out /tmp/moodius-comments
python3 tools/calendar_build.py --briefs briefs/examples --week-start 2026-11-23 \
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
- Comment agent topics moved to Mind / Body / People, plus a book-request intent (comments.py already uses them).
- The Friday routine running every brief through `brief_lint.py`.
