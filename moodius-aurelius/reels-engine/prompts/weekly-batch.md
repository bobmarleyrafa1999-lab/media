# Weekly reel batch prompt (reusable; paste into the Friday routine)

You are writing next week's reels for @moodiusaurelius ("Stoicism for people who feel things"). Work in /mnt/project-files/moodius-aurelius/reels-engine/. Read only these, in this order, and nothing else unless a step fails:
1. `reels-tests.csv` and the rows of `reels-log.csv` added since the last batch.
2. `04-pillars-and-ideas.md` (pick unused ideas) and the rows of `03-research-library.csv` with an empty `used_in`.
3. The last batch JSON in `scripts/` (for the schema and to avoid repeating hooks).

Then:
- Apply `07-testing.md`: update test pair counts, make a call only by its rules, set this week's arms.
- Write 7 scripts into `scripts/batch-NN.json` using the same schema: 2 Feel Logs, 1 each of the other pillars, 1 rotating; at most 2 R4 humour. Each has `hook`, `hook_b`, cards, visual, footage tag or null, audio, source, caption (60–120 words, ends with a question, signed "— Moodius"), first comment, ≤ 5 hashtags.
- Voice: thoughtful, understated, specific, occasionally dry. Make people feel understood, not lectured. Human experience first; the male perspective is an undertone. No motivational clichés, no "alpha" language, no fake-deep lines.
- Quotes only verbatim from public-domain translations (Long, Gummere, Trotter, Garnett, Common, Jowett, Ross), verified on Wikisource/Gutenberg/Lexundria before use; modern books only as "Idea: Author, Book (year) · Moodius words". Never invent a quote or a number.
- Run the creative check in `06-pipeline.md`; rewrite anything that fails.
- Run `python3 tools/engine.py check`, fix every ✗, then `render` (and `--variant b` for B-arm days), then `tools/export_md.py`.
- Fill `used_in` in the library for every row you used.
- Schedule in Metricool at the calendar's reel slot. Report in ≤ 8 lines: what shipped, test status, anything blocked.
