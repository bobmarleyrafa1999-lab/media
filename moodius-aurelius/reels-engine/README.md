# Moodius reels engine (20 Oct 2026)

Research → winning patterns → original scripts → rendered reels → tests → next batch. Follows the approved Phase 1 rules (positioning, palette, fonts, citations). Builds on `../strategy/` and `../tools/` rather than replacing them.

| File | Deliverable |
|---|---|
| `01-competitor-reels-report.md` | 36 accounts (26 in strategy/02 + 10 new adjacent), 2026 reel data, the 10 most repeatable formats and why they work |
| `02-five-formats.md` | The five low-cost formats R1–R5 and the rules for all of them |
| `03-research-library.csv` | 50 insights: idea in 2026 language, source type (quote / idea / data / discussion), citation, verification status, hook seed, where it's used |
| `04-pillars-and-ideas.md` | 5 pillars × 10 ideas |
| `05-scripts-batch-01.md` + `scripts/batch-01.json` | 20 publish-ready scripts: hook + test hook, cards with timings, visual, audio, source, caption, hashtags, first comment |
| `renders/` | R001–R010 rendered (MP4 + cover JPG + caption file), plus B-hook versions of R003–R005 |
| `06-pipeline.md` + `tools/` | Batch pipeline, quality gate, token-saving rules, what needs extra permissions |
| `07-testing.md` + `reels-log.csv` + `reels-tests.csv` | Test queue T1–T7, decision rules, log |
| `08-launch-7-day.md` | 26 Oct – 1 Nov plan with daily split of work |
| `prompts/weekly-batch.md` | The one prompt future sessions need |
| `sources-used.txt` | Generated list of every citation already on the account |

## Tools (all free, no AI calls)
- `tools/engine.py`: quality gate, citation registry, renderer (Phase 1 tokens from `../tools/design.py`), render cache. 1.3 (22 Oct 2026) adds the opt-in beat grammar (frame-0 hook, quiz and reveal cards, loop ending, phone-size QA sheet), `doctor` (Script Doctor brief, `prompts/script-doctor.md`) and a word-for-word quote check; see `06-pipeline.md`.
- `tools/quotes.py`: the quote check against Standard Ebooks texts (cached in `.sources/`). `tools/test_engine.py`: 9 tests.
- `tools/ambient.py`: original ambient beds, 6 moods, NumPy only.
- `tools/export_md.py`: script JSON → readable sheet.
- `../tools/score.py` still works as an alternative music engine.

## Who does what
**Claude, automatically with today's tools:** public-web research, writing, quote verification, quality gate, rendering, hand-off to the account thread for Metricool scheduling (Instagram), weekly metrics pull, test bookkeeping, next batch.

**the owner, by hand:**
1. Add 5 competitors in Metricool (2 min, once).
2. Optional: shoot 8 footage clips (`footage/README.md`, 20 min, once).
3. Comment replies (10 min a day) and adding stories to highlights.
4. Weekly: copy skip rate from the Instagram app into the log if you want the hook test to use it (2 min).

**Outside Phase 1 until the 19 Nov review:** TikTok/YouTube cross-posting, a second daily reel. **Needs extra software or permission (not used now):** paid voice (ElevenLabs) for narrated reels; licensed stock footage downloads (this machine can't reach Pexels/Pixabay); Instagram's full retention curve (app only).

## Not verified
Competitor per-reel hooks, retention and saves (Instagram blocks reading). Launch-week reels are scheduled in Metricool (media hosted on static.metricool.com, so render changes need updateScheduledPost).
