# Welcome sequence: free guide → newsletter → £14 journal

Status: **draft, not sending.** Nothing is emailed to subscribers until Surafel approves this copy and the sending setup (Resend domain or the community agent's mailer, plus a postal address in the footer).

Who sends it: the storefront sends emails 0 and 1 today (double opt-in, then guide delivery; `website/src/newsletter.js`). Emails 2-5 are written here for whichever mailer owns the list once Surafel decides between Substack and Kit. If Substack becomes the single list, emails 2-5 go into Substack's welcome email plus the first essays, and the storefront only forwards sign-ups.

## Rules every email follows

- Sent only to people who ticked the consent box (text and version `2026-10-21` are stored with each subscriber). The guide is the thank-you, not the price of consent: the box is not pre-ticked and the guide page says so.
- One-click unsubscribe link plus `List-Unsubscribe` and `List-Unsubscribe-Post` headers, and the postal address (PO box) in every footer. Both are already in the code.
- Plain text first. No tracking pixels. Link clicks are counted only through `/r/` links with a `src`, which records the click without identifying the reader.
- Same voice as the brand: short, concrete, no hype, no "act now". Quotes cite book and section; paraphrases are labelled.
- At most one sales mention per email, and never in the first two.

## The sequence

| # | When | Subject | Job |
|---|------|---------|-----|
| 0 | Immediately | Confirm your subscription to Moodius Aurelius | Double opt-in (live in code) |
| 1 | On confirm | Your guide: Seven Days of Honest Reflection | Deliver the PDF (live in code) |
| 2 | Day 2 | The one-sentence trick from Day 1 | Help them start; no selling |
| 3 | Day 5 | Why we label every quote | Trust: show how the sources work |
| 4 | Day 8 | You did seven days. Here's what's next. | Offer the journal, once, plainly |
| 5 | Day 12 | Every Thursday, one essay | Hand over to the weekly newsletter |

Anyone who buys the journal (the order webhook knows the email) skips email 4.

### Email 2 · Day 2 · "The one-sentence trick from Day 1"

> Quick one.
>
> Day 1 of the guide asks you to describe a moment the way a camera would, before your mind adds its verdict. Epictetus has an almost comic example: someone bathes quickly, so "do not say that he bathes badly, but that he bathes quickly" (Enchiridion 45, tr. George Long).
>
> If you only do one thing from the guide this week, do that: one plain sentence about your day, no adjectives about yourself.
>
> Tonight's question: what happened today, in words a camera would agree with?
>
> Moodius
>
> [Open the guide again](/r/guide?src=email_welcome_2)

### Email 3 · Day 5 · "Why we label every quote"

> You'll notice the guide marks quotations as "verbatim" or "Moodius paraphrase".
>
> That's because a lot of what circulates as Stoic wisdom online was never said by a Stoic. Verbatim lines come from public-domain translations and are checked word for word against the source. Where the old translation is hard to read, we rewrite it in plain English and say so.
>
> The same goes for psychology. Each day carries a note on how strong the evidence is: empirical (and how strong), philosophical, or simply our opinion. Day 3's note, for example, says the research on naming feelings is lab-based with small to moderate effects. That's less exciting than "science proves journaling works", and closer to true.
>
> Moodius

No link. This email exists to earn trust before email 4.

### Email 4 · Day 8 · "You did seven days. Here's what's next."

> If you worked through the guide, you've done a week of noticing.
>
> The full journal goes further. The Unexamined Self is thirty days in six parts: noticing, what is yours, feeling clearly, how you attach, who you think you are, and what you live by. Each day has a reading, an evidence note, three questions, an exercise and an evening line. There's a values exercise, a feelings vocabulary and 48 references. It comes as a type-in PDF for your phone or tablet and an A4 print edition.
>
> It's £14, and it isn't therapy. It's a structured month of looking at yourself honestly.
>
> [See inside the journal](/r/journal?src=email_welcome_4)
>
> If it isn't for you, no problem. The essays stay free.
>
> Moodius

### Email 5 · Day 12 · "Every Thursday, one essay"

> From here on you'll get one essay a week, on Thursdays. The first few: "Writing to No One", "The Trait You Can't Stand in Other People", and "The Loneliness of Being Fine".
>
> Reply to any of them. I read every reply, though I can't always answer.
>
> Moodius
>
> [Read the latest essay](/r/newsletter?src=email_welcome_5)

The titles are the first three drafted essays in `substack/essays/` (awaiting Surafel's approval); swap them if that changes before launch.

## What to measure

Shown in `/backoffice` → Summary (by `src`) and in the community dashboard once connected:

- Guide sign-up → confirm rate (target above 60%; below that, check the confirm email isn't landing in spam).
- `email_welcome_4` clicks → journal purchases (src carries through checkout to the order).
- Unsubscribes per email. If one email loses more than 2% of readers, rewrite it.
