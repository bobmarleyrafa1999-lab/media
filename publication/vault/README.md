# Obsidian vault

Open this `vault/` folder (or the whole `publication/` folder) as a vault in Obsidian.

- `00-inbox/` new papers and feed items from `scripts/research_feed.py`, one dated checklist per run. Tick what's worth keeping, then run /research-topic or add a source row.
- `10-sources/` one note per research-library row (generated; edit `data/sources.csv`, not these notes).
- `20-ideas/` one note per backlog topic, linked to its sources (generated from `data/editorial.csv`).
- `30-drafts/` free writing and outlines. `40-published/` copies of published essays with their final URL.
- `templates/` source and idea templates.

Recommended community plugins (free): **Dataview** (query notes by `evidence_tier`, `pillar_no`, `status`) and **Obsidian Git** (commit and pull this repo from inside Obsidian). Example Dataview query for a dashboard note:

```dataview
TABLE rank, headline, score, status FROM "20-ideas" SORT number(rank) ASC LIMIT 15
```
