#!/usr/bin/env python3
"""Word-for-word quote check against the public-domain source text (1.3, 22 Oct 2026).

    python3 quotes.py "Meditations" "12.4" "George Long" "Every man loves himself more ..."

Standard Ebooks editions are CC0 and raw.githubusercontent.com is reachable from the project
container, so this runs anywhere. Each segment of a quote between ellipses must appear in the
book's text after normalising quotes, dashes, case and whitespace. Same method as
liberation/tools/verify_quotes.py and business/journal/verify_quotes.py.

Gummere's Letters are not on Standard Ebooks or Gutenberg: those come back "manual", so a person
(or a thread that can reach Wikisource) checks them by hand and records it in source.verified_at.
"""
import os, re, sys, urllib.request

RAW = "https://raw.githubusercontent.com/standardebooks/{repo}/master/src/epub/text/{file}"
CACHE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".sources")

# (work, translator surname) -> (repo, file for a section's first number, or a fixed file)
SOURCES = {
    ("Meditations", "Long"): ("marcus-aurelius_meditations_george-long", lambda book: f"book-{book}.xhtml"),
    ("Discourses", "Long"): ("epictetus_discourses_george-long", lambda book: f"book-{book}.xhtml"),
    ("Enchiridion", "Long"): ("epictetus_short-works_george-long", lambda _: "the-enchiridion.xhtml"),
    ("On Anger", "Stewart"): ("seneca_dialogues_aubrey-stewart", lambda _: "on-anger.xhtml"),
    ("On the Shortness of Life", "Stewart"): ("seneca_dialogues_aubrey-stewart", lambda _: "on-the-shortness-of-life.xhtml"),
    ("On Providence", "Stewart"): ("seneca_dialogues_aubrey-stewart", lambda _: "on-providence.xhtml"),
    ("The Brothers Karamazov", "Garnett"): ("fyodor-dostoevsky_the-brothers-karamazov_constance-garnett", None),
}


def norm(s):
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"(?<=[a-z,.;:!?])\d+(?=[\s,.;:])", "", s)   # endnote numbers glued to words
    s = s.replace("⁠", "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("—", " - ").replace("–", " - ").replace("&amp;", "&")
    s = re.sub(r"[^\w\s]", " ", s)       # punctuation differs between editions; the words must not
    return re.sub(r"\s+", " ", s).strip().lower()


def fetch(repo, file):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"{repo}__{file}")
    if not os.path.exists(path):
        with urllib.request.urlopen(RAW.format(repo=repo, file=file), timeout=60) as r, open(path, "wb") as fh:
            fh.write(r.read())
    return norm(open(path, encoding="utf-8").read())


def find_source(work, translation):
    for (w, tr), spec in SOURCES.items():
        if w.lower() in work.lower() and tr.lower() in translation.lower():
            return spec
    return None


def check(work, section, translation, quote):
    """Return ("ok" | "missing" | "manual", detail)."""
    spec = find_source(work, translation)
    if not spec:
        return "manual", f"no machine-readable source for {work} ({translation}); check by hand"
    repo, file_for = spec
    if file_for is None:
        return "manual", f"{work}: chapter files not mapped; check by hand"
    book = (re.findall(r"\d+", section) or ["1"])[0]
    try:
        text = fetch(repo, file_for(book))
    except OSError as e:
        return "manual", f"source not reachable ({e.__class__.__name__}); check by hand"
    body = quote.strip().strip("\"“”'‘’")
    segs = [norm(p) for p in re.split(r"\s*(?:…|\.\.\.)\s*", body) if norm(p)]
    misses = [p for p in segs if p not in text]
    if misses:
        return "missing", f"not found in {repo}/{file_for(book)}: '{misses[0][:70]}'"
    return "ok", f"{repo}/{file_for(book)}"


if __name__ == "__main__":
    status, detail = check(*sys.argv[1:5])
    print(status, detail)
    sys.exit(0 if status == "ok" else 1)
