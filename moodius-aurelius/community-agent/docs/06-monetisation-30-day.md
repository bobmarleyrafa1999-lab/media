# 06 · 30-day monetisation experiment plan

**Starting point (measured, 20 Oct 2026 screenshots):** ~1,000 accounts reached in 30 days, 93%
non-followers, reels far ahead of feed posts, sends ≈ 0. No newsletter list yet, no revenue yet. That is
too early to sell sponsorships on reach, so the order is: **list first, attribution second, money third.**
No numbers below are forecasts; they are the thresholds that decide the next step.

One experiment changes at a time (same rule as the content tests). Every link carries `?src=` so the
revenue dashboard can say which post, DM or bio link produced each sign-up or sale.

## Week 1 · Measure only
- Agent live in draft-only mode; `/links` page in bio; all links via `/r/<slug>?src=ig_bio`.
- Baseline: comments/day, substantive share, link clicks per 1k reach, sign-ups per 1k reach.

## Week 2 · E1 Newsletter through DM keywords (path C)
- Turn on `DM_KEYWORDS_ENABLED`. One reel per day ends with "Comment JOURNAL and I'll send you the
  worksheet". The DM links to `/free/journal-worksheet`, which links to the newsletter page and its consent box
  (a comment is never treated as consent).
- **Metric:** confirmed sign-ups per keyword comment. **Keep** if ≥ 15%; **rewrite the DM** if lower.

## Week 3 · E2 Affiliate reading list (path A)
- Surafel joins one book affiliate programme (e.g. Bookshop.org UK or Amazon Associates UK) and pastes
  links into `/admin/revenue → Links` with the disclosure text. Claude adds the READ keyword to two
  carousels about the reading list.
- **Metric:** clicks per 1k reach and affiliate revenue entered weekly. **Keep** if any sale in 14 days.
- Disclosure: "#ad / affiliate link" on the post and next to the link (ASA/CAP rules).

## Week 4 · E3 First product + E4 sponsor groundwork (paths D and B)
- If the website thread has the £14 journal live: one carousel + one story sequence with
  `?src=` links; the store posts sales to `/api/integrations/revenue`. **Metric:** purchases per 100 clicks.
- Sponsors: Claude researches the 14 seeded brands (public pages only, robots.txt respected), scores them
  with evidence, drafts dossiers for those scoring ≥ 60. **No emails are sent** this month unless the
  media kit has 4 weeks of measured data and Surafel approves each one.

## Paths not started this month, and their gates
| Path | Start when |
|---|---|
| Paid Substack (C) | 1,000 free subscribers, ≥ 45% opens, 3 essays converting ≥ 5% (from the Substack plan) |
| Sponsorship outreach (B) | 4 weeks of measured reach in the media kit, PO box set up, 3+ qualified prospects |
| Membership (E) | 300+ engaged newsletter readers and a clear "what members get" that you'd keep up weekly |

## Day 30 review (Claude prepares, Surafel decides)
Revenue by stream, revenue per 1k views, sign-ups per 1k reach, best `src`, themes with the most
substantive comments. Decide which one experiment runs next month.
