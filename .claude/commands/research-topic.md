---
description: Research one backlog topic (MA-xxx or free text) and add verified sources to the library
argument-hint: MA-007 | "topic in words"
---
Research **$ARGUMENTS** for Moodius Aurelius. Follow `publication/CLAUDE.md`.

1. If it's an ID, read its row in `publication/data/editorial.csv` (tension, philosophy, research_ids). Read the linked rows in `publication/data/sources.csv`.
2. Find what's missing: prefer systematic reviews and meta-analyses, then large or pre-registered studies, then classic studies, then original philosophical texts in public-domain translations. Run `python3 publication/scripts/research_feed.py papers "<query>" --reviews` when the network allows; otherwise use web search.
3. For each candidate, open the abstract or publisher page. Record: full citation, DOI/URL, design and sample, the finding in one sentence, the caveat, evidence tier (1 Empirical / 2 Philosophical / 3 Moodius / 4 Anecdotal), and `verification` = what you actually opened and when.
4. Append new rows to `publication/data/sources.csv` with the next N-number. Never add a number, quote or finding you didn't see in a source. Mark anything from memory as "canonical record, not re-opened".
5. Update the topic's `research_ids` and `effort` in `editorial.csv`, then run `python3 publication/scripts/build_db.py`.
6. Report: sources added, what's contested, what's still unverified.
