#!/usr/bin/env bash
# One-time Cloudflare setup and first deploy, in test mode. Safe to re-run.
# Needs: `npx wrangler login` done once in a browser, and scripts/configure.mjs run first.
#   bash scripts/setup-cloudflare.sh
# It never asks for or stores Stripe, Resend or other keys: you paste those into the
# Cloudflare dashboard yourself (see business/setup/your-part.md).
set -euo pipefail
cd "$(dirname "$0")/.."
W="npx --yes wrangler@4.146.0"

if grep -q 'REPLACE_WITH_YOUR_DOMAIN' wrangler.toml; then
  echo "Run scripts/configure.mjs --domain ... first." >&2; exit 1
fi

echo "== D1 database"
if grep -q 'REPLACE_WITH_ID_FROM_wrangler_d1_create' wrangler.toml; then
  id=$($W d1 create moodius 2>&1 | grep -oE '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' | head -1 || true)
  if [ -z "$id" ]; then
    id=$($W d1 list --json | node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{const d=JSON.parse(s).find(x=>x.name==="moodius");console.log(d?d.uuid:"")})')
  fi
  [ -n "$id" ] || { echo "Could not create or find the D1 database." >&2; exit 1; }
  sed -i.bak "s/REPLACE_WITH_ID_FROM_wrangler_d1_create/$id/g" wrangler.toml && rm -f wrangler.toml.bak
  echo "database id $id written to wrangler.toml"
fi
$W d1 migrations apply moodius --remote

echo "== R2 bucket (private) and product files"
$W r2 bucket create moodius-products 2>/dev/null || echo "bucket already exists"
for f in A5-digital A4-print; do
  $W r2 object put "moodius-products/products/the-unexamined-self/v1/The-Unexamined-Self-$f.pdf" \
    --file "../journal/out/The-Unexamined-Self-$f.pdf" --remote
done

echo "== Pages project"
$W pages project create moodius --production-branch main 2>/dev/null || echo "project already exists"

echo "== Admin token (saved to ~/moodius-admin-token.txt, readable only by you)"
if [ ! -f .admin-token-set ]; then
  token=$(node -e 'console.log(require("crypto").randomBytes(32).toString("hex"))')
  printf '%s' "$token" | $W pages secret put ADMIN_TOKEN --project-name moodius
  printf '%s' "$(node -e 'console.log(require("crypto").randomBytes(16).toString("hex"))')" | $W pages secret put IP_HASH_SALT --project-name moodius
  touch .admin-token-set
  ( umask 077; printf '%s\n' "$token" > "$HOME/moodius-admin-token.txt" )
  echo "saved; move it into your password manager and delete the file"
fi

echo "== Build and deploy"
npm run deploy

echo
echo "Done. Next: add the Stripe and Resend keys in the Cloudflare dashboard (business/setup/your-part.md),"
echo "then make a test purchase with card 4242 4242 4242 4242."
