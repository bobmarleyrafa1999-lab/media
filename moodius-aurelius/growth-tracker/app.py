"""Moodius growth dashboard. Run on your Mac:  streamlit run app.py
It only listens on your own computer (see .streamlit/config.toml); nothing is published."""
import json

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from moodius_growth import db, forecast as fc, metrics as mx
import os

from moodius_growth.config import DATA_DIR, DEMO_DB, REAL_DB, SCENARIOS_PATH

# Validated categorical palette (dataviz reference slots 1-4); colour follows the format, never its rank.
FORMAT_COLOURS = {"carousel": "#2a78d6", "reel": "#eb6834", "image": "#1baf7a", "story": "#eda100", "unknown": "#8a8a85"}
SCEN_COLOURS = {"conservative": "#2a78d6", "base": "#eb6834", "optimistic": "#1baf7a"}

st.set_page_config(page_title="Moodius growth", layout="wide")
which = st.sidebar.radio("Data", ["Real data", "Demo data (synthetic)"])
is_demo = which.startswith("Demo")
con = db.connect(DEMO_DB if is_demo else REAL_DB)
if is_demo:
    st.error("DEMO DATA: synthetic numbers for trying the dashboard. Not @moodiusaurelius.")

acc, meta = mx.load_account(con)
if acc.empty:
    st.info("No data yet. Import a CSV first: see docs/IMPORT-GUIDE.md.")
    st.stop()
daily = mx.daily_changes(acc)
posts = mx.load_posts(con)
cfg = fc.load_scenarios(SCENARIOS_PATH)

# Freshness strip (always visible)
fr = mx.freshness(con)
icons = {"fresh": "🟢", "stale": "🟠", "old": "🔴"}
st.caption("Data freshness: " + " · ".join(f"{icons[r.status]} {r.source}: {r.hours_old:.0f} h old" for r in fr.itertuples())
           + f" · reporting days in {', '.join(meta['reporting_tz'])}")

tab_over, tab_content, tab_fc, tab_exp, tab_dq = st.tabs(["Overview", "Content", "Forecasts", "Experiments", "Data quality"])

with tab_over:
    end = daily["followers_total"].last_valid_index()
    cur = mx.period_summary(daily, end - pd.Timedelta(days=6), end)
    prev = mx.period_summary(daily, end - pd.Timedelta(days=13), end - pd.Timedelta(days=7))
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Followers", f"{cur['followers_end']:,.0f}", f"{cur['net_change']:+,.0f} in 7 days" if pd.notna(cur["net_change"]) else None)
    c2.metric("Reach-days, 7 days", f"{cur['reach_day_sum']:,.0f}" if pd.notna(cur["reach_day_sum"]) else "n/a",
              f"{cur['reach_day_sum'] - prev['reach_day_sum']:+,.0f}" if pd.notna(prev["reach_day_sum"]) else None)
    c3.metric("Net followers per 1k reach (proxy)", f"{cur['net_per_1k_reach_proxy']:.1f}" if pd.notna(cur["net_per_1k_reach_proxy"]) else "n/a")
    c4.metric("Possible bot-wave days", len(cur["bot_wave_days"]))
    st.caption("Reach-days = sum of daily unique reach; the same person on two days counts twice.")
    fig = px.line(daily.reset_index(), x="date", y="followers_total", markers=True, title="Follower total")
    fig.update_traces(line=dict(width=2, color="#2a78d6"))
    flagged = daily[daily["bot_wave_flag"].fillna(False)]
    if len(flagged):
        fig.add_scatter(x=flagged.index, y=flagged["followers_total"], mode="markers", name="possible bot wave",
                        marker=dict(symbol="x", size=11, color="#e34948"))
    st.plotly_chart(fig, use_container_width=True)
    fig2 = px.bar(daily.reset_index(), x="date", y="reach", title="Daily reach (unique accounts per day)")
    fig2.update_traces(marker_color="#2a78d6")
    st.plotly_chart(fig2, use_container_width=True)
    try:
        with open(os.path.join(DATA_DIR, "reports", ("DEMO-" if is_demo else "") + "weekly-latest.md"), encoding="utf-8") as f:
            rep = f.read()
        part = rep.split("## 3.")[1].split("## 4.")[0]
        st.subheader("This week's three actions")
        st.markdown(part.split("\n", 1)[1])
    except (OSError, IndexError):
        st.caption("Run `python3 -m moodius_growth report` to see this week's three actions here.")

with tab_content:
    if posts.empty:
        st.info("No post data yet.")
    else:
        min_age = st.slider("Only posts at least this many days old", 0, 14, 3)
        days = st.slider("Published in the last N days", 7, 180, 28)
        last = posts["published_at_london"].max()
        pool = posts[(posts["age_hours"] >= min_age * 24) & (posts["published_at_london"] >= last - pd.Timedelta(days=days))
                     & ~posts["is_paid"] & posts["reach"].notna()]
        st.markdown("**Formats** (medians; fewer than 5 posts = lead only; 80% range is a bootstrap interval)")
        st.dataframe(mx.compare(pool, "format").round(1), use_container_width=True, hide_index=True)
        fig = px.strip(mx.flag_outliers(pool), x="format", y="reach", color="format", color_discrete_map=FORMAT_COLOURS,
                       hover_data=["first_line", "published_at_london", "eng_by_reach_pct", "shares_per_1k"],
                       title="Reach per post by format (each dot is a post)")
        st.plotly_chart(fig, use_container_width=True)
        for col, label in (("pillar", "Pillar"), ("hook_type", "Hook"), ("cta", "CTA"), ("hour_london", "Posting hour (UK)")):
            if col in pool and pool[col].notna().sum() >= 3:
                st.markdown(f"**{label}**")
                st.dataframe(mx.compare(pool.dropna(subset=[col]), col).round(1), use_container_width=True, hide_index=True)
        st.caption("Patterns here are observational leads to test, not proof of cause.")
        st.markdown("**All posts**")
        show = ["published_at_london", "format", "first_line", "reach", "eng_by_reach_pct", "saves_per_1k", "shares_per_1k",
                "follows", "follows_per_1k", "avg_watch_s", "view_rate_3s_pct", "age_hours"]
        st.dataframe(posts.sort_values("published_at_london", ascending=False)[show].round(1), use_container_width=True, hide_index=True)
        eff = mx.posting_effort(posts, daily)
        if not eff.empty:
            st.markdown("**Posting effort vs results, by week** (does more posting pay for the time?)")
            st.dataframe(eff, use_container_width=True)

with tab_fc:
    res = fc.forecast(daily)
    st.markdown(f"**Statistical forecasts** ({res['history_days']} days of follower totals)")
    for h, e in res["horizons"].items():
        if e["supported"]:
            st.write(f"{h} days: **{e['point']:,.0f}** on {e['target_date']:%d %b %Y} "
                     f"(80% range {e['lo80']:,.0f} to {e['hi80']:,.0f}; model {e['model']}; backtest MAE {e['mae']:.1f} followers)")
        else:
            st.write(f"{h} days: not supported yet. {e['reason']}")
    with st.expander("Backtest scores (rolling origin, no future data)"):
        st.dataframe(pd.DataFrame([s for e in res["horizons"].values() for s in e["scores"]]), use_container_width=True)

    st.markdown("**Scenario explorer** (assumption-based projections, not forecasts)")
    from moodius_growth.report import posted_dates
    inputs = fc.scenario_inputs(daily, cfg, posted_dates(posts))
    c1, c2, c3 = st.columns(3)
    ratio = c1.slider("Posts per week vs now", 0.5, 2.0, 1.0, 0.1, help="1.0 = keep the current schedule")
    elast = c2.slider("Reach elasticity (assumption)", 0.0, 1.0, float(cfg["posting_explorer"]["elasticity"]), 0.1,
                      help=cfg["posting_explorer"]["_elasticity_note"])
    conv = c3.slider("Follower conversion vs measured", 0.5, 2.0, 1.0, 0.1)
    horizon = cfg["horizon_days"]
    start = daily.index.max()
    start_total = daily["followers_total"].dropna().iloc[-1]
    fig = go.Figure()
    table = []
    for name, inp in inputs.items():
        if pd.isna(inp["reach_per_day"]) or pd.isna(inp["net_per_1k"]):
            continue
        path = fc.run_scenario(start_total, inp, horizon, ratio, elast, conv)
        dates = pd.date_range(start + pd.Timedelta(days=1), periods=horizon)
        fig.add_scatter(x=dates, y=path, name=name, line=dict(width=2, color=SCEN_COLOURS[name]))
        ms = fc.milestones(start, path, start_total=start_total)
        table.append({"scenario": name, "reach/day": round(inp["reach_per_day"]), "net per 1k": round(inp["net_per_1k"], 1),
                      "+30 d": round(path[29]), "+60 d": round(path[59]), "+90 d": round(path[89]), **{f"{k:,}": v for k, v in ms.items()},
                      "assumptions": inp["assumptions"]})
    fig.add_vrect(x0=start + pd.Timedelta(days=90), x1=start + pd.Timedelta(days=horizon), fillcolor="#8a8a85", opacity=0.12,
                  line_width=0, annotation_text="exploratory", annotation_position="top left")
    fig.update_layout(title="Followers under each scenario", yaxis_title="followers")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(pd.DataFrame(table), use_container_width=True)
    st.caption("Doubling posts does not double growth: reach scales by (posts ratio) ^ elasticity. Viral days and possible "
               "bot-wave days are left out of the measured rates.")
    fva = fc.forecast_vs_actual(con, daily, is_demo)
    if not fva.empty:
        st.markdown("**Past forecasts vs what happened**")
        st.dataframe(fva, use_container_width=True)

with tab_exp:
    exp = pd.read_sql_query("SELECT * FROM experiment", con)
    st.dataframe(exp, use_container_width=True)
    if not posts.empty and "experiment_id" in posts and posts["experiment_id"].notna().any():
        for eid, g in posts.dropna(subset=["experiment_id"]).groupby("experiment_id"):
            st.markdown(f"**{eid}**")
            st.dataframe(g.groupby("arm").agg(n=("media_id", "count"), median_reach=("reach", "median"),
                                              median_shares_per_1k=("shares_per_1k", "median"),
                                              median_follows_per_1k=("follows_per_1k", "median")), use_container_width=True)
    else:
        st.caption("Tag posts with experiment_id and arm in content_tags.csv to track progress here.")

with tab_dq:
    st.markdown("**Freshness**")
    st.dataframe(fr, use_container_width=True)
    st.markdown("**How many of the last 28 days report each account metric** (missing is n/a, never 0)")
    st.dataframe(mx.completeness(acc), use_container_width=True)
    st.markdown("**Metric scope** (organic, paid, or both as the source labels it)")
    st.json(meta["scopes"])
    st.markdown("**Imports**")
    st.dataframe(pd.read_sql_query("SELECT import_id, source, kind, file_name, imported_at_utc, rows_in, rows_stored FROM raw_import ORDER BY import_id DESC", con),
                 use_container_width=True)
    st.markdown("**Collection runs**")
    st.dataframe(pd.read_sql_query("SELECT * FROM collection_log ORDER BY run_at_utc DESC LIMIT 20", con), use_container_width=True)
