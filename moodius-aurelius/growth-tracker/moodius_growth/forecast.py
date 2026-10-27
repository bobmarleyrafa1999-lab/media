"""Follower forecasts with honest limits.

1. Baselines first: no-growth, recent-drift (average daily net change over the
   last k days) and weekly seasonal-naive (repeat last week's daily changes).
2. statsmodels models (damped-trend exponential smoothing, ARIMA(0,1,1) with
   drift) are only tried once there are MIN_DAYS_FOR_STATSMODELS days.
3. Every model is scored with rolling-origin backtests: train on days up to
   the origin, predict origin + h, compare. No future data is used.
4. Prediction intervals for baselines come from the model's own past backtest
   errors at that horizon (empirical quantiles). An interval is only shown when
   at least MIN_ERRORS_FOR_INTERVAL past errors exist; otherwise "no interval".
5. A horizon is only forecast when at least MIN_ORIGINS backtest origins exist
   for it. Longer horizons fall back to the assumption-based scenarios.
6. The simplest model is kept unless a more complex one has >= 10% lower MAE.
"""
import json
import warnings

import numpy as np
import pandas as pd

MIN_TRAIN_DAYS = 14
MIN_ORIGINS = 5
MIN_ERRORS_FOR_INTERVAL = 5
MIN_DAYS_FOR_STATSMODELS = 56
ORIGIN_STEP = 7
SIMPLICITY = ["no_growth", "drift_7", "drift_28", "seasonal_naive_7", "ets_damped", "arima_011_drift"]
MILESTONES = [1000, 5000, 10000, 25000, 50000]


def followers_series(daily):
    s = daily["followers_total"].astype(float)
    first = s.first_valid_index()
    return s.loc[first:] if first is not None else s.iloc[0:0]


# ---------- models: each returns point forecasts for days 1..h ----------

def _last(train):
    return train.dropna().iloc[-1]


def m_no_growth(train, h):
    return np.full(h, _last(train))


def _drift(train, h, k):
    t = train.dropna()
    end = t.index[-1]
    past = t.loc[:end - pd.Timedelta(days=k)]
    if past.empty:
        past = t.iloc[:1]
    days = max((end - past.index[-1]).days, 1)
    slope = (t.iloc[-1] - past.iloc[-1]) / days
    return t.iloc[-1] + slope * np.arange(1, h + 1)


def m_drift_7(train, h):
    return _drift(train, h, 7)


def m_drift_28(train, h):
    return _drift(train, h, 28)


def m_seasonal_naive_7(train, h):
    t = train.interpolate(limit_area="inside").dropna()
    changes = t.diff().iloc[-7:].fillna(0).to_numpy()
    if len(changes) < 7:
        return m_drift_7(train, h)
    steps = np.resize(changes, h)
    return t.iloc[-1] + np.cumsum(steps)


def m_ets_damped(train, h):
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    t = train.interpolate(limit_area="inside").dropna()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fit = ExponentialSmoothing(t.to_numpy(), trend="add", damped_trend=True).fit()
    return fit.forecast(h)


def m_arima_011_drift(train, h):
    from statsmodels.tsa.arima.model import ARIMA
    t = train.interpolate(limit_area="inside").dropna()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fit = ARIMA(t.to_numpy(), order=(0, 1, 1), trend="t").fit()
    return fit.forecast(h)


MODELS = {
    "no_growth": m_no_growth, "drift_7": m_drift_7, "drift_28": m_drift_28,
    "seasonal_naive_7": m_seasonal_naive_7, "ets_damped": m_ets_damped, "arima_011_drift": m_arima_011_drift,
}


def available_models(series):
    n = series.notna().sum()
    names = ["no_growth", "drift_7"]
    if n >= 28:
        names.append("drift_28")
    if n >= 14:
        names.append("seasonal_naive_7")
    if n >= MIN_DAYS_FOR_STATSMODELS:
        names += ["ets_damped", "arima_011_drift"]
    return names


# ---------- backtest ----------

def origins_for(series, h):
    s = series.dropna()
    if s.empty:
        return []
    start = s.index[0] + pd.Timedelta(days=MIN_TRAIN_DAYS - 1)
    last_origin = s.index[-1] - pd.Timedelta(days=h)
    out, o = [], last_origin
    while o >= start:                          # walk back from the newest origin
        if not pd.isna(series.get(o + pd.Timedelta(days=h), np.nan)) and not pd.isna(series.get(o, np.nan)):
            out.append(o)
        o -= pd.Timedelta(days=ORIGIN_STEP)
    return sorted(out)


def backtest(series, model, h):
    rows = []
    for o in origins_for(series, h):
        train = series.loc[:o]
        try:
            pred = MODELS[model](train, h)[-1]
        except Exception:                     # a model that fails to fit is scored as missing
            continue
        actual = series.loc[o + pd.Timedelta(days=h)]
        rows.append({"origin": o.date(), "target": (o + pd.Timedelta(days=h)).date(),
                     "pred": float(pred), "actual": float(actual), "error": float(actual - pred)})
    bt = pd.DataFrame(rows)
    if bt.empty:
        return bt, {"model": model, "h": h, "origins": 0, "mae": np.nan, "coverage80": np.nan, "coverage_n": 0}
    # Interval coverage without leakage: the interval at origin i uses only errors from origins < i.
    hits = []
    for i in range(len(bt)):
        past = bt["error"].iloc[:i]
        if len(past) >= MIN_ERRORS_FOR_INTERVAL:
            lo, hi = past.quantile(0.1), past.quantile(0.9)
            hits.append(lo <= bt["error"].iloc[i] <= hi)
    return bt, {"model": model, "h": h, "origins": len(bt), "mae": float(bt["error"].abs().mean()),
                "coverage80": float(np.mean(hits)) if hits else np.nan, "coverage_n": len(hits)}


def choose_model(scores):
    """Lowest MAE, but keep a simpler model unless the complex one is >= 10% better."""
    valid = [s for s in scores if s["origins"] >= MIN_ORIGINS and pd.notna(s["mae"])]
    if not valid:
        return None
    valid.sort(key=lambda s: SIMPLICITY.index(s["model"]))
    best = valid[0]
    for s in valid[1:]:
        if s["mae"] <= best["mae"] * 0.9:
            best = s
    return best


def forecast(daily, horizons=(30, 60, 90)):
    """Returns a dict per horizon: supported?, chosen model, point, 80% interval, scores."""
    series = followers_series(daily)
    result = {"history_days": int(series.notna().sum()),
              "last_date": series.dropna().index[-1].date() if series.notna().any() else None,
              "last_total": float(series.dropna().iloc[-1]) if series.notna().any() else None,
              "horizons": {}}
    for h in horizons:
        scores, bts = [], {}
        for m in available_models(series):
            bt, sc = backtest(series, m, h)
            scores.append(sc)
            bts[m] = bt
        best = choose_model(scores)
        entry = {"supported": best is not None, "scores": scores}
        if best is None:
            need = MIN_TRAIN_DAYS + h + ORIGIN_STEP * (MIN_ORIGINS - 1)
            entry["reason"] = (f"Needs about {need} days of daily follower totals for {MIN_ORIGINS} honest "
                               f"backtests at {h} days; have {result['history_days']}.")
        else:
            m = best["model"]
            point = float(MODELS[m](series, h)[-1])
            errs = bts[m]["error"]
            if len(errs) >= MIN_ERRORS_FOR_INTERVAL:
                lo, hi = point + errs.quantile(0.1), point + errs.quantile(0.9)
            else:
                lo = hi = np.nan
            entry.update({"model": m, "point": point, "lo80": lo, "hi80": hi, "mae": best["mae"],
                          "target_date": (series.dropna().index[-1] + pd.Timedelta(days=h)).date()})
        result["horizons"][h] = entry
    return result


def short_backtest(daily, h=7):
    """What we CAN measure now: 7-day-ahead errors of the baselines (descriptive only)."""
    series = followers_series(daily)
    out = []
    for m in available_models(series):
        _, sc = backtest(series, m, h)
        out.append(sc)
    return out


# ---------- assumption-based scenarios ----------

def scenario_inputs(daily, cfg):
    """Turn scenarios.json into numbers measured from the data, with labels."""
    d = daily.copy()
    if cfg.get("exclude_bot_wave_days", True):
        d = d[~d["bot_wave_flag"].fillna(False)]
    end = daily.index.max()
    out = {}
    for name, sc in cfg["scenarios"].items():
        w = d.loc[end - pd.Timedelta(days=sc["reach_window_days"] - 1):end]
        reach = w["reach"].dropna()
        both = w.dropna(subset=["reach", "net_change"])
        pooled = both["net_change"].sum() / both["reach"].sum() * 1000 if both["reach"].sum() > 0 else np.nan
        conv_daily = (both["net_change"] / both["reach"] * 1000).replace([np.inf, -np.inf], np.nan).dropna()
        conv = {"pooled": pooled, "p25": conv_daily.quantile(0.25) if len(conv_daily) else np.nan,
                "p75": conv_daily.quantile(0.75) if len(conv_daily) else np.nan}[sc["conversion"]]
        out[name] = {
            "reach_per_day": float(reach.median()) if len(reach) else np.nan,
            "reach_basis": f"median daily reach over the last {sc['reach_window_days']} days ({len(reach)} days with data)",
            "net_per_1k": float(conv) if pd.notna(conv) else np.nan,
            "net_per_1k_basis": f"{sc['conversion']} net followers per 1,000 reached over the same days (proxy)",
            "reach_growth_month_pct": sc["reach_growth_month_pct"],
            "churn_month_pct": sc["churn_month_pct"],
            "assumptions": sc["assumptions"],
        }
    return out


def run_scenario(start_total, inp, days, posts_ratio=1.0, elasticity=0.5, conv_change=1.0):
    """Daily simulation. posts_ratio = new posts per week / current posts per week.
    Reach scales with posts_ratio ** elasticity (diminishing returns, an assumption)."""
    f = start_total
    reach = inp["reach_per_day"] * (posts_ratio ** elasticity)
    g = (1 + inp["reach_growth_month_pct"] / 100) ** (1 / 30.4)
    churn = 1 - (1 - inp["churn_month_pct"] / 100) ** (1 / 30.4)
    path = []
    for _ in range(days):
        f = f + reach * inp["net_per_1k"] * conv_change / 1000 - f * churn
        reach *= g
        path.append(f)
    return np.array(path)


def milestones(start_date, path, horizon_label_days=90, start_total=None):
    out = {}
    for m in MILESTONES:
        if start_total is not None and start_total >= m:
            out[m] = "already reached"
            continue
        idx = np.argmax(path >= m) if (path >= m).any() else None
        if idx is None:
            out[m] = "Not reached within the modelled horizon"
        else:
            day = pd.Timestamp(start_date) + pd.Timedelta(days=int(idx) + 1)
            tag = "" if idx + 1 <= horizon_label_days else " (exploratory, beyond 90 days)"
            out[m] = day.strftime("%d %b %Y") + tag
    return out


def load_scenarios(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def log_forecasts(con, made_on, fc, scen_paths, is_demo=False):
    """Store this week's forecasts so next week's report can score them."""
    for h, e in fc["horizons"].items():
        if e.get("supported"):
            con.execute("INSERT OR REPLACE INTO forecast_log VALUES (?,?,?,?,?,?,?,?)",
                        (str(made_on), e["model"], str(e["target_date"]), h, e["point"],
                         None if pd.isna(e["lo80"]) else e["lo80"], None if pd.isna(e["hi80"]) else e["hi80"], int(is_demo)))
    for name, (start, path) in scen_paths.items():
        for h in (7, 30):
            if len(path) >= h:
                con.execute("INSERT OR REPLACE INTO forecast_log VALUES (?,?,?,?,?,?,?,?)",
                            (str(made_on), f"scenario_{name}", str((pd.Timestamp(start) + pd.Timedelta(days=h)).date()),
                             h, float(path[h - 1]), None, None, int(is_demo)))
    con.commit()


def forecast_vs_actual(con, daily, is_demo=False):
    log = pd.read_sql_query("SELECT * FROM forecast_log WHERE is_demo = ?", con, params=(int(is_demo),))
    if log.empty or daily.empty:
        return pd.DataFrame()
    tot = daily["followers_total"]
    log["actual"] = [tot.get(pd.Timestamp(t), np.nan) for t in log["target_date"]]
    log = log.dropna(subset=["actual"])
    log["error"] = log["actual"] - log["point"]
    log["inside_80"] = np.where(log["lo80"].notna(), (log["actual"] >= log["lo80"]) & (log["actual"] <= log["hi80"]), None)
    return log
