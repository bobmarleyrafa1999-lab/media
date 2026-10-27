"""Calculations (pandas). Every ratio uses matched periods and valid denominators.

Conventions
* Missing stays NaN. A ratio is NaN when any part is missing or the
  denominator is 0, and the n behind every group result is shown.
* Daily account reach is unique per day only. Summing days gives
  "reach-days", which is NOT unique reach for the week; it is labelled so.
* Pooled rates (sum of numerators / sum of denominators) are used for groups,
  so one tiny post cannot swing the result. Per-post rates are for ranking.
* "Net followers per 1,000 reached" from account totals is a PROXY: it
  mixes followers from every source with reach from every format.
"""
import datetime as dt
import sqlite3

import numpy as np
import pandas as pd

from .config import LONDON

SOURCE_RANK = {"meta_api": 0, "metricool_connector": 1, "metricool_csv": 2, "ig_export": 3, "manual_csv": 4, "demo": 5}
MIN_N = 5            # below this a group result is a lead, not a finding
MIN_AGE_H = 72       # posts younger than this are still collecting reach
BOT_WAVE_PER_100 = 2.0   # net new followers per 100 reached above this = check for bots
BOT_WAVE_MIN_NET = 10    # ignore tiny days (3 -> 6 followers is not a wave)


# ---------- loading ----------

def load_account(con):
    """Wide daily table: one row per date, one column per metric (preferred source)."""
    df = pd.read_sql_query("SELECT date, reporting_tz, metric, value, scope, source, collected_at_utc FROM account_latest", con)
    if df.empty:
        return pd.DataFrame(), {}
    df["rank"] = df["source"].map(SOURCE_RANK).fillna(9)
    df["missing"] = df["value"].isna()          # a source that reported a number beats one that reported n/a
    df = df.sort_values(["date", "metric", "missing", "rank"]).drop_duplicates(["date", "metric"], keep="first")
    wide = df.pivot(index="date", columns="metric", values="value")
    wide.index = pd.to_datetime(wide.index)
    wide = wide.sort_index()
    full = pd.date_range(wide.index.min(), wide.index.max(), freq="D")
    wide = wide.reindex(full)
    wide.index.name = "date"
    meta = {
        "reporting_tz": sorted(df["reporting_tz"].unique()),
        "sources": sorted(df["source"].unique()),
        "scopes": df.groupby("metric")["scope"].agg(lambda s: ", ".join(sorted(set(s)))).to_dict(),
    }
    return wide, meta


def load_posts(con):
    """One row per post: latest organic snapshot values, paid reach, tags, age."""
    content = pd.read_sql_query("SELECT * FROM content", con)
    if content.empty:
        return content
    snap = pd.read_sql_query("SELECT media_id, metric, value, scope, collected_at_utc, age_hours FROM content_latest", con)
    org = snap[snap.scope.isin(["organic", "unknown"])]
    wide = org.pivot_table(index="media_id", columns="metric", values="value", aggfunc="first")
    paid = snap[snap.scope == "paid"].pivot_table(index="media_id", columns="metric", values="value", aggfunc="first")
    paid = paid.add_prefix("paid_")
    age = snap.groupby("media_id").agg(age_hours=("age_hours", "max"), collected_at_utc=("collected_at_utc", "max"))
    tags = pd.read_sql_query("SELECT * FROM content_tags", con).set_index("media_id")
    posts = content.set_index("media_id").join(wide).join(paid).join(age).join(tags)
    posts["published_at_london"] = pd.to_datetime(posts["published_at_london"], utc=True).dt.tz_convert(LONDON)
    posts["hour_london"] = posts["published_at_london"].dt.hour
    posts["weekday"] = posts["published_at_london"].dt.day_name()
    for col in ["reach", "views", "likes", "comments", "saves", "shares", "follows", "profile_visits",
                "avg_watch_s", "view_rate_3s_pct"]:
        if col not in posts:
            posts[col] = np.nan
    posts["paid_reach"] = posts["paid_reach"] if "paid_reach" in posts else np.nan
    posts["is_paid"] = posts["paid_reach"].fillna(0) > 0
    return add_post_rates(posts.reset_index())


# ---------- per-post rates ----------

def _ratio(num, den, scale):
    num, den = pd.to_numeric(num), pd.to_numeric(den)
    out = num / den * scale
    return out.where(den > 0)


def add_post_rates(posts):
    inter = posts[["likes", "comments", "saves", "shares"]]
    total = inter.sum(axis=1, min_count=4)                    # NaN unless all four reported
    posts["interactions"] = total
    posts["eng_by_reach_pct"] = _ratio(total, posts["reach"], 100)
    posts["saves_per_1k"] = _ratio(posts["saves"], posts["reach"], 1000)
    posts["shares_per_1k"] = _ratio(posts["shares"], posts["reach"], 1000)
    # Meta reports post-attributed follows for feed posts and stories only.
    fol = posts["follows"].where(posts["format"] != "reel")
    posts["follows_per_1k"] = _ratio(fol, posts["reach"], 1000)
    hours = posts["production_minutes"] / 60 if "production_minutes" in posts else np.nan
    posts["follows_per_prod_hour"] = _ratio(fol, hours, 1) if "production_minutes" in posts else np.nan
    return posts


# ---------- account-level changes ----------

def daily_changes(acc):
    """Net follower change from consecutive totals, plus the bot-wave check."""
    out = pd.DataFrame(index=acc.index)
    tot = acc.get("followers_total")
    out["followers_total"] = tot
    out["net_change"] = tot.diff() if tot is not None else np.nan   # NaN if either day missing
    for c in ("follows", "unfollows", "reach", "views", "accounts_engaged", "profile_visits", "link_taps"):
        out[c] = acc[c] if c in acc else np.nan
    out["net_per_100_reached"] = _ratio(out["net_change"], out["reach"], 100)
    out["bot_wave_flag"] = (out["net_change"] >= BOT_WAVE_MIN_NET) & (
        (out["net_per_100_reached"] > BOT_WAVE_PER_100) |
        (out["net_change"] > out["accounts_engaged"].where(out["accounts_engaged"] > 0)))
    return out


def period_summary(daily, start, end):
    """Matched-period summary between two dates (inclusive). Growth % uses the
    total on the day before `start` as the starting follower count."""
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    window = daily.loc[start:end]
    before = daily["followers_total"].get(start - pd.Timedelta(days=1), np.nan)
    if pd.isna(before):                                  # fall back to first day in window, labelled
        before = window["followers_total"].iloc[0] if len(window) else np.nan
        start_label = "first day of period"
    else:
        start_label = "end of previous day"
    end_total = window["followers_total"].dropna()
    end_val = end_total.iloc[-1] if len(end_total) else np.nan
    net = end_val - before if pd.notna(before) and pd.notna(end_val) else np.nan
    days = len(window)

    def summed(col):
        s = window[col]
        return (s.sum() if s.notna().any() else np.nan), int(s.notna().sum())

    reach, reach_n = summed("reach")
    views, views_n = summed("views")
    follows, follows_n = summed("follows")
    unfollows, unf_n = summed("unfollows")
    pv, pv_n = summed("profile_visits")
    lt, lt_n = summed("link_taps")
    return {
        "start": start.date(), "end": end.date(), "days": days,
        "followers_start": before, "followers_start_basis": start_label, "followers_end": end_val,
        "net_change": net,
        "growth_pct": (net / before * 100) if pd.notna(net) and before and before > 0 else np.nan,
        "reach_day_sum": reach, "reach_days_reported": reach_n,
        "views": views, "views_days_reported": views_n,
        "insights_follows": follows, "follows_days_reported": follows_n,
        "insights_unfollows": unfollows, "unfollows_days_reported": unf_n,
        "profile_visits": pv, "profile_visits_days_reported": pv_n,
        "link_taps": lt, "link_taps_days_reported": lt_n,
        "net_per_1k_reach_proxy": (net / reach * 1000) if pd.notna(net) and reach and reach_n == days else np.nan,
        "bot_wave_days": [d.date() for d in window.index[window["bot_wave_flag"].fillna(False)]],
    }


def weekly_table(daily):
    """Monday-Sunday weeks (reporting-day dates)."""
    rows = []
    if daily.empty:
        return pd.DataFrame()
    first = daily.index.min() - pd.Timedelta(days=daily.index.min().weekday())
    wk = first
    while wk <= daily.index.max():
        s = period_summary(daily, wk, min(wk + pd.Timedelta(days=6), daily.index.max()))
        rows.append(s)
        wk += pd.Timedelta(days=7)
    return pd.DataFrame(rows)


def monthly_table(daily):
    rows = []
    for p in pd.period_range(daily.index.min(), daily.index.max(), freq="M"):
        rows.append(period_summary(daily, max(p.start_time, daily.index.min()), min(p.end_time.normalize(), daily.index.max())))
    return pd.DataFrame(rows)


# ---------- content comparisons ----------

def boot_median_ci(values, level=0.8, n_boot=2000, seed=7):
    v = np.asarray(pd.Series(values).dropna(), dtype=float)
    if len(v) < 3:
        return (np.nan, np.nan)
    rng = np.random.default_rng(seed)
    meds = np.median(rng.choice(v, size=(n_boot, len(v)), replace=True), axis=1)
    a = (1 - level) / 2
    return (float(np.quantile(meds, a)), float(np.quantile(meds, 1 - a)))


def flag_outliers(posts, col="reach", by="format"):
    """Viral outlier = above Q3 + 3*IQR of its own format (needs >= 4 posts)."""
    posts = posts.copy()
    posts["outlier"] = False
    for _, g in posts.groupby(by):
        v = g[col].dropna()
        if len(v) < 4:
            continue
        q1, q3 = v.quantile(0.25), v.quantile(0.75)
        posts.loc[g.index, "outlier"] = g[col] > q3 + 3 * (q3 - q1)
    return posts


def eligible(posts, min_age_h=MIN_AGE_H, organic_only=True):
    p = posts[(posts["age_hours"] >= min_age_h) & posts["reach"].notna()]
    if organic_only:
        p = p[~p["is_paid"]]
    return p


def compare(posts, by="format"):
    """Group table with n, medians, 80% bootstrap CI, pooled per-1k rates, typical vs all."""
    posts = flag_outliers(posts)
    rows = []
    for key, g in posts.groupby(by, dropna=True):
        typical = g[~g["outlier"]]
        lo, hi = boot_median_ci(g["reach"])
        reach_sum = g["reach"].where(g["saves"].notna() & g["shares"].notna()).sum()
        feed = g[g["format"] != "reel"]
        fol_reach = feed["reach"].where(feed["follows"].notna()).sum()
        rows.append({
            by: key, "n": len(g), "lead_only": len(g) < MIN_N,
            "median_reach": g["reach"].median(), "reach_ci80": (round(lo), round(hi)) if pd.notna(lo) else None,
            "median_reach_typical": typical["reach"].median(), "outliers": int(g["outlier"].sum()),
            "median_eng_by_reach_pct": g["eng_by_reach_pct"].median(),
            "saves_per_1k_pooled": g["saves"].sum() / reach_sum * 1000 if reach_sum else np.nan,
            "shares_per_1k_pooled": g["shares"].sum() / reach_sum * 1000 if reach_sum else np.nan,
            "follows_per_1k_pooled": feed["follows"].sum() / fol_reach * 1000 if fol_reach else np.nan,
            "follows_n": int(feed["follows"].notna().sum()),
            "median_avg_watch_s": g["avg_watch_s"].median() if (g["format"] == "reel").any() else np.nan,
            "median_view_rate_3s_pct": g["view_rate_3s_pct"].median() if (g["format"] == "reel").any() else np.nan,
        })
    return pd.DataFrame(rows).sort_values("median_reach", ascending=False) if rows else pd.DataFrame()


def posting_effort(posts, daily):
    """Posts per week vs that week's reach-days and net followers (observational)."""
    if posts.empty or daily.empty:
        return pd.DataFrame()
    p = posts.dropna(subset=["published_at_london"]).copy()
    p["week"] = p["published_at_london"].dt.tz_localize(None).dt.to_period("W-SUN").dt.start_time
    per_week = p.groupby("week").agg(posts=("media_id", "count"),
                                     production_hours=("production_minutes", lambda s: s.sum(min_count=1) / 60))
    wk = weekly_table(daily).set_index(pd.to_datetime(weekly_table(daily)["start"]))
    out = per_week.join(wk[["reach_day_sum", "net_change"]], how="outer")
    out["net_per_production_hour"] = out["net_change"] / out["production_hours"]
    return out


def freshness(con):
    q = """SELECT source, MAX(collected_at_utc) AS last_collected FROM (
             SELECT source, collected_at_utc FROM account_metric
             UNION ALL SELECT source, collected_at_utc FROM content_snapshot) GROUP BY source"""
    df = pd.read_sql_query(q, con)
    if df.empty:
        return df
    now = pd.Timestamp.now(tz="UTC")
    df["hours_old"] = ((now - pd.to_datetime(df["last_collected"], utc=True)).dt.total_seconds() / 3600).round(1)
    df["status"] = np.where(df["hours_old"] <= 48, "fresh", np.where(df["hours_old"] <= 24 * 8, "stale", "old"))
    return df


def completeness(acc, days=28):
    """Share of the last `days` days on which each account metric was reported."""
    if acc.empty:
        return pd.DataFrame()
    recent = acc.iloc[-days:]
    rows = []
    for m in sorted(acc.columns):
        rows.append({"metric": m, "days_reported": int(recent[m].notna().sum()), "of_days": len(recent)})
    return pd.DataFrame(rows)
