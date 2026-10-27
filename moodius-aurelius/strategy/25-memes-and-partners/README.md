# Memes, warmth and advertiser-readiness (27 Oct 2026)

Brief: more humour, warmth and curiosity; intelligent memes people send to friends; a page suitable advertisers would trust; every commercial decision stays with the owner.

**Data used.** Metricool, brand 7224060, pulled 27 Oct 2026: every feed post and reel 6–26 Oct, daily account evolution 28 Sep–26 Oct, country and age/gender breakdown. Earlier project findings (22 Oct clear-out, 25 Oct reach batch, 27 Oct anti-bot audit).
**Not inspected.** Instagram itself is blocked from this container, so the live profile, current bio, the four new highlights' contents, comments and DMs were not seen. Profile visits and unfollows aren't returned by the API for this account. Nothing below pretends otherwise.

| File | What it is |
|---|---|
| [README.md](README.md) | The nine deliverables, short |
| [01-page-changes.md](01-page-changes.md) | Five changes, three bios, highlights, pins, enquiries line |
| [02-memes.md](02-memes.md) | Meme style rules + the 20 concepts (renders in `renders/`) |
| [03-sources-and-process.md](03-sources-and-process.md) | Source shortlist, tool verdicts, cheapest workflow, costs |
| [04-calendar-14-day.csv](04-calendar-14-day.csv) | Two-week sample calendar (23 Nov–6 Dec) |
| [05-revenue-and-media-kit.md](05-revenue-and-media-kit.md) | Two revenue routes, disclosure rules, media-kit outline |
| [06-measurement-plan.md](06-measurement-plan.md) | 30-day experiment, metrics, decision rules |
| [07-approval-cards.md](07-approval-cards.md) | Commercial approval card template + two filled examples |
| [08-next-30-days.md](08-next-30-days.md) | Monetisation readiness: gates, week-by-week plan, yes/no list |
| `data/queue.csv`, `data/commercial.csv` | The approval tracker (also on the tap-to-approve page) |
| `tools/meme_queue.py` | Queue: import links, dedupe, filter, reuse gate, render, learn |
| `highlights/text-cards/` | Live covers for Reading Room and Training Room (dark text cards matching Zeno and Resilience) |

## The answers in one screen

**1. Five changes, in order**
1. Add a meme lane: 3–4 of the 8 weekly feed slots, as 2-slide carousels, from Mon 23 Nov.
2. New bio + a business email button (hello@moodius.co.uk). No personal details anywhere.
3. Fill your four new highlights with a clear job each; covers are ready.
4. Pin the self-trust carousel, the 2am replay carousel, and the first meme that beats the median.
5. Commercial guardrails before any money: employer OBI declaration, disclosure rules, approval cards.

**2. Three bios** are in [01-page-changes.md](01-page-changes.md). Recommended: B1.

**3. Meme sources (verified).** Discovery = your own Instagram "Saved" folder + links you send (inspiration only). Reuse = written permission from the creator, never attribution alone. Assets = our own Pillow drawings, Openverse CC0/PDM, The Met CC0, Pexels (no people). Details and checks in [03](03-sources-and-process.md).

**4. Cheapest workflow.** Save links on your phone → paste them in chat once a week → Claude dedupes, filters, writes original jokes from the inspiration-only ones and renders drafts → you tap Approve / Edit / Reject on one page → account thread schedules. £0. About 15 min a week for you.

**5. Twenty original memes** are in [02-memes.md](02-memes.md) and `renders/MM01.png`…`MP07.png`. All original, so all are cleared to post once you approve.

**6. Two-week calendar**: [04-calendar-14-day.csv](04-calendar-14-day.csv). It works around the five Mino reels already scheduled for 24–29 Nov.

**7. Approval tracker**: the tap-to-approve page, backed by `data/queue.csv` and `data/commercial.csv`.

**8. Revenue routes**: (1) your own journal + free guide + newsletter, (2) Bookshop.org UK affiliate links on book recommendations. Sponsorships wait for 1,000 real followers. Media-kit outline uses only Metricool numbers with dates.

**9. Measurement**: 30 days, 23 Nov–22 Dec. Main metric: shares + saves per 1,000 reach, at day 7, medians not averages, outliers reported separately.

## Tools (verified 27 Oct 2026)

| Tool | Verdict | Why |
|---|---|---|
| Pillow 12.3.0 | 🟢 use | MIT-CMU licence. 12.2.0+ fixes CVE-2026-42309 (heap overflow). 13.0.0 is 11 days old, so wait. Already used across the repo. |
| instaloader 4.16 | 🔴 skip | MIT, maintained (released 26 Oct). Needs an Instagram login for reliable use, Instagram blocks datacenter IPs, its endpoints change every few weeks, and it downloads media we have no right to repost. |
| gallery-dl 1.32.18 | 🔴 skip | GPL-2.0, maintained (released 25 Oct). Same login and rights problems for Instagram. Reddit's API needs approval for commercial use. Our footage workflow already fetches licensed assets. |
| Meta Hashtag Search API | 🔴 skip | App Review, 30 hashtags per 7 days, returns media IDs with no reuse rights. |

## How decisions flow back

Taps on the Meme Desk page are saved in the page's own database (collection `decisions`, one document per meme or card). Claude reads them, runs `meme_queue.py decide …` so `data/queue.csv` and `data/commercial.csv` match, then hands approved memes to the account thread for the meme slots. Rebuild the page with `python3 tools/build_page.py`.

Tests: `python3 -m unittest discover -s tests` (17 tests: dedupe, reuse gates, filters, copy detection, learning can't loosen rules, every concept renders).
