# 07 · Who does what

## Claude does (automatically, once deployed)
- Reads every comment (webhook + 5-minute poll), classifies it, drafts a reply, routes risky ones to you.
- Emails you: urgent alerts at once, substantive comments at once (max 12/hour), the rest at 20:30, weekly report Monday 08:00.
- Sends the one keyword DM per comment (only after you switch DMs on).
- Refreshes the Instagram token, syncs post insights twice a day, deletes old data on schedule.
- Researches sponsor prospects from public pages, scores them with evidence, drafts dossiers and emails.
- Tracks clicks, sign-ups and purchases by source; builds the dashboard and media kit from measured data only.

## Surafel does by hand
**Once (≈ 2 hours in total, spread over week 1):**
- OK the VPS (€4–6/month) and rent it; DNS records.
- Fill `.env` on the server (secrets never go in chat or the project folder).
- Meta app, permissions, token, webhook, App Review screencast (docs/03).
- Resend account + verify the sending domain (SPF/DKIM/DMARC).
- Before any outreach: a PO box or virtual office address (keeps the brand anonymous, required by PECR).
- Add to the privacy notice: "Comments on our Instagram posts are processed with an AI service to draft
  replies; a person approves replies; comment data is deleted after 12 months."

**Daily (5–10 minutes):** open the email alerts; approve, edit or reject drafts in `/admin/queue`;
answer anything marked URGENT yourself (crisis comments: reply personally, point to Samaritans 116 123).

**Weekly (10 minutes):** read the Monday report; approve or skip sponsor drafts; enter any affiliate
revenue the networks don't report automatically.

## Decisions only Surafel can make
VPS spend · switching reply mode from draft-only · turning DMs on · every outreach email · prices.
