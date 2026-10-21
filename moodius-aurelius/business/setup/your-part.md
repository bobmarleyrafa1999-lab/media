# Your part: about 30 minutes, once

Everything else is done or scripted. These steps need you personally, because each one involves your identity, your money, or accepting a contract in your name. I can't sign up to Stripe or a mail address service as you, and I can't pay for things.

Do them in this order. Each step ends with what to send me.

## 1. Cloudflare account and domain (5 min, about £5-8 a year)

1. Sign up at dash.cloudflare.com with your Gmail.
2. Go to **Domain Registration → Register Domains**, search for the names below in this order, and buy the first one that's free. Cloudflare charges cost price (about $10.46 a year for a .com) with no renewal mark-up.
   1. `moodius.co.uk`
   2. `moodiusaurelius.com`
   3. `moodius.co`
   4. `moodiusaurelius.co.uk`
3. Still in Cloudflare: **Email → Email Routing → Enable**, then add a rule that sends `hello@<your domain>` to your Gmail. It's free, and it means no extra inbox to pay for.

**Send me:** the domain you bought.

## 2. Business address (5 min, £13 a month or £130 a year, plus ID check)

UK law requires a shop to show a postal address, and marketing emails need one too. Use a mail-forwarding address, never your home.

My pick is i-support-business.co.uk, **Business Address → Post Forwarding**: £13 a month or £130 a year, works for sole traders, and has a £20 postage deposit. Expect an ID check that takes a day or two.

**Send me:** the address exactly as they give it, once it's active.

## 3. Stripe (10 min)

1. Sign up at dashboard.stripe.com. Choose **Individual / sole trader** and the UK, add your ID and your bank account for payouts. For "business website" give `https://<your domain>`.
2. Stay in **Test mode** (the toggle at the top).
3. Search the dashboard for **Managed Payments** and apply. That makes Stripe the seller, so it handles VAT. If it says you're not eligible, tell me and I'll switch to Lemon Squeezy, which is one setting.

**Send me:** "Stripe done", and whether Managed Payments was approved. Never send me keys.

## 4. Resend, for order emails (2 min, free)

Sign up at resend.com with Google. Add your domain under **Domains**. If Resend offers to set up DNS automatically with Cloudflare, accept; otherwise copy the records it shows into Cloudflare DNS.

**Send me:** "Resend done".

## 5. Let me deploy from your Mac (1 min)

Approve the Remote Control prompt in this thread, then run `npx wrangler login` once in the terminal it opens and click **Allow** in the browser. I then run `scripts/configure.mjs` and `scripts/setup-cloudflare.sh`. Those create the database and storage, upload the journal, set the admin token (saved to `~/moodius-admin-token.txt`, only on your Mac) and put the site live in test mode.

## 6. Paste three keys into Cloudflare yourself (3 min)

After the deploy, go to Cloudflare → **Workers & Pages → moodius → Settings → Variables and secrets** and add these as **Secret** (encrypted):

| Name | Where to get it |
|---|---|
| `STRIPE_SECRET_KEY` | Stripe → Developers → API keys → Secret key (`sk_test_...`) |
| `STRIPE_WEBHOOK_SECRET` | Stripe → Developers → Webhooks → Add endpoint. URL `https://<domain>/api/shop/webhooks/stripe`, events `checkout.session.completed`, `checkout.session.async_payment_succeeded`, `charge.refunded`. Copy its signing secret (`whsec_...`) |
| `RESEND_API_KEY` | Resend → API Keys → Create |

Tell me when that's done. I'll switch email sending on, redeploy, and run a test purchase with card 4242 4242 4242 4242 to check the whole flow: payment, emails, download, refund.

## 7. Go live (your decision)

When you've seen a test order work, say **"go live"**. You then swap the two Stripe test keys for live ones in the same Cloudflare screen, and I flip `LIVE_MODE` and redeploy. Real money only moves after that.

---

**Already done for you:** the site, the journal, personal and gift editions, prices, the legal pages (filled in from your details by the configure script; a solicitor's read is optional, not required to launch), the refund window (14 days), the deploy scripts, the welcome emails, and the reels.
