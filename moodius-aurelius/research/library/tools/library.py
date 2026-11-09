#!/usr/bin/env python3
"""Moodius research library: sourced tidbits, checked word for word against the source (1.0, 22 Oct 2026).

    python3 library.py verify                      # check every tidbit in ../tidbits/*.csv
    python3 library.py verify tidbits/epictetus.csv
    python3 library.py locate discourses "iron lamp"   # which section says this?
    python3 library.py section enchiridion 5           # print one section
    python3 library.py sources                         # list the machine-checkable texts
    python3 library.py discover "Epictetus" --apis gutendex,openlibrary,archive,openalex,semanticscholar,wikisource
    python3 library.py index                           # rebuild ../LIBRARY.md from the CSVs

How a tidbit is verified
  * kind=text: `evidence` must appear word for word (after normalising quotes, dashes, case and
    punctuation) inside the section named by `locator` of a registered public-domain text. That is
    a machine check; it fails loudly if the wording or the section is wrong.
  * kind=web: the source is a page or book we cannot fetch from here. `verified_by` must name who
    read it and when, and `link` must point at it. Shown as "manual" until a person or a thread
    with access confirms it.
Never add a tidbit without evidence: no invented studies, stats or quotes (project rule).

Only raw.githubusercontent.com is reachable from the project container, so the texts below come
from Standard Ebooks (CC0) and Perseus Digital Library (CC BY-SA 4.0 encoding of public-domain
translations) on GitHub. `discover` calls APIs that are blocked here; run it on the Mac or with the
GitHub Action "Research discover" (.github/workflows/research-discover.yml).
"""
import csv, glob, json, os, re, sys, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))     # research/library
CACHE = os.path.join(HERE, ".sources")
RAW = "https://raw.githubusercontent.com/{repo}/master/{path}"
SE = "src/epub/text/"
TEI = "{http://www.tei-c.org/ns/1.0}"

# key -> how to fetch and split a text into numbered sections.
#   se_chapters: Standard Ebooks file per book, <section id="chapter-B-C"> -> "B.C"
#   se_numbered: one file, <section id="PREFIX-N"> -> "N"
#   se_books: file per book -> "B". Standard Ebooks does not mark Meditations section numbers, so a
#             locator like "11.34" is checked against all of book 11 and the section number by hand.
#   se_whole: one file, the whole text is section "all"
#   tei_book_chapter: Perseus TEI, div book n=B / chapter n=C -> "B.C"
SOURCES = {
    "discourses": dict(title="Discourses", author="Epictetus (recorded by Arrian)", translator="George Long (1877)",
                       repo="standardebooks/epictetus_discourses_george-long", kind="se_chapters", books=4,
                       licence="CC0 (Standard Ebooks); translation public domain",
                       web="https://standardebooks.org/ebooks/epictetus/discourses/george-long/text/single-page"),
    "discourses-preface": dict(title="Discourses: Arrian's letter to Lucius Gellius", author="Arrian", translator="George Long (1877)",
                       repo="standardebooks/epictetus_discourses_george-long", kind="se_whole", file="preface.xhtml",
                       licence="CC0 (Standard Ebooks); translation public domain",
                       web="https://standardebooks.org/ebooks/epictetus/discourses/george-long/text/preface"),
    "long-introduction": dict(title="Introduction to the Discourses", author="George Long (1877)", translator="",
                       repo="standardebooks/epictetus_discourses_george-long", kind="se_whole", file="introduction.xhtml",
                       licence="CC0 (Standard Ebooks); text public domain",
                       web="https://standardebooks.org/ebooks/epictetus/discourses/george-long/text/introduction"),
    "enchiridion": dict(title="Enchiridion", author="Epictetus (compiled by Arrian)", translator="George Long (1877)",
                       repo="standardebooks/epictetus_short-works_george-long", kind="se_numbered",
                       file="the-enchiridion.xhtml", prefix="the-enchiridion-",
                       licence="CC0 (Standard Ebooks); translation public domain",
                       web="https://standardebooks.org/ebooks/epictetus/short-works/george-long/text/the-enchiridion"),
    "fragments": dict(title="Fragments", author="Epictetus", translator="George Long (1877)",
                       repo="standardebooks/epictetus_short-works_george-long", kind="se_whole", file="fragments.xhtml",
                       licence="CC0 (Standard Ebooks); translation public domain",
                       web="https://standardebooks.org/ebooks/epictetus/short-works/george-long/text/fragments"),
    "meditations": dict(title="Meditations", author="Marcus Aurelius", translator="George Long (1862)",
                       repo="standardebooks/marcus-aurelius_meditations_george-long", kind="se_books", books=12,
                       licence="CC0 (Standard Ebooks); translation public domain",
                       web="https://standardebooks.org/ebooks/marcus-aurelius/meditations/george-long/text/single-page"),
    "attic-nights": dict(title="Attic Nights", author="Aulus Gellius", translator="John C. Rolfe (Loeb, 1927)",
                       repo="PerseusDL/canonical-latinLit", kind="tei_book_chapter",
                       file="data/phi1254/phi001/phi1254.phi001.perseus-eng1.xml",
                       licence="Translation public domain (US, published 1927; Rolfe d. 1943); Perseus encoding CC BY-SA 4.0, credit Perseus",
                       web="https://scaife.perseus.org/reader/urn:cts:latinLit:phi1254.phi001.perseus-eng1/"),
}


# ---------------------------------------------------------------- fetching and sectioning

def fetch(repo, path):
    os.makedirs(CACHE, exist_ok=True)
    local = os.path.join(CACHE, (repo + "__" + path).replace("/", "_"))
    if not os.path.exists(local):
        with urllib.request.urlopen(RAW.format(repo=repo, path=path), timeout=60) as r, open(local, "wb") as fh:
            fh.write(r.read())
    return open(local, encoding="utf-8").read()


def strip(html):
    html = re.sub(r'<a[^>]*epub:type="noteref"[^>]*>.*?</a>', "", html, flags=re.S)   # endnote markers
    html = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", html.replace("&amp;", "&")).strip()


def norm(s):
    s = s.replace("⁠", "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("—", " ").replace("–", " ")
    s = re.sub(r"[^\w\s]", " ", s)          # punctuation differs between editions; the words must not
    return re.sub(r"\s+", " ", s).strip().lower()


_sections = {}

def sections(key):
    """Return {locator: plain text} for a registered source."""
    if key in _sections:
        return _sections[key]
    s = SOURCES[key]
    out = {}
    if s["kind"] == "se_chapters":
        for b in range(1, s["books"] + 1):
            html = fetch(s["repo"], f"{SE}book-{b}.xhtml")
            for m in re.finditer(r'<section id="chapter-(\d+)-(\d+)"[^>]*>(.*?)(?=<section id="chapter-|</body>)', html, re.S):
                out[f"{m.group(1)}.{m.group(2)}"] = strip(m.group(3))
    elif s["kind"] == "se_numbered":
        html = fetch(s["repo"], SE + s["file"])
        pat = r'<section id="' + re.escape(s["prefix"]) + r'(\d+)"[^>]*>(.*?)(?=<section id="|</body>)'
        for m in re.finditer(pat, html, re.S):
            out[m.group(1)] = strip(m.group(2))
    elif s["kind"] == "se_books":
        for b in range(1, s["books"] + 1):
            out[str(b)] = strip(fetch(s["repo"], f"{SE}book-{b}.xhtml"))
    elif s["kind"] == "se_whole":
        out["all"] = strip(fetch(s["repo"], SE + s["file"]))
    elif s["kind"] == "tei_book_chapter":
        root = ET.fromstring(fetch(s["repo"], s["file"]).encode("utf-8"))
        for book in root.iter(TEI + "div"):
            if book.get("subtype") != "book" or not (book.get("n") or "").isdigit():
                continue
            for ch in book:
                if ch.tag == TEI + "div" and ch.get("subtype") == "chapter":
                    loc = f"{book.get('n')}.{ch.get('n')}"
                    # drop the translator's footnotes: they are Rolfe's, not Gellius's
                    for note in [n for n in ch.iter() if n.tag == TEI + "note"]:
                        tail = note.tail
                        note.clear()          # empties the note but keeps the text after it
                        note.tail = tail
                    out[loc] = re.sub(r"\s+", " ", " ".join(ch.itertext())).strip()
    _sections[key] = out
    return out


def find_key(source):
    source = (source or "").strip().lower()
    if source in SOURCES:
        return source
    for k, s in SOURCES.items():
        if source and source in s["title"].lower():
            return k
    return None


# ---------------------------------------------------------------- tidbits

FIELDS = ["id", "figure", "topic", "claim", "evidence", "kind", "source", "locator", "author", "translator",
          "link", "licence", "tier", "caveat", "verified_by", "verified_at", "status", "use_in"]


def read_tidbits(paths):
    rows = []
    for p in paths:
        with open(p, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                r["_file"] = os.path.relpath(p, HERE)
                rows.append(r)
    return rows


def check_tidbit(r):
    """Return (status, detail). status: ok | manual | fail."""
    for f in ("id", "claim", "evidence", "kind", "source", "locator", "link", "licence", "tier"):
        if not (r.get(f) or "").strip():
            return "fail", f"missing field '{f}'"
    if r["kind"] == "web":
        if not r.get("verified_by", "").strip() or not r.get("verified_at", "").strip():
            return "fail", "web source needs verified_by and verified_at"
        return "manual", f"read by {r['verified_by']} on {r['verified_at']}"
    key = find_key(r["source"])
    if not key:
        return "fail", f"source '{r['source']}' is not a registered text (python3 library.py sources)"
    try:
        secs = sections(key)
    except OSError as e:
        return "fail", f"could not fetch {key}: {e.__class__.__name__}"
    loc = r["locator"].strip()
    scope = loc
    if loc not in secs and SOURCES[key]["kind"] == "se_books":
        scope = loc.split(".")[0]          # book-level check, section number confirmed by hand
    if scope not in secs:
        return "fail", f"{key} has no section '{loc}'"
    hay = norm(secs[scope])
    segs = [norm(p) for p in re.split(r"\s*(?:…|\.\.\.)\s*", r["evidence"].strip().strip("\"“”")) if norm(p)]
    for seg in segs:
        if seg not in hay:
            elsewhere = [l for l, t in secs.items() if seg in norm(t)]
            hint = f" (found in {key} {', '.join(elsewhere[:3])})" if elsewhere else ""
            return "fail", f"evidence not in {key} {loc}: '{seg[:60]}'{hint}"
    return "ok", f"{key} {loc}" + (f" (word check on book {scope}; section number by hand)" if scope != loc else "")


def cmd_verify(args):
    paths = args or sorted(glob.glob(os.path.join(HERE, "tidbits", "*.csv")))
    rows = read_tidbits(paths)
    counts = {"ok": 0, "manual": 0, "fail": 0}
    seen = set()
    for r in rows:
        status, detail = check_tidbit(r)
        if r["id"] in seen:
            status, detail = "fail", "duplicate id"
        seen.add(r["id"])
        counts[status] += 1
        mark = {"ok": "OK    ", "manual": "MANUAL", "fail": "FAIL  "}[status]
        print(f"{mark} {r['id']:<8} {detail}")
    print(f"\n{counts['ok']} checked word for word, {counts['manual']} read by hand, {counts['fail']} failed")
    return 1 if counts["fail"] else 0


def cmd_locate(args):
    key = find_key(args[0])
    needle = norm(" ".join(args[1:]))
    hits = [(l, t) for l, t in sections(key).items() if needle in norm(t)]
    for l, t in hits:
        i = norm(t).find(needle)
        print(f"{key} {l}: ...{norm(t)[max(0, i - 80):i + len(needle) + 80]}...")
    if not hits:
        print("not found")
    return 0 if hits else 1


def cmd_section(args):
    print(sections(find_key(args[0]))[args[1]])
    return 0


def cmd_sources(_):
    for k, s in SOURCES.items():
        print(f"{k:<20} {s['title']} - {s['author']}" + (f", tr. {s['translator']}" if s["translator"] else ""))
        print(f"{'':<20} {s['licence']}\n{'':<20} {s['web']}")
    return 0


def cmd_index(_):
    rows = read_tidbits(sorted(glob.glob(os.path.join(HERE, "tidbits", "*.csv"))))
    lines = ["# Moodius research library", "",
             "Generated by `tools/library.py index` from `tidbits/*.csv`. Edit the CSVs, not this file.", "",
             "Status: 🟢 checked word for word against the source text · 🟠 read by hand, recheck before a big post · 🔴 failed or retired, do not use", ""]
    for fig in sorted({r["figure"] for r in rows}):
        lines += [f"## {fig}", ""]
        for r in [x for x in rows if x["figure"] == fig]:
            st = {"ok": "🟢", "manual": "🟠"}.get(check_tidbit(r)[0], "🔴")
            key = find_key(r["source"]) if r["kind"] == "text" else None
            title = SOURCES[key]["title"] if key else r["source"]
            cite = f"{r['author']}, *{title}* {'' if r['locator'] == 'all' else r['locator']}".rstrip()
            if r.get("translator"):
                cite += f", tr. {r['translator']}"
            lines.append(f"- {st} **{r['id']}** {r['claim']}  ")
            lines.append(f"  > {r['evidence']}  ")
            lines.append(f"  {cite} · [{r['licence']}]({r['link']})" + (f" · ⚠️ {r['caveat']}" if r.get("caveat") else ""))
        lines.append("")
    with open(os.path.join(HERE, "LIBRARY.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print(f"wrote LIBRARY.md ({len(rows)} tidbits)")
    return 0


# ---------------------------------------------------------------- discovery (needs open internet)

UA = {"User-Agent": "moodius-research-library/1.0 (research; contact via GitHub repo)"}

def get_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def d_gutendex(q):
    j = get_json("https://gutendex.com/books/?search=" + urllib.parse.quote(q))
    return [dict(title=b["title"], authors=[a["name"] for a in b["authors"]], year=None,
                 link=f"https://www.gutenberg.org/ebooks/{b['id']}", licence="Public domain in the USA (Project Gutenberg); check UK status by author death date",
                 text=b["formats"].get("text/plain; charset=utf-8") or b["formats"].get("text/plain; charset=us-ascii"))
            for b in j.get("results", [])[:15]]


def d_openlibrary(q):
    j = get_json("https://openlibrary.org/search.json?limit=15&fields=key,title,author_name,first_publish_year,ia,public_scan_b&q=" + urllib.parse.quote(q))
    return [dict(title=d.get("title"), authors=d.get("author_name", []), year=d.get("first_publish_year"),
                 link="https://openlibrary.org" + d["key"], licence="Catalogue data CC0; full text only if public_scan",
                 text=("https://archive.org/details/" + d["ia"][0]) if d.get("public_scan_b") and d.get("ia") else None)
            for d in j.get("docs", [])]


def d_archive(q):
    j = get_json("https://archive.org/advancedsearch.php?rows=15&output=json&fl[]=identifier&fl[]=title&fl[]=creator&fl[]=year&fl[]=licenseurl"
                 "&q=" + urllib.parse.quote(f"({q}) AND mediatype:texts"))
    return [dict(title=d.get("title"), authors=[d["creator"]] if isinstance(d.get("creator"), str) else d.get("creator", []),
                 year=d.get("year"), link="https://archive.org/details/" + d["identifier"],
                 licence=d.get("licenseurl") or "No licence stated: treat as copyrighted unless old enough to be public domain",
                 text=f"https://archive.org/download/{d['identifier']}/{d['identifier']}_djvu.txt")
            for d in j.get("response", {}).get("docs", [])]


def d_openalex(q):
    j = get_json("https://api.openalex.org/works?per-page=15&filter=is_oa:true&sort=cited_by_count:desc&search=" + urllib.parse.quote(q))
    return [dict(title=w.get("title"), authors=[a["author"]["display_name"] for a in w.get("authorships", [])[:4]],
                 year=w.get("publication_year"), link=w.get("doi") or w.get("id"), cited_by=w.get("cited_by_count"),
                 licence=(w.get("best_oa_location") or {}).get("license") or "metadata CC0; paper licence unknown",
                 text=(w.get("best_oa_location") or {}).get("pdf_url"))
            for w in j.get("results", [])]


def d_semanticscholar(q):
    j = get_json("https://api.semanticscholar.org/graph/v1/paper/search?limit=15&fields=title,year,authors,citationCount,externalIds,openAccessPdf,tldr&query=" + urllib.parse.quote(q))
    return [dict(title=p.get("title"), authors=[a["name"] for a in p.get("authors", [])[:4]], year=p.get("year"),
                 cited_by=p.get("citationCount"),
                 link=("https://doi.org/" + p["externalIds"]["DOI"]) if (p.get("externalIds") or {}).get("DOI") else f"https://www.semanticscholar.org/paper/{p['paperId']}",
                 licence="metadata only; read the paper's own licence", text=(p.get("openAccessPdf") or {}).get("url"),
                 tldr=(p.get("tldr") or {}).get("text"))
            for p in j.get("data", [])]


def d_wikisource(q):
    j = get_json("https://en.wikisource.org/w/api.php?action=query&list=search&format=json&srlimit=15&srsearch=" + urllib.parse.quote(q))
    return [dict(title=s["title"], authors=[], year=None, link="https://en.wikisource.org/wiki/" + urllib.parse.quote(s["title"].replace(" ", "_")),
                 licence="Wikisource hosts public-domain texts; check the page's licence box", text=None,
                 snippet=re.sub(r"<[^>]+>", "", s.get("snippet", "")))
            for s in j.get("query", {}).get("search", [])]


APIS = {"gutendex": d_gutendex, "openlibrary": d_openlibrary, "archive": d_archive,
        "openalex": d_openalex, "semanticscholar": d_semanticscholar, "wikisource": d_wikisource}


def cmd_discover(args):
    apis = list(APIS)
    if "--apis" in args:
        i = args.index("--apis")
        apis = args[i + 1].split(",")
        args = args[:i] + args[i + 2:]
    q = " ".join(args)
    result = {"query": q, "results": {}}
    for a in apis:
        try:
            result["results"][a] = APIS[a](q)
            print(f"{a:<16} {len(result['results'][a])} results")
        except Exception as e:   # one API down should not stop the others
            result["results"][a] = {"error": f"{e.__class__.__name__}: {e}"[:200]}
            print(f"{a:<16} error {e.__class__.__name__}")
    slug = re.sub(r"[^a-z0-9]+", "-", q.lower()).strip("-")[:60]
    out = os.path.join(HERE, "discover", f"{slug}.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, ensure_ascii=False)
    print(f"wrote {os.path.relpath(out, HERE)}  (leads only: nothing here is a tidbit until it is checked)")
    return 0


if __name__ == "__main__":
    cmds = {"verify": cmd_verify, "locate": cmd_locate, "section": cmd_section, "sources": cmd_sources,
            "discover": cmd_discover, "index": cmd_index}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        print(__doc__)
        sys.exit(2)
    sys.exit(cmds[sys.argv[1]](sys.argv[2:]))
