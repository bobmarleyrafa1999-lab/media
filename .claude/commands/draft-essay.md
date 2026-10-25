---
description: Draft a 1,200-1,800 word Substack essay from a backlog topic, with exercise, questions and sources
argument-hint: MA-007
---
Draft the essay for backlog topic **$ARGUMENTS**. Follow `moodius-aurelius/substack/CLAUDE.md` and use `moodius-aurelius/substack/essays/01-writing-to-no-one.md` as the structural template (front matter, five headline options, publish markers, editor's notes).

1. Read the topic row in `moodius-aurelius/substack/data/editorial.csv` and every linked source in `data/sources.csv`. If fewer than 4 verified sources, run /research-topic first.
2. Write: five headline options (precise paradox, unexpected noun, honest limit; no listicles), the selected title + one-sentence subtitle, a scene-first introduction, a 1,200-1,800 word body that labels every claim, one public-domain quote at most two, a worked illustration marked as such, "Try this" exercise, "Three questions for your journal", a memorable close, a mental-health signpost where the topic needs one, the subscriber invitation, and numbered sources with DOIs.
3. Voice: a perceptive friend who reads too much. No banned phrases (see `scripts/qc.py`), no "it's not X, it's Y" chains, no fake profundity, no therapy claims.
4. Save as `moodius-aurelius/substack/essays/NN-<slug>.md`, set the topic's `status` to "draft v1 (awaiting approval)" and `essay_file`, run `python3 moodius-aurelius/substack/scripts/qc.py` until it passes, then `python3 moodius-aurelius/substack/scripts/build_db.py`.
5. Add the essay row to `moodius-aurelius/substack/queue/approval-queue.csv` (status "awaiting approval"). Do not publish or schedule anything.
