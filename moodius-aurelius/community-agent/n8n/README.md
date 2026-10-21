# n8n: schedules only

n8n keeps time; the agent does the work. `workflows/00-scheduler.json` calls the agent's
`/api/cron/<job>` endpoints with `Authorization: Bearer $CRON_SECRET`:

| Job | When (Europe/Madrid) | What it does |
|---|---|---|
| process-queue | every minute | classifies new comments, drafts, emails, DMs |
| poll-comments | every 5 min | fallback for missed or not-yet-approved webhooks |
| sync-insights | 08:30 and 20:30 | reach, views, saves, shares per post |
| daily-digest | 20:30 | one email with everything that waited |
| weekly-report | Mon 08:00 | themes, conversions, sponsors, revenue |
| refresh-token | Sun 04:15 | refreshes the 60-day Instagram token |
| retention | 03:45 | deletes data past its retention period |
| sponsor-followups | 09:00 | creates follow-up tasks (never sends) |

Import: n8n → Workflows → Import from file → `00-scheduler.json` → Activate.
`AGENT_URL` and `CRON_SECRET` come from docker-compose.yml.

Don't want n8n? Run `npm run worker` (scripts/worker.ts) instead: same jobs, same times, no extra service.
If a job fails three times n8n marks the execution as failed (Executions tab); the agent itself emails
OWNER_EMAIL when a queued job dies or the token refresh fails.

The two earlier workflows in `strategy/automation/n8n/` (IG stats → Sheet, keyword DM) are superseded:
this agent does the keyword DM with consent tracking and stores the stats in Postgres.
