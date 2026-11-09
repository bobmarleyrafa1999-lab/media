# CRM for Moodius: verdict and interim (21 Oct 2026)

Surafel shared two repos: `alongot/creator-crm` and `oratis/influencex`. Both were cloned and read.

> **Update 21 Oct 21:50 UTC:** Surafel's "Autonomous community & revenue agent" brief asks for a sponsorship CRM inside one system. That is being built in the **Community and revenue agent** thread (`../../community-agent/`). No separate CRM app gets deployed from here. The three CSVs below are the interim and the seed data for that build; the reuse notes are at the bottom.

## Verdict on the two repos as stand-alone apps: neither, for now.

Both tools are built for the **other side of the market**: a brand that finds creators, pitches them, briefs them and pays them. Moodius is the creator. Today it has no sponsors, no collaborators and a small follower base, so either tool would be an empty database plus hosting to maintain.

| | creator-crm | influencex |
|---|---|---|
| What it is | Influencer-outreach CRM for a brand hiring creators. Pipeline Lead → Outreached → Replied → Negotiating → Briefed → Content In → Live → Paid. Roster, tasks, tags, notes, AI fit score + pitch drafts | Full KOL marketing platform: discovery (YouTube API, Apify for IG/TikTok), email finding (Hunter.io), outreach via Resend, campaigns, ROI dashboard, plus ~18 AI agents (content, publisher, SEO, ads, community) and a social-publishing package |
| Stack | Next.js 16, Postgres (Neon), Drizzle. ~900 lines of logic | Node/Express 5, React, Postgres or SQLite, Docker, GCP Cloud Run. ~320 files |
| Licence | MIT | MIT |
| Maturity | One commit (25 Jun 2026), a template | Active (last commit 8 Sep 2026), 65+ tests; internal docs mostly in Chinese, built around a partner's private app |
| Hosting cost | €0 on Vercel + Neon free tiers | €0 locally (SQLite); €5-15/month as a Docker VPS or Cloud Run + Cloud SQL |
| Upkeep | Low | High: many integrations, migrations, multi-user auth |
| Security notes | One shared password; the login cookie holds the password itself; discovery endpoint open unless `CRON_SECRET` is set. Fix before using with real contacts | Proper RBAC and secret handling; large surface area |
| Fit for Moodius now | Low (wrong direction, nothing to track) | Low (agency-scale tool, overlaps what Claude + Metricool already do) |

**Worth keeping from influencex:** its community rules (`packages/social-ops`): at least 7 helpful contributions per promotional post on Reddit, read each subreddit's rules first, state who you are, no cold mass DMs. These match the Reddit plan in `../13-distribution-channels.md` and are now the rule for it.

## When to switch, and to which

Move to a real CRM when **any one** of these happens:
1. The first paid sponsor or affiliate deal **and** a second inquiry within a month.
2. More than **50 active contacts** or **3+ open deals** at once in `contacts.csv` / `deals.csv`.
3. The agency phase starts (`../09-scaling-roadmap.md` Phase 2, brand 2 or a client brand) and that brand **hires or pitches creators**.

Pick **creator-crm** at that point (Vercel + Neon, €0, small enough for Claude to adapt): rename stages for sponsor deals, harden the login, import `contacts.csv` (columns already match its seed script: `contact_id` → `creator_id`, plus Name, Handle, Platform, Profile URL, Follower count, Niche, Last contact date, Owner). influencex only makes sense if several brands run creator campaigns with a team, which is Phase 3+.

## The interim (live now)

| File | One row per | Who fills it |
|---|---|---|
| `contacts.csv` | Sponsor, affiliate, collaborator or brand client. Stages: Idea → Contacted → Replied → Negotiating → Agreed → Live → Paid → Past / Cold | Claude adds prospects and updates stages; Surafel tells Claude when someone replies |
| `deals.csv` | A deal with a contact (value, deliverables, links to the posts) | Claude, from what Surafel reports |
| `community.csv` | A follower who keeps showing up (meaningful comments or DMs); superfans flagged | Claude, from comments; Surafel, from DMs |

Seeded with 5 sponsor/affiliate ideas (classics publishers, journaling apps and makers, Bookshop.org affiliate) and 2 collaborator slots waiting for the competitor list. **Nobody has been contacted.** No emails or phone numbers are stored until a person replies, and Kit subscriber details stay in Kit (no personal data copied here).

When the n8n comment workflow goes live (`../automation/n8n/`), its `comments-inbox` tab feeds `community.csv`.

## Claude does / You do
**Claude, automatically:** keeps the three files current in the Friday routine, suggests 2 collaborator pages a month from the Metricool competitor data, drafts any pitch for your approval (nothing is sent without your yes), and flags it when a threshold above is hit.
**You, by hand:** reply to sponsor or collab DMs and tell Claude what was said (a one-line note is enough); sign up for Bookshop.org affiliates when Substack goes live; add the 5 Metricool competitors (already on your list) so the collaborator slots can be filled.

## Reuse notes for the community-agent build
- **creator-crm:** take the data model (`lib/db/schema.ts`: contacts, outreach, activities, tasks, tags, campaigns), the stage → auto-task pattern (`lib/stage-automations.ts`), the activity timeline, and the outreach system-prompt shape (`lib/outreach-prompt.ts`, JSON subject/body, <150 words, lead with what we noticed). Don't take the auth (cookie stores the raw password; no-password means open), the UGC rate bands (`lib/rate-estimator.ts` prices creators, the reverse of what we need), or the US-only filters.
- **influencex:** take `packages/social-ops/edm/` (compliance floor, consent-only audience, suppression list, warm-up caps, complaint-rate breaker) and `community/` (7:1 contribution rule, explicit identity, no cold mass DMs) as reference; both are dependency-free JS. Its compliance check wants a postal address in every bulk email (CAN-SPAM); for an anonymous brand use a PO box or virtual address. Skip the rest (agents, GCP deploy, Feishu, Hunter.io email scraping, which clashes with "never invent contacts").
