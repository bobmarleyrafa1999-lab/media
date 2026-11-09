# Hook Intel · Moodius Aurelius

A local, free system that finds short-form videos in Moodius's niches, works out which openings
beat their own creator's normal results, files them in a searchable library, and turns the best
patterns into original, brand-safe reel scripts with three test hooks each. It never posts.

```
discover-hooks  ->  analyse-hooks  ->  generate-reels  ->  (the owner picks)  ->  review-performance
   metadata         classify, score,     briefs, then         account thread     baseline, A/B
   only, cached     outlier ratio,       QC'd scripts,        books slots in      stats, next
                    patterns             SRT, storyboards     Metricool           experiment
```

## Setup (Mac or Linux, once)

```bash
cd moodius-aurelius/hook-intel
./setup.sh                    # venv, yt-dlp, FTS5 check, tests
source .venv/bin/activate
```

No API keys are needed. `.env.example` lists the only optional one (a free YouTube Data API key)
and documents that paid AI APIs stay off.

## The five commands

| Command | What it does | Cost |
|---|---|---|
| `bin/discover-hooks [--fetch requests/x.json] [--full]` | Ingests every fetched cycle in `data/raw/`, manual URL sheets (`data/manual-urls*.csv`), editorial notes and Metricool imports; classifies; writes `reports/discover-<cycle>.md`. With `--fetch` it first runs the fetcher (needs a machine that can reach YouTube/TikTok). | free |
| `bin/analyse-hooks [--cycle NAME] [--top 5]` | Scores every hook, computes outlier ratios, groups hooks into patterns and ranks them. | free |
| `bin/generate-reels briefs` / `bin/generate-reels build data/scripts/<batch>.json` | `briefs` turns the top patterns into writing briefs. `build` QCs a written batch, adds timestamps, storyboard, overlay specs, SRT subtitles for each hook, and three reels-engine scripts per reel, then runs the existing reels-engine QC gate. | free |
| `bin/review-performance [--import data/imports/x.json]` | Account baseline (median and IQR), every reel against it, A/B tests with a two-proportion test, recommendations. | free |
| `bin/weekly-content-plan [--week 2026-11-30]` | Proposes where each concept and hook variant goes in a week. Proposal only. | free |

Helpers: `python3 -m hookintel search "loneliness"`, `python3 -m hookintel export` (CSV + JSON of every
table to `exports/`), `python3 -m hookintel dashboard` (http://127.0.0.1:8765), or
`python3 -m hookintel dashboard --static reports/dashboard.html` for a single shareable file.

## Where the data comes from, and what it can't see

| Source | Route | What we get | What we don't |
|---|---|---|---|
| YouTube Shorts | yt-dlp flat search (results filtered to "this month, under 4 min") | title, views, duration, channel | upload date on this route, likes, comments |
| YouTube channels | channel RSS feed + Shorts tab | last 15 uploads with publish date, views, rating count (likes); views of the last 30 Shorts = creator baseline; follower count | comments; first spoken sentence; retention |
| YouTube full page | `--full` on a home connection | exact likes, comments, upload date, captions (first ~6 s = first spoken sentence) | blocked on datacenter IPs ("sign in to confirm you're not a bot"); we never pass cookies |
| TikTok (research only) | yt-dlp profile feed | per video: date, views, likes, comments, duration, caption | TikTok search; single video pages fail on datacenter IPs |
| Instagram Reels | manual URL sheet; Metricool competitors once added; Mac with the instagram-transcript tool | whatever you paste | automated discovery: Instagram is blocked here and needs login for listings |
| Podcasts | Apple Podcasts search API | episode titles, dates, length | views (podcasts don't publish them) |
| Moodius's own reels | Metricool connector, saved to `data/imports/` | reach, views, 3 s view rate, avg watch, likes, comments, saves, shares, reposts | follows per reel, organic duration, retention curve |

Every fetch writes `access-log.json` with each request's success or error, and the dashboard's
Discover tab shows it. A metric the source doesn't give stays empty. Nothing is estimated.

**Cover text.** For Shorts the fetcher reads the cover image with Tesseract OCR. A cover is not
always the first frame, so it is labelled "cover text (OCR)", and used as the hook only when no
spoken or on-screen line is known. When only a title exists, the hook is labelled
"title (proxy: not the spoken hook)" and its confidence is capped at medium.

### Running discovery

The cloud container that built this can't reach YouTube, TikTok or Instagram, so discovery runs in
one of two places:

1. **GitHub Actions (default).** Commit a request file to `requests/` on a `claude/project-thread-*`
   branch. `.github/workflows/hook-intel-fetch.yml` runs `remote/fetch.py` on that file, then commits
   `data/raw/<name>/` back. It has no schedule: it runs only when a request is pushed. The repo is
   public, so Actions minutes are free.
2. **the owner's Mac.** `bin/discover-hooks --fetch requests/x.json --full`. A home connection also
   gets full YouTube pages and captions. Still no login or cookies.

A request is a small JSON file: search terms, channel handles, TikTok handles, podcast terms,
manual URLs. See `requests/2026-10-22-mvp.json`.

## How a hook is scored

1. **Hook text**: first spoken sentence > first on-screen text > cover OCR > title (labelled).
2. **Category** (10 from the brief) by weighted cue phrases, with a secondary category and a
   confidence. "Visual disruption" needs a `visual_opening` note: text alone can't show it.
3. **Structure**: question, two-branch, list opener, negation reframe, "people who", named thinker,
   second-person scene, first-person story, statement.
4. **Six 0-5 scores**: specificity, clarity, originality (trigram overlap with the whole library,
   and clichés), emotional relevance, visual compatibility (works as text over still or archival
   imagery, no face), brand alignment (pillars; red-pill and grindset terms set it to 0).
   Weighted into a 0-100 **text score**. That number is a judgement about the words, not proof.
5. **Outlier ratio** = views / median views of the creator's last 30 Shorts (needs 5 or more).
   It's left empty when there's no baseline.
6. **Priority** = 60% outlier evidence (log scale, 1x = neutral) + 40% text score. So a video that
   beat its creator's normal by 4x ranks above a well-worded one with no evidence.
7. **Moodius priors** from `strategy/16-lessons-2026-10-22.md`: other-person/conflict hooks held
   43% median past 3 s on this account (n=5), list openers 29% (n=3). These nudge alignment and
   pattern rank, and are always shown as "Moodius data", never as proof about other accounts.

Patterns = category x structure. Rank = (log2 median outlier + 1) x log2(1 + videos with a
baseline) + a small prior from Moodius's own retention + the mean text score.

## Writing reels

`generate-reels briefs` writes `data/scripts/briefs.json`. Scripts are written by hand or by Claude
in a Claude Code session (his plan, no metered API) into `data/scripts/<batch>.json`, then
`generate-reels build` rejects anything that:

- has more or fewer than 3 hooks, or a hook over 12 words
- runs outside 15-45 s, or a card too fast to read (0.4 s + 1 s per 4.5 words)
- passes fewer than 6 of the 7 hold rules (`strategy/reel-first/hook-system.md`)
- uses an off-brand or cliché phrase, or a quote without a public-domain translation, or an idea
  without an "Idea: ... · Moodius words" card
- has a shot without a rights note

Outputs per reel: `reports/reels/<batch>/<id>.md` (hooks, timestamped script, shot list, overlay
spec, B-roll keywords, sound design, caption, hashtags, QC), `srt/<id>{a,b,c}.srt`, and
`<batch>-engine.json` with three reels-engine scripts (A/B/C) ready for
`python3 ../reels-engine/tools/engine.py render`.

## A/B testing (X6)

One experiment at a time: X5 (hook test on 18:00 reels) runs to 19-23 Nov, so this is X6. Per
reel: A on the grid, B and C as Instagram trial reels (non-followers only) in matched slots on the
next two days, posted by hand. Log the post URLs in `data/experiments/<id>.json`:

```json
{"id": "X6-HI01", "concept_id": "HI01", "hypothesis": "...", "metric": "3 s hold", "status": "running",
 "variants": {"a": {"hook": "...", "post_url": "https://www.instagram.com/reel/..."}, "b": {...}, "c": {...}}}
```

After the next Metricool import, `review-performance` compares the variants with a two-proportion
test on 3 s hold. It says **evidence** only at p < 0.05 with 100+ views per arm. Anything else is
a **hypothesis**. Each reel is also banded against the account's own IQR.

## Budget and safety

- Free: Python standard library, yt-dlp, Tesseract, SQLite, GitHub Actions on a public repo.
- Cheap filtering first: metadata and regex scoring run on everything. Manual viewing or
  transcription only happens for the top-ranked handful.
- Cached: raw fetches are kept per cycle and re-ingesting is idempotent (upsert by platform:id).
  Covers aren't downloaded twice. No video files are downloaded at all.
- No scheduled jobs, no paid APIs, no posting. Concepts stay `draft` until the owner picks one.
  The account thread books Metricool slots.
- Rights: other creators' videos are references only (links). Shots come from public-domain or
  licensed sources listed in `hookintel/config.py`, or the owner's own footage.

## Repositories reviewed

| Repo | Licence | Used | Why |
|---|---|---|---|
| yt-dlp/yt-dlp | Unlicense | yes, as a CLI | metadata only (`--flat-playlist`, `-J`, `--skip-download`); no downloads, no cookies |
| miloagents/niche-hook-miner | custom "free edition" (use and modify OK, no redistribution) | ideas only, no files copied | It's a prompt (SKILL.md), not code. Its signals (small-account breakout, creator concentration, freshness) are reimplemented here as the outlier ratio and per-creator baselines. Its "never invent engagement numbers" rule matches ours. |
| hellnoo/auto-clipper | no licence file (all rights reserved) | no code | It clips other people's long videos and uploads through `instagrapi` (unofficial Instagram login). Both clash with the brief. Ideas kept: cache downloads and transcripts by URL, and spread clips across the video. |
| Jakeschincariol/instagram-agent-skill | MIT | ideas | Outlier multiple (views / account median, 3x = signal) is the same method used here. Its hook formulas are built for selling, and "The Statistic" conflicts with the no-invented-numbers rule. |
| social-media-skills/skills | MIT | ideas | experimentation-and-ab-testing, platform specs. The AI-generator and TikTok skills were skipped. |

## Tests

```bash
python3 -m unittest discover -s tests
```

These cover ingest (short-form filter, baselines, nothing invented when a metric is missing,
manual CSV), the classifier and scores, the off-brand screen, ranking, patterns, full-text search,
script QC rejections, the timeline/SRT/engine export, the baseline and two-proportion test,
experiment labels, the weekly plan and the static dashboard.
