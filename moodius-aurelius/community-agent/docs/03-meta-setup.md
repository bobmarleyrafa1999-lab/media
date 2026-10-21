# 03 · Meta Developer setup (Surafel, about 45 minutes plus review wait)

Uses the **Instagram API with Instagram Login** (no Facebook Page needed). Check each screen against
Meta's current docs as you go: Meta renames menus often. Nothing here costs money.

## Before you start
- @moodiusaurelius must be a **professional** account (Creator or Business) and **public**.
- The agent must be deployed first (docs/04), because Meta checks the webhook URL when you save it.

## 1 · Create the app (10 min)
1. developers.facebook.com → My Apps → **Create app**.
2. Use case: **Manage messaging & content on Instagram**. App type: Business. Name: anything neutral
   (e.g. "MA Community Tools"); it is visible in App Review, not to followers.
3. In the app: **Instagram → API setup with Instagram login**.

## 2 · Permissions
Add these three, and nothing else:

| Permission | Used for |
|---|---|
| `instagram_business_basic` | read posts, captions, insights |
| `instagram_business_manage_comments` | read comments, publish approved replies |
| `instagram_business_manage_messages` | the one private reply per comment for JOURNAL/READ/REFLECT/NEWSLETTER |

## 3 · Token (5 min)
1. API setup → **Generate access token** → log in as @moodiusaurelius → allow.
2. Copy the token into `.env` as `IG_ACCESS_TOKEN` and the account ID shown into `IG_USER_ID`.
3. App settings → Basic → **App secret** → `META_APP_SECRET`. (Paste these into `.env` on the server only.
   Never into chat, docs or the project folder.)
4. The token lasts 60 days. The agent refreshes it every Sunday and stores the new one encrypted.
   If a refresh fails you get an email.

## 4 · Webhooks (5 min)
1. API setup → **Configure webhooks**.
2. Callback URL: `https://<AGENT_HOST>/api/webhooks/instagram`. Verify token: the value of `META_VERIFY_TOKEN`.
3. Subscribe to the field **comments**. (Optionally `messages` later.)
4. In `/admin/settings` run the job **subscribe-webhooks** (it calls `POST me/subscribed_apps?subscribed_fields=comments`).

## 5 · Live mode and App Review (the slow part)
- Comment webhooks are only delivered when the app is **Live** and has **Advanced Access** to
  `instagram_business_manage_comments`. Advanced Access needs **App Review**, and Meta may ask for
  **Business Verification** (any registered business details; for an anonymous brand use the legal
  entity that owns it).
- Until then the agent still works: the **poll-comments** job reads new comments every 5 minutes with
  your own token (standard access is enough for your own account). The webhook simply makes it instant.
- For App Review you need: a privacy policy URL (`/privacy-newsletter` covers the newsletter; add the
  comment-processing paragraph from docs/07), a screencast of `/admin/queue` showing a comment being
  drafted and a human approving it, and the use-case text below.

> We read comments on our own Instagram account, draft replies with AI, and a human approves each reply
> before it is published. When a commenter types a keyword we asked for (e.g. JOURNAL) we send one private
> reply with the resource link. We do not message anyone who did not comment, and we do not store data
> beyond 12 months.

## 6 · Switch on, one step at a time
1. Keep `AGENT_MODE=draft_only` and `DM_KEYWORDS_ENABLED=false`. Watch a week of drafts.
2. Turn DMs on (`DM_KEYWORDS_ENABLED=true`) once the free resources and newsletter page are live.
3. Only then consider mode B (assisted) in `/admin/settings`.

## Not tested yet
None of this has been tested against the real Instagram API: there are no credentials in this project.
Everything was tested with signed mock webhooks and mock Graph responses. The first real run should be
in draft-only mode with the email inbox open.
