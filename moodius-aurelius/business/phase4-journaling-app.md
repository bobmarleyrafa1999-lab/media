# Phase 4: a private journaling app (plan, not built)

Working name: **The Examined Self**, a subscription web app for daily reflection that carries the journal's method (readings, prompts, evening review) into something people use every day.

Recommendation in one line: **build it after the journal has sold about 50 copies**, as a fork of **usememos/memos** with an encryption layer, Stripe subscriptions and the journal's prompt library, starting as an installable web app (PWA), not native apps.

## Why memos

Checked 21 Oct 2026 (latest commit that day).

| | memos |
|---|---|
| Licence | MIT: we can fork, modify and sell a hosted service |
| Stack | Go server, React web app, SQLite / Postgres / MySQL |
| Maintenance | Very active (around 50 commits in the last two weeks), large community |
| Already has | Accounts and SSO, Markdown notes, tags, search, attachments, full export (`core/memoexport`), per-user usage limits (`core/usagelimit`), an API, an MCP server, an optional AI provider |
| Missing for us | Encryption of entries at rest, billing, multi-tenant hardening for strangers on one server, a formal security-advisory history (still version 0.x) |

Alternatives considered: Standard Notes (AGPL, end-to-end encrypted, but the licence would force us to publish all our changes and it's a heavier codebase); building from scratch on the storefront's Cloudflare stack (cheapest to run, but months more work to reach memos' feature level). memos gives the most for the least work, and MIT keeps options open.

## Entries are sensitive data

Journal entries about feelings, relationships and mental state are likely to count as health-related "special category" data under UK GDPR. That shapes everything:

1. **Encrypted at rest, per user.** Each user gets a data key; entries are encrypted with AES-GCM before they reach the database, and the data key is wrapped by a server key held in a key service, never in the database. Version 2 option: end-to-end encryption, where the key comes from the user's passphrase and we can't read entries at all (the trade-off is no server-side search and no account recovery without a recovery code).
2. **No training, ever, without informed opt-in.** Entries are never used to train or fine-tune any model. This is written into the terms and privacy policy, and enforced technically by not logging entry text anywhere.
3. **AI is optional and off by default.** If a user turns on reflection prompts that read their entry, the call goes to Claude through Anthropic's API with zero data retention, only the current entry is sent, and the settings page says exactly that. Claude Haiku costs well under a penny per prompt, so it fits in the subscription price.
4. **Export and delete are one click.** Export as Markdown and JSON (memos' exporter). Delete wipes the entries, attachments and data key immediately; backups age out within 30 days, and the policy says so.
5. **Minimal records.** Email, subscription status and entries. No tracking scripts inside the app, no third-party analytics, no selling or sharing.
6. **Security basics before launch:** passkeys or TOTP two-factor, rate-limited login, strict Content-Security-Policy, dependency scanning in CI, daily encrypted backups, an external penetration test before taking payments (about £500-1,500, **needs OK**), and a written breach procedure (72-hour ICO reporting).
7. **Crisis safety.** A permanent "If you're struggling" link to Samaritans and findahelpline.com. The app never presents itself as treatment.

A Data Protection Impact Assessment is needed before launch because of the special-category data; it's a document we write, not a fee.

## Product

- Daily prompt from the journal's library (30 days, then rotating themed tracks: attachment, values, anger, grief, work).
- Free-writing entries, tags, search.
- Evening review: three questions, one line each, with a streak that doesn't punish missed days.
- Monthly "look back": the user's own entries resurfaced, generated without AI by default.
- Export, delete, and a printable PDF of any month.

Pricing idea: **£4 a month or £36 a year**, 14-day free trial; journal buyers get 3 months free. Subscriptions through Stripe (Managed Payments if it covers subscriptions for the account, tax code `txcd_10103000`, SaaS for personal use), reusing the storefront's webhook and order code.

## Hosting and cost

| Stage | Setup | Cost a month |
|---|---|---|
| Private beta (≤100 users) | One small VPS (Hetzner CX22 in the EU) with memos on SQLite, nightly encrypted backups to R2 | €5-6 |
| Launch (≤2,000 users) | VPS + managed Postgres | €20-30 |
| AI prompts | Claude Haiku, opt-in users only | Under €0.05 per active user |

Even the beta VPS is new spend and needs Surafel's OK.

## Roadmap

| Phase | Work | Rough effort |
|---|---|---|
| 0 | Decide go / no-go at 50 journal sales; write the DPIA | 1 day |
| 1 | Fork memos, strip features we don't need, add per-user encryption, the prompt library and the brand design | 2-3 weeks |
| 2 | Stripe subscriptions, trial, journal-buyer offer, account deletion flow | 1 week |
| 3 | Private beta with 20-50 newsletter readers, security review, pen test | 2-3 weeks |
| 4 | Public launch; optional AI prompts behind an opt-in | 1 week |

## Open questions for Surafel

- Go / no-go threshold: is 50 journal sales the right trigger?
- Encryption level for version 1: server-side keys (search works, recoverable) or end-to-end (most private, no recovery)?
- Whether AI prompts belong in the product at all, given the brand's "no AI filler" stance. They can stay out entirely.
