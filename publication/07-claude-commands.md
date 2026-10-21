# 7. Reusable Claude Code commands

Saved in the repo at `.claude/commands/`, so they appear as slash commands in any Claude Code session on `bobmarleyrafa1999-lab/media`. Each one follows `publication/CLAUDE.md` (no publishing without approval, no invented sources, evidence labels).

| Command | Argument | What it does | Ends with |
|---|---|---|---|
| `/add-idea` | "headline" [pillar] | Adds a scored, de-duplicated topic to `data/editorial.csv` | New rank |
| `/research-topic` | MA-xxx or topic | Finds reviews/meta-analyses and primary texts, logs each with tier, caveat and what was actually opened | New `sources.csv` rows |
| `/draft-essay` | MA-xxx | Writes the 1,200–1,800 word essay to the house template, runs `qc.py` | Essay in the approval queue |
| `/verify-sources` | essay path | Checks every study, number and quote against the source, fixes the text, logs it | Dated verification log |
| `/repurpose` | essay path | Builds reels, carousel, cards, stories, pins, Notes; runs the reels engine check | Package in the approval queue |
| `/export-substack` | essay path | Approved essays only: QC, HTML export, paste checklist | `exports/<slug>/` |
| `/weekly-plan` | — | Next week's essay and distribution from calendar + metrics | `queue/week-<date>.md` |
| `/metrics-review` | weekly / day30 / day60 / day90 | Substack CSVs + Metricool → `metrics.csv`, re-scores pillars on evidence | `reviews/<date>.md` |

**Typical week:** Monday `/weekly-plan` → `/research-topic MA-005` → `/draft-essay MA-005` → `/verify-sources` → `/repurpose` → Surafel approves → Thursday `/export-substack` → Sunday `/metrics-review weekly`.

In this project you don't need to type the commands: asking "draft MA-005" in a thread does the same steps.
