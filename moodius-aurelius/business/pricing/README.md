# Pricing and margins

Checked 21-22 Oct 2026. The numbers come from `margins.py`, which writes `margins.csv` from the assumptions at its top. Change an assumption there and re-run it rather than editing figures by hand. The finance model in `business/finance/` uses these same numbers.

## The product line

| Product | Price | Status | Why this price |
|---|---|---|---|
| Seven Days of Honest Reflection | Free | Live | Lead magnet: it buys an email address, not money |
| Themed 14-day journal (one per Instagram highlight) | £6 | Planned | Impulse price for people who found one highlight useful; a step up from free |
| Workbook (Feeling Clearly, How You Attach, What You Live By) | £9 | Planned | Deeper single-topic product, mostly sold inside the bundle |
| **The Unexamined Self** | **£14** | **Live (test mode)** | The core product, see below |
| Personal edition | £19 (+£5) | Built (test mode) | Same journal, made in the buyer's name |
| Gift edition | £22 (+£8) | Built (test mode) | Personal edition plus a gift page, emailed to the recipient on a chosen day |
| Bundle upgrade for journal buyers | £15 | Planned | The difference between £14 and £29, so nobody pays twice |
| The Examined Life bundle | £29 | Planned | Journal + three workbooks + card set, about £45 if bought separately |
| Personal bundle | £34 | Planned | Bundle with the journal personalised |

### How £14 compares

Stoic journals sold as PDFs mostly cost $8-15:

| Comparable | Price | What it is |
|---|---|---|
| "The Daily Stoic Practice Journal", Payhip | $7.99 | 90 days, 104 pages, printable US Letter, no fill-in fields |
| "The Daily Stoic Discipline Journal", Gumroad | $7.99 | 30-day framework |
| "The Stoic Journal: 60 Days", Gumroad | $9.99 | 60 days |
| "Stoic Mindset Workbook", Etsy | €12.40 ($14.56) | 48 pages, 12 exercises, three PDF sizes, not editable |

£14 (about $18) sits at the top of that range, and that's deliberate. The journal is longer (117 pages), has type-in fields on every page, checks its sources, and carries a brand people already follow. It shouldn't go higher until reviews and sales back it up. If cold traffic from reels converts poorly in the first month, the first thing to test is a newsletter-only launch price of £11, not a permanent cut.

## What you keep from each sale

Prices include VAT. Stripe Managed Payments is the legal seller: it collects and pays the VAT, and you receive what's left after fees.

| Product | Price | VAT (assumed 20%) | Fees, UK card | **You keep, UK card** | You keep, EEA card | You keep, Lemon Squeezy |
|---|---|---|---|---|---|---|
| Journal | £14.00 | £2.33 | £0.90 | **£10.77 (77%)** | £10.35 | £10.59 |
| Themed 14-day journal | £6.00 | £1.00 | £0.50 | **£4.50 (75%)** | £4.32 | £4.32 |
| Workbook | £9.00 | £1.50 | £0.65 | **£6.85 (76%)** | £6.58 | £6.67 |
| Personal edition | £19.00 | £3.17 | £1.15 | **£13.93 (73%)** | £13.36 | £13.75 |
| Gift edition | £22.00 | £3.67 | £1.30 | **£16.03 (73%)** | £15.37 | £15.85 |
| Bundle upgrade | £15.00 | £2.50 | £0.95 | **£11.55 (77%)** | £11.10 | £11.37 |
| Bundle | £29.00 | £4.83 | £1.65 | **£22.52 (78%)** | £21.65 | £22.34 |
| Personal bundle | £34.00 | £5.67 | £1.90 | **£25.68 (76%)** | £24.66 | £25.50 |

Personal and gift editions also deduct 3-4 minutes of your time at £15 an hour for running the build command.

What goes into those numbers:
- **Fees**: Stripe UK cards 1.5% + 20p, EEA cards 2.5% + 20p plus 2% currency conversion, international 3.15% + 20p plus 2% ([stripe.com/gb/pricing](https://stripe.com/gb/pricing)), plus 3.5% for Managed Payments. Lemon Squeezy is 5% + 50¢.
- **VAT** is assumed at 20% on every sale, which is the cautious case. UK e-publications are zero-rated, but HMRC may treat a journal made mainly for writing in like a diary, which is standard-rated. EU rates vary and are often lower for ebooks. If the journal qualifies for zero-rating in the UK, UK buyers would leave you about £2.30 more per £14 sale. That's a question for an accountant before you rely on it.
- **Delivery** costs nothing per sale: files come from Cloudflare R2 and emails go through Resend's free tier.
- **Refunds** aren't deducted here. Plan for about 3% (an assumption, not a measured rate).
- **Profit is before income tax.**

## Fixed costs and break-even

| Cost | Per month |
|---|---|
| Domain (about £8 a year at Cloudflare's cost price) | £0.67 |
| Business address: i-support Post Forwarding (£13 a month, or £130 a year) | £13.00 |
| Cloudflare hosting, database, file storage, Access | £0 |
| Resend email (up to 3,000 a month) | £0 |
| **Total** | **£13.67** |

**Break-even on shop costs only is under two journal sales a month** (1.3, or 1.8 with a €6 server for the community agent). The whole-business break-even, which also counts Metricool and other tools, is about three sales a month; see `business/finance/moodius-finance-model.xlsx`. That model also applies a 3% refund allowance and a 60/20/20 UK/EEA/international mix, so its blended figure per journal is £10.16 against the £10.77 UK-card figure here.

Illustration, not a forecast (UK cards, journal only, before refunds and tax):

| Journal sales a month | You keep |
|---|---|
| 10 | £94 |
| 30 | £310 |
| 100 | £1,063 |

Personal and gift editions raise the average order. If one buyer in five picks the personal edition, the average sale is £15 and you keep about £11.40 of it.
