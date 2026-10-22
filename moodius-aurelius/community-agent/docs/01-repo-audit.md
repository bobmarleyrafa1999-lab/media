# 01 · Repo audit: what was kept, what was replaced

Checked 21 Oct 2026 (licences read from each repo's LICENSE file; "no licence" means all rights
reserved, so no code was copied). The rule Surafel set: reuse the useful parts, replace the rest.

## Brief repos

| Repo | Licence | What it is | Kept | Replaced / dropped, and why |
|---|---|---|---|---|
| arunbaghel/Instagram-comment-automation-agent | none | Python bot that replies to every comment | The idea of a classify → draft → reply loop | Everything else. No licence, auto-replies to everyone, no approval step, no dedupe. Rewritten from scratch in `src/lib/pipeline.ts` |
| devgine/n8n-ig-comments-management | MIT | n8n flow that answers IG comments with an LLM | Dedupe-by-comment-ID SQL pattern, Graph error classifier (retry on 4/17/32/613/5xx), webhook fixtures (`tests/fixtures/devgine/`, attribution kept) | "Reply to everyone" behaviour (breaks the draft-only rule); logic moved out of n8n into tested code |
| alongot/creator-crm | MIT | Next.js creator/brand CRM | Data model (brand, contact, activity, task), stage auto-tasks | Its cookie auth (unsigned cookie = anyone can forge admin) → HMAC-signed session in `src/lib/auth.ts` |
| oratis/influencex | MIT | Influencer outreach platform | Consent + suppression rules, AES-GCM "enc:v1" token format (`src/lib/crypto.ts`, `sponsors/compliance.ts`) | Apify scraping and Hunter email-guessing (against the brief: no unofficial scraping, never invent contacts) |
| n8n-io/n8n | Sustainable Use | Workflow tool | Schedules only (`n8n/workflows/00-scheduler.json`) | Business logic stays in code with tests; `npm run worker` replaces n8n entirely if wanted |

## Store / site repos Surafel added

| Repo | Licence | Verdict |
|---|---|---|
| jurczykpawel/sellf | Elastic 2.0 (self-host OK, not as a hosted service) | **Later store.** Active, Stripe-based, sells digital files with expiring links. Webhook receiver already built (`/api/integrations/sellf`) |
| freecoffee-bio/freecoffee.bio | none | Skip. Tip-jar link page; replaced by our own `/links` page with first-party click tracking |
| tishonator/TishCommerce | MIT | Skip. Download links are shareable static URLs (one buyer can share with everyone) |
| sharananurag998/opengrove | no LICENSE file, abandoned | Skip |
| Vojislav77/digital-downloads-website | none | Skip. Static demo; payment is simulated |
| plausible/analytics | AGPL-3.0 | Not now. `/r/` click logging covers attribution with no cookies; Plausible Cloud later if the site passes ~10k visits/month |

**Store recommendation:** sell the first product through Lemon Squeezy or Gumroad (they are merchant of
record and handle EU/UK VAT), move to self-hosted Sellf once sales justify it. Payhip is an alternative.
All three can post to `/api/integrations/revenue` (see `INTEGRATION-CONTRACT.md`).

## Existing workspace

Nothing in `moodius-aurelius/` was overwritten. The two earlier n8n workflows in
`strategy/automation/n8n/` (stats → Sheet, keyword DM) are superseded by this agent but left in place.
