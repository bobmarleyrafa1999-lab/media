# 04 · Deployment and monthly cost

## Deploy (about 30 minutes, once)
1. Rent a small VPS: 2 vCPU / 2 GB RAM, Ubuntu 24.04 (e.g. Hetzner CX22 or similar, about €4–6/month).
   **New spend: needs Surafel's OK.**
2. Point two DNS records at it: `agent.<domain>` and `n8n.<domain>` (the website thread owns the root domain
   and proxies `/r/*`, `/links`, `/newsletter*`, `/free/*` to this service, see `INTEGRATION-CONTRACT.md`).
3. On the server:
   ```bash
   git clone <repo> && cd media/moodius-aurelius/community-agent
   cp .env.example .env && nano .env        # fill in secrets on the server only
   docker compose up -d --build
   docker compose run --rm app npx tsx scripts/migrate.ts
   docker compose run --rm app npx tsx scripts/seed.ts     # 14 unresearched prospects + default links
   ```
4. Open `https://n8n.<domain>`, create the owner login, import `n8n/workflows/00-scheduler.json`, activate.
5. Open `https://agent.<domain>/admin`, log in with `ADMIN_PASSWORD`, check **Settings → Health**.
6. Backups: `docker compose exec db pg_dump -U moodius moodius | gzip > backup.sql.gz` nightly (cron) to
   the VPS provider's backup or object storage.

Cheaper: skip n8n (use the `worker` service in docker-compose.yml), which saves ~400 MB RAM.

## Monthly cost

| Item | Cost | Notes |
|---|---|---|
| VPS | €4–6 | runs Postgres, agent, n8n, Caddy |
| Claude API | €1–10 | see below |
| Resend email | €0 | free tier: 3,000 emails/month, 100/day; alerts + digests use ~300 |
| Domain | ~€1 | if not already owned by the website thread |
| PO box / virtual office | €0 until outreach starts, then ~£5–20 | required in outreach emails under PECR |
| n8n | €0 | self-hosted |
| **Total** | **≈ €6–17 to start** | inside the €20–25 lean budget |

**Claude per comment** (Opus 5.5, $4 input / $20 output per million tokens, system prompt cached):
about 1k fresh input + 2k cached + ~800 output tokens ≈ **$0.02 per comment**.

| Comments per day | Opus 5.5 (default) | Sonnet 5.5 | Haiku 5.5 |
|---|---|---|---|
| 5 | ~$3/month | ~$1.5 | ~$0.1 |
| 30 | ~$18/month | ~$9 | ~$0.5 |

Spam and keyword-only comments skip Claude entirely. Change `CLAUDE_MODEL` in `.env` if volume grows;
draft quality is best on Opus, so start there while volume is low.
