# Weekly reel batch prompt (reusable; paste into the Friday routine)

You are writing next week's reels for @moodiusaurelius ("Stoicism for people who feel things"). Work in /mnt/project-files/moodius-aurelius/reels-engine/. Read only these, in this order, and nothing else unless a step fails:
1. `reels-tests.csv` and the rows of `reels-log.csv` added since the last batch.
2. `04-pillars-and-ideas.md` (pick unused ideas) and the rows of `03-research-library.csv` with an empty `used_in`.
3. The last batch JSON in `scripts/` (for the schema and to avoid repeating hooks).

Then:
- Apply `07-testing.md`: update test pair counts, make a call only by its rules, set this week's arms.
- Write 7 scripts into `scripts/batch-NN.json` using the same schema: 2 Journal, 1 each of the other pillars, 1 rotating; at most 2 R4 humour. Each has `hook`, `hook_b`, cards, visual, footage tag or null, audio, source, caption (60–120 words, ends with a question, signed "— Moodius"), first comment, ≤ 5 hashtags.
- Voice: thoughtful, understated, specific, occasionally dry. Make people feel understood, not lectured. Human experience first; the male perspective is an undertone. No motivational clichés, no "alpha" language, no fake-deep lines.
- Quotes only verbatim from public-domain translations (Long, Gummere, Trotter, Garnett, Common, Jowett, Ross), verified before use (engine check does Long's Meditations, Discourses and Enchiridion and Stewart's Seneca Dialogues automatically; Gummere, Trotter, Common by hand on Wikisource/Gutenberg/Lexundria); modern books only as "Idea: Author, Book (year) · Moodius words". Never invent a quote or a number.
- Beat grammar (engine 1.3, from 2 Nov): put `"grammar": "beat"` at the top of the batch JSON. Card 1 is on screen at frame 0; put the hook-system midpoint break at 5-10 s as a `"quiz"` card (a question the viewer answers in their head, 2-3.5 s, never "comment below") or an Ember label; answer it with a `"reveal"` card (2-4 lines joined by `\n`, each appears in turn) or a body card; the payoff reuses the hook's words; keep the Phase 1 CTA; the engine adds the loop back to the hook.
- Run the creative check in `06-pipeline.md`; rewrite anything that fails.
- Script Doctor: `python3 tools/engine.py doctor scripts/batch-NN.json` prints `prompts/script-doctor.md` and every draft with timings. Score each 0-100, rewrite anything under 70, store `"doctor": {score, issues, rewritten, by}` on the script.
- Run `python3 tools/engine.py check`, fix every ✗ (it now checks every quote word for word against the Standard Ebooks text; a "not machine-checked" warning means verify by hand and fill `source.verified_at`), then `render` (and `--variant b` for B-arm days), then `tools/export_md.py`.
- Open each render's `-qa.png` (frame 0, every card, last frame at phone size, Instagram's button and caption zones shaded) and read its `-qa.json`: `frame0_has_text` and `loop_matches_frame0` must be true. This replaces the one contact-sheet frame per batch.
- Fill `used_in` in the library for every row you used.
- Hand the files to the account thread, which owns Metricool scheduling, for the calendar's 18:00 reel slot (Fri 17:00). Report in ≤ 8 lines: what shipped, test status, anything blocked.
