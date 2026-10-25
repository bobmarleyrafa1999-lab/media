#!/usr/bin/env python3
"""Post-brief checker for Moodius Aurelius.

Every post starts as a small JSON brief (see briefs/examples/). This script
checks a brief against the approved 90-day plan (25 Oct 2026) before anything is
drafted, rendered or scheduled:

  * the eight parts every post needs (hook, idea, evidence, explanation,
    visual direction, caption, discussion question, reason to follow)
  * one of the three pillars (Mind, Body, People) and one of the six series,
    with each series' own rules (book label, film credit, named tradition)
  * Body posts carry an evidence label and no doses; medical history carries
    its disclaimer
  * the caption ends on a 1-3 word question
  * every evidence id exists in the tidbit library; hand-read ids are flagged
  * no red-pill / young-men framing, no miracle-cure wording, no faces
  * book reviews only for books Surafel has actually read

Usage:
  python3 brief_lint.py BRIEF.json [BRIEF.json ...] --library 'path/to/tidbits/*.csv'
Exit code 1 if any brief has an error. Warnings never block.
"""
import argparse
import csv
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PILLARS_PATH = os.path.join(HERE, "..", "pillars.json")
REQUIRED = ["id", "pillar", "series", "format", "opener_tone", "hook", "idea", "evidence", "explanation",
            "visual", "caption", "question", "follow_reason"]


def load_config(path=PILLARS_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_library(patterns):
    """Return {tidbit_id: row} from every CSV matching the glob patterns."""
    lib = {}
    for pattern in patterns:
        for path in sorted(glob.glob(pattern)):
            with open(path, encoding="utf-8-sig", newline="") as f:
                for row in csv.DictReader(f):
                    if row.get("id"):
                        lib[row["id"].strip()] = row
    return lib


def words(text):
    return re.findall(r"[\w'’-]+", text or "")


def contains_phrase(text, phrase):
    return re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text, re.IGNORECASE) is not None


def lint(brief, cfg, lib):
    errors, warnings = [], []

    for key in REQUIRED:
        value = brief.get(key)
        if value in (None, "", [], {}):
            errors.append(f"missing '{key}'")
    if errors:
        return errors, warnings

    pillar = cfg["pillars"].get(brief["pillar"])
    if not pillar:
        errors.append(f"pillar '{brief['pillar']}' is not one of {sorted(cfg['pillars'])}")
        return errors, warnings
    if brief["format"] not in cfg["formats"]:
        errors.append(f"format '{brief['format']}' is not one of {cfg['formats']}")
    series = cfg["series"].get(brief["series"])
    if not series:
        errors.append(f"series '{brief['series']}' is not one of {sorted(cfg['series'])}")
        return errors, warnings
    if brief["pillar"] not in series["pillars"]:
        errors.append(f"{series['name']} runs in {series['pillars']}, not '{brief['pillar']}'")
    if brief["format"] not in series["formats"]:
        errors.append(f"{series['name']} is made as {series['formats']}, not '{brief['format']}'")
    if brief["opener_tone"] not in cfg["opener_tones"]:
        errors.append(f"opener_tone must be one of {cfg['opener_tones']}")

    # Hook: short, on screen at frame 0, no numbered-list opener.
    hook_words = words(brief["hook"])
    if len(hook_words) > cfg["hook_max_words"]:
        warnings.append(f"hook is {len(hook_words)} words; aim for {cfg['hook_max_words']} or fewer")
    if hook_words and re.match(r"^\d", hook_words[0]):
        warnings.append("hook opens on a number; numbered openers held worst in the Words That Hold data")

    # Question: 1-3 words, ends with '?', and is the last line of the caption.
    q = brief["question"].strip()
    if not q.endswith("?"):
        errors.append("question must end with '?'")
    qn = len(words(q))
    if qn < 1 or qn > cfg["question_max_words"]:
        errors.append(f"question is {qn} words; it must be 1-{cfg['question_max_words']}")
    last_line = [ln for ln in brief["caption"].strip().splitlines() if ln.strip() and not ln.strip().startswith("#")]
    if not last_line or last_line[-1].strip() != q:
        errors.append("caption must end on the question (hashtags may follow on their own lines)")

    # Evidence: every id must resolve in the library.
    for eid in brief["evidence"]:
        row = lib.get(eid)
        if row is None:
            errors.append(f"evidence '{eid}' is not in the tidbit library")
        elif row.get("status", "").strip() != "verified":
            warnings.append(f"evidence '{eid}' is '{row.get('status') or 'unverified'}': hand-read the source before publishing")

    # Body: an evidence label on every post, no doses, and medical history carries its line.
    text = " ".join(str(brief.get(k, "")) for k in ("hook", "idea", "explanation", "caption", "follow_reason"))
    if pillar.get("needs_evidence_label") or series.get("needs_evidence_label"):
        if brief.get("evidence_label") not in cfg["evidence_labels"]:
            errors.append(f"{pillar['name']} posts need an evidence_label: one of {cfg['evidence_labels']}")
    if pillar.get("no_doses") and re.search(cfg["dose_pattern"], text, re.IGNORECASE):
        errors.append("no doses in Body posts (found an amount with a unit)")
    if series.get("medical_history_disclaimer_when_body") and brief["pillar"] == "body" \
            and cfg["medical_history_disclaimer"] not in brief["caption"]:
        errors.append(f"medical history needs the line: \"{cfg['medical_history_disclaimer']}\"")

    # Series rules.
    if series.get("needs_book_label"):
        label = brief.get("book_label")
        if label not in cfg["book_labels"]:
            errors.append(f"{series['name']} needs book_label: one of {cfg['book_labels']}")
        elif label == cfg["book_labels"][1] and not brief.get("read_by_surafel"):
            errors.append("a Moodius review needs \"read_by_surafel\": true (he has read it and said what he thought)")
    if brief["format"] == "book_review" and not brief.get("read_by_surafel"):
        errors.append("book reviews need \"read_by_surafel\": true (authentic reviews only)")
    if series.get("needs_film"):
        film = brief.get("film") or {}
        if not all(film.get(k) for k in ("title", "year", "director")):
            errors.append(f"{series['name']} needs film.title, film.year and film.director")
    if series.get("needs_tradition_source") and not brief.get("tradition_source"):
        errors.append(f"{series['name']} needs tradition_source naming the tradition and text")

    # Framing and claims, across every text field.
    for phrase in cfg["banned_phrases"]:
        if contains_phrase(text, phrase):
            errors.append(f"banned framing: '{phrase}'")
    for phrase in cfg["claim_words"]:
        if contains_phrase(text, phrase):
            msg = f"claim wording '{phrase}': history and education, never treatment claims"
            (errors if brief["pillar"] == "body" else warnings).append(msg)

    # Visual: no faces in automated posts, no house-style bans.
    visual = brief["visual"]
    if not isinstance(visual, dict) or not visual.get("direction"):
        errors.append("visual needs a 'direction'")
    else:
        if visual.get("faces", False) and not brief.get("made_by_hand", False):
            errors.append("faces are only allowed in posts Surafel makes by hand")
        for word in cfg["banned_visuals"]:
            if contains_phrase(visual["direction"], word):
                warnings.append(f"visual mentions '{word}', which the design system or film rules avoid")

    if brief.get("affiliate") and "affiliate" not in brief["caption"].lower():
        errors.append("affiliate link present: the caption must say so")

    return errors, warnings


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("briefs", nargs="+")
    ap.add_argument("--library", action="append", default=[],
                    help="glob for tidbit CSVs; repeatable")
    ap.add_argument("--json", action="store_true", help="print results as JSON")
    args = ap.parse_args(argv)

    cfg = load_config()
    lib = load_library(args.library)
    results, failed = [], False
    for path in args.briefs:
        with open(path, encoding="utf-8") as f:
            brief = json.load(f)
        errors, warnings = lint(brief, cfg, lib)
        failed |= bool(errors)
        results.append({"brief": path, "id": brief.get("id"), "ok": not errors,
                        "errors": errors, "warnings": warnings})

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for r in results:
            print(f"{'PASS' if r['ok'] else 'FAIL'}  {r['id']}  ({r['brief']})")
            for e in r["errors"]:
                print(f"   error:   {e}")
            for w in r["warnings"]:
                print(f"   warning: {w}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
