#!/usr/bin/env python3
"""Fetch free-licence b-roll from Wikimedia Commons for the reels engine (runs on GitHub Actions).

    python3 fetch_footage.py requests/<name>.json --out ../footage-pool

Only Public domain, CC0 and CC BY (attribution, no share-alike) files are kept; every clip's
licence, author and source page go into manifest.csv so captions can credit them. Each clip is
cut to a 9:16 1080x1920 H.264 file with no audio, plus a 4-frame contact sheet for a face check.
No account, no API key, no spend.
"""
import argparse, csv, json, os, re, subprocess, time, urllib.error, urllib.parse, urllib.request

API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "moodius-footage-fetch/1.0 (GitHub Actions; contact via repository)"}
OK_LICENCE = re.compile(r"^(public domain|pd|cc0|cc[- ]by[- ](1|2|2\.5|3|4)\.0)$|^cc[- ]by[- ][0-9.]+$|^pd-", re.I)


def get(params):
    url = API + "?" + urllib.parse.urlencode(params | {"format": "json"})
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
        return json.load(r)


def strip(html):
    return re.sub(r"<[^>]+>", "", html or "").strip()


def search(term, n):
    js = get({"action": "query", "generator": "search", "gsrsearch": f"{term} filetype:video", "gsrnamespace": 6,
              "gsrlimit": n, "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata"})
    out = []
    for p in (js.get("query", {}).get("pages") or {}).values():
        ii = (p.get("imageinfo") or [{}])[0]
        md = ii.get("extmetadata", {})
        lic = strip(md.get("LicenseShortName", {}).get("value", ""))
        out.append({"title": p["title"], "url": ii.get("url"), "page": ii.get("descriptionurl"),
                    "duration": ii.get("duration"), "w": ii.get("width"), "h": ii.get("height"),
                    "licence": lic, "author": strip(md.get("Artist", {}).get("value", ""))[:120],
                    "desc": strip(md.get("ImageDescription", {}).get("value", ""))[:200]})
    return out


BLOCK = re.compile(r"police|deput|suspect|chase|marine|army|soldier|navy|protest|interview|people|\bman\b|woman|girl|boy|kid|"
                   r"festival|competition|trailer|disassembl|upgrade|cartoon|episode|news|parade|match|game|speech|lecture", re.I)


def relevant(c, term):
    title = c["title"].lower()
    words = [w for w in re.findall(r"[a-z]+", term.lower()) if len(w) > 2]
    return all(w.rstrip("s") in title for w in words) and not BLOCK.search(title + " " + c["desc"])


def fetch(url, tries=4):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as ex:
            if ex.code != 429 or k == tries - 1:
                raise
            time.sleep(20 * (k + 1))


def transcoded(url):
    """Wikimedia's 720p VP9 derivative (smaller, kinder to their servers); the original if it is missing."""
    m = re.match(r"(https://upload\.wikimedia\.org/wikipedia/commons)/(\w)/(\w\w)/(.+)$", url or "")
    return [f"{m[1]}/transcoded/{m[2]}/{m[3]}/{m[4]}/{m[4]}.720p.vp9.webm", url] if m else [url]


def usable(c):
    lic = c["licence"].lower().replace("-", " ")
    if "sa" in lic.split() or "share" in lic or "nc" in lic.split() or "nd" in lic.split():
        return False
    if not (lic.startswith("public domain") or lic.startswith("cc0") or lic.startswith("pd") or
            re.match(r"^cc by [0-9.]+$", lic)):
        return False
    return (c["w"] or 0) >= 640 and 4 <= (c["duration"] or 0) <= 900


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("request")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    req = json.load(open(a.request))
    os.makedirs(a.out, exist_ok=True)
    man_path = os.path.join(a.out, "manifest.csv")
    rows = list(csv.DictReader(open(man_path))) if os.path.exists(man_path) else []
    have = {r["source"] for r in rows}
    log = []
    for tag, terms in req["tags"].items():
        got = sum(1 for r in rows if r["tag"] == tag)
        for term in terms:
            if got >= req.get("per_tag", 3):
                break
            try:
                cands = [c for c in search(term, 40) if usable(c) and relevant(c, term) and c["url"] not in have]
                time.sleep(2)
            except Exception as ex:  # noqa: BLE001
                log.append(f"search {term}: {ex}")
                continue
            log.append(f"search {term}: {len(cands)} usable")
            for c in cands[:2]:
                if got >= req.get("per_tag", 3):
                    break
                name = f"{tag}-{got + 1}"
                src = os.path.join(a.out, "_src")
                try:
                    for u in transcoded(c["url"]):
                        try:
                            open(src, "wb").write(fetch(u))
                            break
                        except urllib.error.HTTPError as ex:
                            if ex.code != 404:
                                raise
                    start = max(0.0, min((c["duration"] or 10) * 0.3, (c["duration"] or 10) - 9))
                    mp4 = os.path.join(a.out, name + ".mp4")
                    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{start:.1f}", "-i", src, "-t", "8", "-an",
                                    "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
                                    "-c:v", "libx264", "-crf", "26", "-preset", "slow", "-pix_fmt", "yuv420p", mp4], check=True)
                    sheet = os.path.join(a.out, name + "-sheet.jpg")
                    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-vf",
                                    "fps=0.5,scale=270:480,tile=4x1", "-frames:v", "1", sheet], check=True)
                except Exception as ex:  # noqa: BLE001
                    log.append(f"  {c['title']}: {ex}")
                    continue
                finally:
                    if os.path.exists(src):
                        os.remove(src)
                rows.append({"file": name + ".mp4", "tag": tag, "term": term, "title": c["title"], "licence": c["licence"],
                             "author": c["author"], "page": c["page"], "source": c["url"], "desc": c["desc"],
                             "faces_checked": "no"})
                have.add(c["url"])
                got += 1
                log.append(f"  kept {name}: {c['title']} ({c['licence']})")
                time.sleep(4)
    with open(man_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["file", "tag", "term", "title", "licence", "author", "page", "source", "desc", "faces_checked"])
        w.writeheader()
        w.writerows(rows)
    open(os.path.join(a.out, "fetch-log.txt"), "a").write("\n".join(log) + "\n")
    print("\n".join(log))


if __name__ == "__main__":
    main()
