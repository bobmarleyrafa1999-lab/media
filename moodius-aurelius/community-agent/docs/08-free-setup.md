# 08 · Free setup: no server (about 40 minutes, once)

**Cost: €0 a month.** GitHub runs the agent every 10 minutes for free (the repo is public, so Actions
minutes are unlimited), Supabase's free plan holds the database, and Resend's free plan sends the
emails. Claude is optional: without a key the agent drafts from its own templates. With a key it uses
Claude Haiku 5.5, at about $0.0005 per comment (well under €1 a month at today's volume).

**What you get:** an email for every comment that matters, with a suggested reply, sentiment, topic,
priority and a link to the comment; urgent emails for crisis or sponsorship comments; a 20:30 digest;
a Monday report. You paste the replies you like into Instagram yourself.

**What you don't get, compared with the €5 server:** no web dashboard or approve button (you reply
in Instagram), alerts arrive within 10 to 20 minutes instead of seconds, and no keyword DMs. You can move to
the server later without losing anything: the database stays the same.

Never paste keys into chat or into a file. They go only into the GitHub secrets screen in step 4.

## 1 · Database (Supabase, 5 min, no card)
1. supabase.com → Start your project → sign in with GitHub → New project. Name `moodius-agent`,
   region London or Frankfurt, generate a strong database password.
2. Click **Connect** → **Session pooler** → copy the URI. Replace `[YOUR-PASSWORD]` with the password
   and add `?sslmode=no-verify` at the end. This is `MOODIUS_DATABASE_URL`.

## 2 · Instagram (Meta app, 15 min, no App Review needed)
Follow docs/03-meta-setup.md steps 1 to 3 only (create the app, add the permissions, generate the token).
Polling your own account works without App Review or webhooks. You need:
- `MOODIUS_IG_ACCESS_TOKEN`: the long-lived token
- `MOODIUS_IG_USER_ID`: the account ID shown next to it

## 3 · Email (Resend, 5 min, no card)
resend.com → sign up **with the same email you want alerts at** → API keys → Create (Sending access).
Without a domain, Resend sends only to your own address, which is all the agent needs.
- `MOODIUS_RESEND_API_KEY`, and `MOODIUS_OWNER_EMAIL` = that same email address

## 4 · Encryption key (1 min)
On your Mac, open Terminal and run `openssl rand -base64 32`. Copy the output: `MOODIUS_ENCRYPTION_KEY`.

## 5 · Put the secrets in GitHub (5 min)
github.com/bobmarleyrafa1999-lab/media → Settings → Secrets and variables → Actions:
- **Secrets** tab → New repository secret, once for each:
  `MOODIUS_DATABASE_URL`, `MOODIUS_IG_ACCESS_TOKEN`, `MOODIUS_IG_USER_ID`, `MOODIUS_RESEND_API_KEY`,
  `MOODIUS_OWNER_EMAIL`, `MOODIUS_ENCRYPTION_KEY`, and optionally `MOODIUS_ANTHROPIC_API_KEY`
  (console.anthropic.com → API keys; needs a small prepaid credit).
- **Variables** tab → New repository variable: `MOODIUS_AGENT_ENABLED` = `true`. This is the on switch.
  Set it to `false` to pause.

## 6 · First run (2 min)
Actions tab → **Moodius comment agent** → Run workflow. A green tick within a few minutes means it worked;
emails for any recent comments arrive straight after. From then on it runs by itself.

## Good to know
- The logs are public (public repo), so the agent hides names, comments and emails in them.
- GitHub pauses scheduled workflows in a repo with no commits for 60 days. This repo gets commits weekly.
- GitHub may run the 10-minute schedule late at busy times. That's normal.
