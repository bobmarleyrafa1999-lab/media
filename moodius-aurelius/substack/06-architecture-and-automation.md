# 6. GitHub architecture and automation

*21 October 2026. Principle: plain files in Git are the system of record; every tool around them is optional and replaceable. Zero paid dependencies. Nothing publishes on its own.*

## The flow
```
 Research in                 Editorial core (this repo)                         Out (human-approved)
 ───────────                 ─────────────────────────                          ───────────────────
 Crossref / OpenAlex ─┐      data/inbox.csv ──/research-topic──► data/sources.csv
 Substack + RSS feeds ┼─►    vault/00-inbox      (verified rows only)      │
 Surafel's links ─────┘                                                    ▼
                             data/editorial.csv ◄──/add-idea      build_db.py ─► editorial.db, 03-backlog.md, vault notes
                                    │
                             /draft-essay ─► essays/NN.md ─► qc.py ─► /verify-sources
                                    │                                       │
                             /repurpose ─► packages/NN.json ─► render_packages.py ─► engine.py check
                                    │                                       │
                                    └──────────► queue/approval-queue.csv ◄─┘
                                                         │  Surafel approves (fills approved_by)
                                                         ▼
                             export_substack.py ─► exports/<slug>/ ─► Surafel pastes into Substack
                             reels / carousels ─► Metricool queue (account thread, approved rows only)
                             metrics: Substack CSV + Metricool ─► data/metrics.csv ─► /metrics-review
```

## Repository layout (`bobmarleyrafa1999-lab/media`)
```
.claude/commands/          8 reusable Claude Code commands (deliverable 7)
.github/workflows/         research-feed.yml (weekly, opens a PR) · editorial-qc.yml (on every change)
moodius-aurelius/substack/
  CLAUDE.md                rules every Claude session follows in this folder
  01–10 *.md               the ten deliverables
  data/
    editorial.csv          backlog: source of truth (50 topics)
    sources.csv            research library: source of truth (91 rows: engine-v2's 61 + 30 new)
    feeds.csv              15 feeds watched weekly
    inbox.csv              unreviewed papers/feed items (generated)
    metrics.csv            one row per essay (filled by /metrics-review)
    imports/               Substack CSV exports dropped here by Surafel
    editorial.db           SQLite + full-text search (generated)
  essays/                  NN-slug.md with publish markers and editor's notes
  packages/                NN.json (source) → NN-slug.md (readable) + reels-batch.json
  exports/<slug>/          post.html, preview.html, meta.txt for Substack
  queue/                   approval-queue.csv, weekly plans
  reviews/                 day-30/60/90 and weekly reviews
  scripts/                 qc.py, build_db.py, research_feed.py, render_packages.py, export_substack.py
  vault/                   Obsidian vault (inbox, sources, ideas, drafts, published, templates)
moodius-aurelius/          existing Instagram system (on other branches; untouched here)
```
The reels engine, audio library and Pinterest scripts stay where they are in the project files (`reels-engine/`, `audio/`, `pinterest/`). The publication folder calls them; it doesn't copy them.

## Open-source audit (Phase 6)
Each was checked for licence and maintenance by web search on 21 Oct 2026 or is a long-established tool; "Verified" means a page was found today. Network access from this container to the APIs was blocked, so none was run live from here.

| Need | Chosen | Licence / cost | Why this one | Rejected and why |
|---|---|---|---|---|
| Academic search | **Crossref REST API** (stdlib client in `research_feed.py`) | Free, no key; polite pool with a contact email | Covers almost every DOI; zero install | Semantic Scholar (needs a key, rate-limited without), Google Scholar (no API, scraping breaks ToS) |
| Academic search, richer filters | **OpenAlex API** (optional) | Data CC0; since Feb 2026 an API key is required, with about $1/day free usage per key (lists ≈$0.10/1,000 calls, search ≈$1/1,000) ([CASRAI, Jul 2026](https://casrai.org/news/openalex-api-keys-mandatory-usage-based-pricing-2026)) | Review/type filters, citation counts; weekly run uses ~20 calls, well inside the free allowance | `pyalex` (MIT, maintained) is fine but adds a dependency for 20 lines of code |
| Feed ingestion | **stdlib RSS/Atom parser** in `research_feed.py` | Free | Every Substack has `/feed`; no server needed | Miniflux/FreshRSS (need hosting), `feedparser` (dependency, not needed) |
| Deduplication | **difflib title similarity + DOI/URL keys** | stdlib | Enough at this scale (hundreds of rows) | `rapidfuzz` (MIT, faster; switch if inbox passes ~10k rows), MinHash/`datasketch`, embeddings (cost, overkill) |
| Knowledge base | **Obsidian** + **Dataview** + **Obsidian Git** plugins | Obsidian free for personal use; plugins open source (MIT) | Markdown files in this repo stay the truth; Obsidian is just a nicer window | Obsidian Sync ($4–5/mo, unnecessary with Git), Notion (lock-in, no plain files) |
| Searchable database | **SQLite FTS5** via `build_db.py` | stdlib | One file, full-text search, opens in any SQLite viewer | Datasette (Apache-2.0, nice web UI; optional `pip install datasette` then `datasette publication/data/editorial.db`), Airtable (cost, lock-in) |
| Citation manager (optional) | **Zotero** + Better BibTeX | AGPL / MIT, free | If Surafel wants a reading app; export CSV into `sources.csv` | Mendeley (closed) |
| Markdown → Substack | **pandoc** in `export_substack.py` | GPL, free | Substack's editor ignores pasted Markdown but keeps pasted rich text ([Kaleidic, Jan 2025](https://kaleidic.substack.com/p/pasting-markdown-into-substack-cli)) | — |
| Substack drafts via API | **python-substack** (optional, later) | MIT; **unofficial**, uses undocumented endpoints, cookie or password login; v0.10.0, 7 Oct 2026 ([PyPI](https://pypi.org/p/python-substack)) | Can create *unpublished* drafts from Markdown, with publishing as a separate confirmed step | Not adopted by default: unofficial, could break or breach Substack's terms, and needs Surafel's session cookie. If used, drafts only |
| Repurposing | **reels-engine `engine.py`**, `stills_v3.py`, `pinterest/pins.py`, audio `mix.py` (our own) | ours | Already built, branded and gated | Canva autofill (connector can't create editable designs, per Phase 1 notes), CapCut (desktop only) |
| Scheduling | **Metricool** (existing, €20/mo) via the account thread | paid, existing | Already connected for Instagram/Facebook; Pinterest/Threads once connected | n8n can't post through Metricool on this plan (n8n thread, 21 Oct) |
| Analytics | **Substack CSV exports** + **Metricool connector** → `metrics.csv` | free / existing | Substack has no public analytics API; its dashboard exports subscriber and post data | Scraping Substack (fragile, ToS) |
| Automation runner | **GitHub Actions** | free tier (2,000 min/month on private repos) | The weekly feed job takes ~1 minute | n8n (useful for the Instagram stats workflow already built, not needed here) |

## Why this shape
- **Plain text wins.** Every artifact is Markdown, CSV or JSON in Git. If any tool disappears, nothing is lost.
- **Human approval is structural, not a promise.** The only path out is through `queue/approval-queue.csv` with Surafel's name in `approved_by`. The weekly GitHub job can only open a pull request into the inbox.
- **Cheap by default.** No servers, no paid APIs, no embeddings. The two optional extras (OpenAlex key, Datasette) cost nothing.

## Claude does / You do
**Claude:** runs the commands, keeps the CSVs and vault in sync, reviews the weekly research PR, writes and checks drafts and packages, exports approved essays.
**You:** approve or edit essays and packages (fill `approved_by` or just tell Claude "approved"), paste into Substack, merge or close the weekly research PR (or ask Claude to), and optionally add the `OPENALEX_API_KEY` and `CROSSREF_MAILTO` repository secrets.
