#!/usr/bin/env python3
"""Build readable repurposing packages and machine files from packages/NN.json.

Usage: python3 scripts/render_packages.py

Writes, for every packages/NN.json:
  packages/NN-<slug>.md          the human-readable package (what Surafel approves)
And once for all packages:
  packages/reels-batch.json      reel scripts in reels-engine schema (engine.py check|render)
  queue/approval-queue.csv       one row per asset, status "awaiting approval"
Nothing here schedules or publishes anything.
"""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower().replace("'", "").replace("’", "")).strip("-")


def render_md(p):
    L = [f"# Package {p['n']:02d}: {p['title']}", "",
         f"Essay: `{p['essay']}` · A/B alternative headline: **{p['ab_alt']}** · IG highlight: {p['pillar']}",
         "", "Status: **draft, awaiting approval**. Nothing here is scheduled.", ""]
    L += ["## 1. Two reels (engine formats A–F)", ""]
    for r in p["reels"]:
        L += [f"### {r['id']} · Format {r['format']} ({r['series']}) · {r['length_s']} s", "",
              "| # | Card | Seconds | Kind |", "|---|---|---|---|"]
        for i, (t, d, k) in enumerate(r["cards"], 1):
            L.append(f"| {i} | {t.replace(chr(10), ' / ')} | {d} | {k} |")
        L += ["", f"- **Hook B (for A/B):** {r['hook_b']}", f"- **Visual:** {r['visual']}",
              f"- **Audio:** ambient `{r['audio']['mood']}` (seed {r['audio']['seed']})",
              f"- **Evidence:** {r['evidence']}", f"- **First comment:** {r['first_comment']}",
              f"- **Hashtags:** {' '.join(r['hashtags'])}", "", "**Caption**", "", "```", r["caption"], "```", ""]
    L += [f"## 2. {len(p['carousel'])}-slide carousel (1080×1350)", "", "| Slide | Role | Main text | Small text | Component |", "|---|---|---|---|---|"]
    for i, (role, main, small, comp) in enumerate(p["carousel"], 1):
        L.append(f"| {i} | {role} | {main} | {small} | {comp} |")
    L += ["", "**Caption**", "", "```", p["carousel_caption"], "```", ""]
    # cards, stories and pins are optional (the 12-title batch asked for reels, carousel and Notes only)
    if p.get("cards"):
        L += ["## 3. Quote / insight cards (1080×1350, also 1080×1920 for stories)", ""]
        for i, (text, who) in enumerate(p["cards"], 1):
            L.append(f"{i}. {text} — *{who}*")
        L.append("")
    if p.get("stories"):
        L += ["## 4. Story concepts", ""]
        for i, (kind, text, how) in enumerate(p["stories"], 1):
            L.append(f"{i}. **{kind}:** \"{text}\" {how}")
        L.append("")
    if p.get("pins"):
        L += ["## 5. Pinterest pins (1000×1500, link to the essay)", ""]
        for i, (t, d) in enumerate(p["pins"], 1):
            L.append(f"{i}. **{t}** ({len(t)} chars). {d}")
        L.append("")
    L += ["## 6. Three Substack Notes (aim 250–300 characters; embed the post, don't link out)", ""]
    for i, n in enumerate(p["notes"], 1):
        L.append(f"{i}. {n} *({len(n)} chars)*")
    v = p["visuals"]
    L += ["", "## 7. A/B headline", "", f"Selected: **{p['title']}** · Alternative: **{p['ab_alt']}**", "",
          "## 8. Visuals, type and music", "", f"- **Look:** {v['look']}", f"- **Type:** {v['type']}",
          f"- **Music mood:** {v['music']}", f"- **Pinterest:** {v['pinterest']}",
          "- **Always:** Slate #1B1F24, Graphite #2A2F36, Charcoal #3A4049, Bone #F3EFE7, Ash #B8B3A9, Ember #C9742E once; Playfair + Inter; 96 px margins; no statues, marble, gold or gradients.", ""]
    return "\n".join(L)


def main():
    packs = [json.loads(f.read_text(encoding="utf-8")) for f in sorted((ROOT / "packages").glob("[0-9][0-9].json"))]
    reels, queue = [], []
    for p in packs:
        md = ROOT / "packages" / f"{p['n']:02d}-{slug(p['title'])}.md"
        md.write_text(render_md(p), encoding="utf-8")
        reels += p["reels"]
        base = dict(package=p["n"], essay=p["title"], status="awaiting approval", approved_by="", scheduled_for="")
        queue.append(dict(base, asset="essay", platform="Substack", detail=p["essay"]))
        queue += [dict(base, asset=f"reel {r['id']}", platform="Instagram", detail=r["hook"]) for r in p["reels"]]
        queue.append(dict(base, asset="carousel", platform="Instagram", detail=p["carousel"][0][1]))
        queue += [dict(base, asset=f"card {i}", platform="IG story/Threads/Pinterest", detail=c[0]) for i, c in enumerate(p.get("cards", []), 1)]
        queue += [dict(base, asset=f"story {i}", platform="Instagram", detail=s[1]) for i, s in enumerate(p.get("stories", []), 1)]
        queue += [dict(base, asset=f"pin {i}", platform="Pinterest", detail=t) for i, (t, _) in enumerate(p.get("pins", []), 1)]
        queue += [dict(base, asset=f"note {i}", platform="Substack Notes", detail=n[:80]) for i, n in enumerate(p["notes"], 1)]
        print("package", md.relative_to(ROOT))
    batch = {"batch": "substack-essays", "written": "2026-10-21",
             "schema": "reels-engine formats-AF (engine.py 1.2)", "scripts": reels}
    (ROOT / "packages" / "reels-batch.json").write_text(json.dumps(batch, indent=1, ensure_ascii=False), encoding="utf-8")
    (ROOT / "queue").mkdir(exist_ok=True)
    with open(ROOT / "queue" / "approval-queue.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["package", "essay", "asset", "platform", "detail", "status", "approved_by", "scheduled_for"])
        w.writeheader()
        w.writerows(queue)
    print(f"{len(reels)} reels, {len(queue)} queue rows")


if __name__ == "__main__":
    main()
