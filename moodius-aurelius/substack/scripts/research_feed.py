#!/usr/bin/env python3
"""Weekly research ingestion: academic papers + publication feeds -> one deduplicated inbox (stdlib only).

Usage:
  python3 scripts/research_feed.py papers "self-distancing journaling" [--since 2018] [--reviews]
  python3 scripts/research_feed.py feeds
  python3 scripts/research_feed.py weekly          # every pillar query + every feed (what the GitHub Action runs)

Papers come from Crossref (free, no key) and, if OPENALEX_API_KEY is set, OpenAlex
(free daily allowance since Feb 2026). Feeds come from data/feeds.csv.
Everything lands in data/inbox.csv and vault/00-inbox/<date>.md with status "unreviewed".
Nothing enters data/sources.csv until a human (or /verify-sources) checks it.
"""
import csv
import datetime as dt
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INBOX = ROOT / "data" / "inbox.csv"
FIELDS = ["found", "kind", "pillar", "title", "authors", "year", "venue", "doi", "url", "cited_by", "is_review", "status"]
UA = {"User-Agent": "MoodiusResearch/1.0 (mailto:research@moodius.invalid)"}  # set a real contact in CROSSREF_MAILTO
REVIEW_WORDS = re.compile(r"meta-analy|systematic review|review of|umbrella review", re.I)
PILLAR_QUERIES = {
    1: "expressive writing journaling wellbeing", 2: "defensive projection thought suppression",
    3: "masculine norms help-seeking men", 4: "stoic philosophy cognitive behavioural therapy",
    5: "adult attachment loneliness friendship", 6: "burnout perfectionism high achievers",
    7: "smartphone attention mind wandering", 8: "bereavement grief resilience trajectories",
    9: "shame guilt self-compassion emotion regulation", 10: "income wellbeing materialism hedonic adaptation",
}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def crossref(query, since, rows=20):
    mail = os.environ.get("CROSSREF_MAILTO", "")
    q = urllib.parse.urlencode({"query.bibliographic": query, "rows": rows, "sort": "relevance",
                                "filter": f"from-pub-date:{since},type:journal-article", **({"mailto": mail} if mail else {})})
    items = json.loads(get(f"https://api.crossref.org/works?{q}"))["message"]["items"]
    return [parse_crossref(i) for i in items]


def parse_crossref(i):
    title = " ".join(i.get("title") or [""])
    return dict(kind="paper", title=title,
                authors="; ".join(f"{a.get('family', '')}, {a.get('given', '')[:1]}." for a in i.get("author", [])[:6]),
                year=str((i.get("issued", {}).get("date-parts") or [[""]])[0][0]),
                venue=" ".join(i.get("container-title") or [""]), doi=i.get("DOI", "").lower(),
                url=f"https://doi.org/{i.get('DOI', '')}", cited_by=str(i.get("is-referenced-by-count", "")),
                is_review="yes" if REVIEW_WORDS.search(title) else "")


def openalex(query, since, rows=20):
    key = os.environ.get("OPENALEX_API_KEY")
    if not key:
        return []
    q = urllib.parse.urlencode({"search": query, "per_page": rows, "api_key": key,
                                "filter": f"from_publication_date:{since}-01-01,type:article"})
    return [parse_openalex(w) for w in json.loads(get(f"https://api.openalex.org/works?{q}"))["results"]]


def parse_openalex(w):
    title = w.get("title") or ""
    doi = (w.get("doi") or "").replace("https://doi.org/", "").lower()
    return dict(kind="paper", title=title,
                authors="; ".join(a["author"]["display_name"] for a in w.get("authorships", [])[:6]),
                year=str(w.get("publication_year", "")),
                venue=((w.get("primary_location") or {}).get("source") or {}).get("display_name", ""),
                doi=doi, url=f"https://doi.org/{doi}" if doi else w.get("id", ""),
                cited_by=str(w.get("cited_by_count", "")), is_review="yes" if REVIEW_WORDS.search(title) or w.get("type") == "review" else "")


def feed_items(xml_bytes, source):
    """Parse RSS 2.0 or Atom into inbox rows."""
    root = ET.fromstring(xml_bytes)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    out = []
    for it in root.iter("item"):
        out.append(dict(kind="feed", title=(it.findtext("title") or "").strip(), authors=source,
                        year=(re.findall(r"\b(?:19|20)\d\d\b", it.findtext("pubDate") or "") or [""])[0], venue=source,
                        doi="", url=(it.findtext("link") or "").strip(), cited_by="", is_review=""))
    for e in root.findall("a:entry", ns):
        link = e.find("a:link", ns)
        out.append(dict(kind="feed", title=(e.findtext("a:title", "", ns)).strip(), authors=source,
                        year=(e.findtext("a:updated", "", ns))[:4], venue=source, doi="",
                        url=link.get("href") if link is not None else "", cited_by="", is_review=""))
    return out


def norm(t):
    return re.sub(r"[^a-z0-9 ]", "", t.lower()).strip()


def known():
    """Titles, DOIs and URLs already in the library or the inbox, for deduplication."""
    titles, ids = [], set()
    for name in ("sources.csv", "inbox.csv"):
        p = ROOT / "data" / name
        if not p.exists():
            continue
        for r in csv.DictReader(open(p, encoding="utf-8")):
            titles.append(norm(r.get("title") or r.get("source") or ""))
            for k in ("doi", "url"):
                v = (r.get(k) or "").lower().replace("https://doi.org/", "")
                if v:
                    ids.add(v)
    return titles, ids


def dedupe(rows, titles, ids, threshold=0.88):
    fresh = []
    for r in rows:
        key = (r["doi"] or r["url"]).lower().replace("https://doi.org/", "")
        t = norm(r["title"])
        if not t or key in ids or any(SequenceMatcher(None, t, k).ratio() >= threshold for k in titles if k):
            continue
        ids.add(key)
        titles.append(t)
        fresh.append(r)
    return fresh


def save(rows, pillar=""):
    today = dt.date.today().isoformat()
    new_file = not INBOX.exists()
    with open(INBOX, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            w.writeheader()
        for r in rows:
            w.writerow({**{k: "" for k in FIELDS}, **r, "found": today, "pillar": r.get("pillar", pillar), "status": "unreviewed"})
    note = ROOT / "vault" / "00-inbox" / f"{today}.md"
    note.parent.mkdir(parents=True, exist_ok=True)
    with open(note, "a", encoding="utf-8") as f:
        for r in rows:
            tag = " **[review]**" if r.get("is_review") else ""
            f.write(f"- [ ] {r['title']} ({r['authors'][:60]}, {r['year']}){tag} {r['url']} #pillar{r.get('pillar', pillar)}\n")
    return len(rows)


def papers(query, since, pillar="", reviews_only=False):
    rows = []
    for fn in (crossref, openalex):
        try:
            rows += fn(query, since)
        except Exception as e:  # one source failing shouldn't stop the run
            print(f"  {fn.__name__}: {e}", file=sys.stderr)
    if reviews_only:
        rows = [r for r in rows if r["is_review"]]
    rows.sort(key=lambda r: (-(r["is_review"] == "yes"), -int(r["cited_by"] or 0)))
    titles, ids = known()
    for r in rows:
        r["pillar"] = str(pillar)
    return save(dedupe(rows, titles, ids), pillar)


def feeds():
    rows = []
    for f in csv.DictReader(open(ROOT / "data" / "feeds.csv", encoding="utf-8")):
        try:
            for r in feed_items(get(f["url"]), f["name"])[:10]:
                r["pillar"] = f["pillar"]
                rows.append(r)
        except Exception as e:
            print(f"  feed {f['name']}: {e}", file=sys.stderr)
    titles, ids = known()
    return save(dedupe(rows, titles, ids))


if __name__ == "__main__":
    a = sys.argv[1:]
    since = a[a.index("--since") + 1] if "--since" in a else str(dt.date.today().year - 8)
    if a[:1] == ["papers"]:
        print(papers(a[1], since, reviews_only="--reviews" in a), "new papers")
    elif a[:1] == ["feeds"]:
        print(feeds(), "new feed items")
    elif a[:1] == ["weekly"]:
        n = sum(papers(q, since, p) for p, q in PILLAR_QUERIES.items())
        print(n, "new papers;", feeds(), "new feed items")
    else:
        print(__doc__)
