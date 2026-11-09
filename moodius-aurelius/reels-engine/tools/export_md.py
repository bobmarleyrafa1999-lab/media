#!/usr/bin/env python3
"""Turn a scripts batch JSON into the readable script sheet (no AI call needed).

    python3 export_md.py ../scripts/batch-01.json ../05-scripts-batch-01.md
"""
import json, sys

FORMATS = {"R1": "Quiet Truth", "R2": "Situation → old line", "R3": "Myth vs the text",
           "R4": "Dry humour", "R5": "One book, one idea"}


def main(src, dst):
    b = json.load(open(src, encoding="utf-8"))
    out = [f"# Reel scripts, {b['batch']} ({b['written']})", "",
           "Machine-readable source: `scripts/" + src.split("/")[-1] + "` (render with `tools/engine.py`). "
           "Every script passed the quality gate in `06-pipeline.md`.", "",
           "| # | Reel | Format | Pillar | Length | Source |", "|---|---|---|---|---|---|"]
    for s in b["scripts"]:
        src_ = s["source"]
        cite = f"{src_['author']}, {src_['work']} {src_['section']}" if src_["type"] == "quote" else f"{src_['type']}: {src_['author']}"
        out.append(f"| {s['id']} | {s['hook']} | {s['format']} {FORMATS[s['format']]} | {s['pillar']} | {s['length_s']}s | {cite[:70]} |")
    for s in b["scripts"]:
        out += ["", "---", "", f"## {s['id']} · {s['hook']}", "",
                f"**Format** {s['format']} {FORMATS[s['format']]} · **Pillar** {s['pillar']} · **Length** {s['length_s']}s · **CTA** {s['cta']}",
                f"**Hook B (test arm):** {s['hook_b']}", "", "| Card | On screen | Seconds | Style |", "|---|---|---|---|"]
        for i, (t, d, k) in enumerate(s["cards"], 1):
            out.append(f"| {i} | {t.replace('|', '/')} | {d} | {k} |")
        a = s["audio"]
        audio = f"ambient bed, mood '{a['mood']}', seed {a['seed']}" if a.get("engine", "ambient") == "ambient" else f"score.py '{a['style']}'"
        src_ = s["source"]
        out += ["", f"**Visual:** {s['visual']}", f"**Audio:** {audio}. No voice-over.",
                f"**Source ({src_['type']}):** {src_['author']}, *{src_['work']}* {src_['section']} · {src_.get('translation', '')}",
                "", "**Caption**", "", "> " + s["caption"].replace("\n", "\n> "), "",
                "**Hashtags** " + " ".join(s["hashtags"]), "", f"**First comment:** {s['first_comment']}"]
    open(dst, "w", encoding="utf-8").write("\n".join(out) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
