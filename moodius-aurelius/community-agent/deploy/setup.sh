#!/usr/bin/env bash
# One-command setup for the Moodius comment agent on a fresh Ubuntu 24.04 server.
#
#   curl -fsSL https://raw.githubusercontent.com/bobmarleyrafa1999-lab/media/claude/project-thread-ycspok/moodius-aurelius/community-agent/deploy/setup.sh | sudo bash
#
# What it does: installs Docker, downloads the agent, generates every internal secret, asks you for
# an admin password and your email, starts everything in DRAFT-ONLY mode with DMs OFF, and prints
# the two values you paste into Meta. Instagram/Claude/email keys are added afterwards with
# deploy/set-key.sh (hidden input, nothing is echoed or logged). Safe to run again.
set -euo pipefail

REPO="${REPO:-https://github.com/bobmarleyrafa1999-lab/media.git}"
BRANCH="${BRANCH:-claude/project-thread-ycspok}"
DIR=/opt/moodius
APP="$DIR/media/moodius-aurelius/community-agent"

[ "$(id -u)" = 0 ] || { echo "Run with sudo."; exit 1; }
exec < /dev/tty   # read answers from the keyboard even when piped from curl

echo "== 1/5 Docker"
if ! command -v docker >/dev/null; then curl -fsSL https://get.docker.com | sh; fi
apt-get install -y -qq git openssl >/dev/null

echo "== 2/5 Download the agent"
mkdir -p "$DIR"
if [ -d "$DIR/media/.git" ]; then
  git -C "$DIR/media" fetch -q origin "$BRANCH" && git -C "$DIR/media" checkout -q -B "$BRANCH" "origin/$BRANCH"
else
  if ! git clone -q --depth 1 --branch "$BRANCH" "$REPO" "$DIR/media" 2>/dev/null; then
    echo "The repository is private. Create a read-only GitHub token (Settings > Developer settings >"
    echo "Fine-grained tokens > only the 'media' repo > Contents: Read-only) and paste it here."
    read -rsp "GitHub token (hidden): " GHT; echo
    git clone -q --depth 1 --branch "$BRANCH" "https://x-access-token:${GHT}@github.com/bobmarleyrafa1999-lab/media.git" "$DIR/media"
    git -C "$DIR/media" remote set-url origin "https://x-access-token:${GHT}@github.com/bobmarleyrafa1999-lab/media.git"
    unset GHT
  fi
fi
cd "$APP"

echo "== 3/5 Settings"
if [ ! -f .env ]; then
  # Copy the template without the explanatory end-of-line comments.
  sed -E '/^[A-Z_]+=/ s/[[:space:]]+#.*$//' .env.example > .env
  set_env() { # key value: replaces the line KEY=... (value may contain / and +)
    local k="$1" v="$2"
    if grep -q "^$k=" .env; then
      python3 - "$k" "$v" <<'PY'
import sys,re
k,v=sys.argv[1],sys.argv[2]
s=open('.env').read()
s=re.sub(rf'^{re.escape(k)}=.*$', lambda m: f'{k}={v}', s, flags=re.M)
open('.env','w').write(s)
PY
    else echo "$k=$v" >> .env; fi
  }
  IP=$(curl -fsS4 https://api.ipify.org || hostname -I | awk '{print $1}')
  DEFAULT_HOST="agent.$(echo "$IP" | tr . -).sslip.io"
  read -rp "Web address for the agent [$DEFAULT_HOST] (Enter = use this free one): " HOST; HOST=${HOST:-$DEFAULT_HOST}
  read -rp "Your email (alerts and digests go here; use the one you'll sign up to Resend with): " OWNER
  read -rp "Website address if the shop is already live, e.g. https://moodius.com (Enter = not yet): " SITE; SITE=${SITE:-https://$HOST}
  while :; do read -rsp "Admin password for /admin (12+ characters, hidden): " PW; echo; [ ${#PW} -ge 12 ] && break; echo "Too short."; done
  set_env AGENT_HOST "$HOST"
  set_env APP_BASE_URL "https://$HOST"
  set_env OWNER_EMAIL "$OWNER"
  set_env PUBLIC_SITE_URL "$SITE"
  # Resend's test sender works for emails to your own address with no domain to verify.
  set_env EMAIL_FROM "Moodius Agent <onboarding@resend.dev>"
  set_env OUTREACH_FROM ""
  set_env ADMIN_PASSWORD "$PW"; unset PW
  set_env POSTGRES_PASSWORD "$(openssl rand -hex 24)"
  set_env SESSION_SECRET "$(openssl rand -hex 32)"
  set_env ENCRYPTION_KEY "$(openssl rand -base64 32)"
  set_env CRON_SECRET "$(openssl rand -hex 24)"
  set_env META_VERIFY_TOKEN "$(openssl rand -hex 16)"
  set_env REVENUE_WEBHOOK_SECRET "$(openssl rand -hex 24)"
  set_env IMPORT_TOKEN "$(openssl rand -hex 24)"
  set_env N8N_ENCRYPTION_KEY "$(openssl rand -hex 24)"
  set_env AGENT_MODE draft_only
  set_env DM_KEYWORDS_ENABLED false
  set_env DATABASE_URL "postgres://moodius@db:5432/moodius"
  chmod 600 .env
else
  echo ".env already exists: keeping it."
fi

echo "== 4/5 Build and start (first build takes 3-5 minutes)"
docker compose up -d --build db
docker compose run --rm app npx tsx scripts/migrate.ts
docker compose run --rm app npx tsx scripts/seed.ts
docker compose up -d --build

echo "== 5/5 Check"
envget() { grep -m1 "^$1=" .env | cut -d= -f2-; }
AGENT_HOST=$(envget AGENT_HOST); META_VERIFY_TOKEN=$(envget META_VERIFY_TOKEN)
for i in $(seq 1 30); do curl -fsS "https://$AGENT_HOST/api/health" >/dev/null 2>&1 && break; sleep 5; done
curl -fsS "https://$AGENT_HOST/api/health" && echo || echo "Not reachable over HTTPS yet: check that ports 80 and 443 are open, then run: docker compose logs caddy"

cat <<MSG

Done. The agent is running in DRAFT-ONLY mode with DMs OFF. Nothing is posted without you.

  Admin:            https://$AGENT_HOST/admin
  Meta callback URL: https://$AGENT_HOST/api/webhooks/instagram
  Meta verify token: $META_VERIFY_TOKEN

Next: add your keys one by one (hidden input):
  sudo $APP/deploy/set-key.sh
MSG
