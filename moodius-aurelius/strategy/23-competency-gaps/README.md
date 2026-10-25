# Competency gaps and the repos that help (25 Oct 2026)

Scope: the @moodiusaurelius page and the system behind it (reels-engine, growth-system, community-agent, hook-intel, strategy/). Data: Metricool brand 7224060 evolution metrics 1-25 Oct, growth-system real-data weekly.md, performance lessons (strategy/16), reach batch (strategy/19), 90-day plan (strategy/22-90-day-plan). Nothing installed, nothing scheduled, no spend.

Files: `gaps.csv` (16 gaps), `repos.csv` (13 repos checked), `decisions.md` (yes/no items).

## The short version

The page's biggest gaps are not tools. Reels look like carousels in motion and get a fixed ~116 reach each, the format that grows (carousels) has no automatic quote check, the comment agent is waiting on secrets, and decisions are backed up. Repos help three gaps properly (visual library, quote checking, leak checks), shrink two (motion for history posts, hook lint) and do nothing for five (story-reply data, replying to people, stickers, pillar mix, owner time).

## Fresh numbers (Metricool, 1-25 Oct)

| Day | Account reach | Feed-post reach | Reel reach | Followers |
|---|---|---|---|---|
| 21 Oct | 2,141 | 342 | 190 | 14 |
| 22 Oct | 5,734 | 585 | 127 | 51 |
| 23 Oct | 2,398 | 473 | 163 | 57 |
| 24 Oct | 804 | 6 | 127 | 59 |

Average reach per reel over the month: 116. Daily reel reach since 6 Oct sits between 32 and 190 in Metricool (single reels peaked at 211 in the 22 Oct lessons). Story metrics read 0 (scheduled stories start 26 Oct). Followers gained/lost return empty from the API.

## Gaps by severity

### High
- **G01 Reels plateau.** Fix with G02 visuals plus the X5/X6 hook tests; keep the carousel-led week until the 19 Nov review. Repos shrink it, none fix distribution.
- **G02 No footage library.** `reels-engine/footage/` is empty though the engine has supported backgrounds since 1.2. Repos: Met Open Access (CC0) and Openverse (filter CC0/PDM), run from GitHub Actions because museum APIs are blocked from the cloud container. Filter out portraits and statues (no-faces and no-statues rules).
- **G04 Quote check skips carousels.** `19-reach-batch/build/carousels.py` prints Legge and Long quotes and calls no checker. Three separate checkers exist. Repo: RapidFuzz, to merge them into one checker that also shows the closest true sentence.
- **G05 Repo anonymity.** Going private is the fix. Gitleaks on every push stops new leaks (identifiers kept in a repo secret, so the rule doesn't leak them). git-filter-repo only if the repo stays public, and only with an explicit OK because it rewrites every branch.
- **G06 Comment agent not live.** Five secrets. No repo.
- **G15 Owner time and backlog.** No repo.

### Medium
- **G03 Motion for history posts.** Manim (MIT) for one timeline/map test reel. Amber.
- **G07 Replying to people.** No repo.
- **G08 Story replies / profile visits.** API limit in Europe; every tool that reads them needs an Instagram login, rejected. Sunday 2-minute count.
- **G09 Reach doesn't reconcile.** Merge analytics.py (PR #12), yes to the weekly pull. No new repo.
- **G10 One pillar.** Owner's yes/no. No repo.
- **G11 Hook second line.** textstat in brief_lint. Small help.

### Low
- **G12 Voice**: Kokoro amber, not now. Piper red.
- **G13 Captions**: only if voice; Whisper verdict stands.
- **G14 Stickers**: hand-post only.
- **G16 Blocked research sources**: Actions route already exists.

## Already judged (not re-audited)
Remotion amber, MoviePy red, Whisper amber Mac-only, Ollama amber, Zotero green, Langfuse amber, Postiz red, Outline red, n8n amber, plus the creator-repo, hook-intel and Mino Lee verdicts.

## Rules applied
Rejected anything that needs Instagram credentials. Stars were not treated as a security audit. Licence and last commit read from each repo's default branch on 25 Oct 2026.
