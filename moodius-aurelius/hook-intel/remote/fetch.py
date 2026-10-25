#!/usr/bin/env python3
"""Hook-intel fetcher: public metadata only. No login, no cookies, no video downloads.

Runs anywhere yt-dlp can reach the platforms (GitHub Actions runner, or the owner's Mac).
The cloud container that builds this project cannot reach YouTube, TikTok or Instagram.

    python3 remote/fetch.py requests/2026-10-22-mvp.json     # writes data/raw/<request name>/
    python3 remote/fetch.py requests/x.json --full           # also tries full video pages + captions
                                                            # (blocked on datacenter IPs; works on a home IP)
Sources per request:
  youtube_search   results filtered to "this month, under 4 min" (falls back to plain ytsearch):
                   title, duration, views, channel. No upload date on this route.
  youtube_channels channel RSS (last 15 uploads: date, views, rating count) + Shorts tab (views of the
                   last 30 Shorts, the creator baseline) + follower count
  tiktok_users     public profile feed through yt-dlp (research only: Moodius never posts to TikTok)
  podcasts         Apple Podcasts search API (titles, dates; podcasts publish no view counts)
  urls             manually supplied video URLs (any yt-dlp-supported site), full-page attempt
Every attempt is logged in access-log.json as ok/failed with the error, so missing data is never hidden.
"""
import argparse, datetime as dt, json, os, re, subprocess, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015",
      "m": "http://search.yahoo.com/mrss/"}
SP_MONTH_SHORT = "EgQIBBgB"  # YouTube results filter: uploaded this month + under 4 minutes


class Fetcher:
    def __init__(self, out, pause=1.0):
        self.out, self.pause, self.log = out, pause, []
        os.makedirs(out, exist_ok=True)

    def note(self, source, target, ok, detail=""):
        self.log.append({"source": source, "target": target, "ok": ok, "detail": str(detail)[-300:],
                         "at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")})
        print("OK  " if ok else "FAIL", source, target, "" if ok else str(detail)[-160:], flush=True)

    def ytdlp(self, args, timeout=180):
        time.sleep(self.pause)  # stay well under any rate limit
        p = subprocess.run(["yt-dlp", "--no-warnings", "--ignore-config", *args],
                           capture_output=True, text=True, timeout=timeout)
        if p.returncode != 0 or p.stdout.strip() in ("", "null"):
            raise RuntimeError(p.stderr.strip().splitlines()[-1] if p.stderr.strip() else "no output")
        return json.loads(p.stdout)

    def http(self, url, timeout=25):
        time.sleep(self.pause)
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=timeout) as r:
            return r.read()

    # ---------- YouTube ----------
    def youtube_search(self, query, n):
        dated = "https://www.youtube.com/results?" + urllib.parse.urlencode({"search_query": query, "sp": SP_MONTH_SHORT})
        for route, target in (("results_month_short", dated), ("ytsearch", f"ytsearch{n}:{query} shorts")):
            try:
                data = self.ytdlp(["--flat-playlist", "-J", "--playlist-end", str(n), target])
                rows = [e | {"_route": route, "_query": query} for e in data.get("entries") or []]
                self.note("youtube_search", f"{query} [{route}]", True, f"{len(rows)} results")
                return rows
            except Exception as ex:  # noqa: BLE001
                self.note("youtube_search", f"{query} [{route}]", False, ex)
        return []

    def youtube_rss(self, channel_id):
        root = ET.fromstring(self.http(f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"))
        out = []
        for e in root.findall("a:entry", NS):
            stats = e.find("m:group/m:community/m:statistics", NS)
            rating = e.find("m:group/m:community/m:starRating", NS)
            link = e.find("a:link", NS).get("href")
            out.append({"id": e.find("yt:videoId", NS).text, "title": e.find("a:title", NS).text, "url": link,
                        "is_short": "/shorts/" in link, "published": e.find("a:published", NS).text,
                        "views": int(stats.get("views")) if stats is not None else None,
                        "rating_count": int(rating.get("count")) if rating is not None else None,
                        "description": (e.find("m:group/m:description", NS).text or "")[:600]})
        return out

    def youtube_channel(self, ref):
        """ref: channel id (UC...) or @handle."""
        base = f"https://www.youtube.com/channel/{ref}" if ref.startswith("UC") else f"https://www.youtube.com/{ref}"
        ch = {"ref": ref}
        try:
            data = self.ytdlp(["--flat-playlist", "-J", "--playlist-end", "30", base + "/shorts"])
            ch.update(channel_id=data.get("channel_id"), channel=data.get("channel"),
                      handle=data.get("uploader_id"), followers=data.get("channel_follower_count"),
                      shorts=[{"id": e.get("id"), "title": e.get("title"), "views": e.get("view_count")}
                              for e in data.get("entries") or []])
            self.note("youtube_shorts_tab", ref, True, f"{len(ch['shorts'])} shorts, followers={ch['followers']}")
        except Exception as ex:  # noqa: BLE001
            self.note("youtube_shorts_tab", ref, False, ex)
        for tab in getattr(self, "tabs", []):  # e.g. "videos" for long-form titles + view counts
            try:
                data = self.ytdlp(["--flat-playlist", "-J", "--playlist-end", str(getattr(self, "tab_n", 60)), base + "/" + tab])
                ch.setdefault("channel_id", data.get("channel_id"))
                ch[tab] = [{"id": e.get("id"), "title": e.get("title"), "views": e.get("view_count"),
                            "duration": e.get("duration")} for e in data.get("entries") or []]
                self.note(f"youtube_{tab}_tab", ref, True, f"{len(ch[tab])} items")
            except Exception as ex:  # noqa: BLE001
                self.note(f"youtube_{tab}_tab", ref, False, ex)
        cid = ch.get("channel_id") or (ref if ref.startswith("UC") else None)
        if cid:
            try:
                ch["rss"] = self.youtube_rss(cid)
                self.note("youtube_rss", cid, True, f"{len(ch['rss'])} uploads")
            except Exception as ex:  # noqa: BLE001
                self.note("youtube_rss", cid, False, ex)
        return ch

    # ---------- full page (home IP only) ----------
    def full_video(self, url):
        try:
            d = self.ytdlp(["-J", "--skip-download", url])
        except Exception as ex:  # noqa: BLE001
            self.note("full_video", url, False, ex)
            return None
        keep = {k: d.get(k) for k in ("id", "title", "upload_date", "duration", "view_count", "like_count",
                                       "comment_count", "channel", "channel_id", "channel_follower_count",
                                       "uploader", "uploader_id", "description", "webpage_url", "extractor_key")}
        keep["first_spoken"] = self.first_caption_line(d)
        self.note("full_video", url, True, "captions" if keep["first_spoken"] else "no captions")
        return keep

    def first_caption_line(self, info):
        """First ~6 s of English captions (json3), if the platform exposes them. No transcription model needed."""
        for bucket in ("subtitles", "automatic_captions"):
            for lang, tracks in (info.get(bucket) or {}).items():
                if not lang.startswith("en"):
                    continue
                for t in tracks:
                    if t.get("ext") != "json3":
                        continue
                    try:
                        words = []
                        for ev in json.loads(self.http(t["url"])).get("events", []):
                            if ev.get("tStartMs", 0) > 6000:
                                break
                            words += [s.get("utf8", "") for s in ev.get("segs") or []]
                        return re.sub(r"\s+", " ", "".join(words)).strip() or None
                    except Exception:  # noqa: BLE001
                        pass
        return None

    # ---------- TikTok ----------
    def tiktok_user(self, handle, n):
        try:
            data = self.ytdlp(["--flat-playlist", "-J", "--playlist-end", str(n), f"https://www.tiktok.com/@{handle}"])
            keep = ("id", "title", "description", "timestamp", "duration", "view_count", "like_count",
                    "comment_count", "repost_count", "channel", "uploader", "uploader_id", "track", "artist")
            rows = [{k: e.get(k) for k in keep} | {"url": f"https://www.tiktok.com/@{handle}/video/{e.get('id')}"}
                    for e in data.get("entries") or []]
            self.note("tiktok_user", handle, True, f"{len(rows)} videos")
            return rows
        except Exception as ex:  # noqa: BLE001
            self.note("tiktok_user", handle, False, ex)
            return []

    # ---------- podcasts ----------
    def podcasts(self, term, n):
        try:
            q = urllib.parse.urlencode({"term": term, "entity": "podcastEpisode", "limit": n})
            js = json.loads(self.http(f"https://itunes.apple.com/search?{q}"))
            rows = [{k: r.get(k) for k in ("trackName", "collectionName", "releaseDate", "trackTimeMillis",
                                           "trackViewUrl", "description")} for r in js.get("results", [])]
            self.note("podcasts", term, True, f"{len(rows)} episodes")
            return rows
        except Exception as ex:  # noqa: BLE001
            self.note("podcasts", term, False, ex)
            return []

    # ---------- covers + OCR (cover text, which is not necessarily the first frame) ----------
    def thumbnail(self, vid):
        path = os.path.join(self.out, "thumbs", f"{vid}.jpg")
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            try:
                open(path, "wb").write(self.http(f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"))
            except Exception as ex:  # noqa: BLE001
                self.note("thumbnail", vid, False, ex)
                return None
        return path

    @staticmethod
    def ocr(path):
        try:
            p = subprocess.run(["tesseract", path, "-", "--psm", "6"], capture_output=True, text=True, timeout=60)
            return re.sub(r"\s+", " ", p.stdout).strip() or None
        except FileNotFoundError:
            return None


def run(request_path, out_root, full=False):
    req = json.load(open(request_path))
    name = req.get("name") or os.path.splitext(os.path.basename(request_path))[0]
    out = os.path.join(out_root, name)
    f = Fetcher(out, pause=req.get("pause_s", 1.0))
    f.tabs, f.tab_n = req.get("channel_tabs", []), req.get("tab_n", 60)
    result = {"request": req, "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
              "youtube_search": [], "youtube_channels": [], "tiktok": {}, "podcasts": {}, "full": {}}
    for q in req.get("youtube_search", []):
        result["youtube_search"] += f.youtube_search(q, req.get("per_query", 20))
    refs = list(dict.fromkeys(req.get("youtube_channels", [])))
    if req.get("expand_search_channels", True):  # every channel that surfaced a short-form hit
        for e in result["youtube_search"]:
            if (e.get("duration") or 999) <= 180 and e.get("channel_id") and e["channel_id"] not in refs:
                refs.append(e["channel_id"])
    for ref in refs[: req.get("max_channels", 40)]:
        result["youtube_channels"].append(f.youtube_channel(ref))
    for h in req.get("tiktok_users", []):
        result["tiktok"][h] = f.tiktok_user(h, req.get("tiktok_per_user", 20))
    for t in req.get("podcasts", []):
        result["podcasts"][t] = f.podcasts(t, req.get("podcasts_per_term", 10))
    urls = list(req.get("urls", []))
    if full:
        for ch in result["youtube_channels"]:
            urls += [r["url"] for r in ch.get("rss", []) if r.get("is_short")][:5]
    for u in dict.fromkeys(urls):
        result["full"][u] = f.full_video(u)
    if req.get("thumbnails", True):
        for ch in result["youtube_channels"]:
            for r in ch.get("rss", []):
                if r.get("is_short"):
                    p = f.thumbnail(r["id"])
                    r["cover_ocr"] = f.ocr(p) if p else None
    if req.get("thumb_tabs"):  # covers + OCR for every Shorts-tab entry, not only the last 15 RSS uploads
        for ch in result["youtube_channels"]:
            for r in (ch.get("shorts") or [])[: req.get("thumb_tabs_n", 60)]:
                p = f.thumbnail(r["id"]) if r.get("id") else None
                r["cover_ocr"] = f.ocr(p) if p else None
    json.dump(result, open(os.path.join(out, "fetch.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(f.log, open(os.path.join(out, "access-log.json"), "w"), indent=1)
    print(f"done: {sum(x['ok'] for x in f.log)}/{len(f.log)} requests ok -> {out}")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("request")
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "raw"))
    ap.add_argument("--full", action="store_true", help="also try full video pages and captions (home IP)")
    a = ap.parse_args()
    run(a.request, a.out, a.full)
