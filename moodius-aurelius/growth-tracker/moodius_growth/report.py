"""Weekly report (Markdown). Rule-based: Python does the maths, no AI calls."""
import datetime as dt

import numpy as np
import pandas as pd

from . import forecast as fc
from . import metrics as mx


def _n(x, d=0):
    if x is None or (isinstance(x, float) and np.isnan(x)) or pd.isna(x):
        return "n/a"
    return f"{x:,.{d}f}"


def _pct(x, d=1):
    return "n/a" if x is None or pd.isna(x) else f"{x:+.{d}f}%"


def _delta(a, b, d=0):
    if pd.isna(a) or pd.isna(b):
        return "n/a"
    return f"{a - b:+,.{d}f}"


def md_table(df, index=True):
    """Small Markdown table without extra dependencies."""
    d = df.reset_index() if index else df
    head = "| " + " | ".join(map(str, d.columns)) + " |"
    sep = "|" + "---|" * len(d.columns)
    rows = ["| " + " | ".join("n/a" if pd.isna(v) else (f"{v:,.1f}" if isinstance(v, float) else str(v)) for v in r) + " |"
            for r in d.itertuples(index=False)]
    return "\n".join([head, sep] + rows)


def build(con, scenarios_cfg, week_ending=None, is_demo=False):
    acc, meta = mx.load_account(con)
    if acc.empty:
        return "# Weekly report\n\nNo account data yet. Import a CSV first (docs/IMPORT-GUIDE.md).\n", {}
    daily = mx.daily_changes(acc)
    end = pd.Timestamp(week_ending) if week_ending else daily["followers_total"].last_valid_index()
    start = end - pd.Timedelta(days=6)
    prev_end, prev_start = start - pd.Timedelta(days=1), start - pd.Timedelta(days=7)
    cur = mx.period_summary(daily.loc[:end], start, end)
    prev = mx.period_summary(daily.loc[:end], prev_start, prev_end)

    posts = mx.load_posts(con)
    ready = mx.eligible(posts) if not posts.empty else posts
    recent28 = ready[ready["published_at_london"].dt.tz_localize(None) >= end - pd.Timedelta(days=27)] if not ready.empty else ready
    week_posts = posts[(posts["published_at_london"].dt.tz_localize(None) >= start) &
                       (posts["published_at_london"].dt.tz_localize(None) < end + pd.Timedelta(days=1))] if not posts.empty else posts
    by_format = mx.compare(recent28, "format") if not recent28.empty else pd.DataFrame()

    L = []
    banner = "> **DEMO DATA. Synthetic numbers for testing, not @moodiusaurelius.**\n\n" if is_demo else ""
    L.append(f"# Weekly growth report: {start:%d %b} to {end:%d %b %Y}\n")
    L.append(banner + f"_Reporting days follow {', '.join(meta['reporting_tz'])}. Sources: {', '.join(meta['sources'])}. "
             f"Generated {dt.datetime.now():%d %b %Y %H:%M} (UK time on your Mac)._\n")

    # 1. What changed
    L.append("## 1. What changed\n")
    L.append("| | This week | Previous week | Change |\n|---|---|---|---|")
    L.append(f"| Followers at end | {_n(cur['followers_end'])} | {_n(prev['followers_end'])} | {_delta(cur['followers_end'], prev['followers_end'])} |")
    L.append(f"| Net follower change | {_n(cur['net_change'])} | {_n(prev['net_change'])} | {_delta(cur['net_change'], prev['net_change'])} |")
    L.append(f"| Follower growth % | {_pct(cur['growth_pct'])} | {_pct(prev['growth_pct'])} | |")
    L.append(f"| Reach-days (sum of daily reach; not unique people) | {_n(cur['reach_day_sum'])} | {_n(prev['reach_day_sum'])} | {_delta(cur['reach_day_sum'], prev['reach_day_sum'])} |")
    L.append(f"| Views | {_n(cur['views'])} | {_n(prev['views'])} | {_delta(cur['views'], prev['views'])} |")
    L.append(f"| Net followers per 1,000 reach-days (proxy) | {_n(cur['net_per_1k_reach_proxy'], 1)} | {_n(prev['net_per_1k_reach_proxy'], 1)} | |")
    L.append(f"| Insights follows / unfollows (days reported) | {_n(cur['insights_follows'])} / {_n(cur['insights_unfollows'])} ({cur['follows_days_reported']}/{cur['days']} d) | {_n(prev['insights_follows'])} / {_n(prev['insights_unfollows'])} ({prev['follows_days_reported']}/{prev['days']} d) | |")
    L.append(f"| Profile visits | {_n(cur['profile_visits'])} ({cur['profile_visits_days_reported']}/{cur['days']} d) | {_n(prev['profile_visits'])} | |")
    L.append(f"| Link taps | {_n(cur['link_taps'])} ({cur['link_taps_days_reported']}/{cur['days']} d) | {_n(prev['link_taps'])} | |")
    L.append(f"| Posts published (feed + reels) | {len(week_posts[week_posts['format'] != 'story']) if not week_posts.empty else 0} | | |\n")
    L.append("Follower totals and the Insights 'follows' count are different measures: totals come from the "
             "account's follower count, follows/unfollows from Meta's daily Insights, which can lag and miss days. "
             "Growth % uses totals.\n")
    if pd.notna(prev["followers_start"]) and prev["followers_start"] < 50 or pd.notna(cur["followers_start"]) and cur["followers_start"] < 50:
        L.append("_With fewer than 50 followers at the start of a week, growth % swings wildly; read the net change instead._\n")

    # 2. Evidence
    L.append("## 2. Evidence and plausible explanations\n")
    findings = []
    if cur["bot_wave_days"]:
        days = ", ".join(d.strftime("%a %d %b") for d in cur["bot_wave_days"])
        findings.append(f"**Possible bot wave on {days}:** more than {mx.BOT_WAVE_PER_100:g} net new followers per 100 accounts "
                        "reached, or more new followers than accounts that engaged. Real audiences rarely convert that fast. "
                        "These days are left out of scenario conversion rates.")
    if not by_format.empty:
        L.append("**Formats, posts at least 3 days old, last 28 days (organic only).** Medians, not averages; "
                 "80% range is a bootstrap interval for the median. Fewer than 5 posts = lead only.\n")
        L.append("| Format | n | Median reach (80% range) | Typical median (no outliers) | Viral outliers | Median engagement by reach | Saves / 1k | Shares / 1k | Follows / 1k (n) | Reel avg watch | Reel 3 s view rate |")
        L.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for _, r in by_format.iterrows():
            ci = f"{r['reach_ci80'][0]:,}-{r['reach_ci80'][1]:,}" if r["reach_ci80"] else "n/a"
            lead = " (lead only)" if r["lead_only"] else ""
            L.append(f"| {r['format']}{lead} | {r['n']} | {_n(r['median_reach'])} ({ci}) | {_n(r['median_reach_typical'])} | {r['outliers']} | "
                     f"{_n(r['median_eng_by_reach_pct'], 1)}% | {_n(r['saves_per_1k_pooled'], 1)} | {_n(r['shares_per_1k_pooled'], 1)} | "
                     f"{_n(r['follows_per_1k_pooled'], 1)} ({r['follows_n']}) | {_n(r['median_avg_watch_s'], 1) + ' s' if pd.notna(r['median_avg_watch_s']) else '-'} | {_n(r['median_view_rate_3s_pct'], 0) + '%' if pd.notna(r['median_view_rate_3s_pct']) else '-'} |")
        L.append("\nReels have no per-post follows in Meta's API, so reel 'Follows / 1k' is n/a, not 0.\n")
        f = by_format.set_index("format")
        if {"carousel", "reel"} <= set(f.index):
            c, r = f.loc["carousel"], f.loc["reel"]
            if c["n"] >= mx.MIN_N and r["n"] >= mx.MIN_N and r["median_reach"] > 0:
                ratio = c["median_reach"] / r["median_reach"]
                findings.append(f"**Carousels vs reels:** carousel median reach {_n(c['median_reach'])} vs reel {_n(r['median_reach'])} "
                                f"({ratio:.1f}x, n={c['n']} vs {r['n']}). Plausible reasons: carousels get saved and resurfaced, and the "
                                "carousel topics differed from reel topics. This is observational, not proof the format causes it.")
    if not week_posts.empty and week_posts["reach"].notna().any():
        top = week_posts.sort_values("reach", ascending=False).head(3)
        L.append("**This week's posts, by reach** (young posts are still collecting):\n")
        L.append("| Published (UK) | Format | First line | Reach | Eng. by reach | Shares / 1k | Follows | Age at collection |")
        L.append("|---|---|---|---|---|---|---|---|")
        for _, p in week_posts.sort_values("published_at_london").iterrows():
            L.append(f"| {p['published_at_london']:%a %d %b %H:%M} | {p['format']} | {str(p['first_line'])[:60]} | {_n(p['reach'])} | "
                     f"{_n(p['eng_by_reach_pct'], 1)}% | {_n(p['shares_per_1k'], 1)} | {_n(p['follows'])} | {_n(p['age_hours'] / 24, 1)} d |")
        L.append("")
        best = top.iloc[0]
        findings.append(f"**Top post this week:** \"{str(best['first_line'])[:70]}\" ({best['format']}, reach {_n(best['reach'])}).")
    for x in findings:
        L.append(f"- {x}")
    L.append("")

    # 3. Actions
    actions = choose_actions(cur, by_format, posts, acc)
    L.append("## 3. Three actions for this week (in order)\n")
    for i, a in enumerate(actions[:3], 1):
        L.append(f"{i}. **{a['do']}** {a['why']}")
    L.append("")

    # 4. Experiment
    L.append("## 4. One controlled experiment\n")
    exp = pd.read_sql_query("SELECT * FROM experiment WHERE status IN ('running','planned') ORDER BY status DESC, start_date", con)
    if exp.empty:
        L.append("No experiment recorded. Add one to templates/experiments.csv and import it.\n")
    else:
        e = exp.iloc[0]
        L.append(f"**{e['experiment_id']} ({e['status']})**\n")
        L.append(f"- Hypothesis: {e['hypothesis']}\n- Variable: {e['variable']}\n- Primary metric: {e['primary_metric']}\n"
                 f"- Observation window: {e['window_days']} days per post, run {e['start_date'] or '?'} to {e['end_date'] or '?'}\n"
                 f"- Decision rule: {e['decision_rule']}\n")
        arm = posts.dropna(subset=["experiment_id"]) if "experiment_id" in posts else pd.DataFrame()
        arm = arm[arm["experiment_id"] == e["experiment_id"]] if not arm.empty else arm
        if not arm.empty:
            g = arm.groupby("arm").agg(n=("media_id", "count"), median_shares_per_1k=("shares_per_1k", "median"),
                                       median_reach=("reach", "median"))
            L.append("Progress so far:\n\n" + md_table(g) + "\n")
        else:
            L.append("Progress: no posts tagged with this experiment yet (set experiment_id and arm in content_tags.csv).\n")

    # 5. Forecast vs actual
    L.append("## 5. Forecast vs actual\n")
    fva = fc.forecast_vs_actual(con, daily, is_demo)
    if fva.empty:
        L.append("Nothing to score yet: this is the first logged week. This report's forecasts are saved and will be scored next week.\n")
    else:
        L.append(md_table(fva.tail(8)[["made_on", "model", "target_date", "point", "actual", "error", "inside_80"]], index=False))
        worst = fva["error"].abs().max()
        L.append(f"\nModel update needed? {'Yes: actuals are outside the 80% range or far off' if (fva['inside_80'] == False).any() or worst > 0.2 * fva['actual'].mean() else 'No: errors are within range'}.\n")

    f30 = fc.forecast(daily.loc[:end])
    L.append("**Statistical forecast status:** " + "; ".join(
        f"{h} days: " + (f"{_n(e['point'])} followers on {e['target_date']:%d %b} (80% range {_n(e['lo80'])}-{_n(e['hi80'])}, model {e['model']}, backtest MAE {_n(e['mae'], 1)})"
                         if e["supported"] else "not supported yet. " + e["reason"])
        for h, e in f30["horizons"].items()) + "\n")
    if any(e["supported"] and pd.notna(e["lo80"]) and not (e["lo80"] <= e["point"] <= e["hi80"]) for e in f30["horizons"].values()):
        L.append("Where the point sits outside its 80% range, the model has been consistently too low or too high in past "
                 "backtests; the range (built from those past errors) is the better guide.\n")
    bt7 = fc.short_backtest(daily.loc[:end], 7)
    usable = [b for b in bt7 if b["origins"] > 0]
    if usable:
        few = max(b["origins"] for b in usable) < fc.MIN_ORIGINS
        L.append("7-day-ahead backtests so far" + (" (descriptive only: too few origins to choose a model)" if few else "") + ": " +
                 "; ".join(f"{b['model']} MAE {_n(b['mae'], 1)} followers over {b['origins']} origins" for b in usable) + ".\n")

    inputs = fc.scenario_inputs(daily.loc[:end], scenarios_cfg)
    start_total = cur["followers_end"]
    L.append(f"**Assumption-based scenarios from {_n(start_total)} followers** (projections, not forecasts):\n")
    L.append("| Scenario | Reach / day | Net followers per 1k reach | +30 d | +60 d | +90 d | 1k | 5k | 10k | 25k | 50k |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    paths = {}
    for name, inp in inputs.items():
        if pd.isna(inp["reach_per_day"]) or pd.isna(inp["net_per_1k"]) or pd.isna(start_total):
            L.append(f"| {name} | not enough data | | | | | | | | | |")
            continue
        path = fc.run_scenario(start_total, inp, scenarios_cfg["horizon_days"])
        paths[name] = (end.date(), path)
        ms = fc.milestones(end.date(), path, start_total=start_total)
        L.append(f"| {name} | {_n(inp['reach_per_day'])} | {_n(inp['net_per_1k'], 1)} | {_n(path[29])} | {_n(path[59])} | {_n(path[89])} | "
                 + " | ".join(ms[m].replace("Not reached within the modelled horizon", "not within 180 d") for m in fc.MILESTONES) + " |")
    L.append("")
    for name, inp in inputs.items():
        L.append(f"- *{name}*: {inp['assumptions']} Reach basis: {inp['reach_basis']}. Conversion basis: {inp['net_per_1k_basis']}.")
    L.append("\nDays 91-180 are exploratory. None of these assume viral spikes repeat; they use medians.\n")
    fc.log_forecasts(con, end.date(), f30, paths, is_demo)

    # 6. Data quality
    L.append("## 6. Data quality\n")
    fr = mx.freshness(con)
    if not fr.empty:
        L.append("| Source | Last collected (UTC) | Age | Status |\n|---|---|---|---|")
        for _, r in fr.iterrows():
            L.append(f"| {r['source']} | {r['last_collected']} | {r['hours_old']} h | {r['status']} |")
    comp = mx.completeness(acc)
    missing = comp[comp["days_reported"] == 0]["metric"].tolist() if not comp.empty else []
    tracked = set(acc.columns)
    never = [m for m in ("profile_visits", "link_taps", "follows", "unfollows", "story_reach") if m not in tracked]
    gaps = missing + never
    if gaps:
        L.append(f"\nNot available in the last 28 days: {', '.join(sorted(set(gaps)))}. Shown as n/a, never as 0.")
    if not week_posts.empty and pd.notna(cur["reach_day_sum"]):
        post_sum = week_posts["reach"].sum()
        if post_sum > 0 and cur["reach_day_sum"] > 3 * post_sum:
            L.append(f"\n**Check:** this week's account reach-days ({_n(cur['reach_day_sum'])}) are more than 3x the summed reach of "
                     f"the week's posts ({_n(post_sum)}). Some post figures may be early snapshots that the source never refreshed. "
                     "Open one of these posts in the Instagram app (View insights) and compare its reach with the table above.")
    L.append("\nMetricool reports account days on Madrid time (one hour ahead of the UK all year), so a 'day' runs 23:00-23:00 UK. "
             "Post times are converted to UK time exactly.\n")
    return "\n".join(L), {"actions": actions[:3], "current": cur, "previous": prev, "by_format": by_format,
                          "inputs": inputs, "forecast": f30}


def choose_actions(cur, by_format, posts, acc):
    """Ranked, rule-based actions. Highest priority first."""
    acts = []
    if cur["bot_wave_days"]:
        acts.append((1, {"do": "Spot-check the followers who arrived on the flagged days.",
                         "why": "Open Followers > sort by Date followed: Latest; remove accounts with no posts, no picture or spam names. "
                                "Fake followers lower reach for real posts."}))
    f = by_format.set_index("format") if not by_format.empty else pd.DataFrame()
    if {"carousel", "reel"} <= set(f.index) and f.loc["carousel", "n"] >= mx.MIN_N and f.loc["reel", "n"] >= mx.MIN_N:
        c, r = f.loc["carousel"], f.loc["reel"]
        if c["median_reach"] >= 1.5 * r["median_reach"]:
            acts.append((2, {"do": "Keep the daily carousel as the main growth format.",
                             "why": f"Its median reach is {c['median_reach'] / r['median_reach']:.1f}x the reel median over the last 28 days. "
                                    "Keep reels at the planned count rather than adding more until a reel beats the carousel median."}))
        if pd.notna(r["median_view_rate_3s_pct"]) and r["median_view_rate_3s_pct"] < 35:
            acts.append((3, {"do": "Fix the first 3 seconds of reels.",
                             "why": f"Only {r['median_view_rate_3s_pct']:.0f}% of reel views pass 3 s (median). Open on the other person or the conflict, "
                                    "and make line two pay off the hook by second 3."}))
    if not posts.empty:
        last = posts["published_at_london"].max()
        feed = posts[(posts["format"] != "reel") & posts["follows_per_1k"].notna() & (posts["reach"] >= 100)
                     & (posts["published_at_london"] >= last - pd.Timedelta(days=28))]
        if len(feed):
            best = feed.sort_values("follows_per_1k", ascending=False).iloc[0]
            if best["follows_per_1k"] > 0:
                acts.append((4, {"do": f"Make a follow-up to \"{str(best['first_line'])[:60]}\".",
                                 "why": f"It has the best attributed follows per 1,000 reached ({best['follows_per_1k']:.1f}) of posts with 100+ reach. "
                                        "One post is a lead, not proof: treat it as a repeat test."}))
        if "pillar" in posts and posts["pillar"].isna().mean() > 0.5:
            acts.append((6, {"do": "Tag last week's posts in content_tags.csv (5 minutes).",
                             "why": "Topic, hook, CTA and production minutes are missing for most posts, so the report can't say which topics or hooks work."}))
    if "profile_visits" not in acc.columns or acc["profile_visits"].iloc[-7:].isna().all():
        acts.append((5, {"do": "Add profile visits and link taps for the week (2 minutes, from the app).",
                         "why": "They're the step between reach and a follow; without them we can't see where people drop off."}))
    acts.append((9, {"do": "Reply to every substantive comment within a day.",
                     "why": "Comments with replies are the clearest sign of people who return; it costs no production time."}))
    acts.sort(key=lambda x: x[0])
    return [a for _, a in acts]
