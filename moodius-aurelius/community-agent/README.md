# Moodius Aurelius · community & revenue agent

Comment agent, newsletter sign-up, link-in-bio, sponsorship CRM and revenue dashboard for
@moodiusaurelius. One Next.js service + Postgres; n8n (or `npm run worker`) keeps the schedule.

**Status (21 Oct 2026):** built and tested on mock data. **Not connected to anything real yet:** there are no
Instagram, Claude, Resend or store credentials in this project. Nothing has been posted, DMed or emailed.

| Tested | How |
|---|---|
| Webhook signature, handshake, parsing, dedupe | unit tests + curl against the production build |
| Classifier rules, draft veto, repetition, policy caps | unit tests (heuristic classifier; the Claude path is typed but untested without a key) |
| Draft-only flow, escalation, urgent email, digest | end-to-end tests on real Postgres with mock Graph API |
| One reply / one DM per comment | tests |
| Newsletter double opt-in, unsubscribe, erase | tests |
| Sponsor research (fixture site), scoring, stages, PECR blocks, opt-out | tests |
| Revenue webhook signature, dedupe, refunds, Sellf mapping | tests |
| Admin login, all admin pages render | curl smoke test |

## Run locally
```bash
npm install
createdb moodius && export DATABASE_URL=postgres://localhost/moodius
npm run migrate && npm run seed
npm run demo          # mock comments through the whole pipeline, prints what happened
ADMIN_PASSWORD=change-me-please npm run dev   # http://localhost:3000/admin
npm test              # needs a moodius_test database (TEST_DATABASE_URL)
```

## Layout
```
app/                 pages (/links, /newsletter, /free, /admin/*) and API routes
src/lib/             all logic (see docs/02-architecture.md)
db/migrations/       SQL schema
n8n/workflows/       schedule (import into n8n)
scripts/             migrate, seed, demo, worker
tests/               vitest suites + MIT fixtures from devgine
deploy/Caddyfile     HTTPS
docs/                01 repo audit · 02 architecture · 03 Meta setup · 04 deploy & costs ·
                     05 7-day launch · 06 30-day monetisation · 07 who does what ·
                     08 free setup (GitHub Actions, no server)
```

Integration with the website/store: `INTEGRATION-CONTRACT.md`.

## The 14 deliverables
1 repo structure (above) · 2 webhook handler `app/api/webhooks/instagram` · 3 classifier + generator
`src/lib/classifier.ts` · 4 n8n `n8n/workflows` · 5 email + digest `src/lib/email` · 6 sponsorship CRM
`src/lib/sponsors`, `/admin/sponsors` · 7 email drafting `sponsors/drafting.ts` · 8 newsletter conversion
tracking `newsletter.ts`, `tracking.ts`, `/r/` · 9 dashboard `/admin` · 10 tests, `.env.example`,
`docker-compose.yml`, this README · 11 docs/03 · 12 docs/04 · 13 docs/05 · 14 docs/06

## Rules built into the code
Draft-only by default · crisis/sensitive/sponsor/commercial/criticism always go to a human · no links,
hashtags, invented studies or unverified quotes in replies · a comment is never consent to email ·
outreach only to a publicly listed business address with its source URL, corporate entities only,
human-approved, opt-out line + postal address, daily cap · revenue and media kit show measured numbers only.
