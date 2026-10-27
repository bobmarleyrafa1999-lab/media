"""Paths, time zone and metric vocabulary shared by every module."""
import datetime as dt
import os
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_DIR = os.environ.get("MOODIUS_DATA_DIR", os.path.join(ROOT, "data"))
RAW_DIR = os.path.join(DATA_DIR, "raw")
REAL_DB = os.path.join(DATA_DIR, "moodius.sqlite")
DEMO_DB = os.path.join(DATA_DIR, "demo.sqlite")       # synthetic data lives in its own file
LOG_DIR = os.environ.get("MOODIUS_LOG_DIR", os.path.join(ROOT, "logs"))
SCENARIOS_PATH = os.path.join(ROOT, "scenarios.json")

LONDON = ZoneInfo("Europe/London")
UTC = dt.timezone.utc

# Account-level metrics, one value per reporting day.
ACCOUNT_METRICS = {
    "followers_total": "Follower count at the end of the day (a level, never summed)",
    "following_total": "Accounts @moodiusaurelius follows (a level)",
    "follows": "Insights: accounts that started following that day",
    "unfollows": "Insights: accounts that stopped following that day",
    "reach": "Unique accounts reached that day (estimated by Meta)",
    "views": "Times content was displayed that day",
    "accounts_engaged": "Unique accounts that interacted that day",
    "profile_visits": "Profile visits that day",
    "link_taps": "Taps on the bio link / contact buttons that day",
    "story_reach": "Reach of stories that day (sum across stories, not unique)",
    "posts_published": "Feed posts + reels published that day",
    "stories_published": "Stories published that day",
}

# Per-post metrics, lifetime totals at collection time.
CONTENT_METRICS = {
    "reach": "Unique accounts that saw the post",
    "views": "Times the post was displayed / played",
    "likes": "Likes",
    "comments": "Comments (can include your own pinned comment)",
    "saves": "Saves",
    "shares": "Shares",
    "follows": "Follows attributed to this post (feed posts and stories only)",
    "profile_visits": "Profile visits from this post (feed posts and stories only)",
    "avg_watch_s": "Reels: average watch time, seconds",
    "total_watch_s": "Reels: total watch time, seconds",
    "skip_rate_pct": "Reels: % of views skipped in the first 3 s",
    "view_rate_3s_pct": "Reels: % of views watched past 3 s (Metricool)",
    "replies": "Stories: replies (Meta returns 0 for European accounts)",
    "taps_forward": "Stories: taps forward",
    "taps_back": "Stories: taps back",
    "exits": "Stories: exits",
}

FORMATS = ("reel", "carousel", "image", "story")
SCOPES = ("organic", "paid", "organic+paid", "unknown")


def now_utc_iso():
    return dt.datetime.now(UTC).replace(microsecond=0).isoformat()


def to_london(ts_utc):
    """datetime (aware or naive UTC) -> aware Europe/London datetime."""
    if ts_utc.tzinfo is None:
        ts_utc = ts_utc.replace(tzinfo=UTC)
    return ts_utc.astimezone(LONDON)


def today_london():
    return dt.datetime.now(LONDON).date()
