# Workflow: research → design → schedule → reply → measure (£0 a month)

Nothing here costs money. Metricool is already paid; nothing new is added.

## The weekly loop

| When | Who | What | Time for you |
|---|---|---|---|
| Friday 17:52 (existing routine) | Claude | Builds next week's 14 stories from 07-calendar.csv: renders `_auto` frames with build/templates.py, checks every fact has a source line, schedules them in Metricool (21:00 and 09:00). Puts the `_hand` versions for the week's hand-sticker nights in one folder. | 0 |
| Friday evening | You (optional) | Read the week's "Moodius take" frames. Edit anything that isn't your view. | 5 min |
| Hand-sticker nights (2-3 a week, marked in the calendar) | You (optional) | At 21:05, post the `_hand` image from your phone and add the sticker listed. Leave the scheduled 21:00 story up: the hand version is an extra, and comparing the two is test X11. | 1 min |
| Daily, any time | You | Answer replies with the response bank. Heart the one-word ones. | 5-10 min |
| 09:05 after a question-box night (S06, S11) | You | Share 3-5 real question-box answers with the share button. Never invent them. | 3 min |
| Sunday | You | Fill the tracker from the app (Archive → story → swipe up). | 10 min |
| 19 Nov review, then monthly | Claude | Reads the tracker, calls the A/B tests, updates the calendar. | 0 |

## Why stickers are by hand

Instagram's API, which every scheduler uses, can post a story image or video but cannot add any sticker: poll, quiz, slider, question box, Add Yours or link. That's Meta's rule, not Metricool's. So:

- **Scheduled (automatic):** the `_auto` image asks for a typed reply ("Reply A or B"). Replies arrive as DMs, which Instagram counts as a closeness signal.
- **By hand (optional, ~1 min):** the `_hand` image with the real sticker. Easier to answer (one tap), and you see the results in the app.

The A/B plan finds out whether the extra minute is worth it.

## Tools and repositories (checked 25 Oct 2026)

Checked for: last activity, licence, dependencies, known vulnerabilities (PyPI's advisory feed), and whether it needs your Instagram password. Nothing was installed or run except Pillow and Playwright, which were already in use. GitHub's API is blocked from this workspace, so activity was checked by cloning the history.

| Tool | What it would do | Last activity | Licence | Needs IG password? | Verdict |
|---|---|---|---|---|---|
| **Metricool** (already paid) | Schedules `_auto` stories via Meta's official API | n/a | commercial | No (official login) | 🟢 Keep. Story analytics come back empty for us; don't rely on it for stories. |
| **Meta Business Suite** (free, official) | Backup scheduler, and a second place to see story insights | n/a | Meta terms | No | 🟢 Backup only. |
| **Pillow** (python-pillow) | Renders every template in this folder | release 16 Oct 2026 | MIT-CMU | No | 🟢 In use. 0 known advisories for the current version on PyPI. |
| **Playwright** (Microsoft) | Optional: turn HTML templates into images | release 22 Oct 2026 | Apache-2.0 | No | 🟢 Already installed; only needed if templates move to HTML. |
| **facebook-python-business-sdk** (Meta, official) | Read story insights through the Graph API | last commit 17 Sep 2026 | Meta platform licence | No (uses a page token) | 🟢 For the optional insights job. Plain HTTPS calls work too, without the SDK. |
| **Datasette + sqlite-utils** (Simon Willison) | Optional browsable view of the tracker | releases Sep 2026 / Aug 2026; active daily | Apache-2.0 | No | 🟢 Optional. growth-system/analytics.py already writes SQLite. |
| **vercel/satori** | HTML/CSS → image for templates | commits to 20 Oct 2026 | MPL-2.0 | No | 🟠 Not needed. Would add Node.js for what Pillow already does. |
| **Canva** (connector available) | Hand-editing templates | n/a | Canva terms | No | 🟠 Optional. The palette and fonts can be set up there if you prefer dragging to code; free plan is enough. |
| **subzeroid/instagrapi** | Could post stories *with stickers* | very active (25 Oct 2026) | MIT | **Yes: logs in with your username and password to Instagram's private mobile API** | 🔴 No. Against Instagram's terms, a real risk of the account being locked, and it would hold your password in a script. The one tool that "solves" stickers is the one we must not use. |
| **instaloader** | Downloads posts/stories, scrapes accounts | active (24 Oct 2026) | MIT | Yes, for stories | 🔴 No. Scraping; breaks Instagram's terms. |
| Already decided elsewhere | Postiz 🔴, Outline 🔴, n8n 🟠 (parked), Langfuse 🟠, hook-intel 🟢, vyralcontent/content-skills 🟢 checklist | | | | See project memory; not re-audited. |

## Optional, free: automatic story insights (yes/no)

Story numbers disappear from the API after 24 hours. A small GitHub Actions job (free on this repo's plan) could call Meta's official API every 6 hours, save each live story's reach, taps, exits, shares, follows and profile visits into the tracker CSV, and commit it. It would use the same page token the comment agent is waiting for, no password. **Replies would still read 0** (Meta excludes Europe), so you'd still count replies by hand. Say yes and I'll build it; say no and the Sunday 10-minute manual fill is the system.

## Safety rules (unchanged)

- No bots for likes, follows, comments or DMs. No follow/unfollow. No engagement pods.
- No auto-replies to DMs (comment agent stays draft-only, DMs off).
- No faces in automated stories. Add Yours: photo of an object or a page, never a person.
- Facts carry their source on the card; quotes are paraphrases labelled as such unless already verified against Standard Ebooks.
