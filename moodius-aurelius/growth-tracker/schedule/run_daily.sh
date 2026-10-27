#!/bin/bash
# Daily collection on your Mac (used by the launchd job). Retries once after 10 minutes.
# Logs: logs/schedule.log (the token never appears in logs).
cd "$(dirname "$0")/.." || exit 1
source .venv/bin/activate
mkdir -p logs
IG_ID="$(cat ig_user_id.txt 2>/dev/null)"
run() { python -m moodius_growth collect-meta --ig-user-id "$IG_ID" --days-back 3; }
{
  echo "=== $(date '+%Y-%m-%d %H:%M %Z') ==="
  if ! run; then echo "first try failed, retrying in 10 minutes"; sleep 600; run || echo "FAILED again"; fi
  if [ "$(date +%u)" = "1" ]; then python -m moodius_growth report; fi   # Mondays: weekly report
} >> logs/schedule.log 2>&1
