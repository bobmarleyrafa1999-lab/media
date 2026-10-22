"""Group analysed hooks into patterns (category x structure) and rank them.

Rank = how far the pattern's videos beat their own creators' medians (proven), times how often it
appears (log), plus a small prior from Moodius's own retention data where the account has used it.
"""
import json, math, statistics

from . import config, db, hooks

NAMES = {
    ("psychological_revelation", "people_who"): "\"People who...\" psychological portrait",
    ("emotional_recognition", "second_person_scene"): "Second-person scene you recognise",
    ("contrarian", "negation_reframe"): "It isn't X, it's Y reframe",
    ("unexpected_question", "question"): "Direct personal question",
    ("curiosity_gap", "statement"): "Withheld reason",
    ("uncomfortable_truth", "second_person_scene"): "Hard truth about you",
    ("story_opening", "named_thinker"): "Thinker's moment, told as a scene",
    ("story_opening", "first_person_story"): "First-person confession",
    ("identity_challenge", "people_who"): "Which kind are you",
    ("psychological_revelation", "hidden_cost"): "The hidden cost of an everyday habit",
    ("contrarian", "imperative_stop"): "Stop doing X (a correction, not advice)",
    ("curiosity_gap", "insider_reveal"): "Insider reveal: what X actually is or does",
    ("philosophical_paradox", "versus"): "X vs Y: two things you thought were one",
    ("psychological_revelation", "question"): "Why does a feeling run backwards?",
    ("unexpected_question", "question"): "A question about something you were told as fact",
}

TEMPLATES = {  # Moodius-shaped skeletons; slots in {braces}. Written for text-on-image reels, no face.
    "psychological_revelation": "People who {behaviour} usually learned it {where}.",
    "emotional_recognition": "You {small specific act} again. Here's what it was really about.",
    "contrarian": "It isn't {the thing they blame}. It's {the thing underneath}.",
    "unexpected_question": "When did you last {honest act} without {the usual defence}?",
    "curiosity_gap": "The reason you {pattern} isn't {the obvious reason}.",
    "uncomfortable_truth": "{Person} isn't going to {thing you wait for}. {Turn}.",
    "identity_challenge": "Two people {same situation}. Only one of them is {state}.",
    "philosophical_paradox": "The more you {chase X}, the less {X} you have.",
    "story_opening": "{Thinker} was {situation}. He wrote {one line} that night.",
    "visual_disruption": "{Cut from a still archival frame to a single word card}",
}


def build(con, cycle=None, top=5):
    hk = db.rows(con, """SELECT h.*, v.outlier_ratio, v.views, v.creator_median_views, v.url, v.creator, v.platform, v.cycle
                         FROM hooks h JOIN videos v ON v.id = h.video_id
                         WHERE h.category IS NOT NULL AND h.relevant = 1 AND COALESCE(v.in_window, 1) = 1"""
                 + (" AND v.cycle = ?" if cycle else ""),
                 (cycle,) if cycle else ())
    own = hooks.classify_own(con)
    groups = {}
    for h in hk:
        if "off_brand" in (h.get("flags") or ""):
            continue
        groups.setdefault((h["category"], h["structure"]), []).append(h)
    out = []
    for (cat, struct), members in groups.items():
        outs = [o for o in (hooks.usable_outlier(m) for m in members) if o]
        med = statistics.median(outs) if outs else None
        own_m = [o for o in own if o["category"] == cat or o["structure"] == struct]
        own_note = None
        if own_m:
            holds = [o["view_rate_3s"] for o in own_m if o["view_rate_3s"] is not None]
            watch = [o["avg_watch_s"] for o in own_m if o["avg_watch_s"] is not None]
            own_note = (f"Moodius used it {len(own_m)}x: median 3s hold {statistics.median(holds):.0f}%, "
                        f"median avg watch {statistics.median(watch):.1f}s") if holds and watch else None
        own_all = [o["view_rate_3s"] for o in own if o["view_rate_3s"] is not None]
        prior = 0.0
        if own_m and own_all:
            delta = statistics.median([o["view_rate_3s"] for o in own_m if o["view_rate_3s"] is not None] or [0]) \
                - statistics.median(own_all)
            prior = max(-0.3, min(0.3, delta / 30))
        if struct == "list_opener":
            prior -= 0.3   # lowest hold on the account (doc 16)
        # median log-outlier, shrunk toward 0 (= creator's normal) when few videos back it
        lift = statistics.median(math.log2(o) for o in outs) * len(outs) / (len(outs) + 3) if outs else 0.0
        sc = round(lift + prior + statistics.mean(m["hook_score"] for m in members) / 100, 3)
        ex = sorted(members, key=lambda m: -(m["priority"] or 0))[:4]
        out.append({
            "id": f"{cat}:{struct}", "cycle": cycle, "category": cat, "structure": struct,
            "name": NAMES.get((cat, struct), f"{config.CATEGORIES[cat]} / {struct.replace('_', ' ')}"),
            "description": f"{len(members)} hooks; {len(outs)} with a creator baseline",
            "n": len(members), "n_with_baseline": len(outs), "median_outlier": round(med, 2) if med else None,
            "best_outlier": max(outs) if outs else None, "own_evidence": own_note, "score": sc,
            "examples": [{"video_id": m["video_id"], "hook": m["hook_text"], "outlier": hooks.usable_outlier(m),
                          "url": m["url"], "creator": m["creator"]} for m in ex],
            "template": TEMPLATES.get(cat)})
    out.sort(key=lambda p: -p["score"])
    con.execute("DELETE FROM patterns" + (" WHERE cycle = ?" if cycle else ""), (cycle,) if cycle else ())
    for i, p in enumerate(out, 1):
        p["rank"] = i
        db.upsert(con, "patterns", {**p, "examples": json.dumps(p["examples"], ensure_ascii=False)})
    con.commit()
    return out[:top], out
