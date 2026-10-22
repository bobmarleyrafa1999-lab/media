#!/usr/bin/env bash
# Adds or replaces one secret in .env with hidden input, then restarts the agent.
# Usage: sudo ./set-key.sh            (menu)
#        sudo ./set-key.sh IG_ACCESS_TOKEN
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f .env ] || { echo "Run deploy/setup.sh first."; exit 1; }

KEYS=(IG_ACCESS_TOKEN IG_USER_ID META_APP_SECRET ANTHROPIC_API_KEY RESEND_API_KEY EMAIL_FROM)
HELP=(
  "Instagram long-lived token (Meta app > Instagram > API setup > Generate token)"
  "Instagram account ID (shown next to the token)"
  "Instagram app secret (Meta app > App settings > Basic)"
  "Claude API key (console.anthropic.com > API keys)"
  "Resend API key (resend.com > API keys)"
  "Sender, e.g. Moodius Agent <agent@yourdomain.com> (domain verified in Resend)"
)

KEY="${1:-}"
if [ -z "$KEY" ]; then
  for i in "${!KEYS[@]}"; do
    state="empty"; grep -q "^${KEYS[$i]}=..*" .env && state="set"
    printf "%d) %-18s [%s]  %s\n" $((i+1)) "${KEYS[$i]}" "$state" "${HELP[$i]}"
  done
  read -rp "Which one (number)? " n
  KEY="${KEYS[$((n-1))]}"
fi

if [ "$KEY" = "EMAIL_FROM" ] || [ "$KEY" = "IG_USER_ID" ]; then read -rp "$KEY: " VAL
else read -rsp "$KEY (hidden): " VAL; echo; fi
[ -n "$VAL" ] || { echo "Nothing entered; unchanged."; exit 0; }

python3 - "$KEY" "$VAL" <<'PY'
import sys,re
k,v=sys.argv[1],sys.argv[2]
s=open('.env').read()
if re.search(rf'^{re.escape(k)}=', s, flags=re.M):
    s=re.sub(rf'^{re.escape(k)}=.*$', lambda m: f'{k}={v}', s, flags=re.M)
else:
    s+=f'\n{k}={v}\n'
open('.env','w').write(s)
PY
unset VAL
chmod 600 .env
docker compose up -d app worker >/dev/null
echo "$KEY saved. Agent restarted. Health:"
sleep 5; curl -fsS "https://$(grep -m1 "^AGENT_HOST=" .env | cut -d= -f2-)/api/health" || true; echo
