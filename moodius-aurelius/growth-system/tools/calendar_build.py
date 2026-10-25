#!/usr/bin/env python3
"""Weekly calendar builder (Stage 6 prototype).

Takes a folder of post briefs, keeps only the ones that pass brief_lint, and
fills one week of feed slots so the three pillars meet their shares
(Mind 40%, Body 25%, People 35%). Layouts (--layout, default auto):
  * carousel-daily, until 22 Nov: 12:00 carousel + 18:00 reel daily (Fri 17:00)
  * standard, from 23 Nov: carousels Mon-Fri 12:00, reels Tue/Thu 18:00, Fri 17:00
  * reel-first: the 22 Oct plan
Rules while filling: biggest pillar shortfall first, no same pillar twice in a
row when another fits, at most 4 hurt openers, at least 2 in 3 openers from
curiosity or appreciation, a brief's own "not_before" date respected. Book
reviews count as carousels.

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


# Slot layouts: (dow, time, kind) for every feed slot in the week.
#   carousel-daily: the reach-batch addendum (PR #13). Carousels drove the
#     21-23 Oct reach jump, so a 12:00 carousel and an 18:00 reel run daily
#     until the 19 Nov review.
#   standard: the approved standard week from 20 Nov (90-day plan): carousels
#     Mon-Fri 12:00, reels Tue/Thu 18:00 and Fri 17:00. Story nights are made
#     by hand and are not filled here.
#   reel-first: the 22 Oct plan, kept for comparison.
LAYOUTS = {
    "carousel-daily": [(d, t, k) for d in DAYS for t, k in
                       (("12:00", "carousel"), ("17:00" if d == "Fri" else "18:00", "reel"))],
    "standard": [(d, "12:00", "carousel") for d in DAYS[:5]]
                + [("Tue", "18:00", "reel"), ("Thu", "18:00", "reel"), ("Fri", "17:00", "reel")],
    "reel-first": [(d, t, k) for d in DAYS for t, k in
                   (("12:00", "carousel" if d in ("Wed", "Sun") else "reel"),
                    ("17:00" if d == "Fri" else "18:00", "reel"))],
}
STANDARD_FROM = dt.date(2026, 11, 23)   # first full week of the standard layout


def pick_layout(monday, layout="auto"):
    if layout != "auto":
        return layout
    return "standard" if monday >= STANDARD_FROM else "carousel-daily"


def week_slots(monday, layout="auto"):
    slots = []
    for dow, time, kind in LAYOUTS[pick_layout(monday, layout)]:
        day = monday + dt.timedelta(days=DAYS.index(dow))
        slots.append((day, dow, time, kind))
    return sorted(slots, key=lambda s: (s[0], s[2]))


def targets(cfg, n_slots):
    """Pillar share x slots, rounded by largest remainder so the targets add up to n_slots."""
    raw = {k: p["share"] * n_slots for k, p in cfg["pillars"].items()}
    out = {k: int(v) for k, v in raw.items()}
    for k in sorted(raw, key=lambda k: raw[k] - out[k], reverse=True)[:n_slots - sum(out.values())]:
        out[k] += 1
    return out


def is_hurt(brief):
    return brief.get("opener_tone") == "hurt" or bool(brief.get("hurt_conflict"))


def fits(brief, kind):
    fmt = brief["format"]
    return fmt == kind or (kind == "carousel" and fmt == "book_review")


def build(briefs, cfg, monday, layout="auto"):
    slots = week_slots(monday, layout)
    need = targets(cfg, len(slots))
    cap = cfg["tone"]["max_hurt_or_conflict_per_week"]
    want_light = cfg["tone"]["min_curiosity_or_appreciation_share"]
    pool = list(briefs)
    plan, hurt, light, prev = [], 0, 0, None
    for day, dow, time, kind in slots:
        options = [b for b in pool if fits(b, kind)
                   and day.isoformat() >= b.get("not_before", "")
                   and not (is_hurt(b) and hurt >= cap)]
        if not options:
            plan.append({"date": day.isoformat(), "dow": dow, "time": time, "kind": kind, "brief": None})
            continue
        placed = sum(1 for s in plan if s["brief"])
        behind_on_light = light < want_light * (placed + 1)

        def score(b):
            p = b["pillar"]
            is_light = b.get("opener_tone") in ("curiosity", "appreciation")
            return (need.get(p, 0) > 0, p != prev, is_light or not behind_on_light, need.get(p, 0))

        best = max(options, key=score)
        pool.remove(best)
        need[best["pillar"]] = need.get(best["pillar"], 0) - 1
        hurt += 1 if is_hurt(best) else 0
        light += 1 if best.get("opener_tone") in ("curiosity", "appreciation") else 0
        prev = best["pillar"]
        plan.append({"date": day.isoformat(), "dow": dow, "time": time, "kind": kind, "brief": best})
    return plan, need, hurt, pool


def write_outputs(plan, need, hurt, leftover, rejected, cfg, monday, out):
    os.makedirs(out, exist_ok=True)
    tag = monday.isoformat()
    names = {k: p["name"] for k, p in cfg["pillars"].items()}
    with open(os.path.join(out, f"week-{tag}.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "dow", "slot", "type", "pillar", "series", "format", "hook", "opener_tone", "source",
                    "status", "owner", "brief_id", "experiment", "arm"])
        for s in plan:
            b = s["brief"] or {}
            w.writerow([s["date"], s["dow"], s["time"], s["kind"].upper(), names.get(b.get("pillar"), ""),
                        cfg["series"].get(b.get("series"), {}).get("name", ""), b.get("format", ""),
                        b.get("hook", "EMPTY SLOT"), b.get("opener_tone", ""), " ".join(b.get("evidence", [])),
                        "draft" if b else "empty", "Claude", b.get("id", ""), b.get("experiment", ""),
                        b.get("arm", "")])

    filled = [s for s in plan if s["brief"]]
    lines = [f"# Week of {tag}: draft check", "",
             f"{len(filled)} of {len(plan)} slots filled. Status: draft. Nothing is in Metricool.", "",
             "| pillar | planned | target |", "|---|---|---|"]
    goal = targets(cfg, len(plan))
    for k, p in cfg["pillars"].items():
        have = sum(1 for s in filled if s["brief"]["pillar"] == k)
        lines.append(f"| {p['name']} | {have} | {goal[k]} |")
    cap = cfg["tone"]["max_hurt_or_conflict_per_week"]
    light = sum(1 for s in filled if s["brief"].get("opener_tone") in ("curiosity", "appreciation"))
    share = light / len(filled) if filled else 0
    ok = share >= cfg["tone"]["min_curiosity_or_appreciation_share"] - 1e-9
    lines += ["", f"Hurt/conflict openers: {hurt} (cap {cap}).",
              f"Curiosity or appreciation openers: {light} of {len(filled)} ({share:.0%}; rule is 2 in 3)"
              + ("" if ok else "  **below the rule**") + ".",
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
               "note": "For the account thread. Drafts: queue only through the Friday routine's normal approval.",
               "posts": [{"date": s["date"], "time_madrid": s["time"], "type": s["kind"],
                          "brief_id": s["brief"]["id"], "pillar": s["brief"]["pillar"],
                          "series": s["brief"]["series"], "opener_tone": s["brief"]["opener_tone"],
                          "hook": s["brief"]["hook"], "caption": s["brief"]["caption"],
                          "visual": s["brief"]["visual"], "evidence": s["brief"]["evidence"]}
                         for s in filled]}
    with open(os.path.join(out, f"handoff-{tag}.json"), "w", encoding="utf-8") as f:
        json.dump(handoff, f, indent=2, ensure_ascii=False)
    return "\n".join(lines)


def run(brief_dir, library, monday, out, layout="auto"):
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
    ap.add_argument("--layout", choices=["auto"] + sorted(LAYOUTS), default="auto",
                    help="auto: carousel-daily until 22 Nov, standard from 23 Nov")
    args = ap.parse_args(argv)
    monday = dt.date.fromisoformat(args.week_start)
    if monday.weekday() != 0:
        ap.error("--week-start must be a Monday")
    *_, summary = run(args.briefs, args.library, monday, args.out, args.layout)
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
