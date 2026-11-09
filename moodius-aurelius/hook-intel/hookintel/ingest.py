"""Load fetched metadata, manual URL sheets, editorial notes and Metricool exports into the database.

Nothing here invents a number: a field the source did not provide stays NULL and is listed in `missing`.
"""
import csv, datetime as dt, glob, json, os, statistics

from . import config, db

VIDEO_FIELDS = ["published", "duration_s", "views", "likes", "comments", "followers", "creator_median_views",
                "first_spoken", "first_onscreen", "visual_opening"]


def _date(s):
    if not s:
        return None
    s = str(s)
    if s.isdigit() and len(s) == 8:                     # yt-dlp upload_date
        return f"{s[:4]}-{s[4:6]}-{s[6:]}"
    if s.isdigit():                                      # unix timestamp
        return dt.datetime.fromtimestamp(int(s), dt.timezone.utc).date().isoformat()
    return s[:10]


def _in_window(published, ref):
    if not published:
        return None
    try:
        age = (dt.date.fromisoformat(ref[:10]) - dt.date.fromisoformat(published)).days
    except ValueError:
        return None
    return int(0 <= age <= config.RESEARCH_WINDOW_DAYS)


def _median(values):
    vals = [v for v in values if isinstance(v, (int, float))]
    return (statistics.median(vals), len(vals)) if len(vals) >= config.MIN_BASELINE_N else (None, len(vals))


def finish(row, ref):
    """Derive outlier ratio, window flag and the missing-field list."""
    if row.get("views") and row.get("creator_median_views"):
        row["outlier_ratio"] = round(row["views"] / row["creator_median_views"], 2)
    row["in_window"] = _in_window(row.get("published"), ref)
    if row.get("duration_s") is not None:
        row["short_form"] = int(row["duration_s"] <= config.SHORT_FORM_MAX_S)
    row["missing"] = [f for f in VIDEO_FIELDS + ["outlier_ratio"] if row.get(f) in (None, "")]
    return row


def ingest_fetch(con, path, cycle=None):
    """path: data/raw/<cycle>/fetch.json written by remote/fetch.py."""
    data = json.load(open(path))
    cycle = cycle or os.path.basename(os.path.dirname(path))
    ref = data["fetched_at"]
    videos = {}
    search_by_id = {e["id"]: e for e in data.get("youtube_search", []) if e.get("id")}

    for ch in data.get("youtube_channels", []):
        cid = ch.get("channel_id")
        if not cid:
            continue
        median, n = _median([s.get("views") for s in ch.get("shorts", [])])
        source = "median views of the channel's last 30 Shorts (Shorts tab, rounded counts)"
        if median is None:  # no Shorts tab: fall back to the Shorts inside the RSS feed (exact counts)
            median, n = _median([r.get("views") for r in ch.get("rss", []) if r.get("is_short")])
            source = "median views of the Shorts among the channel's last 15 uploads (RSS)"
        db.upsert(con, "creators", {
            "id": f"youtube:{cid}", "platform": "youtube", "name": ch.get("channel"), "handle": ch.get("handle"),
            "url": f"https://www.youtube.com/channel/{cid}", "followers": ch.get("followers"),
            "baseline_median_views": median, "baseline_n": n,
            "baseline_source": source,
            "fetched_at": ref})
        for r in ch.get("rss", []):
            if not r.get("is_short"):
                continue
            s = search_by_id.get(r["id"], {})
            videos[f"youtube:{r['id']}"] = {
                "id": f"youtube:{r['id']}", "platform": "youtube", "url": r["url"], "creator_id": f"youtube:{cid}",
                "creator": ch.get("channel"), "title": r.get("title"), "published": _date(r.get("published")),
                "duration_s": s.get("duration"), "views": r.get("views"), "likes": r.get("rating_count"),
                "likes_source": "YouTube RSS rating count" if r.get("rating_count") is not None else None,
                "comments": None, "followers": ch.get("followers"), "creator_median_views": median,
                "cover_text": r.get("cover_ocr"), "route": "channel_rss", "query": None, "fetched_at": ref,
                "cycle": cycle, "short_form": 1, "notes": (r.get("description") or "")[:300] or None}

    channel_baseline = {c["id"]: c for c in db.rows(con, "SELECT * FROM creators")}
    for e in data.get("youtube_search", []):
        vid = f"youtube:{e.get('id')}"
        if vid in videos or not e.get("id") or (e.get("duration") or 999) > config.SHORT_FORM_MAX_S:
            continue
        c = channel_baseline.get(f"youtube:{e.get('channel_id')}", {})
        videos[vid] = {
            "id": vid, "platform": "youtube", "url": f"https://www.youtube.com/shorts/{e['id']}",
            "creator_id": f"youtube:{e.get('channel_id')}", "creator": e.get("channel"), "title": e.get("title"),
            "published": _date(e.get("timestamp")), "duration_s": e.get("duration"), "views": e.get("view_count"),
            "followers": c.get("followers"), "creator_median_views": c.get("baseline_median_views"),
            "route": e.get("_route"), "query": e.get("_query"), "fetched_at": ref, "cycle": cycle}

    for handle, items in (data.get("tiktok") or {}).items():
        median, n = _median([i.get("view_count") for i in items])
        db.upsert(con, "creators", {"id": f"tiktok:{handle}", "platform": "tiktok", "name": handle, "handle": handle,
                                    "url": f"https://www.tiktok.com/@{handle}", "baseline_median_views": median,
                                    "baseline_n": n, "baseline_source": "median views of the profile's fetched videos",
                                    "fetched_at": ref})
        for i in items:
            videos[f"tiktok:{i['id']}"] = {
                "id": f"tiktok:{i['id']}", "platform": "tiktok", "url": i["url"], "creator_id": f"tiktok:{handle}",
                "creator": handle, "title": i.get("title") or i.get("description"), "published": _date(i.get("timestamp")),
                "duration_s": i.get("duration"), "views": i.get("view_count"), "likes": i.get("like_count"),
                "likes_source": "TikTok" if i.get("like_count") is not None else None, "comments": i.get("comment_count"),
                "creator_median_views": median, "route": "tiktok_profile", "fetched_at": ref, "cycle": cycle,
                "notes": "Research only: Moodius does not post to TikTok."}

    for term, items in (data.get("podcasts") or {}).items():
        for i in items:
            url = i.get("trackViewUrl")
            if not url:
                continue
            videos[f"podcast:{url}"] = {
                "id": f"podcast:{url}", "platform": "podcast", "url": url, "creator": i.get("collectionName"),
                "title": i.get("trackName"), "published": _date(i.get("releaseDate")),
                "duration_s": (i.get("trackTimeMillis") or 0) / 1000 or None, "route": "apple_podcasts_search",
                "query": term, "fetched_at": ref, "cycle": cycle, "short_form": 0,
                "notes": "Podcasts publish no view counts; useful as source material for evergreen ideas only."}

    for url, full in (data.get("full") or {}).items():
        if not full:
            continue
        platform = (full.get("extractor_key") or "web").lower()
        vid = f"{'youtube' if 'youtube' in platform else platform}:{full.get('id')}"
        row = videos.get(vid, {"id": vid, "platform": platform, "url": url, "cycle": cycle, "fetched_at": ref,
                               "route": "full_page"})
        row.update({k: v for k, v in {
            "title": full.get("title"), "published": _date(full.get("upload_date")), "duration_s": full.get("duration"),
            "views": full.get("view_count"), "likes": full.get("like_count"), "comments": full.get("comment_count"),
            "followers": full.get("channel_follower_count"), "first_spoken": full.get("first_spoken"),
            "creator": full.get("channel") or full.get("uploader")}.items() if v is not None})
        if full.get("like_count") is not None:
            row["likes_source"] = "platform"
        videos[vid] = row

    for row in videos.values():
        db.upsert(con, "videos", finish(row, ref))
    con.commit()
    return len(videos)


def ingest_manual(con, csv_path, cycle="manual"):
    """Manually supplied URLs (Instagram reels, podcast clips...). Columns: see data/manual-urls.example.csv."""
    n = 0
    ref = dt.datetime.now(dt.timezone.utc).isoformat()
    for r in csv.DictReader(open(csv_path, encoding="utf-8")):
        if not r.get("url"):
            continue
        num = lambda k: float(r[k]) if r.get(k) not in (None, "") else None  # noqa: E731
        row = {"id": r.get("id") or f"{r.get('platform') or 'manual'}:{r['url'].rstrip('/').split('/')[-1]}",
               "platform": r.get("platform") or "manual", "url": r["url"], "creator": r.get("creator") or None,
               "title": r.get("title") or None, "published": r.get("published") or None,
               "duration_s": num("duration_s"), "views": num("views"), "likes": num("likes"),
               "likes_source": "manual" if r.get("likes") else None, "comments": num("comments"),
               "followers": num("followers"), "creator_median_views": num("creator_median_views"),
               "first_spoken": r.get("first_spoken") or None, "first_onscreen": r.get("first_onscreen") or None,
               "visual_opening": r.get("visual_opening") or None, "notes": r.get("notes") or None,
               "route": "manual", "fetched_at": ref, "cycle": cycle}
        db.upsert(con, "videos", finish(row, ref))
        n += 1
    con.commit()
    return n


def apply_editorial(con, path):
    """Editorial notes: fields that need a human (or a Claude session) to watch or judge the video."""
    notes = json.load(open(path))
    video_cols = {"first_spoken", "first_onscreen", "visual_opening", "subject", "emotional_trigger", "narrative_format"}
    hook_cols = {"why", "adaptation", "first_frame", "music", "length_s", "visual_style"}
    n = 0
    for vid, fields in notes.get("videos", {}).items():
        if not db.rows(con, "SELECT id FROM videos WHERE id=?", (vid,)):
            continue
        v = {k: fields[k] for k in video_cols if fields.get(k)}
        if v:
            sets = ",".join(f"{k}=?" for k in v)
            con.execute(f"UPDATE videos SET {sets} WHERE id=?", [*v.values(), vid])
        h = {k: fields[k] for k in hook_cols if fields.get(k)}
        if h:
            db.upsert(con, "hooks", {"video_id": vid, **h}, key="video_id")
        n += 1
    con.commit()
    return n


def ingest_all(con):
    total = 0
    for path in sorted(glob.glob(os.path.join(config.RAW, "*", "fetch.json"))):
        total += ingest_fetch(con, path)
    for path in sorted(glob.glob(os.path.join(config.DATA, "manual-urls*.csv"))):
        if "example" not in path:
            total += ingest_manual(con, path)
    for path in sorted(glob.glob(os.path.join(config.EDITORIAL, "*.json"))):
        apply_editorial(con, path)
    return total


# ---------- own account (Metricool) ----------
METRICOOL_REELS = {  # Metricool Data Studio field id -> own_posts column
    "IGRE02": "published", "IGRE03": "caption", "IGRE06": "url", "IGRE07": "comments", "IGRE10": "likes",
    "IGRE11": "reach", "IGRE12": "saves", "IGRE21": "shares", "IGRE23": "views", "IGRE24": "avg_watch_s",
    "IGRE26": "duration_s", "IGRE27": "retention", "IGRE28": "view_rate_3s", "IGRE29": "reposts"}


def ingest_metricool(con, path):
    """A Metricool getAnalyticsDataByMetrics export saved as {"fields": [...], "rows": [[...]]}."""
    data = json.load(open(path))
    fields = data["fields"]
    n = 0
    for r in data["rows"]:
        rec = {METRICOOL_REELS.get(f, f): v for f, v in zip(fields, r)}
        ts = rec.get("published") or ""
        published = (f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}T{ts[8:10]}:{ts[10:12]}Z" if len(ts) >= 12 else ts) or None
        num = lambda k: float(rec[k]) if rec.get(k) not in (None, "") else None  # noqa: E731
        caption = rec.get("caption") or ""
        db.upsert(con, "own_posts", {
            "id": (rec.get("url") or "").rstrip("/").split("/")[-1] or published, "url": rec.get("url"),
            "published": published, "kind": "reel", "hook": caption.split("\n")[0].strip() or None, "caption": caption,
            "reach": num("reach"), "views": num("views"), "avg_watch_s": num("avg_watch_s"),
            "view_rate_3s": num("view_rate_3s"), "duration_s": num("duration_s"), "likes": num("likes"),
            "comments": num("comments"), "saves": num("saves"), "shares": num("shares"), "follows": None,
            "reposts": num("reposts"), "source": f"Metricool brand {data.get('brand_id', '?')}",
            "imported_at": data.get("pulled_at")})
        n += 1
    con.commit()
    return n
