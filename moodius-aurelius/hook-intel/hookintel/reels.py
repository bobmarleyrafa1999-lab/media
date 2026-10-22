"""Reel generation pipeline.

Two steps, so nothing expensive runs by accident:
  briefs  top patterns -> writing briefs (pattern, proven examples, template, the 7 hold rules)
  build   a written script batch -> QC, timestamps, storyboard, subtitles (SRT), overlay specs,
          three engine-ready hook variants, and the existing reels-engine QC gate

Scripts are written by a person or by Claude in a session (no API key, no per-call cost). The
pipeline refuses scripts that break the brand or the hold rules; it never publishes anything.
"""
import json, os, re, subprocess

from . import config, db

WORD = re.compile(r"[\w’']+")
OVERLAY = {  # kind -> how the card is set (reels-engine design tokens)
    "hook": "Playfair Display 84 pt, Bone #F3EFE7 on Slate #1B1F24, upper third, rise-and-fade in 0.3 s",
    "question": "Playfair Display 88 pt, Bone, upper third, thin Ember #C9742E rule under it",
    "body": "Inter Medium 60 pt, Bone, centred, max 2 lines",
    "labelled": "Ember label (Inter SemiBold 30 pt, caps) over Inter Medium 60 pt body",
    "quote": "Cormorant/Playfair italic 64 pt, Bone, centred",
    "cite": "Inter Medium 32 pt, Ash #B8B3A9, lower third",
    "cta": "Inter SemiBold 50 pt, Bone, lower third",
    "pause": "no text: image only, slow 2% drift",
}
RULES = {
    "1": "Promise = cover = card 1", "2": "Opens a gap the viewer half-knows", "3": "Starts mid-scene",
    "4": "Three acts", "5": "One mid-sentence cut", "6": "Re-engage at 7-9 s", "7": "Pays off in the hook's own words",
}
REQUIRED = ["id", "title", "pattern_id", "pillar", "hooks", "cards", "shots", "broll_keywords", "first_frame",
            "sound", "caption", "first_comment", "hashtags", "intended_emotion", "save_share_reason", "source", "rules"]


def words(s):
    return len(WORD.findall(s))


def need_s(text):
    return 0.4 + words(text) / 4.5          # reels-engine reading-speed rule


def briefs(con, n=5):
    pats = db.rows(con, "SELECT * FROM patterns ORDER BY rank LIMIT ?", (n,))
    out = []
    for p in pats:
        ex = json.loads(p["examples"] or "[]")
        out.append({"pattern_id": p["id"], "pattern": p["name"], "rank": p["rank"],
                    "median_outlier": p["median_outlier"], "own_evidence": p["own_evidence"],
                    "template": p["template"], "examples": ex,
                    "write": "3 hooks (<=12 words, card 1 = cover), 15-30 s of cards, card 2 by 3 s part-pays the hook, "
                             "midpoint break at 7-9 s, payoff reuses the hook's key word. Quotes only from public-domain "
                             "translations with book+section; otherwise 'Idea: ... · Moodius words'.",
                    "rules": RULES})
    return out


def validate(s):
    """Return (errors, warnings) for one hook-intel script."""
    err, warn = [], []
    for k in REQUIRED:
        if k not in s or s[k] in (None, "", []):
            err.append(f"missing {k}")
    if err:
        return err, warn
    if len(s["hooks"]) != 3:
        err.append("needs exactly 3 hooks")
    for i, h in enumerate(s["hooks"]):
        if words(h) > 12:
            err.append(f"hook {'abc'[i]} has {words(h)} words (max 12)")
    if re.search(config.STRUCTURES[1][1], s["hooks"][0].lower()):
        warn.append("hook a is a numbered list: lowest 3s hold on this account")
    total = sum(c[1] for c in s["cards"])
    if not 15 <= total <= 45:
        err.append(f"length {total:.1f}s outside 15-45 s")
    for i, (text, dur, kind) in enumerate(s["cards"]):
        if kind not in OVERLAY:
            err.append(f"card {i + 1}: unknown kind {kind}")
        if kind not in ("cite", "pause") and dur < need_s(text) - 0.2:
            err.append(f"card {i + 1} too fast ({dur}s for {words(text)} words)")
    t = 0.0
    for i, (_, dur, _) in enumerate(s["cards"]):
        if i == 1 and t > 3.2:
            warn.append(f"card 2 starts at {t:.1f}s; the hook should be part-paid by 3 s")
        t += dur
    shot_cards = {sh["card"] for sh in s["shots"]}
    if missing := [i + 1 for i in range(len(s["cards"])) if i + 1 not in shot_cards]:
        err.append(f"no shot for cards {missing}")
    if len(s["hashtags"]) != 3:
        err.append("needs exactly 3 hashtags")
    passed = [k for k, v in s["rules"].items() if v]
    if len(passed) < 6:
        err.append(f"passes {len(passed)}/7 hold rules (needs 6)")
    blob = " ".join([c[0] for c in s["cards"]] + s["hooks"] + [s["caption"], s["first_comment"]]).lower()
    for p in config.OFF_BRAND + config.CLICHES:
        if re.search(p, blob):
            err.append(f"off-brand or cliché phrase: {p}")
    src = s["source"]
    if any(c[2] == "quote" for c in s["cards"]):
        if src.get("type") != "quote" or not src.get("translation"):
            err.append("quote card needs source.type 'quote' with a public-domain translation")
    if src.get("type") == "idea" and not any(c[2] == "cite" and "Idea:" in c[0] for c in s["cards"]):
        err.append("idea needs an 'Idea: ... · Moodius words' cite card")
    for sh in s["shots"]:
        if not sh.get("rights"):
            err.append(f"shot for card {sh['card']} has no rights note")
    return err, warn


def timeline(s, hook_index=0):
    cards = [list(c) for c in s["cards"]]
    cards[0][0] = s["hooks"][hook_index]
    cards[0][1] = max(cards[0][1], round(need_s(cards[0][0]), 1))
    t, out = 0.0, []
    for i, (text, dur, kind) in enumerate(cards):
        out.append({"n": i + 1, "start": round(t, 2), "end": round(t + dur, 2), "text": text, "kind": kind})
        t += dur
    return out


def srt(tl):
    def ts(x):
        ms = int(round(x * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    return "\n".join(f"{c['n']}\n{ts(c['start'])} --> {ts(c['end'])}\n{c['text']}\n"
                     for c in tl if c["kind"] != "pause")


def engine_script(s, variant):
    """reels-engine schema (scripts/batch-01.json) for one hook variant."""
    i = "abc".index(variant)
    tl = timeline(s, i)
    return {"id": f"{s['id']}{variant}", "slug": s["slug"] + ("" if variant == "a" else f"-{variant}"),
            "format": s.get("format", "R2"), "series": s.get("series", "Hook Intel"), "pillar": s["pillar"],
            "hook": s["hooks"][i], "hook_b": s["hooks"][(i + 1) % 3],
            "cards": [[c["text"], round(c["end"] - c["start"], 2), c["kind"]] for c in tl],
            "visual": s["first_frame"], "footage": s.get("footage", ""), "texture": s.get("texture", "grain"),
            "audio": s.get("audio", {"engine": "ambient", "mood": "room", "seed": 300 + i}), "source": s["source"],
            "evidence": s.get("evidence", ""), "caption": s["caption"], "first_comment": s["first_comment"],
            "hashtags": s["hashtags"], "cta": s.get("cta", "send"), "max_s": max(20.5, round(tl[-1]["end"] + 0.5, 1)),
            "length_s": tl[-1]["end"]}


def storyboard_md(s, err, warn, engine_note):
    tl = timeline(s)
    shots = {sh["card"]: sh for sh in s["shots"]}
    lines = [f"# {s['id']} · {s['title']}", "",
             f"**Pattern:** {s['pattern_id']} · **Pillar:** {s['pillar']} · **Length:** {tl[-1]['end']:.1f} s · "
             f"**Intended emotion:** {s['intended_emotion']}", "",
             f"**Why it gets saved or sent:** {s['save_share_reason']}", ""]
    if s.get("pattern_evidence"):
        lines += [f"**Evidence behind the pattern:** {s['pattern_evidence']}", ""]
    lines += ["## Three hooks (A/B/C: only card 1 and the cover change)", ""]
    lines += [f"- **{'ABC'[i]}** {h} ({words(h)} words)" for i, h in enumerate(s["hooks"])]
    lines += ["", "## Script, shot list and overlays", "",
              "| # | Time | On screen | Visual (shot) | Overlay | Rights |", "|---|---|---|---|---|---|"]
    for c in tl:
        sh = shots.get(c["n"], {})
        lines.append(f"| {c['n']} | {c['start']:.1f}-{c['end']:.1f}s | {c['text'].replace(chr(10), ' / ')} | {sh.get('visual', '')}"
                     f"{' · ' + sh['motion'] if sh.get('motion') else ''} | {OVERLAY[c['kind']]} | {sh.get('rights', '')} |")
    lines += ["", f"**First frame:** {s['first_frame']}", "",
              f"**B-roll search keywords:** {', '.join(s['broll_keywords'])}", "",
              f"**Sound design:** {s['sound']}", "",
              "**Subtitles:** the cards are the subtitles (no voice). Burned in by reels-engine; the SRT is for "
              "accessibility upload and for any voiced cut.", "",
              "## Caption", "", s["caption"], "", f"First comment: {s['first_comment']}", "",
              f"Hashtags: {' '.join(s['hashtags'])}", "",
              f"**Source:** {json.dumps(s['source'], ensure_ascii=False)}", "",
              "## Hold rules", ""]
    lines += [f"- [{'x' if s['rules'].get(k) else ' '}] {k}. {v}" for k, v in RULES.items()]
    lines += ["", "## QC", "", f"Errors: {'; '.join(err) or 'none'}", f"Warnings: {'; '.join(warn) or 'none'}",
              f"reels-engine check: {engine_note}", "",
              "_Status: draft. Nothing is scheduled or published until the owner picks it._"]
    return "\n".join(lines) + "\n"


def engine_check(path):
    if not os.path.exists(config.ENGINE):
        return "skipped (reels-engine not found next to hook-intel; run from the project folder)"
    p = subprocess.run(["python3", config.ENGINE, "check", path], capture_output=True, text=True, timeout=300)
    out = (p.stdout + p.stderr).strip()
    return ("passed" if p.returncode == 0 else "FAILED") + (": " + " | ".join(out.splitlines()[-6:]) if out else "")


def build(con, path, out_dir=None, run_engine=True):
    batch = json.load(open(path))
    name = batch.get("batch") or os.path.splitext(os.path.basename(path))[0]
    out_dir = out_dir or os.path.join(config.REPORTS, "reels", name)
    os.makedirs(os.path.join(out_dir, "srt"), exist_ok=True)
    results, engine_batch = [], {"batch": name, "written": batch.get("written"), "schema": "reels-engine 1.2",
                                 "scripts": []}
    for s in batch["scripts"]:
        err, warn = validate(s)
        results.append((s, err, warn))
        if not err:
            engine_batch["scripts"] += [engine_script(s, v) for v in "abc"]
    engine_path = os.path.join(out_dir, f"{name}-engine.json")
    json.dump(engine_batch, open(engine_path, "w"), indent=1, ensure_ascii=False)
    note = engine_check(engine_path) if run_engine and engine_batch["scripts"] else "not run"
    summary = []
    for s, err, warn in results:
        for i, v in enumerate("abc"):
            if not err:
                open(os.path.join(out_dir, "srt", f"{s['id']}{v}.srt"), "w").write(srt(timeline(s, i)))
        open(os.path.join(out_dir, f"{s['id']}.md"), "w").write(storyboard_md(s, err, warn, note))
        db.upsert(con, "concepts", {"id": s["id"], "batch": name, "pattern_id": s.get("pattern_id"),
                                    "title": s.get("title"), "pillar": s.get("pillar"),
                                    "status": "draft" if not err else "rejected",
                                    "qc": {"errors": err, "warnings": warn, "engine": note}, "data": s})
        summary.append({"id": s["id"], "title": s.get("title"), "errors": err, "warnings": warn})
    con.commit()
    return summary, note, out_dir
