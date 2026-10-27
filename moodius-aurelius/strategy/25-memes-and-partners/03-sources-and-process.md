# Meme sources, tools and the cheapest workflow

Checked 27 Oct 2026. Where something could not be checked from here, it says so.

## Discovery is not permission

Every find gets one of four reuse statuses, and the queue enforces them:

| Status | Meaning | What we may post |
|---|---|---|
| `original` | Our own joke and our own or CC0/licensed image | It, after your approval |
| `authorised` | Written permission saved (DM screenshot, email, licence URL) that covers commercial use **and** edits, creator named, watermark kept | It, credited, after your approval |
| `permission-needed` | We'd like to repost but have nothing in writing | Nothing yet. You decide whether to ask (asking is outreach, so it needs your OK each time) |
| `inspiration-only` | Anything else we found | Only a genuinely new joke written by us. The queue measures text similarity and blocks anything at 0.6 or above, so a caption copied onto a new background can't pass |

For each find we keep: original URL, creator, platform, date found, any reuse terms shown, and where the permission is written.

## Verified source shortlist

**For ideas (inspiration only)**
1. **Your Instagram "Saved" folder.** Make a collection called "Moodius ideas" and save anything that makes you laugh. Free, no login shared, no scraping. Strongest signal of your taste.
2. **Links you send in chat** from anywhere you browse (Instagram, Reddit, X, newsletters). Same status: inspiration only.
3. **Our own data.** The best-performing themes (the 2am replay, rude people, procrastination) are already proven topics. Six of the 20 concepts come straight from them.

**For reuse (needs the status above)**
4. **Creator permission, case by case.** A short DM asking to repost with credit, for commercial use, unedited apart from size, watermark kept. Each DM is outreach, so it waits for your OK on that creator. Reply rate unknown; we'll log it.
5. **Instagram Collab posts** later (both accounts post it). Only after a relationship exists, per the 90-day plan (days 61–90).
6. **Creator submissions** later (at about 1,000 followers): a DM keyword and a short licence text they agree to. Not worth setting up for 146 followers.

**For images inside our own memes**
7. **Pillow drawings** (charts, flowcharts, Venn, type). No licence risk. 20 of 20 concepts work this way.
8. **Openverse** with the CC0/Public Domain filter, **The Met Open Access** (CC0), **Pexels** (free licence, commercial use allowed; we only use clips and photos with no people). Already verified in the 25 Oct gap analysis and used by the footage workflow.

Checked and rejected for discovery:
- **Instagram Hashtag Search API**: App Review needed, 30 hashtags per rolling 7 days, returns media IDs, says nothing about reuse rights ([Meta docs](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-facebook-login/hashtag-search)).
- **Reddit API**: free tier is non-commercial; commercial use needs Reddit's written approval, and new self-service API keys are closed (third-party summary, [xpoz.ai](https://www.xpoz.ai/blog/guides/reddit-api-pricing-tiers-and-alternatives/); Reddit itself is blocked from this container, so not confirmed first-hand). Reddit stays a place you browse by hand.
- **Reposting in general**: Instagram has ranked original content above reposts since 2022 and strengthened it in 2024 ([Tubefilter](https://www.tubefilter.com/2022/04/21/instagram-adam-mosseri-algorithm-change-original-content/), [Gigazine](https://www.gigazine.net/gsc_news/en/20240502-instagram-updated-algorithm-prioritizes-original-content)), and a high share of reposted content can block Creator Marketplace eligibility ([inro.social](https://www.inro.social/blog/instagram-creator-marketplace)). Originals are also the route to advertisers.

## The three repositories

| | instaloader | gallery-dl | Pillow |
|---|---|---|---|
| Latest stable | 4.16, 26 Oct 2026 | 1.32.18, 25 Oct 2026 | 13.0.0, 16 Oct 2026 (12.3.0 before it) |
| Licence | MIT | GPL-2.0-only | MIT-CMU |
| Dependencies | requests (+ browser_cookie3 optional) | requests (+ yt-dlp optional) | none required |
| Advisories found | none found | none confirmed (a CVE search turned up nothing specific) | CVE-2026-42309 heap overflow, fixed in 12.2.0 |
| Verdict | 🔴 don't install | 🔴 don't install | 🟢 use, pinned to 12.3.0 |

Why no to the collectors: Instagram blocks datacenter IPs (this container and GitHub Actions both are), reliable collection needs an Instagram login or session cookies (we never hold those), Instagram's internal endpoints rotate every 2–4 weeks ([socialcrawl.dev](https://www.socialcrawl.dev/blog/instagram-scraping-2026.md)), Instagram's terms forbid automated collection without permission, and what they download is mostly inspiration-only anyway. A fragile scraper would save no posting time and adds account risk to an anonymous page. Both releases are also under two weeks old.

Pillow install, isolated, only if it isn't already on a machine:
```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # pillow==12.3.0
```

## The workflow

Discover → Remove duplicates → Review humour and context → Check reuse status → Prepare draft → Your approval → Schedule → Measure

| Step | Who | How | Time |
|---|---|---|---|
| Discover | You | Save to "Moodius ideas" while scrolling. Once a week, paste the links in chat, one per line (optional: `link \| creator \| note`) | 5 min/week |
| Dedupe | Tool | Same post saved twice (any link form) or near-identical caption is dropped | 0 |
| Review | Claude | Describes image + context, scores, flags excluded topics, writes the concern | 0 for you |
| Reuse check | Tool + Claude | Sets status; blocks anything not `original` or properly `authorised` | 0 |
| Draft | Claude | Writes original jokes from inspiration-only finds, renders 1080×1350 in the house style | 0 |
| Approve | You | One page, tap Approve / Edit / Reject per meme or for a whole batch | 10 min/week |
| Schedule | Account thread | Only approved items, into the meme slots | 0 |
| Measure | Friday report | Shares + saves per 1,000 reach at day 7, vs baseline | 0 |

Learning: the tool counts your approvals and reject reasons per theme and nudges review order (themes you reject drop down the list, never below 0.7×). The exclusion list, reuse gates and flags are fixed in code and tests check they can't loosen.

## Cost per usable meme

| Route | Money | Setup | Upkeep | Review of junk | Usable posts |
|---|---|---|---|---|---|
| **Saved links + original drafts (chosen)** | £0 | done | ~15 min/week of yours | low: Claude pre-filters | 4 a week is easy; 20 already drafted |
| Scraper (instaloader/gallery-dl) | £0 software, plus paid residential proxies to work at all | hours, plus your IG login (refused) | breaks every few weeks | high | few: most finds can't be reposted |
| Meta Hashtag API | £0 | Meta app + App Review | low | high | few, no rights info |
| Permission reposts | £0 | none | ~10 min per creator + waiting | medium | unknown until we try |
| Paid meme tools | monthly fee | low | low | medium | no measured gain; not recommended. We'll ask before any spend |
