#!/usr/bin/env bash
# One-time setup. Creates .venv, installs yt-dlp, checks SQLite FTS5, runs the tests.
set -euo pipefail
cd "$(dirname "$0")"
python3 -c 'import sys; assert sys.version_info >= (3, 10), "Python 3.10+ needed"'
python3 -m venv .venv
. .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
python3 -c 'import sqlite3; c=sqlite3.connect(":memory:"); c.execute("create virtual table t using fts5(x)"); print("SQLite FTS5: ok")'
[ -f .env ] || cp .env.example .env
command -v ffmpeg >/dev/null || echo "note: ffmpeg not found (only needed to render reels with reels-engine)"
command -v tesseract >/dev/null || echo "note: tesseract not found (optional: reads text on Shorts covers; brew install tesseract)"
python3 -m unittest discover -s tests -q
echo
echo "Ready. Activate with:  source .venv/bin/activate"
echo "Then: bin/discover-hooks  |  bin/analyse-hooks  |  python3 -m hookintel dashboard"
