# Comment automation: the two GitHub repos, reviewed (21 Oct 2026)

**Verdict:** use neither repo as it is. Keep our own n8n workflows (02 for the TOOLS keyword DM, new 03 for reply drafts) and borrow two ideas from devgine. Replies start in draft-only mode: Claude drafts, you approve in the Sheet, n8n posts.

## The two repos
| | arunbaghel-git/Instagram-comment-automation-agent | devgine/n8n-ig-comments-management |
|---|---|---|
| How it talks to Instagram | Official Graph API + Meta webhook. No scraping, so no ban risk from the method itself | Official Graph API + Meta webhook, core n8n nodes only |
| What it actually does | Reads a number 1 to 5 in a comment (also Hindi words "ek, do, teen") and posts a canned public reply per post type (wedding, birthday, tea). Then DMs the same text. The README promises GPT-4o-mini, but the workflow has no AI node at all | DMs **every** commenter (a keyword message, or a default one if no keyword matches), then posts a random canned public reply. Postgres table to avoid doing it twice, retries with backoff, test payloads |
| Licence | None. The README's "License" heading is empty, so legally all rights reserved | MIT |
| Upkeep | One commit (9 Jul 2026), one author | Four commits over two days (15 to 16 Aug 2026) |
| Security notes | Verify token hardcoded in the export; depends on a third-party community node (`@mookielianhd/n8n-nodes-instagram`); builds the DM JSON by pasting text into a string, which breaks on quotes | Token read from environment variables; no signature check on webhooks (documented, not built) |
| Fit for Moodius | Poor. Built for a different job, nothing to adapt | Good plumbing, wrong behaviour: auto-DMing every commenter and random canned public replies is the "comment bot" pattern 11-community.md rules out, and it would make replies sound identical |

## What we take from devgine
1. **One action per comment.** Meta can deliver the same webhook twice. Workflow 03 treats the row that already has a status as the truth for that comment, so a duplicate row is never drafted or posted twice.
2. **Counted retries.** A failed post is tried at most three times, then marked `post_failed` with Meta's error, instead of looping.

Postgres isn't worth adding at our volume; the tracker Sheet already holds the `comments-inbox` tab and you can see and edit it from your phone.

## What we built instead
`03-comment-reply-queue.json`, every 10 minutes:
1. Reads new rows in `comments-inbox` (workflow 02 logs every comment there).
2. A word filter sends anything about grief, self-harm, crisis, abuse or illness straight to you as `escalate`, without asking Claude. Spam, links and tag-only comments become `skip`.
3. Everything else goes to Claude with the post's caption and the Moodius reply rules (`comment-reply-prompt.md`). Claude can still choose `escalate` or `skip`. A draft with a link, over 400 characters or empty is sent to you instead.
4. You change `status` to `approved` (optionally rewriting the text in `final_reply`). On the next run n8n posts it as a public reply and writes `posted`, the time and Meta's reply id.

Nothing is posted without your `approved`. That is mode A in your brief. Modes B and C (auto-posting low-risk categories) should only switch on after a couple of weeks of drafts you'd have approved unchanged.

## Cost
- Claude API: model `claude-opus-5-5` at low effort, roughly 1,500 tokens in and 300 out per comment, so about 1 to 2 cents a comment. At 20 comments a day that is about €4 to €10 a month. Switching `MODEL` in the Config node to `claude-haiku-5-5` cuts it to well under €1 a month, with plainer drafts. Your call.
- n8n: no extra cost; it runs on the same VPS as workflows 01 and 02 (about €4 to €6 a month, still awaiting your OK).
