"""Importers: CSV templates, Instagram/Metricool CSV exports, Metricool connector JSON.

Every importer first registers the raw file (copied, hashed, never imported
twice), then writes normalised rows. Empty cells are stored as NULL
("not reported"), never as 0.
"""
import csv
import datetime as dt
import json
import re

from . import db
from .config import ACCOUNT_METRICS, CONTENT_METRICS, LONDON, UTC, now_utc_iso

# Header aliases seen in Instagram's own export, Metricool's CSV export and
# our templates. Matching is case-insensitive and ignores spaces/underscores.
ALIASES = {
    "media_id": ["media_id", "id", "post id", "postid", "reel id", "story id", "publication id"],
    "format": ["format", "type", "post type", "media type", "media_product_type"],
    "published_at": ["published_at", "timestamp", "publish time", "date", "published", "date with time"],
    "permalink": ["permalink", "url", "post url", "reel url", "link"],
    "first_line": ["first_line", "content", "description", "caption", "text"],
    "reach": ["reach", "reach (organic)", "reach organic", "organic reach", "accounts reached"],
    "views": ["views", "plays", "impressions"],
    "likes": ["likes"],
    "comments": ["comments"],
    "saves": ["saves", "saved"],
    "shares": ["shares"],
    "follows": ["follows", "follows from post"],
    "profile_visits": ["profile_visits", "profile visits", "profile activity"],
    "avg_watch_s": ["avg_watch_s", "average watch time", "avg watch time"],
    "total_watch_s": ["total_watch_s", "video view total time", "watch time"],
    "skip_rate_pct": ["skip_rate_pct", "skip rate"],
    "view_rate_3s_pct": ["view_rate_3s_pct", "reel view rate", "view rate"],
    "replies": ["replies"],
    "taps_forward": ["taps_forward", "taps forward"],
    "taps_back": ["taps_back", "taps back"],
    "exits": ["exits"],
    "scope": ["scope"],
    "collected_at_utc": ["collected_at_utc", "collected at"],
    "published_tz": ["published_tz"],
}


def _key(s):
    return re.sub(r"[\s_]+", " ", (s or "").strip().lower())


def map_headers(headers):
    lookup = {_key(a): canon for canon, names in ALIASES.items() for a in names}
    mapping, unknown = {}, []
    for h in headers:
        canon = lookup.get(_key(h))
        if canon and canon not in mapping.values():
            mapping[h] = canon
        else:
            unknown.append(h)
    return mapping, unknown


def num(value):
    """'1,234' -> 1234.0; '' / None / '-' / 'n/a' -> None (missing, not zero)."""
    if value is None:
        return None
    s = str(value).strip().replace(",", "")
    if s in ("", "-", "--", "n/a", "na", "null", "none"):
        return None
    if s.endswith("%"):
        s = s[:-1]
    try:
        return float(s)
    except ValueError:
        return None


def kind_of(raw):
    r = (raw or "").upper()
    if "REEL" in r or "VIDEO" in r or "CLIP" in r:
        return "reel"
    if "CAROUSEL" in r or "ALBUM" in r:
        return "carousel"
    if "STORY" in r:
        return "story"
    if r:
        return "image"
    return "unknown"


def parse_time(value, tz_name="Europe/London"):
    """Parse common timestamp shapes. Naive times are read in tz_name. Returns aware UTC."""
    s = (value or "").strip()
    if not s:
        return None
    if re.fullmatch(r"\d{14}", s):                       # Metricool 20261026110348 (UTC)
        return dt.datetime.strptime(s, "%Y%m%d%H%M%S").replace(tzinfo=UTC)
    s = s.replace("Z", "+00:00").replace("+0000", "+00:00")
    for fmt in (None, "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M", "%m/%d/%Y %H:%M", "%Y-%m-%d"):
        try:
            t = dt.datetime.fromisoformat(s) if fmt is None else dt.datetime.strptime(s, fmt)
        except ValueError:
            continue
        if t.tzinfo is None:
            from zoneinfo import ZoneInfo
            t = t.replace(tzinfo=ZoneInfo(tz_name))
        return t.astimezone(UTC)
    return None


def _read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
        headers = rows[0].keys() if rows else []
    return rows, list(headers)


def import_account_csv(con, path, source="manual_csv", reporting_tz="Europe/London",
                       default_scope="organic", is_demo=False):
    """templates/account_daily.csv: one row per day, one column per metric."""
    import_id, new = db.register_raw(con, path, source, "account", is_demo)
    if not new:
        return {"status": "skipped", "reason": "this exact file was already imported"}
    rows, headers = _read_csv(path)
    known = set(ACCOUNT_METRICS) | {"date", "scope", "reporting_tz", "collected_at_utc"}
    unknown = [h for h in headers if h not in known]
    stored = 0
    for r in rows:
        date = (r.get("date") or "").strip()[:10]
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            continue
        collected = (r.get("collected_at_utc") or "").strip() or now_utc_iso()
        scope = (r.get("scope") or "").strip() or default_scope
        tz = (r.get("reporting_tz") or "").strip() or reporting_tz
        for metric in ACCOUNT_METRICS:
            if metric not in r:
                continue                         # column absent: metric not tracked by this source
            con.execute(
                "INSERT OR REPLACE INTO account_metric VALUES (?,?,?,?,?,?,?,?,?)",
                (date, tz, metric, num(r[metric]), scope, source, collected, import_id, int(is_demo)),
            )
            stored += 1
    con.execute("UPDATE raw_import SET rows_in=?, rows_stored=? WHERE import_id=?", (len(rows), stored, import_id))
    con.commit()
    return {"status": "ok", "rows": len(rows), "values": stored, "unknown_columns": unknown}


def _store_content(con, media_id, fmt, published_utc, first_line, permalink, source, is_demo):
    pub_london = published_utc.astimezone(LONDON).isoformat() if published_utc else None
    con.execute(
        "INSERT INTO content VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(media_id) DO UPDATE SET "
        "format=excluded.format, published_at_utc=COALESCE(excluded.published_at_utc, published_at_utc), "
        "published_at_london=COALESCE(excluded.published_at_london, published_at_london), "
        "first_line=COALESCE(excluded.first_line, first_line), permalink=COALESCE(excluded.permalink, permalink)",
        (media_id, fmt, published_utc.isoformat() if published_utc else None, pub_london,
         first_line, permalink, source, int(is_demo)),
    )


def _age_hours(published_utc, collected_iso):
    if not published_utc:
        return None
    c = dt.datetime.fromisoformat(collected_iso)
    return round((c - published_utc).total_seconds() / 3600, 1)


def import_content_csv(con, path, source="manual_csv", default_scope="organic", is_demo=False,
                       default_format=None):
    """templates/content_snapshot.csv, or an Instagram / Metricool posts export."""
    import_id, new = db.register_raw(con, path, source, "content", is_demo)
    if not new:
        return {"status": "skipped", "reason": "this exact file was already imported"}
    rows, headers = _read_csv(path)
    mapping, unknown = map_headers(headers)
    stored = 0
    for raw in rows:
        r = {canon: raw.get(h) for h, canon in mapping.items()}
        media_id = (r.get("media_id") or "").strip() or (r.get("permalink") or "").strip()
        if not media_id:
            continue
        tz = (r.get("published_tz") or "").strip() or "Europe/London"
        published = parse_time(r.get("published_at"), tz)
        fmt = kind_of(r.get("format")) if r.get("format") else (default_format or "unknown")
        text = (r.get("first_line") or "").strip()
        _store_content(con, media_id, fmt, published, text.splitlines()[0][:200] if text else None,
                       (r.get("permalink") or "").strip() or None, source, is_demo)
        collected = (r.get("collected_at_utc") or "").strip() or now_utc_iso()
        scope = (r.get("scope") or "").strip() or default_scope
        for metric in CONTENT_METRICS:
            if metric not in r:
                continue
            con.execute(
                "INSERT OR REPLACE INTO content_snapshot VALUES (?,?,?,?,?,?,?,?)",
                (media_id, metric, num(r[metric]), scope, collected,
                 _age_hours(published, collected), source, import_id),
            )
            stored += 1
    con.execute("UPDATE raw_import SET rows_in=?, rows_stored=? WHERE import_id=?", (len(rows), stored, import_id))
    con.commit()
    return {"status": "ok", "rows": len(rows), "values": stored, "unknown_columns": unknown}


def import_tags_csv(con, path, is_demo=False):
    """templates/content_tags.csv: your own labels per post (topic, hook, CTA, effort)."""
    import_id, new = db.register_raw(con, path, "manual_csv", "tags", is_demo)
    rows, _ = _read_csv(path)
    n = 0
    for r in rows:
        mid = (r.get("media_id") or "").strip()
        if not mid:
            continue
        con.execute(
            "INSERT OR REPLACE INTO content_tags VALUES (?,?,?,?,?,?,?,?,?,?)",
            (mid, r.get("pillar") or None, r.get("topic") or None, r.get("hook_type") or None,
             r.get("cta") or None, num(r.get("duration_s")), num(r.get("production_minutes")),
             r.get("experiment_id") or None, r.get("arm") or None, r.get("notes") or None),
        )
        n += 1
    con.commit()
    return {"status": "ok" if new else "re-applied", "rows": n}


def import_experiments_csv(con, path):
    rows, _ = _read_csv(path)
    for r in rows:
        con.execute(
            "INSERT OR REPLACE INTO experiment VALUES (?,?,?,?,?,?,?,?,?,?)",
            (r["experiment_id"], r["hypothesis"], r["variable"], r["primary_metric"],
             int(num(r["window_days"]) or 14), r["decision_rule"], r.get("start_date") or None,
             r.get("end_date") or None, r.get("status") or "planned", r.get("result") or None),
        )
    con.commit()
    return {"status": "ok", "rows": len(rows)}


# Metricool field IDs (Analytics "Data Studio" fields) -> our vocabulary.
METRICOOL_ACCOUNT = {
    "IGEV01": ("followers_total", "unknown"), "IGEV02": ("following_total", "unknown"),
    "IGEV43": ("follows", "unknown"), "IGEV44": ("unfollows", "unknown"),
    "IGEV05": ("views", "organic+paid"), "IGEV06": ("reach", "organic+paid"),
    "IGEV42": ("accounts_engaged", "unknown"), "IGEV18": ("story_reach", "organic"),
    "IGEV16": ("stories_published", "unknown"),
}
METRICOOL_CONTENT = {
    "IGPO14": ("reach", "organic"), "IGPO19": ("reach", "paid"), "IGPO28": ("views", "organic"),
    "IGPO13": ("likes", "organic"), "IGPO08": ("comments", "organic"), "IGPO15": ("saves", "organic"),
    "IGPO27": ("shares", "organic"), "IGPO29": ("follows", "organic"),
    "IGRE11": ("reach", "organic"), "IGRE16": ("reach", "paid"), "IGRE23": ("views", "organic"),
    "IGRE10": ("likes", "organic"), "IGRE07": ("comments", "organic"), "IGRE12": ("saves", "organic"),
    "IGRE21": ("shares", "organic"), "IGRE24": ("avg_watch_s", "organic"),
    "IGRE25": ("total_watch_s", "organic"), "IGRE28": ("view_rate_3s_pct", "organic"),
    "IGST10": ("reach", "organic"), "IGST14": ("reach", "paid"), "IGST11": ("replies", "organic"),
    "IGST08": ("exits", "organic"), "IGST12": ("taps_back", "organic"), "IGST13": ("taps_forward", "organic"),
}
METRICOOL_ID = {"posts": "IGPO04", "reels": "IGRE04", "stories": "IGST04"}
METRICOOL_TIME = {"posts": "IGPO02", "reels": "IGRE02", "stories": "IGST02"}
METRICOOL_TEXT = {"posts": "IGPO03", "reels": "IGRE03", "stories": "IGST03"}
METRICOOL_TYPE = {"posts": "IGPO07", "stories": None, "reels": None}


def import_metricool_json(con, path, is_demo=False):
    """A Metricool connector pull saved as JSON: {"collected_at_utc", "reporting_tz",
    "evolution": {"fields": [...], "rows": [[...]]}, "posts": {...}, "reels": {...}, "stories": {...}}.
    Evolution rows end with the date (YYYYMMDD, Metricool brand time zone)."""
    import_id, new = db.register_raw(con, path, "metricool_connector", "account+content", is_demo)
    if not new:
        return {"status": "skipped", "reason": "this exact file was already imported"}
    with open(path, encoding="utf-8") as f:
        pull = json.load(f)
    collected = pull["collected_at_utc"]
    tz = pull.get("reporting_tz", "Europe/Madrid")
    stored = 0
    evo = pull.get("evolution") or {}
    for row in evo.get("rows", []):
        date = row[-1]
        date = f"{date[:4]}-{date[4:6]}-{date[6:8]}"
        for field, value in zip(evo["fields"], row[:-1]):
            if field not in METRICOOL_ACCOUNT:
                continue
            metric, scope = METRICOOL_ACCOUNT[field]
            con.execute("INSERT OR REPLACE INTO account_metric VALUES (?,?,?,?,?,?,?,?,?)",
                        (date, tz, metric, num(value), scope, "metricool_connector", collected,
                         import_id, int(is_demo)))
            stored += 1
    for block in ("posts", "reels", "stories"):
        part = pull.get(block) or {}
        fields = part.get("fields", [])
        for row in part.get("rows", []):
            rec = dict(zip(fields, row))
            mid = rec.get(METRICOOL_ID[block])
            if not mid:
                continue
            published = parse_time(rec.get(METRICOOL_TIME[block]), "UTC")
            tfield = METRICOOL_TYPE[block]
            fmt = {"reels": "reel", "stories": "story"}.get(block) or kind_of(rec.get(tfield))
            text = (rec.get(METRICOOL_TEXT[block]) or "").strip()
            _store_content(con, mid, fmt, published, text.splitlines()[0][:200] if text else None,
                           None, "metricool_connector", is_demo)
            for field, value in rec.items():
                if field not in METRICOOL_CONTENT:
                    continue
                metric, scope = METRICOOL_CONTENT[field]
                con.execute("INSERT OR REPLACE INTO content_snapshot VALUES (?,?,?,?,?,?,?,?)",
                            (mid, metric, num(value), scope, collected, _age_hours(published, collected),
                             "metricool_connector", import_id))
                stored += 1
    con.execute("UPDATE raw_import SET rows_stored=? WHERE import_id=?", (stored, import_id))
    con.commit()
    return {"status": "ok", "values": stored}
