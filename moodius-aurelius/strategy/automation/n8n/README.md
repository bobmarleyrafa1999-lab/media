# n8n for Moodius Aurelius

**Verdict (21 Oct 2026):** n8n earns a small, specific place. It does not replace the Claude routines; it adds the two things they can't do: react to Instagram events in real time, and write stats straight into the Sheet without you pasting.

## What n8n replaces, adds, and leaves alone
| Job | Today | With n8n |
|---|---|---|
| Writing, rendering, QC, scheduling (weekly Fri 17:52 routine) | Claude + Metricool connector | **Unchanged.** n8n can't call Metricool on our plan: Metricool's API is only on Advanced/Custom plans. |
| Daily 20:40 "did it publish" check | Claude routine | Unchanged |
| Pinterest / Threads posting | Through Metricool once connected | Unchanged |
| Stats into the tracker Sheet | You paste numbers by hand | **Workflow 01**: twice a day, straight from Instagram's own API into an `ig-stats` tab |
| "Comment TOOLS and I'll DM you the guide" | Not possible (Claude routines can't receive webhooks) | **Workflow 02**: instant private DM with the Kit link, and every comment logged to a `comments-inbox` tab for your daily 15-minute pass |
| Kit list | Kit's own free automations | Not needed. Kit already sends the PDF and the welcome email. |

## Licence, maintenance, cost
- **Licence:** n8n's Sustainable Use License (fair-code). Free to self-host for your own business use; you just can't resell n8n itself. Very actively maintained.
- **n8n Cloud:** Starter is about €20–24/month (2,500 runs). That would double the €20 stack, so not recommended.
- **Self-host (recommended):** the free Community edition on the smallest VPS (Hetzner CX22 class, roughly €4–6/month). Workflow 02 needs an always-on public HTTPS address, so a laptop won't do for it. Running total would be ≈ €25/month. **This spend needs your OK.**

## Files
- `01-ig-stats-to-sheet.json`: 08:30 and 20:30 Madrid. Lists the last 14 days of posts, reels and live stories, pulls reach, views, saves, shares (sends), comments, likes, computes sends/reach and saves/reach, and upserts one row per post by `media_id`. Twice a day so each story is caught before it expires.
- `02-comment-keyword-dm.json`: Meta webhook. Logs every comment; if a comment contains the keyword (default `TOOLS`), sends one private reply with the guide link. Ignores the account's own comments.
- `docker-compose.yml` + `env.example`: n8n + Caddy (auto HTTPS) for the VPS.

No credentials are stored in these files. Placeholders start with `PUT_`.

## What only you can do (≈ 60–90 min once, Claude can walk you through it live)
1. **Approve the VPS spend**, create the server (Ubuntu, Docker installed), and point a subdomain at it (e.g. `n8n.yourdomain.com`; a free DuckDNS name works too).
2. On the server: copy `docker-compose.yml`, create `.env` from `env.example`, run `docker compose up -d`, open `https://<domain>` and create your n8n owner login.
3. **Meta app** (developers.facebook.com, Business type, Facebook Login for Business): give it `instagram_basic`, `instagram_manage_insights`, `instagram_manage_comments`, `instagram_manage_messages`, `pages_show_list`, `pages_read_engagement`, `pages_manage_metadata`. Standard Access is enough because it only touches your own account. Add a privacy-policy URL and switch the app to Live, since Meta only delivers webhooks to Live apps. In the Instagram app: Settings > Messages > Connected tools > allow access to messages.
4. Generate a long-lived **Page access token** (Graph API Explorer → long-lived user token → `/me/accounts`). It doesn't expire. In n8n: Credentials > New > *Query Auth*, name `access_token`, value = the token. Use it on every HTTP node.
5. Google Sheets credential in n8n (Google OAuth). Add two tabs to the tracker Sheet with these header rows:
   - `ig-stats`: `media_id, posted_madrid, type, hook, permalink, reach, views, saves, sends, comments, likes, replies, sends_per_reach, saves_per_reach, error, updated_utc`
   - `comments-inbox`: `received_utc, username, text, media_id, comment_id, is_reply, keyword_dm`
6. Import both JSON files (Workflows > Import from file), replace the `PUT_` values (Instagram business account id, Page id, Kit URL, a long random webhook path, a verify token you invent), pick the credentials on each node, and activate.
7. Meta app > Webhooks > Instagram: callback `https://<domain>/webhook/<your path>`, the same verify token, subscribe to `comments`.

## Workflow 03: reply drafts and your approval (added 21 Oct 2026)
`03-comment-reply-queue.json` drafts a reply for each new `comments-inbox` row with Claude, sends sensitive comments to you, and posts only rows you mark `approved`. Why we built it instead of using the two GitHub repos Surafel sent: `comment-repos-review.md`. The prompt is `comment-reply-prompt.md`.
Extra setup on top of steps 1 to 7: add these columns to the right of `keyword_dm` in `comments-inbox`: `status, category, draft_reply, final_reply, note, drafted_utc, posted_utc, reply_id, attempts` (make `status` a dropdown: awaiting_approval, approved, posted, escalate, skip, rejected, post_failed). Create an Anthropic API key at console.anthropic.com, then in n8n Credentials > New > *Header Auth*, name `x-api-key`, value = the key, and pick it on the "Ask Claude for a draft" node. Pick the `access_token` Query Auth credential on the two Graph nodes and the Google credential on the two Sheet nodes. Import, then activate.
Known gap: if n8n posts a reply but crashes before writing `posted` to the Sheet, the next run posts it again. Rare, and visible on the post.

## What Claude does once it's live
Reads the `ig-stats` tab in the Friday routine instead of asking you for numbers, writes the "comment TOOLS" CTA into one carousel and one reel a week, and drafts replies from `comments-inbox`.

## Known limits
- Meta allows one private reply per comment, within 7 days of the comment.
- Webhook signatures aren't verified (it would need extra n8n settings). The random path keeps it private; worst case is junk rows in `comments-inbox`.
- Instagram's metric names change now and then. A failed metric shows in the `error` column instead of stopping the run.
