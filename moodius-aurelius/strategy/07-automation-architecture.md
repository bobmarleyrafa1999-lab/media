# 7. Automation architecture

**Stack (Phase 1):** Claude for copy, in-repo Python renderers for design (Canva brand templates with autofill are an optional later upgrade), Metricool for scheduling and analytics, Sheets as the system of record.

## Pipeline
| Stage | Tool | Who | Status |
|---|---|---|---|
| Research | Metricool analytics + competitors, web | Claude | Live (competitors need adding) |
| Identify winners | Rank by sends/reach and saves/reach | Claude | Live from 21 Oct |
| Extract format | F1–F10 (03) | Claude | Done |
| Generate copy | Claude, from the tracker's theme + source | Claude | Live |
| Design | `stills_v2.py`, `reels_v2.py`, `make_pdf_v2.py` (guide) | Claude | Live |
| Quality check | Citation, design-rule and caption checks before scheduling | Claude | Live (checklist below) |
| Publish | Metricool, autoPublish, raw GitHub media URLs | Claude | Live (Starter plan) |
| Analyse | Weekly pull → post-log.csv, tracker Sheet | Claude + you (paste into Sheet) | Live |
| Optimise | One experiment at a time (08) | Claude | Live |
| Community | Replies, DMs, stickers, email, broadcast (11) | **You**, with Claude's drafts | Manual by platform design |

## Quality check (every post, before scheduling)
1. Quote has author, book and section in a public-domain translation, or says "Moodius paraphrase".
2. No statues, gold, marble or gradients; only the six components and the tokens.
3. Text inside the 96 px margins; stories clear the bottom 260 px.
4. Caption: hook, source, one practice, one CTA, at most 8 hashtags; first-comment question; alt text.
5. Correct UTC offset for the date.

## Costs (per month)
| Item | Cost | Status |
|---|---|---|
| Metricool Starter | €20 (or €16 billed annually) | Paid |
| Claude | your current plan | Paid |
| Rendering, GitHub hosting, Google Sheets | €0 | In use |
| Canva Pro (brand templates + autofill) | ≈ €12, estimate | Optional, needs your OK |
| Voice for F6 (your own recordings, or ElevenLabs Starter $6 / Creator $22) | €0–22 | Optional, needs your OK |
| **Running total today** | **≈ €20** | |

## Phone farm
No legitimate benefit over official APIs, schedulers and one or two real phones. Not used.

## Claude does (automatic)
Everything in the pipeline except the community row. That covers the weekly build, render, QC, scheduling, analytics pull, experiment tracking and the weekly report.

## You do (by hand)
Community actions, adding stories to highlights and stickers, pasting metrics into the Sheet, approving any spend. All of it is in `../your-checklist.md`.
