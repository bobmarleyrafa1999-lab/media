---
description: Add a new article idea to the editorial database, scored and linked to sources
argument-hint: "headline or idea" [pillar number]
---
Add **$ARGUMENTS** to `moodius-aurelius/substack/data/editorial.csv` with the next MA-number. Fill every column: pillar, series, reader tension in one sentence, philosophy, research_ids (existing library rows only; leave a note if none), originality/relevance/effort (1–5, with a one-line reason in your reply), platforms, status "idea", related IDs, reusable assets. Check for near-duplicates of existing headlines and tensions first; if one exists, propose merging instead. Rebuild with `python3 moodius-aurelius/substack/scripts/build_db.py` and report the new rank.
