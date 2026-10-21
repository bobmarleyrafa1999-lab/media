# Tracking: from a social click to a purchase

The whole path is cookieless. Attribution travels in the URL (`?src=`) and is saved with the checkout and the order. There is no cookie banner because there are no tracking cookies.

## How a click becomes an order

```
Reel / pin / story / DM / email
  → https://<domain>/r/journal?src=dm_reel_p001     (logs link_click with src)
  → /shop/the-unexamined-self/?src=dm_reel_p001      (logs page_view with src)
  → Buy → /api/shop/checkout                          (logs checkout_started, saves src on the checkout)
  → Stripe Checkout → webhook                         (order saved with src, logs purchase)
  → Revenue event to the community agent              (includes src)
```

The page script keeps `src` on internal links while the visitor browses, using the URL only (no storage). If someone leaves and comes back days later from a bookmark, the sale shows as "direct". That undercounts slightly and is the honest trade-off for not using cookies.

## Naming `src`

Lowercase letters, numbers, `_` and `-`, at most 40 characters. Anything else is cleaned automatically.

| Where the link sits | `src` | Example |
|---|---|---|
| Instagram bio | `ig_bio` | `/r/links?src=ig_bio` |
| DM sent after a keyword comment on a reel | `dm_reel_<id>` | `/r/journal?src=dm_reel_p001` |
| Story link sticker | `story_<yyyymmdd>` | `/r/journal?src=story_20261103` |
| Pinterest pin | `pin_<pin id>` | `/r/guide?src=pin_p07` |
| Threads post | `threads_<yyyymmdd>` | `/r/guide?src=threads_20261104` |
| Substack essay | `substack_<slug>` | `/r/journal?src=substack_why-vs-what` |
| Welcome emails | `email_welcome_<n>` | `/r/journal?src=email_welcome_4` |

Short-link slugs available today: `shop`, `journal`, `guide`, `newsletter`, `substack`, `instagram`, `pinterest`, `home`. They're defined in `website/src/links.js`.

## What Instagram can't tell us

Instagram allows one bio link and no links in captions, so a reel can't carry its own link. Per-reel attribution therefore comes from the **DM keyword**: the reel says "Comment JOURNAL", and the DM that goes out carries `src=dm_reel_<id>`. Today Surafel sends those DMs by hand (or the community agent drafts them once it's connected). Sales from people who tap the bio link directly show as `ig_bio`.

## Where to see results

- **`/backoffice`** (admin token required, put behind Cloudflare Access): orders, revenue, and a summary table of clicks → views → checkouts → purchases by `src`, plus CSV export.
- **Community agent dashboard**, once connected: receives every paid and refunded order with its `src`, so revenue sits next to follower and comment data.
- **Metricool**: reach and views per reel. Join the two by reel id (P001 ↔ `dm_reel_p001`).

## Weekly check (5 minutes, Fridays)

1. In `/backoffice`, sort the summary by purchases.
2. Note which `src` values sold and which got clicks but no checkouts (that points to the shop page, not the reel).
3. Put the week's top reel id into the weekly content routine so its format gets repeated.
