# Hook Intel · first research cycle (22 Oct 2026)

Cycle `2026-10-22-mvp`. Data fetched 22 Oct 2026, 11:21-11:40 UTC, by the GitHub Actions fetcher
(public metadata only). Every number below comes from `data/hookintel.db`. Nothing is estimated.

## What works (tested)

| Part | Status | How it was tested |
|---|---|---|
| Fetcher (`remote/fetch.py` + workflow) | works | Real run: 12 YouTube searches, 36 channels, 3 TikTok profiles, 2 podcast searches. 73 of 84 requests OK. |
| Ingest, baselines, outlier ratio | works | 356 records from 46 creators; unit tests for the short-form filter, baselines and missing-value handling |
| Hook classifier + six scores + priority | works, with limits (below) | 334 hooks scored; 20 checked by hand against cover frames, and 9 of the 20 needed the category corrected |
| Patterns | works | 29 patterns; the top 5 are below |
| Library search (SQLite FTS5) | works | `python3 -m hookintel search "lonely"` returns 5+ hits |
| Reel pipeline | works | 5 scripts x 3 hooks pass our QC and the existing reels-engine QC gate; HI01a-HI05a rendered with reels-engine (flat Slate preview, no footage yet) |
| A/B framework | built, not yet fed | Unit-tested on synthetic data; waits for real posts (X6 starts after X5) |
| Own-account review | works | 13 reels imported from Metricool (1-22 Oct) |
| Dashboard (5 tabs) + CSV/JSON exports | works | `reports/dashboard.html` (static build) and the local server |
| Tests | 19 pass | `python3 -m unittest discover -s tests` |

**Classifier limit, said plainly.** On titles, the regex classifier left 35% of relevant hooks (69 of 195)
unclassified and mislabelled 9 of the 20 I checked by hand. It's a cheap first filter. The
hand-checked labels in `data/editorial/` override it, and they're what the patterns below use.

## What could not be accessed

| Wanted | Result | Why / workaround |
|---|---|---|
| Instagram Reels discovery | not accessible | Instagram is blocked from the container and needs a login for listings. Use: paste reel URLs into `data/manual-urls.csv`, add competitors in Metricool, or run on the Mac. |
| YouTube full video pages (exact upload date for search hits, comments, captions) | blocked | "Sign in to confirm you're not a bot" on GitHub's IP, for all 6 player clients tried. We don't pass cookies. Works from a home IP: `--full` on the Mac. |
| First spoken sentence | 0 of 20 | Needs captions (blocked above) or audio transcription (Mac only). |
| First on-screen text | 0 verified | Cover OCR ran on 275 covers; only 32 gave readable text. Cover frames were read by eye for the 20 (labelled "cover frame", not "first frame"). |
| YouTube Shorts tab | 10 of 36 channels have none | Baseline falls back to the Shorts in the channel's RSS feed. |
| TikTok search, single TikTok video pages | not supported / blocked | Profile feeds work (2 of 3 handles). The School of Life's TikTok failed. |
| Retention for other creators | not public anywhere | Only our own Insights have retention. |

## Missing metrics

| Metric | YouTube | TikTok | Moodius (Metricool) |
|---|---|---|---|
| Publish date | 281 of 316 (RSS); search-only hits have none | 30 of 30 | yes |
| Views | 316 of 316 | 30 of 30 | yes |
| Likes | 281 of 316 (RSS rating count) | 30 of 30 | yes |
| Comments | 0 | 30 of 30 | yes |
| Duration | 41 of 316 | 30 of 30 | no (organic duration not exposed) |
| Followers | 293 of 316 | 0 | n/a |
| Creator baseline / outlier | 285 of 316 | 30 of 30 | account baseline from 13 reels |
| Follows per reel | n/a | n/a | not exposed by Metricool |
| 3 s hold, avg watch | n/a | n/a | yes |

## The 20 videos

Selected from the 191 relevant short-form videos posted in the last 90 days, by priority (outlier
evidence first), dropping one ad and keeping a spread of creators. Hook text is the title
(proxy). Visual notes are from cover frames.

| # | Video | Creator | Published | Views | Creator median | Outlier | Category |
|---|---|---|---|---|---|---|---|
| 1 | [The psychological cost of being available](https://www.youtube.com/shorts/1yWPZBZLkIs) | Human Friction | 13 Oct | 1,005 | 106 | 9.5x | Psychological revelation |
| 2 | [Stop doing these five things according to the Stoics](https://www.tiktok.com/@daily_stoic/video/7698791827926830349) | daily_stoic (TikTok) | 20 Oct | 34,600 | 2,194 | 15.8x | Contrarian |
| 3 | [What Marcus Aurelius Teaches About Waking Up Early](https://www.youtube.com/shorts/exzb26kBpA8) | Daily Stoic | 18 Oct | 62,213 | 8,700 | 7.2x | Curiosity gap |
| 4 | [The Secret to Never Getting Upset](https://www.youtube.com/shorts/FIPDQ78MfjM) | Daily Stoic | 16 Oct | 50,492 | 8,700 | 5.8x | Curiosity gap |
| 5 | [Is Depression a Neurochemical Imbalance](https://www.youtube.com/shorts/06O2mC2SW8g) | HealthyGamerGG | 17 Oct | 481,539 | 94,500 | 5.1x | Unexpected question |
| 6 | [Depression vs Responsibility](https://www.youtube.com/shorts/lKIg6YaXFnI) | HealthyGamerGG | 18 Oct | 505,965 | 94,500 | 5.4x | Philosophical paradox |
| 7 | [The Job of a Therapist](https://www.youtube.com/shorts/DIfCFnJC7cg) | HealthyGamerGG | 15 Oct | 427,476 | 94,500 | 4.5x | Curiosity gap |
| 8 | [Why This Psychiatrist Learned to Stop Giving Patients Answers](https://www.youtube.com/shorts/k7ejvsP297E) | Mind In Context | 5 Oct | 1,735 | 513 | 3.4x | Curiosity gap |
| 9 | [Why People Who Claim to Know the Absolute Truth Are Dangerous](https://www.youtube.com/shorts/IlD3UoV6DKY) | Mind In Context | 5 Oct | 1,552 | 513 | 3.0x | Psychological revelation |
| 10 | [Perception can easily be distorted](https://www.tiktok.com/@withmindful/video/7692579379729157390) | withmindful (TikTok) | 3 Oct | 11,400 | 3,267 | 3.5x | Psychological revelation |
| 11 | [Five Stoic strategies for dealing with difficult people](https://www.tiktok.com/@daily_stoic/video/7698790535267405070) | daily_stoic (TikTok) | 20 Oct | 7,778 | 2,194 | 3.5x | Curiosity gap (list) |
| 12 | [The Loneliness of Feeling Unseen When You Have People](https://www.youtube.com/shorts/OL85T7jryNE) | Intentional Unwind | 21 Sep | 1,190 | 653 | 1.8x | Emotional recognition |
| 13 | [no one will be hearing from me](https://www.youtube.com/shorts/_wUWUT0Bwow) | BookBitsbyJensa | 11 Oct | 1,033 | 473 | 2.2x | Emotional recognition |
| 14 | [You Can't Change Until You See the Problem](https://www.youtube.com/shorts/NNyePAkfjNs) | Mind In Context | 6 Oct | 1,048 | 513 | 2.0x | Uncomfortable truth |
| 15 | [Has Our Obsession With Utility Left Us Lonely and Lost?](https://www.youtube.com/shorts/u_lrHzjZgL0) | Mind In Context | 5 Oct | 1,155 | 513 | 2.3x | Unexpected question |
| 16 | [Stop Doing These Five Things](https://www.youtube.com/shorts/HwiKlYXBGPI) | Daily Stoic | 20 Oct | 20,526 | 8,700 | 2.4x | Contrarian |
| 17 | [Why Thinking About Death Can Make Every Day Count](https://www.youtube.com/shorts/Da10z9ApAd8) | TheDeeperLifeHQ | 20 Oct | 1,238 | 829 | 1.5x | Philosophical paradox |
| 18 | [The Relationship Truth Most People Learn Too Late](https://www.youtube.com/shorts/CTQUKsYb-sg) | EXODUS . | 11 Oct | 1,581 | 1,100 | 1.4x | Uncomfortable truth |
| 19 | [Stop Treating Books Like Trophies](https://www.youtube.com/shorts/9jTu-zrCNhY) | Daily Stoic | 18 Oct | 12,914 | 8,700 | 1.5x | Contrarian |
| 20 | [Why Does Chaos Feel Safer Than Love](https://www.youtube.com/shorts/9oO_ktZgzlo) | HealthyGamerGG | 16 Oct | 112,017 | 94,500 | 1.2x | Psychological revelation |

Notes: #2 and #16 are the same Daily Stoic video. It's 15.8x on TikTok and 2.4x on YouTube, so the
same hook gets very different lifts depending on the platform. #17 re-uploads someone else's
interview footage, which Moodius never does; only the hook is studied. #5's medical topic is out
of bounds for us, so only the question shape transfers. Every video has a "Why it might work"
note, a Moodius adaptation, a first frame, music and a length in the Library tab.

## Five patterns

Rank = how far these videos beat their own creator's Shorts median, discounted for small samples,
plus a nudge from Moodius's own retention data where we've used the shape.

| # | Pattern | Videos | Median outlier | Moodius evidence | Becomes |
|---|---|---|---|---|---|
| 1 | **Insider reveal**: what X actually is or does | 4 | 5.2x | used 1x (29% 3 s hold) | HI01 |
| 2 | **A question about something you were told as fact** | 6 (2 with baseline) | 3.7x | the two-branch question reel held 16.5 s once | HI02 |
| 3 | **Second-person scene you recognise** | 2 | 2.0x | 3 reels, 41% median 3 s hold vs 32% account | HI03 |
| 4 | **The hidden cost of an everyday habit** | 1 | 9.5x | none | HI04 |
| 5 | **X vs Y**: two things you thought were one | 2 | 3.4x | two-branch structure (n=1) | HI05 |

Confidence: these are leads, not laws. Each pattern rests on 1-6 videos from one research cycle,
and the hook text is a title, not a verified opening line. Pattern 4 is a single video. What
counts is how our own reels do in the X6 test.

## Five original scripts (3 hooks each)

Full storyboards: `reels/hi-batch-01/HI0x.md`. Subtitles: `reels/hi-batch-01/srt/`. Engine
scripts: `reels/hi-batch-01/hi-batch-01-engine.json`. Rendered previews (hook A, flat Slate
background until footage is added) are in the project folder: `hook-intel/reports/reels/hi-batch-01/renders/`.

| Reel | Hook A | Hook B | Hook C | Length | Source |
|---|---|---|---|---|---|
| HI01 | What a Stoic actually did when someone insulted him. | Someone insulted you today. Here's what Epictetus trained for. | The Stoics had a drill for being insulted. | 20.4 s | Idea: Epictetus, Enchiridion 20 |
| HI02 | Is being "too sensitive" a flaw, or is it information? | Someone once told you that you were too sensitive. | "You're too sensitive." Who benefited from you believing that? | 21.5 s | Idea: Epictetus, Enchiridion 1.5 |
| HI03 | You were lonely at a full table, and nobody noticed. | Laughing at dinner. Lonely the whole time. | Have you ever been lonely around people who love you? | 20.2 s | Moodius reflection |
| HI04 | You answer every message within a minute. Here's the cost. | Being always available is teaching people something. | The quiet cost of always replying straight away. | 21.6 s | Idea: Seneca, On the Shortness of Life 3 |
| HI05 | Rest or avoidance? They feel the same from the sofa. | Is it rest, or are you hiding? | Two people skip the gym tonight. Only one is resting. | 19.4 s | Idea: Seneca, On Tranquillity of Mind 17 |

All five use "Idea: ... · Moodius words" cite cards, not verbatim quotes, so there's no wording to
verify. Every hook A opens on a person, a feeling or a scene, not a list. HI01 and HI05 use the
two-branch turn.

## How to operate it

1. **New research cycle**: copy `requests/2026-10-22-mvp.json` to `requests/<date>.json`, edit the
   searches, push. The fetcher commits `data/raw/<date>/` about 15-20 minutes later. Then run
   `bin/discover-hooks` and `bin/analyse-hooks`.
2. **Instagram reels you've seen**: add rows to `data/manual-urls.csv` (copy the example), then
   run `bin/discover-hooks`.
3. **Check the top 20 by eye**: add notes to `data/editorial/<cycle>.json`. Your category beats
   the regex.
4. **Write scripts**: `bin/generate-reels briefs`, write into `data/scripts/<batch>.json` (or ask
   Claude in a thread), then `bin/generate-reels build data/scripts/<batch>.json`.
5. **After posting**: save a Metricool export to `data/imports/` (a Claude thread can pull it),
   log the post URLs in `data/experiments/`, and run `bin/review-performance`.
6. **Look at it**: `python3 -m hookintel dashboard`, or open `reports/dashboard.html`.
