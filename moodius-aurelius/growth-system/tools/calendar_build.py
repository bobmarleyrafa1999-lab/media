#!/usr/bin/env python3
"""Weekly calendar builder (Stage 6 prototype).

Takes a folder of post briefs, keeps only the ones that pass brief_lint, and
fills one week of 14 feed slots so the pillar mix meets pillars.json.
Layouts (--layout):
  * carousel-daily (default): 12:00 carousel every day, 18:00 reel (Fri 17:00)
  * reel-first: 12:00 reels Mon/Tue/Thu/Fri/Sat, carousels Wed and Sun 12:00
Book reviews count as carousels.
Rules while filling: biggest pillar shortfall first, never the same pillar in
two consecutive slots when another fits, hurt/conflict reels capped, a brief's
own "not_before" date respected.

Writes OUT_DIR/week-YYYY-MM-DD.csv (tracker columns), week-YYYY-MM-DD.md
(the check), and handoff-YYYY-MM-DD.json for the account thread. Every row
is status "draft": this script never touches Metricool.

Usage:
  python3 calendar_build.py --briefs DIR --week-start 2026-11-09 \
      --library 'tidbits/*.csv' --out OUT_DIR
"""
import argparse
import csv
import datetime as dt
import glob
import json
import os
import sys

import brief_lint

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


# Slot layouts. "carousel-daily" matches the Friday-routine addendum from the
# reach-batch work (PR #13): carousels drove the 21-23 Oct reach jump, so a
# 12:00 carousel runs every day until the 19 Nov review. "reel-first" is the
# 22 Oct plan (12 reels, carousels Wed and Sun).
LAYOUTS = {
    "carousel-daily": {dow: "carousel" for dow in DAYS},
    "reel-first": {dow: ("carousel" if dow in ("Wed", "Sun") else "reel") for dow in DAYS},
}


def week_slots(monday, layout="carousel-daily"):
    noon = LAYOUTS[layout]
    slots = []
    for i, dow in enumerate(DAYS):
        day = monday + dt.timedelta(days=i)
        slots.append((day, dow, "12:00", noon[dow]))
        slots.append((day, dow, "17:00" if dow == "Fri" else "18:00", "reel"))
    return slots


def fits(brief, kind):
    fmt = brief["format"]
    return fmt == kind or (kind == "carousel" and fmt == "book_review")


def build(briefs, cfg, monday, layout="carousel-daily"):
    pillars = cfg["pillars"]
    need = {k: p["per_week"] for k, p in pillars.items()}
    cap = pillars["human_mind"]["max_hurt_conflict_per_week"]
    pool = list(briefs)
    plan, hurt, prev = [], 0, None
    for day, dow, time, kind in week_slots(monday, layout):
        options = [b for b in pool if fits(b, kind)
                   and day.isoformat() >= b.get("not_before", "")
                   and not (b.get("hurt_conflict") and hurt >= cap)]
        if not options:
            plan.append({"date": day.isoformat(), "dow": dow, "time": time, "kind": kind, "brief": None})
            continue

        def score(b):
            p = b["pillar"]
            return (need.get(p, 0) > 0, p != prev, need.get(p, 0))

        best = max(options, key=score)
        pool.remove(best)
        need[best["pillar"]] = need.get(best["pillar"], 0) - 1
        hurt += 1 if best.get("hurt_conflict") else 0
        prev = best["pillar"]
        plan.append({"date": day.isoformat(), "dow": dow, "time": time, "kind": kind, "brief": best})
    return plan, need, hurt, pool


def write_outputs(plan, need, hurt, leftover, rejected, cfg, monday, out):
    os.makedirs(out, exist_ok=True)
    tag = monday.isoformat()
    names = {k: p["name"] for k, p in cfg["pillars"].items()}
    with open(os.path.join(out, f"week-{tag}.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "dow", "time_madrid", "type", "format", "hook_or_prompt", "source", "pillar",
                    "status", "owner", "brief_id", "experiment", "arm"])
        for s in plan:
            b = s["brief"] or {}
            w.writerow([s["date"], s["dow"], s["time"], s["kind"].upper(), b.get("format", ""),
                        b.get("hook", "EMPTY SLOT"), " ".join(b.get("evidence", [])),
                        names.get(b.get("pillar"), ""), "draft" if b else "empty", "Claude",
                        b.get("id", ""), b.get("experiment", ""), b.get("arm", "")])

    filled = [s for s in plan if s["brief"]]
    lines = [f"# Week of {tag}: draft check", "",
             f"{len(filled)} of {len(plan)} slots filled. Status: draft. Nothing is in Metricool.", "",
             "| pillar | planned | target |", "|---|---|---|"]
    for k, p in cfg["pillars"].items():
        have = sum(1 for s in filled if s["brief"]["pillar"] == k)
        lines.append(f"| {p['name']} | {have} | {p['per_week']} |")
    cap = cfg["pillars"]["human_mind"]["max_hurt_conflict_per_week"]
    lines += ["", f"Hurt/conflict posts: {hurt} (cap {cap}).",
              f"Every caption ends on a 1-3 word question: yes (checked by brief_lint)."]
    empty = [s for s in plan if not s["brief"]]
    if empty:
        lines += ["", "**Empty slots** (no passing brief of the right format):"]
        lines += [f"- {s['dow']} {s['date']} {s['time']} {s['kind']}" for s in empty]
    short = {k: v for k, v in need.items() if v > 0}
    if short:
        lines += ["", "**Pillars short of target:** " + ", ".join(f"{names[k]} {v}" for k, v in short.items())]
    if rejected:
        lines += ["", "**Briefs that failed the checker** (fix, then rebuild):"]
        for bid, errs in rejected:
            lines.append(f"- {bid}: " + "; ".join(errs[:3]))
    if leftover:
        lines += ["", "Passing briefs left for next week: " + ", ".join(b["id"] for b in leftover)]
    with open(os.path.join(out, f"week-{tag}.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    handoff = {"week_start": tag, "status": "draft_not_scheduled",
               "note": "For the account thread. Schedule only after Surafel's OK on the five-pillar mix.",
               "posts": [{"date": s["date"], "time_madrid": s["time"], "type": s["kind"],
                          "brief_id": s["brief"]["id"], "pillar": s["brief"]["pillar"],
                          "hook": s["brief"]["hook"], "caption": s["brief"]["caption"],
                          "visual": s["brief"]["visual"], "evidence": s["brief"]["evidence"]}
                         for s in filled]}
    with open(os.path.join(out, f"handoff-{tag}.json"), "w", encoding="utf-8") as f:
        json.dump(handoff, f, indent=2, ensure_ascii=False)
    return "\n".join(lines)


def run(brief_dir, library, monday, out, layout="carousel-daily"):
    cfg = brief_lint.load_config()
    lib = brief_lint.load_library(library)
    ok, rejected = [], []
    for path in sorted(glob.glob(os.path.join(brief_dir, "*.json"))):
        with open(path, encoding="utf-8") as f:
            brief = json.load(f)
        errors, _ = brief_lint.lint(brief, cfg, lib)
        if errors:
            rejected.append((brief.get("id", os.path.basename(path)), errors))
        else:
            ok.append(brief)
    plan, need, hurt, leftover = build(ok, cfg, monday, layout)
    summary = write_outputs(plan, need, hurt, leftover, rejected, cfg, monday, out)
    return plan, need, hurt, rejected, summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--briefs", required=True)
    ap.add_argument("--week-start", required=True, help="a Monday, YYYY-MM-DD")
    ap.add_argument("--library", action="append", default=[])
    ap.add_argument("--out", required=True)
    ap.add_argument("--layout", choices=sorted(LAYOUTS), default="carousel-daily",
                    help="carousel-daily (default until the 19 Nov review) or reel-first")
    args = ap.parse_args(argv)
    monday = dt.date.fromisoformat(args.week_start)
    if monday.weekday() != 0:
        ap.error("--week-start must be a Monday")
    *_, summary = run(args.briefs, args.library, monday, args.out, args.layout)
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
