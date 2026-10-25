#!/usr/bin/env python3
"""Comment analysis and approval queue (Stage 5 prototype).

Reads a CSV of Instagram comments and writes:
  * queue.csv: one row per comment with intent, pillar, the commenter's actual
    question, a matching tidbit, a DRAFT reply and a follow-up question.
    Nothing is ever sent: every row starts as status=awaiting_approval.
  * ideas.md: questions asked more than once, turned into post ideas.
  * idea-briefs/*.json: brief skeletons for those ideas. They fail brief_lint
    on purpose until a real source is added.

Rule-based, no AI and no account access. The intents match the comment agent
(community-agent/src/lib/taxonomy.ts) plus 'reading_request', so the two can
merge later. Crisis, sensitive, sponsorship, commercial and criticism always
go to Surafel with no draft.

Usage:
  python3 comments.py COMMENTS.csv --library 'tidbits/*.csv' --out OUT_DIR
COMMENTS.csv columns: comment_id, post_date, post_hook, commenter, text
(commenter is a hash or handle; it is never written to the outputs).
"""
import argparse
import collections
import csv
import json
import os
import re
import sys

import brief_lint

STOP = set("""a an the and or but if of to in on at for with from by is are was were be been am i you he she
it we they me my your our their this that these those what which who whom how why when where do does did
can could would should will just so very really about any some there here not no yes have has had more
most also than then too into out up down over again ever never any one all much many like get got
you'd i'd i'm it's that's what's don't""".split())

CRISIS = ["kill myself", "end it all", "suicide", "suicidal", "self harm", "self-harm", "want to disappear",
          "don't want to be here", "dont want to be here", "no reason to live", "hurting myself"]
SENSITIVE = ["passed away", "died", "funeral", "grief", "grieving", "abuse", "abused", "cancer", "diagnosed",
             "miscarriage", "divorce"]
SPONSOR = ["collab", "collaboration", "partnership", "sponsor", "pr package", "brand deal", "business enquiry",
           "business inquiry", "promote your"]
COMMERCIAL = ["buy", "price", "how much", "shop", "journal", "guide", "newsletter", "substack", "course"]
SPAM = ["dm me", "check my page", "followers", "crypto", "forex", "promo code", "link in my bio", "earn $",
        "giveaway"]
TROLL = ["cringe", "garbage", "nobody cares", "idiot", "stupid page"]
CRITICISM = ["wrong", "inaccurate", "misquote", "not what he said", "source?", "citation", "made up", "fake quote"]
DISAGREE = ["disagree", "i don't think", "i dont think", "not sure that", "but isn't", "but isnt", "counterpoint",
            "doesn't that", "doesnt that"]
READING = ["what book", "which book", "book recommendation", "recommend a book", "any books", "reading list",
           "what should i read", "which translation", "best translation", "where can i read", "what to read"]
STORY = ["when i was", "my dad", "my mum", "my mom", "my father", "my mother", "i used to", "this happened",
         "last year i", "i remember"]
PRAISE = ["love this", "needed this", "so true", "beautiful", "great post", "thank you", "thanks", "saving this",
          "saved", "amazing"]
HUMAN_ONLY = {"crisis", "sensitive", "sponsorship", "commercial_interest", "criticism"}
PRIORITY = {"crisis": 100, "sponsorship": 95, "sensitive": 85, "commercial_interest": 80, "reading_request": 72,
            "personal_story": 70, "philosophical_disagreement": 65, "genuine_question": 60, "criticism": 55,
            "answer_to_prompt": 50, "appreciation": 25, "other": 20, "troll": 5, "spam": 0}


def has_any(text, phrases):
    return any(p in text for p in phrases)


def classify(text, post_question=""):
    t = " " + re.sub(r"\s+", " ", text.lower()) + " "
    if has_any(t, CRISIS):
        return "crisis"
    if has_any(t, SPAM):
        return "spam"
    if has_any(t, SPONSOR):
        return "sponsorship"
    if has_any(t, SENSITIVE):
        return "sensitive"
    if has_any(t, READING):
        return "reading_request"
    if has_any(t, CRITICISM):
        return "criticism"
    if has_any(t, TROLL):
        return "troll"
    if has_any(t, COMMERCIAL) and "?" in t:
        return "commercial_interest"
    if has_any(t, DISAGREE):
        return "philosophical_disagreement"
    if "?" in t:
        return "genuine_question"
    if has_any(t, STORY):
        return "personal_story"
    if post_question and len(t.split()) <= 25 and not has_any(t, PRAISE):
        return "answer_to_prompt"
    if has_any(t, PRAISE) or re.fullmatch(r"[\W\s]+", t):
        return "appreciation"
    return "other"


def extract_question(text):
    """The commenter's actual question: the last sentence ending in '?', else ''."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    qs = [p.strip() for p in parts if p.strip().endswith("?")]
    return qs[-1] if qs else ""


def terms(text):
    return [w for w in re.findall(r"[a-z][a-z'-]+", text.lower()) if w not in STOP and len(w) > 2]


def pillar_of(text, cfg, post_pillar=""):
    t = " " + text.lower() + " "
    scores = {}
    for key, p in cfg["pillars"].items():
        scores[key] = sum(1 for k in p.get("keywords", []) if re.search(r"(?<![a-z])" + re.escape(k) + r"(?![a-z])", t))
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        key = (post_pillar or "").strip().lower()
        return key if key in cfg["pillars"] else "unknown"
    return best


def match_tidbit(text, lib):
    """Best tidbit by shared terms with its claim, figure and topic. Needs 2+ shared terms."""
    want = set(terms(text))
    best, best_score = None, 1
    for tid, row in lib.items():
        have = set(terms(" ".join([row.get("claim", ""), row.get("figure", ""), row.get("topic", "")])))
        score = len(want & have)
        if score > best_score:
            best, best_score = tid, score
    return best


def draft_reply(intent, pillar, tidbit, cfg):
    if intent in HUMAN_ONLY or intent in ("spam", "troll"):
        return ""
    follow = cfg.get("follow_up_questions", {}).get(pillar, "What made you think of that?")
    if intent == "reading_request":
        return f"DRAFT: Good question. A start: [Surafel to name a book he has read]. {follow}"
    if intent == "philosophical_disagreement":
        follow = "Where do you think it goes wrong?"
    if tidbit:
        row = tidbit[1]
        src = row.get("source", "").split(".")[0][:80]
        caveat = ""
        if cfg["pillars"].get(pillar, {}).get("needs_disclaimer"):
            caveat = " " + cfg["pillars"][pillar]["disclaimer"]
        return f"DRAFT: {row.get('claim', '').strip()} (source: {src}).{caveat} {follow}"
    if intent in ("genuine_question", "philosophical_disagreement"):
        return f"DRAFT: [Answer needs a source; no tidbit matched.] {follow}"
    if intent in ("personal_story", "answer_to_prompt"):
        return f"DRAFT: Thank you for sharing that. {follow}"
    if intent == "appreciation":
        return "DRAFT: Thank you. Glad it landed."
    return ""


NOTES = {
    "crisis": "Reply yourself today, kindly and briefly, and point to help: UK Samaritans 116 123 (free, 24 hours) "
              "or the local emergency number. Never automate this.",
    "sensitive": "Reply yourself; no facts or advice, just acknowledgement.",
    "sponsorship": "Don't reply publicly. Note it for after the OBI declaration.",
    "commercial_interest": "Answer yourself; nothing is for sale until the shop goes live.",
    "criticism": "Check the source first. If we were wrong, say so and correct the post.",
}


def cluster_questions(rows, threshold=0.34):
    """Greedy grouping of question comments whose whole text shares at least a third of their terms (Jaccard)."""
    clusters = []
    for r in rows:
        ts = set(terms(r["text"])) - {"book", "books", "best", "good", "start", "recommend", "actually"}
        if not ts:
            continue
        for c in clusters:
            if c["pillar"] == r["pillar"] and len(ts & c["terms"]) / len(ts | c["terms"]) >= threshold:
                c["rows"].append(r)
                c["terms"] |= ts
                break
        else:
            clusters.append({"pillar": r["pillar"], "terms": set(ts), "rows": [r]})
    return clusters


def run(comments_path, library, out):
    cfg = brief_lint.load_config()
    lib = brief_lint.load_library(library)
    os.makedirs(out, exist_ok=True)
    rows = []
    with open(comments_path, encoding="utf-8-sig", newline="") as f:
        for c in csv.DictReader(f):
            text = c.get("text", "")
            intent = classify(text, c.get("post_question", ""))
            pillar = pillar_of(text + " " + c.get("post_hook", ""), cfg, c.get("post_pillar", ""))
            tid = match_tidbit(text, lib) if intent not in ("spam", "troll", "crisis") else None
            rows.append({
                "comment_id": c.get("comment_id", ""), "post_date": c.get("post_date", ""),
                "post_hook": c.get("post_hook", "")[:80], "text": text, "intent": intent, "pillar": pillar,
                "question": extract_question(text), "tidbit": tid or "",
                "substantive": "yes" if len(terms(text)) >= 6 or intent in ("reading_request", "genuine_question",
                                                                             "philosophical_disagreement",
                                                                             "personal_story") else "no",
                "priority": PRIORITY[intent], "needs_surafel": "yes" if intent in HUMAN_ONLY else "no",
                "draft_reply": draft_reply(intent, pillar, (tid, lib[tid]) if tid else None, cfg),
                "note": NOTES.get(intent, ""),
                "status": "skip" if intent in ("spam", "troll") else "awaiting_approval",
            })
    rows.sort(key=lambda r: -r["priority"])
    with open(os.path.join(out, "queue.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["comment_id"])
        w.writeheader()
        w.writerows(rows)

    asked = [r for r in rows if r["intent"] in ("genuine_question", "reading_request", "philosophical_disagreement")
             and r["question"]]
    ideas = [c for c in cluster_questions(asked) if len(c["rows"]) >= 2]
    ideas.sort(key=lambda c: -len(c["rows"]))

    lines = ["# Content ideas from comments", "",
             f"{len(rows)} comments; {sum(r['substantive'] == 'yes' for r in rows)} substantive; "
             f"{sum(r['needs_surafel'] == 'yes' for r in rows)} need Surafel personally.", ""]
    counts = collections.Counter(r["intent"] for r in rows)
    lines.append("Intents: " + ", ".join(f"{k} {v}" for k, v in counts.most_common()))
    interest = collections.Counter(r["pillar"] for r in rows if r["substantive"] == "yes")
    lines.append("Substantive comments by pillar: " + ", ".join(
        f"{cfg['pillars'].get(k, {}).get('name', k)} {v}" for k, v in interest.most_common()))
    lines += ["", "## Asked more than once", ""]
    if not ideas:
        lines.append("Nothing repeated yet.")
    os.makedirs(os.path.join(out, "idea-briefs"), exist_ok=True)
    for i, c in enumerate(ideas, 1):
        pillar, group = c["pillar"], c["rows"]
        label = ", ".join(sorted(c["terms"])[:4])
        lines.append(f"- **{label}** ({cfg['pillars'].get(pillar, {}).get('name', pillar)}, asked {len(group)} times): "
                     + " / ".join(f"\"{g['text'][:90]}\"" for g in group[:3]))
        brief = {"id": f"IDEA{i:02d}", "pillar": pillar if pillar in cfg["pillars"] else "mind",
                 "format": "carousel", "hook": "", "idea": f"Answer the repeated question: {group[0]['question']}",
                 "evidence": [], "explanation": "", "visual": {"direction": "", "faces": False},
                 "caption": "", "question": "", "follow_reason": "You asked; this answers it.",
                 "from_comments": [g["comment_id"] for g in group]}
        with open(os.path.join(out, "idea-briefs", f"IDEA{i:02d}.json"), "w", encoding="utf-8") as f:
            json.dump(brief, f, indent=2, ensure_ascii=False)
    with open(os.path.join(out, "ideas.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return rows, ideas


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("comments")
    ap.add_argument("--library", action="append", default=[])
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rows, ideas = run(args.comments, args.library, args.out)
    print(f"{len(rows)} comments -> {args.out}/queue.csv; {len(ideas)} repeated questions -> ideas.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
