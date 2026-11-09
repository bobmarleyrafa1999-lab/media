# 7. Automation architecture

## The pipeline, and what's automated today
| Stage | How | Tool | Status |
|---|---|---|---|
| 1 Research | Weekly pull of own analytics + competitor top posts | Metricool (IGCO/IGCR metrics), web search | Own data: **live**. Competitors: **blocked until you add them in Metricool** |
| 2 Identify winners | Rank last week's posts by the primary metric per format (see `08`) | Claude routine + `post-log.csv` | **To build** (the routine ranks informally today) |
| 3 Extract format | Map each winner to an F-code, note the hook type | `03-format-library.md` | Library done |
| 4 Generate | Claude writes JSON specs (reels.json / stills.json) + caption, first comment, alt text, from format + quote bank | Weekly routine (Fri 17:52) | **Live** |
| 5 Design | Render JPG/MP4 from specs. Canva for hand-made hero posts | `tools/stills.py`, `render_reels.py`, `score.py` | **Live** |
| 6 Quality check | Automatic checks below, plus your spot check of 3 posts a week | `tools/qc.py` | **To build** (spec below) |
| 7 Publish | Commit media to the repo, schedule in Metricool with autoPublish, raw.githubusercontent.com URLs | Metricool Starter | **Live** |
| 8 Analyse | Daily publish check (20:40), weekly analytics pull | Metricool + routines | **Live** |
| 9 Optimise | Update experiment results and format weights; feed into next week's mix | `experiments.csv` | **To build** |

## Quality-check gate (`qc.py`, runs before scheduling; any fail blocks that post)
1. Every quote has author + work + section, or "(paraphrase)".
2. Citation not in any earlier manifest (week*/*.json, strategy/first-five).
3. No line wider than 900px; reel 15–22s (F7 up to 35s); stills exactly 1080×1350 or 1080×1920.
4. Caption ≤ 2,200 characters, ≤ 8 hashtags, has a CTA and a question.
5. First comment present and different from every earlier one.
6. Alt text present.
7. Timestamp offset correct for the date (+02:00 / +01:00).
8. Banned phrases: "studies show", "science proves", "guaranteed", "cure".

## Change the weekly routine needs (Conflict 3 in the audit)
Replace in `research/weekly-routine-prompt-3-a-day.md` step 4:
> ~~Favour list and contrast formats ("3 Stoic rules for...", "5 things you can't control").~~
> Reels use confrontational "you" hooks naming a relationship, insult or excuse (our best 3-second holds, 44–48%). Lists go only in carousels (Tue, Thu, Sun 15:00/18:00 per strategy/06-30-day-calendar.md). Follow the format codes in strategy/03-format-library.md and the accuracy rule in strategy/06-30-day-calendar.md.

## Two stacks
Prices checked where marked ✓ (source and date in brackets); the rest are estimates to confirm at checkout. No spend happens without your OK.

### Lean stack (now, one brand): about €20 a month
| Need | Tool | Cost/month |
|---|---|---|
| Scheduling + analytics + competitor tracking | Metricool Starter (what you just bought) | €20 (from €16 ✓ upload-post.com, 17 Sep) |
| Writing, specs, routines | Claude (your current plan) | already paid |
| Rendering | Python tools in the repo | €0 |
| Media hosting | GitHub repo (raw URLs) | €0 |
| Dashboard | Google Sheets, imported from `post-log.csv` | €0 |
| Voice | Your own phone recordings | €0 |
| Email capture | Kit or Stan Store free tier | €0 |
| **Total** | | **≈ €20** |
Quality cost: none for current formats. The gap is voice: text-only reels for now.

### Recommended stack (once the Phase 0 gate is hit): about €45–75 a month
| Add | Why | Cost/month |
|---|---|---|
| ElevenLabs Starter or Creator | Licensed narration for F7 story reels and YouTube Shorts | $6 or $22 ✓ (eesel.ai, 2026). Starter includes a commercial licence |
| Canva Pro | Brand Kit, brand templates, Connect API autofill for hero posts | ≈ €12 (estimate) |
| Make.com (or keep routines) | Glue for sheets ↔ Metricool if routines aren't enough | ≈ €10 (estimate), optional |
| Metricool Starter, 10 brands | When brand 2 starts | €29 ✓ |
| Object storage (Cloudflare R2 or S3) | Replace GitHub raw URLs at volume | < €2 (estimate) |

### Scale stack (10–20 brands)
| Need | Option A (managed) | Option B (direct APIs) |
|---|---|---|
| Publishing | Metricool Advanced, €69 for 25 brands ✓, includes the Metricool API | Instagram Graph API: free, 100 API posts per account per 24h, carousels up to 20 items, JPEG only, needs a professional account linked to a Page ✓ (Meta docs) |
| YouTube | Metricool | YouTube Data API (free quota) |
| TikTok | Metricool | Content Posting API. TikTok requires an app audit before posts can be public (developer docs; confirm when applying) |
| Data | Google Sheets → Postgres (Supabase free tier) | same |
| Assets | Canva Teams brand templates per brand | Python renderer with a per-brand config |

## Data model (one row per published asset)
`post-log.csv`: post_id, brand, date, slot, platform, type, format_code, pillar, hook_type, hook_text, caption_len, cta_type, slides, visual_style, experiment_id, arm, views, reach, hold_3s_pct, avg_watch_s, duration_s, likes, comments, saves, shares, follows, profile_visits.

## Your hands-on time (what APIs can't do)
| Task | Time |
|---|---|
| Reply to comments (playbook) | 10 min/day |
| Add stories to highlights; question stickers on Feel Logs | 3 min/day |
| Spot-check 3 scheduled posts | 5 min/week |
| Approve any spend | as needed |
