"""Optional collector for Meta's official Instagram API (Instagram API with Facebook Login).

Uses only documented Graph API endpoints and the Python standard library:
  GET /{ig-user-id}?fields=followers_count,follows_count,media_count
  GET /{ig-user-id}/insights?metric=...&period=day&metric_type=total_value&since=&until=
  GET /{ig-user-id}/insights?metric=follows_and_unfollows&breakdown=follow_type&...
  GET /{ig-user-id}/media?fields=id,media_type,media_product_type,timestamp,permalink,caption
  GET /{media-id}/insights?metric=...
  GET /{ig-user-id}/stories (stories are only available for 24 hours)
Reference: developers.facebook.com/docs/instagram-platform (Insights, IG User
Insights, IG Media Insights), checked 27 Oct 2026.

Known limits (from Meta's docs): data can lag up to 48 hours; missing data
comes back as an empty list, not 0; follows_and_unfollows is not returned
under 100 followers; story metrics vanish after 24 hours and values under 5
error; story replies are 0 for accounts in Europe; reels have no per-post
follows or profile visits; album children have no insights.

The token is read from the macOS Keychain (service "moodius-ig-token") or the
MOODIUS_IG_TOKEN environment variable. It is never written to disk or logs.
"""
import datetime as dt
import json
import logging
import os
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

from . import db
from .config import LOG_DIR, LONDON, UTC, now_utc_iso

GRAPH = "https://graph.facebook.com"
VERSION = os.environ.get("MOODIUS_GRAPH_VERSION", "v26.0")
ACCOUNT_DAY_METRICS = ["reach", "views", "accounts_engaged", "total_interactions", "likes", "comments",
                       "saves", "shares", "replies", "profile_links_taps"]
MEDIA_METRICS = {
    "FEED": ["reach", "views", "likes", "comments", "saved", "shares", "follows", "profile_visits", "total_interactions"],
    "REELS": ["reach", "views", "likes", "comments", "saved", "shares", "ig_reels_avg_watch_time",
              "ig_reels_video_view_total_time", "total_interactions"],
    "STORY": ["reach", "views", "replies", "shares", "follows", "profile_visits", "navigation"],
}
RENAME = {"saved": "saves", "ig_reels_avg_watch_time": "avg_watch_s", "ig_reels_video_view_total_time": "total_watch_s",
          "profile_links_taps": "link_taps"}

log = logging.getLogger("moodius.meta")


class TokenMissing(RuntimeError):
    pass


def get_token():
    tok = os.environ.get("MOODIUS_IG_TOKEN")
    if tok:
        return tok.strip()
    try:
        out = subprocess.run(["security", "find-generic-password", "-s", "moodius-ig-token", "-w"],
                             capture_output=True, text=True, timeout=10)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    raise TokenMissing("No token found. See docs/META-API-SETUP.md step 6.")


def _redact(text, token):
    return text.replace(token, "[TOKEN]") if token else text


def call(path, params, token, tries=4):
    """GET with retries (2, 4, 8 s) on network errors, 5xx and rate limits."""
    q = dict(params, access_token=token)
    url = f"{GRAPH}/{VERSION}/{path}?{urllib.parse.urlencode(q)}"
    for attempt in range(1, tries + 1):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            body = _redact(e.read().decode(errors="replace"), token)
            retry = e.code >= 500 or e.code == 429 or '"code":4,' in body or '"code":17,' in body
            log.warning("HTTP %s on %s (try %d): %s", e.code, path, attempt, body[:300])
            if not retry or attempt == tries:
                raise RuntimeError(f"Meta API error {e.code} on {path}: {body[:300]}") from None
        except (urllib.error.URLError, TimeoutError) as e:
            log.warning("Network error on %s (try %d): %s", path, attempt, _redact(str(e), token))
            if attempt == tries:
                raise RuntimeError(f"Network error on {path}") from None
        time.sleep(2 ** attempt)


def _values(resp):
    """{"data":[{"name":..,"total_value":{"value":..}}]} -> {name: value}; missing stays missing."""
    out = {}
    for item in resp.get("data", []):
        tv = item.get("total_value")
        if tv is not None and "value" in tv:
            out[item["name"]] = tv["value"]
        elif item.get("values"):
            out[item["name"]] = item["values"][-1].get("value")
    return out


def collect(con, ig_user_id, days_back=3):
    """Pull the last `days_back` complete UK days plus all recent media. Saves the raw
    JSON responses to data/raw before storing anything."""
    os.makedirs(LOG_DIR, exist_ok=True)
    logging.basicConfig(filename=os.path.join(LOG_DIR, "collect.log"), level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    token = get_token()
    collected = now_utc_iso()
    raw = {"collected_at_utc": collected, "version": VERSION, "account": {}, "days": {}, "media": [], "stories": []}
    status, stored = "ok", 0
    try:
        raw["account"] = call(ig_user_id, {"fields": "followers_count,follows_count,media_count"}, token)
        today = dt.datetime.now(LONDON).date()
        for k in range(days_back, 0, -1):            # complete UK days only
            d = today - dt.timedelta(days=k)
            since = int(dt.datetime(d.year, d.month, d.day, tzinfo=LONDON).timestamp())
            nxt = d + dt.timedelta(days=1)
            until = int(dt.datetime(nxt.year, nxt.month, nxt.day, tzinfo=LONDON).timestamp())
            base = {"period": "day", "metric_type": "total_value", "since": since, "until": until}
            day = {"metrics": call(f"{ig_user_id}/insights", dict(base, metric=",".join(ACCOUNT_DAY_METRICS)), token)}
            try:
                day["follows"] = call(f"{ig_user_id}/insights",
                                      dict(base, metric="follows_and_unfollows", breakdown="follow_type"), token)
            except RuntimeError as e:       # not returned under 100 followers
                day["follows_error"] = str(e)[:200]
            raw["days"][str(d)] = day
        media = call(f"{ig_user_id}/media", {"fields": "id,media_type,media_product_type,timestamp,permalink,caption",
                                             "limit": 50}, token)
        for m in media.get("data", []):
            kind = m.get("media_product_type", "FEED")
            try:
                m["insights"] = call(f"{m['id']}/insights", {"metric": ",".join(MEDIA_METRICS.get(kind, MEDIA_METRICS["FEED"]))}, token)
            except RuntimeError as e:
                m["insights_error"] = str(e)[:200]
            raw["media"].append(m)
        stories = call(f"{ig_user_id}/stories", {"fields": "id,media_type,timestamp,permalink"}, token)
        for s in stories.get("data", []):
            try:
                s["insights"] = call(f"{s['id']}/insights", {"metric": ",".join(MEDIA_METRICS["STORY"])}, token)
            except RuntimeError as e:       # values under 5 return an error
                s["insights_error"] = str(e)[:200]
            raw["stories"].append(s)
    except RuntimeError as e:
        status = "partial" if raw["account"] else "failed"
        log.error(str(e))
    path = _save_raw(raw)
    stored = store(con, path, raw)
    db.log_collection(con, "meta_api", status, stored, None if status == "ok" else "see logs/collect.log")
    log.info("collect %s: %d values stored", status, stored)
    return status, stored


def _save_raw(raw):
    from .config import RAW_DIR
    os.makedirs(RAW_DIR, exist_ok=True)
    path = os.path.join(RAW_DIR, f"meta-api-{raw['collected_at_utc'].replace(':', '')}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(raw, f, indent=1)
    return path


def store(con, path, raw):
    from .importers import _age_hours, _store_content, kind_of, parse_time
    import_id, _ = db.register_raw(con, path, "meta_api", "account+content")
    c = raw["collected_at_utc"]
    n = 0

    def put_acc(date, metric, value, scope="organic"):
        nonlocal n
        con.execute("INSERT OR REPLACE INTO account_metric VALUES (?,?,?,?,?,?,?,?,0)",
                    (date, "Europe/London", metric, value, scope, "meta_api", c, import_id))
        n += 1

    if raw["account"].get("followers_count") is not None:
        # The follower total is a live count: it belongs to the collection day (UK).
        uk_day = dt.datetime.fromisoformat(c).astimezone(LONDON).date().isoformat()
        put_acc(uk_day, "followers_total", raw["account"]["followers_count"], "unknown")
        put_acc(uk_day, "following_total", raw["account"].get("follows_count"), "unknown")
    for date, day in raw["days"].items():
        vals = _values(day.get("metrics", {}))
        for name in ACCOUNT_DAY_METRICS:
            if name in vals and name not in ("total_interactions", "likes", "comments", "saves", "shares", "replies"):
                put_acc(date, RENAME.get(name, name), vals[name], "organic+paid" if name == "total_interactions" else "organic")
        for item in day.get("follows", {}).get("data", []):
            for b in item.get("total_value", {}).get("breakdowns", []):
                for res in b.get("results", []):
                    kind = (res.get("dimension_values") or [""])[0].upper()
                    if kind in ("FOLLOWER", "FOLLOWS"):
                        put_acc(date, "follows", res.get("value"))
                    elif kind in ("NON_FOLLOWER", "UNFOLLOWS", "UNFOLLOWER"):
                        put_acc(date, "unfollows", res.get("value"))
    for m in raw["media"] + raw["stories"]:
        pub = parse_time(m.get("timestamp"), "UTC")
        fmt = "story" if m in raw["stories"] else kind_of(m.get("media_product_type") if m.get("media_product_type") == "REELS" else m.get("media_type"))
        cap = (m.get("caption") or "").strip()
        _store_content(con, m["id"], fmt, pub, cap.splitlines()[0][:200] if cap else None, m.get("permalink"), "meta_api", False)
        for name, val in _values(m.get("insights", {})).items():
            metric = RENAME.get(name, name)
            if metric == "avg_watch_s" and val is not None:
                val = val / 1000                       # Meta returns milliseconds
            if metric == "total_watch_s" and val is not None:
                val = val / 1000
            if metric in ("total_interactions", "navigation"):
                continue
            con.execute("INSERT OR REPLACE INTO content_snapshot VALUES (?,?,?,?,?,?,?,?)",
                        (m["id"], metric, val, "organic", c, _age_hours(pub, c), "meta_api", import_id))
            n += 1
    con.commit()
    return n
