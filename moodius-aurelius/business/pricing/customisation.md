# Customisation buyers can choose

Every option stays inside the brand: Slate, Bone, Ash and Ember only, Playfair and Inter, no gold, statues or marble, and no invented quotes. The opening lines are original Moodius lines, credited to Moodius, one for each Instagram highlight. Any words the buyer adds are their own.

## Built now (test mode)

Buyers choose on the product page (`/shop/the-unexamined-self/`). `journal/personalise.py` builds the copy and the shop emails it.

| Option | Where it shows | Standard (£14) | Personal (£19) | Gift (£22) |
|---|---|---|---|---|
| "This journal belongs to" type-in line | Title page | ✓ | | |
| Name on the cover ("Kept by Amara Okafor") and title page | Cover, title page, copyright line | | ✓ | ✓ |
| Monogram in the Ember square (1-3 letters) | Cover, top right | | ✓ | ✓ |
| Cover: Slate (dark) or Bone (light) | Cover | | ✓ | ✓ |
| Accent: Ember, Ash or Bone | Cover numeral, rule, monogram | | ✓ | ✓ |
| Opening line from one highlight (Manifesto, Daily, Tools, Discipline, Truths, Journal, Identity) | Title page, in place of the Plato epigraph | | ✓ | ✓ |
| Dedication (up to 280 characters) | Its own page after the title | | ✓ | ✓ |
| Dated pages from a chosen start date ("Day 1 · Mon 2 Nov") | Every day page | | ✓ | ✓ |
| Gift page "from" name | Under the dedication | | | ✓ |
| Emailed to the recipient on a chosen date | Delivery | | | ✓ |
| A5 type-in and A4 print editions | Both always included | ✓ | ✓ | ✓ |

The seven opening lines:

| Highlight | Line |
|---|---|
| Manifesto | Feel everything. Be ruled by none of it. |
| Daily | One honest look a day is enough to change a year. |
| Tools | A feeling named is a feeling you can work with. |
| Discipline | Discipline is choosing, again, who you said you'd be. |
| Truths | Most of what hurts is a story told too quickly. |
| Journal | Write it down. Then read it as if a friend had written it. |
| Identity | You are not your worst day, and not your best one either. |

They're new lines I wrote for this, so change any you don't like. They live in `website/src/personal.js` and `journal/build_journal.py`.

### What it costs you to make

| | Standard | Personal | Gift |
|---|---|---|---|
| Your time per order | 0 | About 3 minutes: run `python3 personalise.py <order> --deliver` | About 4 minutes, on or after the send date |
| Money cost per order | £0 | £0 | £0 |
| Extra price | | +£5 | +£8 |
| You keep per sale (UK card) | £10.77 | £13.93 | £16.03 |

How an order flows: the buyer pays, gets the standard PDFs straight away, and you get an email that says "To make: …" with the exact command. Running it builds both personalised editions (about 20 seconds), uploads them to that order's download page, and emails the buyer, or the gift recipient on the day they chose. The buyer's email lists their choices and asks them to reply the same day if there's a typo.

To take the 3 minutes off your plate: a free scheduled GitHub Action can run the same command every hour. That's a small follow-up when orders start coming in.

## Ideas for later, with costs

| Idea | Cost to make | Suggested price | Notes |
|---|---|---|---|
| Phone lock screen with their opening line and name | £0 (generated with the copy) | Free bonus with Personal | Easy to add; good for sharing on stories |
| Themed 14-day journals, one per highlight, each with its own cover mark | Writing time; same build system | £6 each | Turns each highlight into a product |
| Couples / friends edition: two names, with the "How You Attach" days written for two | Writing time for about 6 extra pages | £24 | Fits the relationships content |
| Printed paperback, personalised, via print-on-demand | About £3-4 to print and £3-4 UK postage per copy (estimate from published print-on-demand rates; get a quote) | £24-27 | Stripe Managed Payments covers digital goods only, so print needs plain Stripe or the printer's own shop, plus VAT handling |
| Monthly "Evening Review" refill with dated pages | £0 | £3, or included in the future app subscription | Better as part of the app (see `phase4-journaling-app.md`) |

Off-brand ideas to skip: gold foil, extra colours, star signs or other gimmick personalisation, and AI-written "personal insights" inside the journal.
