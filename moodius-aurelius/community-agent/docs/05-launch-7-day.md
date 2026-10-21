# 05 · 7-day launch plan

Day 1 is the day Surafel OKs the VPS. Everything starts in **draft-only mode**; nothing is published or
emailed to anyone but Surafel in the first week.

| Day | Claude does | Surafel does (time) |
|---|---|---|
| 1 | Prepares the server commands and `.env` checklist; reviews DNS with the website thread | OK the VPS spend; rent it; add DNS records (20 min) |
| 2 | Walks through deploy, migrate, seed; checks `/api/health` | Paste secrets into `.env` on the server; `docker compose up` (30 min) |
| 3 | Answers App Review questions; writes the screencast script | Meta app, permissions, token, webhook (docs/03) (45 min) |
| 4 | Watches the first real polls; fixes anything the real API returns differently from the mocks | Open `/admin/queue` once; approve or edit 3–5 drafts (10 min) |
| 5 | Tunes the voice prompt from your edits (every edit is a signal) | Approve drafts; reply to anything escalated yourself (10 min) |
| 6 | First daily digest + theme table check | Record the App Review screencast and submit (20 min) |
| 7 | First weekly report; proposes whether DMs can go on | Decide: turn on DM keywords? (needs the newsletter page and free resources live) (5 min) |

**Exit criteria for week 1:** every comment ingested exactly once; zero replies published without your
approval; urgent emails arriving within 2 minutes; digest at 20:30; no failed jobs in Settings.

**Not before week 3:** mode B (assisted). Not before App Review passes: relying on webhooks (polling
covers it). Not before a PO box exists: any sponsor outreach.
