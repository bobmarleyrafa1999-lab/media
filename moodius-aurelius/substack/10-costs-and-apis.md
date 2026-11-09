# 10. Operating costs and API requirements

Target: ≈€20–25/month. Result: **€20/month**, unchanged from today, because everything new is free.

## Monthly costs
| Item | Cost | Status | Note |
|---|---|---|---|
| Metricool Starter | €20/mo | existing | Instagram, Facebook; Pinterest/Threads when connected |
| Substack | €0 | new | Free to publish. If paid subscriptions are switched on later: 10% platform fee + Stripe ≈2.9% + €0.30 per payment ([SchoolMaker, updated Sep 2026](https://schoolmaker.com/blog/substack-pricing)) |
| Claude | existing plan | existing | Drafting, research, repurposing, reviews run in this project |
| GitHub | €0 | existing | Private repo; Actions free tier (2,000 min/month); weekly job ≈1 min |
| Crossref API | €0 | new | No key; add a contact email for the polite pool |
| OpenAlex API | €0 | optional | Key required since Feb 2026; ≈$1/day free usage per key; our weekly run uses ~20 calls |
| Obsidian + Dataview + Obsidian Git | €0 | optional | Sync not needed (Git does it) |
| pandoc, Python, SQLite | €0 | — | Already installed where Claude runs |
| Kit (email) | €0 | existing | Free tier; can be retired if the list moves to Substack |
| **Total** | **€20/mo** | | |

## Optional one-offs and later costs (each needs your yes)
| Item | Cost | When it's worth it |
|---|---|---|
| Custom domain on Substack | one-time Substack fee (historically ~$50) + domain ≈€12/yr | Once the publication has ~500 subscribers and you want a brand URL |
| Canva Pro | ≈€12/mo | Only if you want to edit carousels yourself; the engine renders them for free |
| Datasette hosting | €0–5/mo | Only if you want the database as a shared website; locally it's free |
| Paid newsletter tools (beehiiv, Kit paid) | €0 now | Not needed on Substack |
| Ads to grow the list | per spend | Never without a specific approval |

## APIs and access
| Service | Access | Needed for | Status |
|---|---|---|---|
| Substack | **No official API or Claude connector** (checked the connector directory 21 Oct 2026). Unofficial `python-substack` (MIT) can create drafts with your login cookie | Publishing | Manual paste; unofficial drafts only if you ask |
| Metricool | Connected (MCP) | IG/Pinterest/Threads scheduling, analytics | Working |
| Instagram, Pinterest, Reddit, Google Trends | Blocked from Claude's container | Research | Use Metricool data, your screenshots, or a run on your Mac |
| Crossref / OpenAlex / Substack RSS | Blocked from Claude's container today; open on GitHub Actions and on your Mac | Weekly research feed | Runs via GitHub Actions |
| Google Drive / Sheets | Connected | Tracker (existing) | Optional mirror of `metrics.csv` |

## Time cost (yours)
About **25 minutes a week** on top of today's Instagram routine: 10 minutes to approve the essay (read it), 10 to paste and publish, 5 for the three Notes.
