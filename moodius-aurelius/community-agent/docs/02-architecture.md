# 02 · Architecture

Smallest system that meets the brief: **one Next.js service + one Postgres database.** n8n (or the
built-in worker) only keeps time.

```
Instagram ──webhook (signed)──► /api/webhooks/instagram ─┐
          ◄──poll every 5 min── poll-comments job ───────┤  ingest (idempotent on comment_id)
                                                          ▼
                                                   jobs table (Postgres queue, SKIP LOCKED, retries, dead-letter)
                                                          ▼
                       context (caption, thread, history, recent replies)
                                                          ▼
     safety pre-rules ──► Claude classifier + draft ──► draft veto + repetition check
     (crisis, sponsor,     (JSON schema output;           (links, hashtags, invented studies,
      spam, keywords)       heuristic in mock mode)        unverified quotes, clinical advice)
                                                          ▼
                                       policy: mode A/B/C, caps, kill switch
                                 ┌────────────┬───────────┴───────────┐
                         publish (B/C only)  human queue (/admin)   DM keyword (private reply, once, ≤7 days)
                                 └────────────┴───────────┬───────────┘
                                                          ▼
                                 email: urgent now · substantive now (≤12/h) · rest in 20:30 digest
```

## Modules (`src/lib/`)

| Area | Files |
|---|---|
| Instagram | `meta/signature.ts` (X-Hub-Signature-256), `meta/webhook.ts`, `meta/graph.ts` (retries, Retry-After, token refresh), `meta/mock.ts` |
| Brain | `taxonomy.ts`, `safety.ts`, `prompts.ts`, `classifier.ts`, `similarity.ts`, `policy.ts` |
| Flow | `pipeline.ts`, `queue.ts`, `jobs.ts` |
| Email | `email/send.ts` (dedupe, hourly cap), `email/templates.ts` |
| Newsletter | `newsletter.ts` (double opt-in, consent text + version, one-click unsubscribe, erase, export) |
| Tracking | `tracking.ts` (comment → DM → click → signup → purchase), `/r/[slug]` |
| Sponsors | `sponsors/discovery.ts`, `scoring.ts`, `drafting.ts`, `compliance.ts`, `crm.ts`, `outreach.ts` |
| Money | `revenue.ts`, `analytics.ts` |

## Reply modes

| Mode | What publishes by itself | Default |
|---|---|---|
| A · draft only | nothing | ✅ |
| B · assisted | `appreciation` replies only | |
| C · controlled | appreciation, answers to the post's own question, light struggle; max 4/hour, 25/day, confidence ≥ 0.85 | |

Never automatic in any mode: crisis, sensitive, sponsorship, commercial interest, criticism, anything
flagged by the veto, the heuristic fallback, or a Claude error. Kill switch in `/admin/settings`.

## Idempotency

`comments` primary key · `outbound_actions UNIQUE(kind, comment_id)` (one public reply, one DM) ·
`email_log.dedupe_key` · `webhook_events.body_sha256` · `revenue_entries.external_id`.

## Data and privacy

Comments kept 12 months, unconfirmed sign-ups 30 days, webhook bodies and jobs 30 days, email bodies 90
days (`retention` job). IPs are never stored; sign-ups keep a salted hash only. The refreshed Instagram
token is stored AES-256-GCM encrypted.
