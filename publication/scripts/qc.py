#!/usr/bin/env python3
"""Editorial quality gate for Moodius essays (stdlib only).

Usage: python3 scripts/qc.py essays/01-writing-to-no-one.md [more.md ...]

Checks the text between <!-- publish:start --> and <!-- publish:end -->:
word count of the essay body, banned phrases, evidence labels, block quotes
with a citation line, a sources list, a subscriber line, and unresolved
"TODO"/"verify" markers. Exits 1 if any essay fails a hard check.
"""
import re
import sys
from pathlib import Path

BANNED = [
    "in today's fast-paced world", "unlock", "level up", "game-changer", "game changer",
    "delve", "tapestry", "embark on a journey", "your journey", "navigate the complexities",
    "it's important to note", "in conclusion", "transformative", "unleash", "supercharge",
    "high-value man", "alpha", "sigma", "red pill", "hypergamy", "smv", "simp",
    "rewires your brain", "science says", "studies show that", "life-changing", "hack",
]
LABEL = re.compile(r"\*\*\[(Study|Studies|Meta-analysis|Review|Survey|Research synthesis|Theory|"
                   r"Adversarial collaboration|Philosophy|Interpretive framework|Idea|Moodius[^\]]*)[^\]]*\]\*\*")
MIN_WORDS, MAX_WORDS = 1200, 1800


def body(text):
    m = re.search(r"<!-- publish:start -->(.*?)<!-- publish:end -->", text, re.S)
    return m.group(1) if m else text


def essay_words(pub):
    """Words from the subtitle down to the end of the conclusion (excludes exercise lists, sources, sign-off)."""
    main = pub.split("## Sources")[0]
    main = re.split(r"\n---\n", main)[0]
    main = re.sub(r"^#.*$", "", main, flags=re.M)
    return len(re.findall(r"[A-Za-z0-9'’-]+", main))


def check(path):
    text = Path(path).read_text(encoding="utf-8")
    pub = body(text)
    low = pub.lower()
    problems, notes = [], []

    words = essay_words(pub)
    if not MIN_WORDS <= words <= MAX_WORDS:
        problems.append(f"essay length {words} words (target {MIN_WORDS}-{MAX_WORDS})")
    else:
        notes.append(f"{words} words")

    unquoted = re.sub(r'"[^"\n]{0,80}"|“[^”\n]{0,80}”', "", low)  # quoting a cliché to criticise it is allowed
    for phrase in BANNED:
        if re.search(r"\b" + re.escape(phrase) + r"\b", unquoted):
            problems.append(f"banned phrase: '{phrase}'")

    labels = LABEL.findall(pub)
    if len(labels) < 4:
        problems.append(f"only {len(labels)} evidence labels (need 4+)")
    else:
        notes.append(f"{len(labels)} evidence labels")

    quotes = re.findall(r"((?:^>.*\n)+)", pub, re.M)
    for q in quotes:
        if not re.search(r"tr\.|trans\.|\d+\.\d+", q):
            problems.append("block quote without translation + section line")

    if "## Sources" not in pub:
        problems.append("no Sources section")
    else:
        refs = re.findall(r"^\d+\. ", pub.split("## Sources")[1], re.M)
        notes.append(f"{len(refs)} sources")
        if len(refs) < 3:
            problems.append("fewer than 3 sources")

    if "## Three questions" not in pub:
        problems.append("missing three journaling questions")
    if "## Try this" not in pub:
        problems.append("missing reflection exercise")
    if "subscribe" not in low:
        problems.append("missing subscriber invitation")
    if re.search(r"\bTODO\b|\[verify\]", pub):
        problems.append("unresolved TODO/verify marker in publishable text")
    if re.search(r"\b(I|my) (client|patient)s?\b", pub):
        problems.append("possible invented clinical anecdote")
    if pub.count("It's not") + pub.count("it's not") > 3:
        notes.append("watch: 'it's not X' constructions > 3")

    return problems, notes


def main(paths):
    failed = False
    for p in paths:
        problems, notes = check(p)
        status = "FAIL" if problems else "PASS"
        failed |= bool(problems)
        print(f"{status}  {p}  ({', '.join(notes)})")
        for pr in problems:
            print(f"      - {pr}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or sorted(str(p) for p in Path(__file__).parent.parent.glob("essays/*.md"))))
