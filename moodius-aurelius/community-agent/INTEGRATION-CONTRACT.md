# Integration contract: storefront → community agent (revenue, attribution, one domain)

Owner of this file: thread "Community and revenue agent". Code: repo `media`, branch `claude/project-thread-ycspok`, folder `moodius-aurelius/community-agent/`.

## 1. Purchase events → revenue dashboard

`POST {APP_BASE_URL}/api/integrations/revenue`

Header: `X-Moodius-Signature: t=<unix seconds>,v1=<hex HMAC-SHA256(REVENUE_WEBHOOK_SECRET, "<t>.<raw body>")>`
(the same scheme as Sellf's `X-Sellf-Signature`; requests older than 5 minutes are rejected)

Body (JSON):

```json
{
  "id": "ord_123",                 
  "event": "order.paid",           
  "stream": "digital_product",     
  "amount_cents": 1400,
  "currency": "GBP",
  "occurred_at": "2026-10-22T10:00:00Z",
  "product": "the-unexamined-self",
  "src": "reel_r012"
}
```

- `id`: unique per order or refund. Retries with the same id are ignored (`revenue_entries.external_id` is unique).
- `event`: `order.paid` or `order.refunded`. Send refunds with a **positive** `amount_cents`; they are stored as negative.
- `stream`: `digital_product` | `membership` | `affiliate` | `sponsorship` | `substack_paid` | `other`.
- `src`: the click source if known (see 2). Optional.
- Response: `200 {"ok":true,"duplicate":false}`. `401` = bad signature, `400` = invalid body.

Sellf can post its own webhooks straight to `POST /api/integrations/sellf` (verifies `X-Sellf-Signature`, dedupes on `X-Sellf-Delivery-Id`; handles `purchase.completed` minor units, `invoice.paid` major units, `refund.issued`).

## 2. Attribution (social click → purchase)

- Every link in bio, DM, Pinterest pin and reel caption goes through `/r/<slug>?src=<source>` (e.g. `src=reel_r012`, `src=link_shop`, `src=dm_journal`).
- The redirect logs one cookieless `link_click` event (no IP, no user agent) and appends `?src=<source>` to the destination URL.
- Storefront: carry `src` through checkout (Stripe `client_reference_id` or `metadata.src`) and send it back in `src`.

## 3. Newsletter: one list, one consent record

Use the agent's `/newsletter` page or `POST /api/newsletter/subscribe` with JSON `{ "email": "...", "consent": true, "source": "shop_footer" }`.
Double opt-in, stored consent wording + version + timestamp, one-click unsubscribe. Please don't run a second list.

## 4. One domain

Storefront owns the root domain. One reverse proxy (Caddy, or Vercel rewrites) routes these paths to the community agent; everything else goes to the storefront:

`/r/*`, `/links`, `/newsletter*`, `/free/*`, `/privacy-newsletter`, `/api/newsletter/*`, `/api/webhooks/*`, `/api/integrations/*`, `/api/cron/*`, `/api/admin/*`, `/admin*`, `/_agent/*`

(The agent's Next.js assets are served under `/_agent` via `assetPrefix` when it sits behind the storefront.)
