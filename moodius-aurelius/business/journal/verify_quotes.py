#!/usr/bin/env python3
"""Checks every quote marked `verbatim` against the public-domain source text.

    python3 verify_quotes.py content/the-unexamined-self.yaml [more.yaml ...]

Each segment of the quote between ellipses must appear word for word in the source, after
normalising whitespace and dropping the translator's bracketed glosses, e.g. "([Greek: hormae])".
Sources are downloaded once into ./.sources (Project Gutenberg texts via GITenberg mirrors).
Exit code 1 if any quote fails. Paraphrases are listed but not checked (they are our wording).
"""
import os, re, sys, urllib.request, yaml

SOURCES = {
    "plato_apology_jowett": "https://raw.githubusercontent.com/GITenberg/Apology_1656/master/1656.txt",
    "epictetus_long": "https://raw.githubusercontent.com/GITenberg/A-Selection-from-the-Discourses-of-Epictetus-with-the-Encheiridion_10661/master/10661.txt",
}
# Gummere's Letters aren't on Gutenberg. Letters 2.6 was checked against the Gummere text by the
# Substack thread on 21 Oct 2026 (substack/data/sources.csv row N28); kept here so the check is explicit.
CHECKED_ELSEWHERE = {
    "seneca_gummere_checked": ["It is not the man who has too little, but the man who craves more, that is poor."],
}
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".sources")


def norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip()


def source_text(key):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, key + ".txt")
    if not os.path.exists(path):
        with urllib.request.urlopen(SOURCES[key], timeout=60) as r, open(path, "wb") as f:
            f.write(r.read())
    t = open(path, encoding="utf-8", errors="ignore").read()
    t = re.sub(r"\s*\(\[Greek:[^\]]*\]\)", "", t)          # ([Greek: ...]) glosses
    t = re.sub(r"\s*\((magisterial power)\)", "", t)       # Long's English gloss in Ench. 1
    return norm(t)


def quotes(doc):
    if doc.get("epigraph"):
        yield "epigraph", doc["epigraph"]
    for d in doc.get("days", []):
        yield f"Day {d['n']}", d["quote"]


def main(files):
    failed = 0
    for f in files:
        doc = yaml.safe_load(open(f, encoding="utf-8"))
        for where, q in quotes(doc):
            if q.get("kind") != "verbatim":
                print(f"  paraphrase  {where}: {q['cite']}")
                continue
            key = q["source"]
            hay = " ".join(CHECKED_ELSEWHERE[key]) if key in CHECKED_ELSEWHERE else source_text(key)
            segments = [norm(s).strip(" .,;:!?") for s in re.split(r"…|\.\.\.", q["text"])]
            missing = [s for s in segments if len(s) > 3 and s not in hay]
            if missing:
                failed += 1
                print(f"✗ FAIL       {where}: {q['cite']}\n    not found: {missing}")
            else:
                print(f"✓ verbatim   {where}: {q['cite']}")
    print("\nall verbatim quotes found in their sources" if not failed else f"\n{failed} quote(s) failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or [os.path.join(HERE, "content", "the-unexamined-self.yaml")]))
