# Moodius Aurelius: Substack publication system

*Built 21 Oct 2026 from Surafel's master brief. Everything here is a draft or a plan. Nothing has been published or scheduled.*

Moodius Aurelius becomes a research-led Substack publication on psychology, philosophy and the inner life. Instagram, Stories and Pinterest are distribution; this repo and Obsidian are the archive.

| # | Deliverable | Where |
|---|---|---|
| 1 | Brand editorial strategy | `01-editorial-strategy.md` |
| 2 | Competitor and topic research (30 publications) | `02-market-research.md` |
| 3 | Ranked 50-article backlog + searchable database | `03-backlog.md`, `data/editorial.csv`, `data/sources.csv` (91 sources), `data/editorial.db` |
| 4 | Four complete essay drafts | `essays/01–04`, Substack-ready HTML in `exports/` |
| 5 | Cross-platform packages | `packages/01–04-*.md`, 8 rendered reels in project files `substack/renders/` |
| 6 | GitHub architecture + automation audit | `06-architecture-and-automation.md`, `scripts/`, `.github/workflows/` |
| 7 | Reusable Claude Code commands | `07-claude-commands.md`, `.claude/commands/` |
| 8 | 90-day calendar | `08-calendar-90-day.md` + `.csv` |
| 9 | Setup instructions | `09-setup.md` |
| 10 | Costs and APIs | `10-costs-and-apis.md` |
| — | Ghost vs Substack evaluation | `11-ghost-vs-substack.md` |
| — | Your twelve selected essays (weeks 5–16) | `12-selected-essays.md` |
| — | Approval queue (164 items) | `queue/approval-queue.csv` |

## Quick commands
```
python3 scripts/qc.py                  # check essays
python3 scripts/build_db.py            # rebuild database, backlog, vault notes
python3 scripts/build_db.py search shame
python3 scripts/render_packages.py     # packages/NN.json -> readable packages + reels batch + queue
python3 scripts/export_substack.py essays/01-writing-to-no-one.md
python3 scripts/research_feed.py weekly   # needs network (GitHub Actions or your Mac)
```

## Claude does / You do
**Claude, automatically:** research, verification, drafting, packaging, rendering, exports, the approval queue, Instagram/Pinterest scheduling of *approved* items through the account thread, weekly and 30/60/90-day reviews.

**You, by hand:**
1. Read and approve (or edit) essays 01–04 and their packages. Start with 01 and 03.
2. Create the Substack publication (`09-setup.md` §1–2, ~30 minutes).
3. Decide whether to move the Kit list to Substack (recommended).
4. Each Thursday: paste and publish (~10 minutes). Post three Notes a week.
5. Optional: Google Trends screenshots (`02-market-research.md`, end), Obsidian, GitHub secrets.
