"""Hook analysis: classify the opening line, score it, and rank videos.

Free and deterministic (regex cues, no model calls), so it can run on every video before anything
expensive. The text score is a judgement about the words. It is not retention: only Instagram
Insights (own account) or a platform's retention graph can say how long people actually stayed.
"""
import math, re

from . import config, db

WORD = re.compile(r"[\w’']+")


def clean(text):
    """Strip hashtags, emoji and trailing channel noise from a title or caption line."""
    if not text:
        return ""
    text = re.sub(r"#\w+", " ", text)
    text = re.sub(r"[^\w\s’'?!.,:;\-\"“”()/&%$£€]", " ", text)
    text = re.split(r"\s[|•]\s", text)[0]
    return re.sub(r"\s+", " ", text).strip(" -|:")


def readable(text):
    """OCR is often noise on video covers: keep it only when most tokens look like real words."""
    toks = re.findall(r"\S+", text or "")
    good = [t for t in toks if re.fullmatch(r"[A-Za-z’'-]{2,}[.,!?]?", t) and re.search(r"[aeiouyAEIOUY]", t)]
    return len(good) >= 4 and len(good) / max(1, len(toks)) >= 0.7


def hook_text(video):
    """Best available opening text, with where it came from. Order: spoken > on-screen > title > cover OCR."""
    for field, label in (("first_spoken", "first spoken sentence"), ("first_onscreen", "first on-screen text"),
                         ("title", "title (proxy: not the spoken hook)"), ("cover_text", "cover text (OCR)")):
        t = clean(video.get(field))
        if field == "cover_text" and not readable(t):
            continue
        if t:
            return t, label
    return "", "none"


def usable_outlier(video):
    """The outlier ratio only counts above the noise floor."""
    if video.get("outlier_ratio") is None:
        return None
    if (video.get("views") or 0) < config.MIN_VIEWS_FOR_SIGNAL or \
            (video.get("creator_median_views") or 0) < config.MIN_BASELINE_MEDIAN:
        return None
    return video["outlier_ratio"]


def relevant(video, text):
    blob = " ".join(str(x) for x in (text, video.get("title"), video.get("creator"), video.get("query")) if x).lower()
    return bool(re.search(config.NICHE, blob)) or any(re.search(p, blob) for p in config.PILLARS.values())


def classify(text, visual_opening=None):
    low = text.lower()
    scores, cues = {}, {}
    for cat, pats in config.CUES.items():
        for pat, w in pats:
            if re.search(pat, low):
                scores[cat] = scores.get(cat, 0) + w
                cues.setdefault(cat, []).append(pat)
    if visual_opening and re.search(config.VISUAL_DISRUPTION_CUES, visual_opening.lower()):
        scores["visual_disruption"] = scores.get("visual_disruption", 0) + 3
        cues.setdefault("visual_disruption", []).append("visual_opening annotation")
    if not scores:
        return {"category": None, "secondary": None, "confidence": 0.0, "cues": {}, "note": "no cue matched: unclassified"}
    ranked = sorted(scores.items(), key=lambda kv: -kv[1])
    top, top_s = ranked[0]
    second, second_s = ranked[1] if len(ranked) > 1 else (None, 0)
    # a question that is mainly a question stays "unexpected question" only if nothing stronger fired
    confidence = round(min(1.0, 0.35 + 0.15 * top_s - 0.1 * second_s / max(top_s, 1)), 2)
    return {"category": top, "secondary": second, "confidence": max(0.2, confidence), "cues": cues}


def structure(text):
    low = text.lower()
    for name, pat in config.STRUCTURES:
        if re.search(pat, low):
            return name
    return "statement"


def _clip(x):
    return max(0.0, min(5.0, round(x, 2)))


def _trigrams(text):
    w = [x.lower() for x in WORD.findall(text)]
    return {tuple(w[i:i + 3]) for i in range(len(w) - 2)}


def score(text, others=(), visual_opening=None):
    """Six 0-5 scores and a 0-100 total, each with the reason it moved."""
    low = text.lower()
    words = WORD.findall(text)
    n = len(words)
    reasons = {}

    concrete = len(re.findall(config.CONCRETE, low))
    abstract = len(re.findall(config.ABSTRACT, low))
    spec = 2.5 + 0.9 * concrete - 0.8 * abstract + (0.5 if re.search(r"\byou\b", low) else 0)
    reasons["specificity"] = f"{concrete} concrete, {abstract} abstract words"

    clar = 5.0 if 4 <= n <= 12 else 4.0 if n <= 16 else 3.0 if n <= 22 else 1.5
    if n < 4:
        clar -= 1
    if sum(1 for w in words if w.isupper() and len(w) > 2) >= 3:
        clar -= 1
    reasons["clarity"] = f"{n} words"

    mine = _trigrams(text)
    overlap = max((len(mine & _trigrams(o)) / max(1, len(mine)) for o in others if o and o != text), default=0)
    cliche = sum(1 for p in config.CLICHES if re.search(p, low))
    orig = 4.5 - 4 * overlap - 1.5 * cliche
    reasons["originality"] = f"{overlap:.0%} trigram overlap with the library, {cliche} cliché(s)"

    emo_hits = [k for k, p in config.EMOTIONS.items() if re.search(p, low)]
    emo = 1.5 + 1.2 * len(emo_hits) + (0.8 if re.search(r"\b(you|your)\b", low) else 0)
    reasons["emotional"] = ", ".join(emo_hits) or "no emotion word"

    vis = 3.0 + 0.7 * len(re.findall(config.SCENE_WORDS, low)) - 2.0 * bool(re.search(config.FACE_DEPENDENT, low))
    if visual_opening:
        vis += 0.5
    reasons["visual"] = "renders as text over still/archival imagery" if vis >= 3 else "depends on a face or a live demo"

    pillars = [k for k, p in config.PILLARS.items() if re.search(p, low)]
    off = [p for p in config.OFF_BRAND if re.search(p, low)]
    align = 2.0 + 1.0 * min(2, len(pillars)) + 0.5 * bool(emo_hits)
    flags = []
    for key, ev in config.OWN_EVIDENCE.items():
        if re.search(ev["cue"], low):
            align += {"other_person_conflict": 0.5, "list_opener": -1.0, "two_branch": 0.5}[key]
            flags.append(key)
    if off:
        align = 0
        flags.append("off_brand")
    reasons["alignment"] = (", ".join(pillars) or "no pillar keyword") + (f"; off-brand: {off}" if off else "")

    s = {"specificity": _clip(spec), "clarity": _clip(clar), "originality": _clip(orig),
         "emotional": _clip(emo), "visual": _clip(vis), "alignment": _clip(align)}
    weights = {"specificity": 0.2, "clarity": 0.15, "originality": 0.15, "emotional": 0.2, "visual": 0.1, "alignment": 0.2}
    total = round(sum(s[k] * w for k, w in weights.items()) / 5 * 100, 1)
    return s, total, reasons, pillars, emo_hits, flags


def priority(outlier, hook_score):
    """Proven over-performance first. log2 so 4x is twice as strong as 2x; missing baseline counts as 1x."""
    o = outlier if outlier and outlier > 0 else 1.0
    return round(60 * max(0.0, min(1.0, (math.log2(o) + 1) / 4)) + 0.4 * hook_score, 1)


def confidence_label(video, cls):
    evidence = []
    if video.get("outlier_ratio") is not None and usable_outlier(video) is None:
        evidence.append(f"outlier {video['outlier_ratio']}x below the noise floor (ignored)")
    elif video.get("outlier_ratio") is not None:
        evidence.append(f"outlier {video['outlier_ratio']}x vs creator median of {int(video['creator_median_views']):,} views")
    else:
        evidence.append("no creator baseline")
    if video.get("views") is not None:
        evidence.append(f"{int(video['views']):,} views")
    evidence.append(f"hook text from {cls['source']}")
    strong_data = usable_outlier(video) is not None and video.get("published")
    real_hook = cls["source"] in ("first spoken sentence", "first on-screen text")
    level = "high" if strong_data and real_hook and cls["confidence"] >= 0.6 else \
            "medium" if strong_data or real_hook else "low"
    return level, "; ".join(evidence)


def editorial_overrides():
    """Category / structure set by a person (or Claude) who looked at the video. Wins over the regex."""
    import glob, json, os
    out = {}
    for path in sorted(glob.glob(os.path.join(config.EDITORIAL, "*.json"))):
        for vid, f in json.load(open(path)).get("videos", {}).items():
            out[vid] = {k: f[k] for k in ("category", "structure", "pick") if f.get(k) is not None}
    return out


def analyse(con, cycle=None):
    """Classify and score every short-form video. Returns the number analysed."""
    where = "WHERE short_form = 1 OR (short_form IS NULL AND platform != 'podcast')"
    if cycle:
        where += " AND cycle = ?"
    vids = db.rows(con, f"SELECT * FROM videos {where}", (cycle,) if cycle else ())
    texts = {v["id"]: hook_text(v) for v in vids}
    corpus = [t for t, _ in texts.values()]
    own = [r["hook"] for r in db.rows(con, "SELECT hook FROM own_posts") if r["hook"]]
    ed = editorial_overrides()
    for v in vids:
        text, source = texts[v["id"]]
        if not text:
            continue
        cls = classify(text, v.get("visual_opening"))
        cls["source"] = source
        o = ed.get(v["id"], {})
        if o.get("category"):
            if o["category"] != cls["category"]:
                cls["secondary"] = cls["category"]
            cls["category"], cls["confidence"] = o["category"], 0.9
            cls["cues"] = {**cls["cues"], "editorial": ["category set after viewing"]}
        s, total, reasons, pillars, emos, flags = score(text, corpus + own, v.get("visual_opening"))
        level, evidence = confidence_label(v, cls)
        uo = usable_outlier(v)
        rel = relevant(v, text)
        strong = int((uo or 0) >= config.OUTLIER_ABOVE and "off_brand" not in flags and rel and v.get("in_window") != 0)
        db.upsert(con, "hooks", {
            "video_id": v["id"], "hook_text": text, "hook_text_source": source, "category": cls["category"],
            "secondary": cls["secondary"], "structure": o.get("structure") or structure(text), "pick": o.get("pick"), "classifier_confidence": cls["confidence"],
            "cues": {"cues": cls["cues"], "reasons": reasons}, **s, "hook_score": total,
            "priority": priority(uo, total) if rel else 0, "relevant": int(rel), "pillar": pillars[0] if pillars else None,
            "tone": ", ".join(emos) or None, "flags": flags or None, "confidence": level, "evidence": evidence,
            "strong": strong}, key="video_id")
    db.reindex_fts(con)
    con.commit()
    return len(vids)


def classify_own(con):
    """Same classifier on the account's own reels, so patterns can be checked against real retention."""
    out = []
    for p in db.rows(con, "SELECT * FROM own_posts WHERE hook IS NOT NULL"):
        cls = classify(p["hook"])
        out.append({**p, "category": cls["category"], "structure": structure(p["hook"]),
                    "flags": [k for k, ev in config.OWN_EVIDENCE.items() if re.search(ev["cue"], p["hook"].lower())]})
    return out
