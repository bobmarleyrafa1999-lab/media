"""Recount theme/opener/tone shares and the 22 Oct rule from data/content-tags.csv.

    python3 tools/count.py
"""
import collections
import csv
import datetime
import pathlib

ROWS = list(csv.DictReader(open(pathlib.Path(__file__).parent.parent / "data" / "content-tags.csv")))


def share(rows, label):
    n = len(rows)
    theme = collections.Counter(r["theme"] for r in rows)
    opener = collections.Counter(r["opener"] for r in rows)
    tone = collections.Counter(r["tone"] for r in rows)
    struggle = theme["HURT"] + theme["STRUGGLE"]
    stoic = sum(r["tradition"].startswith("Stoic") for r in rows)
    print(f"{label:<10} n={n:>3}  hurt+struggle {struggle/n:4.0%}  pain opener {opener['PAIN']/n:4.0%}"
          f"  negative {tone['negative']/n:4.0%}  stoic-only {stoic/n:4.0%}  {dict(theme)}")


for s in ["published", "queue", "plan", "essay"]:
    share([r for r in ROWS if r["set"] == s], s)
share([r for r in ROWS if r["set"] != "essay"], "all feed")

print("\nweek        posts  hurt/conflict reels (max 4)  appreciation/curiosity openers (need 67%)")
weeks = collections.defaultdict(list)
for r in ROWS:
    if r["set"] in ("queue", "plan"):
        d = datetime.date.fromisoformat(r["date"])
        weeks[d - datetime.timedelta(d.weekday())].append(r)
for monday, rows in sorted(weeks.items()):
    hurt = sum(r["format"] == "REEL" and r["hurt_conflict"] == "Y" for r in rows)
    good = sum(r["opener"] in ("CURIOSITY", "APPRECIATION") for r in rows)
    print(f"{monday}  {len(rows):>5}  {hurt:>27}  {good:>3} = {good/len(rows):.0%}")
