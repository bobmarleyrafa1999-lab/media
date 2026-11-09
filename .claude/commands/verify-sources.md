---
description: Fact-check every citation, number and quote in an essay before approval
argument-hint: moodius-aurelius/substack/essays/NN-slug.md
---
Fact-check **$ARGUMENTS**. Follow `moodius-aurelius/substack/CLAUDE.md`.

For every claim inside `<!-- publish:start -->…<!-- publish:end -->`:
1. **Studies:** open the abstract/DOI. Check authors, year, journal, volume/pages, sample, and that the sentence in the essay doesn't overstate the finding (correlation vs cause, lab vs life, effect size words).
2. **Numbers:** each must appear in the source exactly. Rounding must be stated.
3. **Quotes:** only public-domain translations (Long, Gummere, Stewart, Ross, Trotter…). Match wording and section number against an online copy of that translation. Modern authors in copyright: paraphrase only, labelled "Idea:".
4. **Labels:** every claim carries the right evidence label. Jung/shadow = interpretive framework, never treatment.
5. **Examples:** any scenario must be marked as an illustration. No invented personal or client anecdotes.

Then update the essay's "Editor's notes" with a dated verification log (verified / corrected / still open), fix what's wrong in the text, run `python3 moodius-aurelius/substack/scripts/qc.py $ARGUMENTS`, and list anything Surafel needs to decide.
