# £29 bundle: The Examined Life

Status: **planned, not for sale.** The shop shows it as "coming soon" (`/shop/the-examined-life-bundle/`) with no buy button. The catalog entry (`website/src/catalog.js`) is already there with `status: "coming_soon"`.

## When to build it

After the journal has **25 paid orders** or 6 weeks on sale, whichever comes first. Before that, the effort is better spent on reels that sell the journal. The order records show which days buyers mention in replies, and the bundle should deepen the parts people actually use.

## What's in it

| Item | Format | Status |
|------|--------|--------|
| The Unexamined Self (the journal) | A5 type-in PDF + A4 print PDF | Done |
| Feeling Clearly: a 14-day emotions workbook | Same build system, ~40 pages | To write |
| How You Attach: a 14-day relationships workbook | Same, ~40 pages | To write |
| What You Live By: a values and decisions workbook | Same, ~30 pages | To write |
| The Evening Review card set | 30 printable cards, A6 | To design |

Each workbook expands one part of the journal, using the same YAML schema and `build_journal.py`, so writing a workbook is mostly content work. Same rules: verbatim quotes checked by `verify_quotes.py`, paraphrases labelled, evidence tiers, no therapeutic claims.

Price logic: £14 journal alone, £9 per workbook; £29 for the journal plus three workbooks and cards (about £45 if bought separately). A personal bundle with the journal made in the buyer's name is £34. Margins per sale are in `pricing/README.md`.

## Upgrade path for journal buyers

People who already bought the journal get the bundle for **£15** (the difference). Implementation, about half a day:

1. Add `the-examined-life-upgrade` to the catalog at 1500 pence, `hidden: true`.
2. `/shop/upgrade/?order=<order id>` looks up a paid journal order by the buyer's email through the existing "resend links" flow (the buyer proves the email by clicking a link sent to it), then starts checkout for the upgrade product.
3. Fulfilment works as it does now: one download page, with the extra files.

## Launch

- Email existing buyers once with the upgrade link (they're customers, so this is allowed under the "soft opt-in" rule for similar products, with an unsubscribe link).
- Two reels in the P-series format showing a workbook spread.
- No ads unless Surafel OKs a specific spend.
