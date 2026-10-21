# Moodius Aurelius: digital products business

Built 21-22 Oct 2026. First release: a storefront that sells **The Unexamined Self** (£14) with test-mode payments, secure delivery and order records, plus a free guide, newsletter capture, product reels and a plan for a journaling app.

| Folder | What's in it |
|---|---|
| `website/` | Storefront code, tests, deploy guide (`website/README.md`), `.env.example` |
| `journal/` | The journal and free guide: editable YAML sources, PDF/DOCX builders, quote checker, outputs in `journal/out/` |
| `funnel/` | Welcome emails, £29 bundle plan, tracking guide, six product reels |
| `phase4-journaling-app.md` | Plan for the subscription journaling app |
| `your-checklist.md` | What Surafel needs to do, in order |

## The architecture decision

**Chosen: our own small site on Cloudflare Pages + D1 + R2, with Stripe Checkout in Managed Payments mode.** Fixed cost €0 a month; the domain (about £10 a year) is the only new spend and needs Surafel's OK.

Why not one of the repos: none of them was both commercially usable and safe to sell from today.

| Repo | Licence | Verdict |
|---|---|---|
| sellf | Elastic 2.0 (self-hosting allowed, not resale as a service) | Closest fit and actively maintained, but needs a server plus Supabase. Good "later store" if the catalog grows; the community agent already has a receiver for it |
| freecoffee.bio | No licence | Skip. Tip-jar link page; can't legally reuse; our `/links` page replaces it |
| TishCommerce | MIT | Skip. Download links are static URLs a buyer can share with anyone |
| opengrove | No licence, abandoned | Skip |
| Ghost | MIT | Not now. Great publishing and paid memberships, but it sells subscriptions, not files, needs a server (≈€5-15/month) and duplicates Substack |
| plausible | AGPL-3.0 | Not now. Our cookieless event log covers clicks → purchases; Plausible Cloud later if traffic passes ~10k visits a month |
| usememos/memos | MIT | Not for the store. Strong base for the Phase 4 journaling app (see that plan) |

The full audit of the six earlier repos is in `community-agent/docs/01-repo-audit.md`; this thread reused it and added memos.

## Payments: Stripe vs a merchant of record

Selling a PDF to UK and EU buyers means charging and filing VAT in each buyer's country. Two ways to handle that:

- **Merchant of record** (Lemon Squeezy, Gumroad, Paddle): they're legally the seller and handle VAT. Lemon Squeezy costs 5% + 50¢, so about £1.10 on £14.
- **Stripe directly**: cheaper per sale (1.5% + 20p UK cards, about 41p on £14), but Surafel would be the seller and must register for VAT abroad and file returns.

**Pick: Stripe Managed Payments**, which gives both: Stripe Checkout on our site with Stripe acting as merchant of record and handling VAT. It adds 3.5% on top of normal processing, so about 90p on a £14 sale, cheaper than Lemon Squeezy at this price. It needs Stripe to approve the account; the UK and Spain are supported and ebooks qualify. **Lemon Squeezy is fully wired as the fallback** (one setting to switch), and plain Stripe is one more setting if Surafel ever registers for VAT directly.

## Budget

| Item | Cost |
|---|---|
| Cloudflare Pages, D1, R2, Access | €0 (free tier allows commercial use) |
| Resend email | €0 up to 3,000 emails a month |
| Stripe Managed Payments | No monthly fee; about 90p per £14 sale |
| Domain | About £10 a year (**needs OK**) |
| PO box / virtual address | About £5-15 a month (**needs OK**; legally needed for marketing emails and the legal pages) |

## What Claude did

- Storefront with mobile-first editorial design, shop and product pages, checkout with the digital-content consent required by UK law, Stripe and Lemon Squeezy adapters, signed webhooks, secure expiring downloads, refunds, order records, back office with CSV export, newsletter double opt-in with stored consent, short links and cookieless attribution, and the one-domain link-up with the community agent. 13 unit tests and 23 end-to-end checks pass locally.
- The journal: 30 original days in six parts, 117 pages, type-in A5 and print A4 PDFs plus an editable DOCX and YAML source. Every verbatim quote checked against the public-domain source; everything else labelled as a Moodius paraphrase. Each day carries an evidence note (empirical, philosophical or opinion) and there are 48 references.
- Free seven-day guide (27 pages), guide landing page, five-email welcome sequence, £29 bundle plan, tracking guide, and six product reels rendered with the reels engine.
- Phase 4 plan for a private journaling app.

## What's not done or not tested

- No real Stripe, Lemon Squeezy or Resend calls have been made (no accounts or keys here). The code follows their documented APIs and is unit-tested against their signature schemes.
- Not deployed to Cloudflare yet; that needs Surafel's account.
- Legal pages are drafts that need the operator name, address and a read-through.
- Nothing has been scheduled or sent: no reels in Metricool, no emails.

See `your-checklist.md` for the steps that unblock each of these.
