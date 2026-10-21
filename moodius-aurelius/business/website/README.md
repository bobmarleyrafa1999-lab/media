# Moodius Aurelius storefront

Editorial site, shop, Stripe checkout, secure PDF delivery, order records, consent-based email capture and cookieless conversion tracking. Runs on Cloudflare Pages (free tier, commercial use allowed) with D1 (SQLite) for records and a private R2 bucket for the product files.

```
pages/        page sources (HTML + {{placeholders}}), built into public/
public/       static site + assets (what Cloudflare serves)
functions/    server routes: /api/shop/*, /download/*, /r/*, /api/newsletter/*
src/          shared logic: catalog, orders, providers (stripe, lemonsqueezy), email, links
migrations/   D1 schema
test/         unit tests (node --test) and end-to-end tests (real wrangler dev server)
```

## Run it locally

```bash
npm install
cp .dev.vars.example .dev.vars          # test values only
npm run build
npm run db:migrate:local
npx wrangler r2 object put moodius-products/products/the-unexamined-self/v1/The-Unexamined-Self-A5-digital.pdf --local --file ../journal/out/The-Unexamined-Self-A5-digital.pdf
npx wrangler r2 object put moodius-products/products/the-unexamined-self/v1/The-Unexamined-Self-A4-print.pdf --local --file ../journal/out/The-Unexamined-Self-A4-print.pdf
npm run dev                             # http://localhost:8788
```

With `PAYMENT_PROVIDER=mock`, Buy goes to a fake card page (`/mock-checkout/`) that only works when `ALLOW_MOCK_PAYMENTS=true` and `LIVE_MODE` is off. Emails are written to the `outbox` table instead of being sent (`EMAIL_PROVIDER=log`); read them in `/backoffice` → Outbox.

## Tests

```bash
npm test          # 13 unit tests: signatures, Stripe params, event parsing, guards, contract payloads
npm run test:e2e  # 23 checks against a real local server with D1 + R2
```

The end-to-end run covers: pages and security headers; checkout refused without the digital-content consent; mock purchase → signed webhook → order → download page → file streamed from R2; duplicate webhooks ignored; bad signatures rejected; download limits and expiry; refund revokes links; resend-links rate limit and no email enumeration; back office auth, orders, CSV export; newsletter double opt-in, confirm, unsubscribe; short links with `src`; and, with a stand-in community agent, the one-domain proxy and signed revenue events.

### Tested vs not yet tested

| Works and is tested locally | Written but untested (needs accounts) |
|---|---|
| Checkout flow, consent gate, order records | Real Stripe Checkout session creation (no Stripe key here) |
| Stripe webhook signature check, event parsing, idempotency | Stripe Managed Payments acceptance of our account and product |
| Secure downloads from R2 with limits, expiry, revocation | Lemon Squeezy checkout (fallback) |
| Refund handling and revenue events to the community agent | Real email sending through Resend |
| Newsletter double opt-in, consent record, unsubscribe | An actual Cloudflare deployment and custom domain |
| Cookieless attribution from `/r/` link to order | Community agent proxy against the real agent |
| Back office, CSV export, admin auth | |

## Deploy (first release, test mode)

Everything below is free except the domain. Steps marked **Surafel** need Surafel's own accounts.

### 1. Accounts (Surafel)

- Cloudflare account (free).
- Stripe account in test mode. In the Dashboard, open Managed Payments and apply; Stripe reviews eligibility. Until it's approved, set `STRIPE_MANAGED_PAYMENTS=false` to test plain Stripe Checkout.
- A domain (about £10 a year; needs Surafel's OK). Buying it through Cloudflare Registrar is at-cost and saves a DNS step.
- Resend account (free: 3,000 emails a month) for order and newsletter emails, with the domain verified.
- A PO box or virtual office address for email footers and the legal pages. Never a home address.

### 2. Cloudflare resources

```bash
npx wrangler login
npx wrangler d1 create moodius                     # copy database_id into BOTH places in wrangler.toml
npx wrangler d1 migrations apply moodius --remote
npx wrangler r2 bucket create moodius-products     # keep it private
npx wrangler r2 object put moodius-products/products/the-unexamined-self/v1/The-Unexamined-Self-A5-digital.pdf --remote --file ../journal/out/The-Unexamined-Self-A5-digital.pdf
npx wrangler r2 object put moodius-products/products/the-unexamined-self/v1/The-Unexamined-Self-A4-print.pdf --remote --file ../journal/out/The-Unexamined-Self-A4-print.pdf
```

### 3. Fill in site details

Edit `site.config.json` (operator name, PO box, support email, Pinterest and Substack URLs) and set `SITE_URL` in `[env.production.vars]` of `wrangler.toml`. `npm run deploy` runs the build with `--strict`, which refuses to deploy while any "[to be added]" placeholder is left. Have the three legal pages (`pages/legal/`) read over before launch; they're marked as drafts.

### 4. Secrets

```bash
npx wrangler pages project create moodius --production-branch main
npx wrangler pages secret put STRIPE_SECRET_KEY         # sk_test_... for now
npx wrangler pages secret put STRIPE_WEBHOOK_SECRET     # from step 5
npx wrangler pages secret put ADMIN_TOKEN               # openssl rand -hex 32
npx wrangler pages secret put IP_HASH_SALT              # openssl rand -hex 16
npx wrangler pages secret put RESEND_API_KEY            # when email goes live
npx wrangler pages secret put EMAIL_FROM
npx wrangler pages secret put SUPPORT_EMAIL
npx wrangler pages secret put POSTAL_ADDRESS
```

Never put a secret in `wrangler.toml`, `.env.example` or git.

### 5. Stripe webhook

Dashboard → Developers → Webhooks → Add endpoint:
- URL `https://<domain>/api/shop/webhooks/stripe`
- Events: `checkout.session.completed`, `checkout.session.async_payment_succeeded`, `charge.refunded`
- Copy the signing secret into `STRIPE_WEBHOOK_SECRET`.

### 6. Deploy and test

```bash
npm run deploy
```

Then buy the journal with test card `4242 4242 4242 4242` (any future date, any CVC). You should land on the thank-you page, see the download page within a few seconds, and find the order in `/backoffice`. Refund it from the Stripe Dashboard and check the download link stops working.

Protect `/backoffice` with Cloudflare Zero Trust → Access (free for up to 50 users) using Surafel's email, on top of the admin token.

### 7. Go live (Surafel's call)

1. Replace `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` with live values (and a live webhook endpoint).
2. Set `LIVE_MODE = "true"` in `[env.production.vars]`. The site refuses live keys without it, and refuses test keys with it.
3. Set `EMAIL_PROVIDER = "resend"`, redeploy, and make one real £14 purchase to yourself, then refund it.

### Switching to Lemon Squeezy

If Stripe Managed Payments isn't available for the account: create the product in Lemon Squeezy, set `PAYMENT_PROVIDER = "lemonsqueezy"`, add `LEMONSQUEEZY_API_KEY`, `LEMONSQUEEZY_STORE_ID`, `LEMONSQUEEZY_VARIANT_THE_UNEXAMINED_SELF` and a webhook to `https://<domain>/api/shop/webhooks/lemonsqueezy` (events `order_created`, `order_refunded`) with its secret in `LEMONSQUEEZY_WEBHOOK_SECRET`. Delivery still runs from our R2 bucket, so buyers get the same download page.

### Connecting the community agent

When the agent is deployed, set `COMMUNITY_AGENT_URL` and `REVENUE_WEBHOOK_SECRET` (shared with the agent). The storefront then proxies the agent's paths (`/r/*`, `/newsletter*`, `/api/newsletter/*`, `/admin*` and the rest listed in `functions/_middleware.js`) and stops using its own fallback newsletter and short links. Paid and refunded orders are sent to `/api/integrations/revenue`; `/backoffice` → "Forward pending" re-sends any that failed.

## Security notes

- Download links are random 256-bit tokens stored only as SHA-256 hashes. Opening a link shows a page; the file is only sent on a button press (POST), so email scanners can't use up downloads.
- Webhooks are verified with HMAC and a 5-minute window, and event ids are recorded only after processing succeeds.
- Card details never touch this site; Stripe hosts the payment page.
- Strict Content-Security-Policy, HSTS, no third-party scripts, no tracking cookies.
- Customer records hold email, name, amount and `src` only. Export or delete one through `/backoffice` CSV export plus a D1 query; a delete button is a small follow-up if requests come in.
