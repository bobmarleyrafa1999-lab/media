# 2. Research engine: how the library works (21 Oct 2026)

`02-research-library.csv` holds 61 entries: 37 empirical (E), 15 philosophical (P), 3 house positions (M) and 6 cultural or anecdotal (C). It sits alongside the 50-line library in `../reels-engine/03-research-library.csv`, which stays the source for Stoic quotes already written as hooks.

## Columns
`id, theme, concept, author, source, year, source_kind, evidence_tier, credibility, key_finding, caveat, content_angle, format_fit, verification`

- **evidence_tier**: 1 Empirical · 2 Philosophical · 3 Opinion/creative · 4 Anecdotal/cultural (definitions in `01-brand-identity.md`).
- **credibility**: high / medium / low, with the reason (meta-analysis, single study, self-report, survey, press).
- **caveat**: the reason the idea mustn't be overstated. Read it before writing the script.
- **verification**: what has been checked and when. "canonical citation" means the reference is a standard, widely cited paper that I know well. The wording and numbers in the key finding still have to be checked against the paper before a number goes on screen. Rows marked "verified by web search 21 Oct 2026" were checked today.

## Rules
1. **No invented studies, numbers or quotations.** A number goes on screen only if the row says it was verified, and the cite card names the study.
2. **Modern books are paraphrased**, labelled "Idea: Author, Title (year) · Moodius words". Quotes come only from public-domain translations, with book and section.
3. **Never a diagnosis.** ADHD, attachment styles and alexithymia are described as patterns some people recognise. We never tell a viewer what they have.
4. **Before quoting a classic**, run `python3 ../reels-engine/tools/engine.py registry` so the account never repeats a passage.
5. **Reddit is for language, not proof.** We paraphrase, never quote usernames, and never use anything identifiable from grief or mental-health threads.

## Collecting Reddit and community language (rows C01–C04)
Reddit and Instagram are both blocked from this container, so I can't read threads directly. Two ways in:
- **Claude:** web-search snippets of public threads (e.g. "site:reddit.com r/AskMenOver30 lost touch with friends"). These give short excerpts, enough for wording but not for counts.
- **Surafel (optional, 5 min a week):** save 3–5 threads that hit hard to a text file, or paste links into the thread. I'll paraphrase them into C-rows.
- **Our own comments and DMs** are the best source of all. With consent, an anonymised line can become a hook.

## Weekly loop (Claude, automatically)
1. Pick 7 rows with an empty slot in the content tracker, spread across themes.
2. Check anything marked "to verify" with web search and update `verification`.
3. Write scripts with the format the row suggests.
4. After 7 days, add each post's sends/reach and saves/reach to the reels log. Themes that perform get more rows.
