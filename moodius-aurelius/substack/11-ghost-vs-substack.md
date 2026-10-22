# 11. Ghost or Substack? (21 Oct 2026)

Surafel shared [TryGhost/Ghost](https://github.com/TryGhost/Ghost), the open-source (MIT) publishing, newsletter and membership platform. Question: run the publication on Ghost instead of, or alongside, Substack?

## Recommendation
**Launch on Substack as planned. Keep Ghost as the planned exit, and re-decide at the day-90 review (30 Jan 2027).** Don't run both: two homes split the list and the numbers.

## Comparison
| | Substack | Ghost(Pro) | Ghost self-hosted |
|---|---|---|---|
| Monthly cost now | €0 | Starter ≈$15–18/mo (≤1,000 members, **no paid tier**); Publisher ≈$29/mo for paid ([Typeflo, 2026](https://typeflo.io/blog/ghost-pricing-plans); [TechCrunch, Aug 2025](https://techcrunch.com/2025/08/05/substack-rival-ghost-connects-to-the-open-social-web-with-its-latest-public-release)) | VPS ≈€5.50–12 + Mailgun (only supported sender; pay-as-you-go doubled to $2/1,000 emails in Dec 2025) + backups ≈ **$15–17/mo** for a small list ([Magic Pages, Jun 2026](https://www.magicpages.co/blog/the-real-cost-of-self-hosting-ghost-in-2026/); author sells managed hosting) |
| Fee on paid subs | 10% + Stripe | 0% + Stripe | 0% + Stripe |
| Budget (€20–25 incl. Metricool €20) | Fits | Breaks it | Breaks it |
| Discovery | Notes, recommendations, app network. Substack said its network drove ~40% of free subscriptions (late-2022 figure, old) | ActivityPub/fediverse (Mastodon, Threads, Flipboard) and Bluesky via a bridge since Ghost 6.0; no recommendation network of Substack's size | Same as Pro, plus extra ActivityPub and analytics services to run yourself |
| Your time | Paste + publish ≈10 min/week | Same or less | Plus server upgrades and patches (Node, MySQL, security), occasional evenings |
| Automation | No official API (manual paste) | **Real Admin API**: Claude can create drafts from the repo automatically; you only press publish | Same |
| Anonymity | Pen name; Stripe identity hidden | Same | Same; server account in your name, not public |
| Own domain / SEO | Optional one-time fee | Included | Yours |
| Portability | Export posts + subscriber CSV; repo is already the source of truth | Full JSON export | Full control |

## Why Substack first
1. **Audience is the bottleneck, not tooling.** The newsletter starts at zero. Substack's Notes and recommendations are the only built-in discovery either option offers at meaningful scale, and the strategy leans on them.
2. **Cost.** Ghost adds ≈€15–30/month before there's a reader, which breaks the €20–25 budget.
3. **Time.** Self-hosting adds maintenance to a one-person, anonymous operation.
4. **Lock-in is already handled.** Essays live as Markdown in the repo, and Substack exports subscribers and posts, so moving later costs a day, not the archive.

## When to switch (checked at day 90 and every review after)
Move to Ghost(Pro) Publisher if **any two** hold:
- Paid revenue passes ≈€300/month (Substack's 10% then costs about what Ghost Publisher costs).
- Substack network/Notes bring under 20% of new free subscribers for two months, so the network isn't earning its fee.
- The manual paste becomes the bottleneck (e.g. more than one long piece a week).

## What changes in the delivered package
- **Nothing in the essays, packages, calendar or strategy.** They're platform-neutral.
- **Kit list:** still move it into Substack (one list). If you go to Ghost later, Ghost imports the same CSV and also replaces Kit.
- **Ready for a switch:** a Ghost exporter is about 40 lines on top of `export_substack.py` (Admin API `POST /posts/?source=html` with `status: draft`). Not built now; Claude builds it if the day-90 review says switch.
- `10-costs-and-apis.md` stays at €20/month.

## Claude does / You do
**Claude:** tracks the three switch signals in `/metrics-review` and raises them at day 90.
**You:** nothing now, unless you'd rather start on Ghost anyway. Then say so before you set up Substack.
