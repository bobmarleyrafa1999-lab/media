#!/usr/bin/env python3
"""Find archival photos that are safe for commercial reels, download them, and write the credit lines.

Sources (no keys needed):
  loc       Library of Congress JSON API (keeps only items whose rights advisory says
            "No known restrictions on publication")
  commons   Wikimedia Commons API (keeps public domain, CC0 and CC BY; CC BY-SA only with --allow-sa)
  openverse Openverse API (aggregates Commons, Smithsonian, Met, Flickr Commons and others;
            asks only for licences that allow commercial use and modification)

The container this project usually runs in cannot reach these hosts. Run it on the Mac or with the
"Fetch archive images" GitHub Action (.github/workflows/fetch-archive.yml), then copy the results into
reels-engine/footage/, where engine.py picks up <tag>-<n>.jpg as a drifting still background.

  python3 fetch_archive.py --source loc --query "march on washington 1963" --tag march --n 4
  python3 fetch_archive.py --source commons --query "Frederick Douglass portrait" --tag douglass
  python3 fetch_archive.py --source openverse --query "civil rights march" --tag march --out out/
"""
import argparse
import csv
import json
import os
import re
import sys
import urllib.parse
import urllib.request

UA = "MoodiusArchiveFetcher/1.0 (https://github.com/bobmarleyrafa1999-lab/media)"
CREDIT_FIELDS = ["tag", "file", "title", "creator", "date", "source", "licence", "licence_url",
                 "landing_url", "credit_line", "note"]


# ---------- licence rules (pure functions, unit-tested) ----------
def classify_licence(name, allow_sa=False):
    """Return 'ok', 'sa' or 'no' for a licence label from any of the three sources."""
    n = (name or "").lower().replace("_", " ").replace("-", " ").strip()
    if not n:
        return "no"
    if re.search(r"\b(nc|nd|non ?commercial|no ?derivatives|fair use|non ?free|all rights reserved|copyrighted)\b", n):
        return "no"
    if re.search(r"\b(by sa|sharealike|share alike)\b", n) or n in ("sa",):
        return "ok" if allow_sa else "sa"
    if re.search(r"(public domain|^pd\b|\bpdm\b|\bcc0\b|^cc ?by\b|^by\b|no known (copyright )?restrictions)", n):
        return "ok"
    return "no"


def loc_rights_ok(advisory):
    """LoC rights advisory text (string or list) -> True only for 'no known restrictions'."""
    text = " ".join(advisory) if isinstance(advisory, list) else (advisory or "")
    return bool(re.search(r"no known restrictions", text, re.I))


def credit_line(creator, date, source, licence):
    who = creator.strip() if creator else "Unknown photographer"
    when = f", {date}" if date else ""
    return f"Photo: {who}{when} · {source} ({licence})"


def strip_html(s):
    return re.sub(r"<[^>]+>", "", s or "").strip()


# ---------- parsers (take decoded JSON, return candidate dicts) ----------
def parse_commons(data, allow_sa=False):
    out = []
    for page in (data.get("query", {}).get("pages", {}) or {}).values():
        info = (page.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata", {})
        lic = strip_html(meta.get("LicenseShortName", {}).get("value", ""))
        verdict = classify_licence(lic, allow_sa)
        if verdict != "ok":
            continue
        restrictions = strip_html(meta.get("Restrictions", {}).get("value", ""))
        out.append({
            "title": page.get("title", "").replace("File:", ""),
            "creator": strip_html(meta.get("Artist", {}).get("value", "")),
            "date": strip_html(meta.get("DateTimeOriginal", {}).get("value", ""))[:20],
            "source": "Wikimedia Commons",
            "licence": lic,
            "licence_url": meta.get("LicenseUrl", {}).get("value", ""),
            "landing_url": info.get("descriptionurl", ""),
            "image_url": info.get("thumburl") or info.get("url", ""),
            "note": f"restrictions: {restrictions}" if restrictions else "",
        })
    return out


def parse_openverse(data, allow_sa=False):
    out = []
    for r in data.get("results", []):
        lic = f"CC {r.get('license', '').upper()} {r.get('license_version') or ''}".strip()
        if r.get("license") in ("pdm", "cc0"):
            lic = "Public domain" if r.get("license") == "pdm" else "CC0"
        if classify_licence(lic, allow_sa) != "ok":
            continue
        out.append({
            "title": r.get("title") or "",
            "creator": r.get("creator") or "",
            "date": "",
            "source": f"{r.get('source', '')} via Openverse",
            "licence": lic,
            "licence_url": r.get("license_url", ""),
            "landing_url": r.get("foreign_landing_url", ""),
            "image_url": r.get("url", ""),
            "note": (r.get("attribution") or "")[:300],
        })
    return out


def parse_loc_item(item_json):
    """One loc.gov item (?fo=json) -> candidate or None."""
    item = item_json.get("item", {})
    advisory = item.get("rights_advisory") or item_json.get("rights_advisory") or ""
    if not loc_rights_ok(advisory):
        return None
    images = item_json.get("resources", [{}])[0].get("files", []) if item_json.get("resources") else []
    best = ""
    for group in images:  # pick the largest jpeg in the first file group
        for f in group:
            if f.get("mimetype") == "image/jpeg" and f.get("url"):
                best = f["url"]
    if not best:
        urls = item_json.get("item", {}).get("image_url") or []
        best = urls[-1] if urls else ""
    creators = item.get("contributor_names") or item.get("creators") or []
    if creators and isinstance(creators[0], dict):
        creators = [c.get("title", "") for c in creators]
    adv = " ".join(advisory) if isinstance(advisory, list) else advisory
    return {
        "title": item.get("title", ""),
        "creator": "; ".join(creators[:2]),
        "date": item.get("date", ""),
        "source": "Library of Congress",
        "licence": "No known restrictions on publication",
        "licence_url": "https://www.loc.gov/legal/understanding-copyright/",
        "landing_url": item.get("id") or item_json.get("url", ""),
        "image_url": best,
        "note": adv[:300],
    } if best else None


# ---------- network ----------
def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)


def search(source, query, n, allow_sa):
    q = urllib.parse.quote(query)
    if source == "commons":
        url = ("https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search"
               f"&gsrnamespace=6&gsrlimit={n * 3}&gsrsearch={q}&prop=imageinfo"
               "&iiprop=url|extmetadata&iiurlwidth=1600")
        return parse_commons(get_json(url), allow_sa)
    if source == "openverse":
        lt = "commercial,modification"
        url = f"https://api.openverse.org/v1/images/?q={q}&license_type={lt}&page_size={n * 3}"
        return parse_openverse(get_json(url), allow_sa)
    if source == "loc":
        res = get_json(f"https://www.loc.gov/photos/?q={q}&fo=json&c={n * 3}")
        out = []
        for r in res.get("results", []):
            if len(out) >= n:
                break
            item_url = r.get("id") or r.get("url")
            if not item_url:
                continue
            try:
                cand = parse_loc_item(get_json(item_url.rstrip("/") + "/?fo=json"))
            except Exception as e:  # one broken item shouldn't stop the run
                print(f"  skip {item_url}: {e}", file=sys.stderr)
                continue
            if cand:
                out.append(cand)
        return out
    raise SystemExit(f"unknown source {source}")


def download(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r, open(path, "wb") as f:
        f.write(r.read())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", choices=["loc", "commons", "openverse"], required=True)
    ap.add_argument("--query", required=True)
    ap.add_argument("--tag", required=True, help="footage tag the reel script uses, e.g. march")
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--out", default="archive-out")
    ap.add_argument("--allow-sa", action="store_true",
                    help="also keep CC BY-SA (the reel itself then has to be shared under BY-SA)")
    ap.add_argument("--dry-run", action="store_true", help="list candidates, download nothing")
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    cands = search(a.source, a.query, a.n, a.allow_sa)[: a.n]
    if not cands:
        print("no commercially usable images found; try another query or source")
        return 1
    credits_path = os.path.join(a.out, "credits.csv")
    new = not os.path.exists(credits_path)
    existing = len([f for f in os.listdir(a.out) if f.startswith(a.tag + "-")])
    with open(credits_path, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=CREDIT_FIELDS, extrasaction="ignore")
        if new:
            w.writeheader()
        for i, c in enumerate(cands, start=existing + 1):
            ext = ".png" if c["image_url"].lower().endswith(".png") else ".jpg"
            name = f"{a.tag}-{i}{ext}"
            c.update(tag=a.tag, file=name,
                     credit_line=credit_line(c["creator"], c["date"][:4], c["source"], c["licence"]))
            print(f"{name}  {c['licence']:<36} {c['title'][:60]}")
            if a.dry_run:
                continue
            try:
                download(c["image_url"], os.path.join(a.out, name))
            except Exception as e:
                print(f"  download failed: {e}", file=sys.stderr)
                continue
            w.writerow(c)
    print(f"credits -> {credits_path}  (paste the credit_line into the caption)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
