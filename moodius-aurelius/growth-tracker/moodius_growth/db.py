"""SQLite storage: raw imports kept verbatim, normalised snapshots on top.

Design rules
* Every file or API response is copied into data/raw/ unchanged and listed in
  `raw_import` with its SHA-256, so the same file is never imported twice.
* Account and content metrics are stored "long": one row per date (or post),
  metric, scope and collection time. A metric the source did not report has
  no row, or a row whose value is NULL. Nothing missing ever becomes 0.
* Post metrics are lifetime totals at the moment of collection. They are
  never summed across snapshots: analysis reads the latest snapshot per post
  (or the snapshot closest to a fixed age).
* Follower totals ("followers_total") are levels, not flows. Daily net change
  is computed from consecutive totals, separately from the Insights metrics
  "follows" / "unfollows", which Meta counts differently.
"""
import hashlib
import os
import shutil
import sqlite3

from .config import RAW_DIR, now_utc_iso

SCHEMA = """
CREATE TABLE IF NOT EXISTS raw_import (
    import_id      INTEGER PRIMARY KEY,
    source         TEXT NOT NULL,          -- manual_csv, metricool_csv, metricool_connector, meta_api, demo
    kind           TEXT NOT NULL,          -- account, content, tags, stories, experiments
    file_name      TEXT NOT NULL,
    sha256         TEXT NOT NULL UNIQUE,
    imported_at_utc TEXT NOT NULL,
    rows_in        INTEGER,
    rows_stored    INTEGER,
    is_demo        INTEGER NOT NULL DEFAULT 0,
    notes          TEXT
);

CREATE TABLE IF NOT EXISTS account_metric (
    date           TEXT NOT NULL,          -- YYYY-MM-DD, the source's reporting day
    reporting_tz   TEXT NOT NULL,          -- e.g. Europe/London, Europe/Madrid (Metricool)
    metric         TEXT NOT NULL,          -- see config.ACCOUNT_METRICS
    value          REAL,                   -- NULL = reported as unavailable
    scope          TEXT NOT NULL,          -- organic, paid, organic+paid, unknown
    source         TEXT NOT NULL,
    collected_at_utc TEXT NOT NULL,
    import_id      INTEGER REFERENCES raw_import(import_id),
    is_demo        INTEGER NOT NULL DEFAULT 0,
    UNIQUE (date, metric, scope, source, collected_at_utc)
);

CREATE TABLE IF NOT EXISTS content (
    media_id       TEXT PRIMARY KEY,
    format         TEXT NOT NULL,          -- reel, carousel, image, story
    published_at_utc TEXT,
    published_at_london TEXT,
    first_line     TEXT,
    permalink      TEXT,
    source         TEXT NOT NULL,
    is_demo        INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS content_snapshot (
    media_id       TEXT NOT NULL REFERENCES content(media_id),
    metric         TEXT NOT NULL,          -- see config.CONTENT_METRICS
    value          REAL,
    scope          TEXT NOT NULL,
    collected_at_utc TEXT NOT NULL,
    age_hours      REAL,                   -- post age when collected (observation window)
    source         TEXT NOT NULL,
    import_id      INTEGER REFERENCES raw_import(import_id),
    UNIQUE (media_id, metric, scope, source, collected_at_utc)
);

CREATE TABLE IF NOT EXISTS content_tags (
    media_id       TEXT PRIMARY KEY,
    pillar         TEXT,                   -- Mind, Body, People
    topic          TEXT,
    hook_type      TEXT,
    cta            TEXT,
    duration_s     REAL,
    production_minutes REAL,
    experiment_id  TEXT,
    arm            TEXT,
    notes          TEXT
);

CREATE TABLE IF NOT EXISTS experiment (
    experiment_id  TEXT PRIMARY KEY,
    hypothesis     TEXT NOT NULL,
    variable       TEXT NOT NULL,
    primary_metric TEXT NOT NULL,
    window_days    INTEGER NOT NULL,
    decision_rule  TEXT NOT NULL,
    start_date     TEXT,
    end_date       TEXT,
    status         TEXT NOT NULL DEFAULT 'planned',  -- planned, running, decided
    result         TEXT
);

CREATE TABLE IF NOT EXISTS forecast_log (
    made_on        TEXT NOT NULL,
    model          TEXT NOT NULL,
    target_date    TEXT NOT NULL,
    horizon_days   INTEGER NOT NULL,
    point          REAL,
    lo80           REAL,
    hi80           REAL,
    is_demo        INTEGER NOT NULL DEFAULT 0,
    UNIQUE (made_on, model, target_date, is_demo)
);

CREATE TABLE IF NOT EXISTS collection_log (
    run_at_utc     TEXT NOT NULL,
    source         TEXT NOT NULL,
    status         TEXT NOT NULL,          -- ok, partial, failed
    rows           INTEGER,
    message        TEXT
);

CREATE VIEW IF NOT EXISTS account_latest AS
SELECT a.* FROM account_metric a
JOIN (SELECT date, metric, scope, source, MAX(collected_at_utc) AS m
      FROM account_metric GROUP BY date, metric, scope, source) l
  ON a.date = l.date AND a.metric = l.metric AND a.scope = l.scope
 AND a.source = l.source AND a.collected_at_utc = l.m;

CREATE VIEW IF NOT EXISTS content_latest AS
SELECT s.* FROM content_snapshot s
JOIN (SELECT media_id, metric, scope, MAX(collected_at_utc) AS m
      FROM content_snapshot GROUP BY media_id, metric, scope) l
  ON s.media_id = l.media_id AND s.metric = l.metric AND s.scope = l.scope
 AND s.collected_at_utc = l.m;
"""


def connect(path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    con = sqlite3.connect(path)
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(SCHEMA)
    return con


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def register_raw(con, path, source, kind, is_demo=False, notes=None):
    """Copy the file into data/raw and record it. Returns (import_id, is_new)."""
    digest = sha256_file(path)
    row = con.execute("SELECT import_id FROM raw_import WHERE sha256 = ?", (digest,)).fetchone()
    if row:
        return row[0], False
    os.makedirs(RAW_DIR, exist_ok=True)
    stored_name = f"{digest[:12]}-{os.path.basename(path)}"
    target = os.path.join(RAW_DIR, stored_name)
    if os.path.abspath(path) != os.path.abspath(target):
        shutil.copy2(path, target)
    cur = con.execute(
        "INSERT INTO raw_import (source, kind, file_name, sha256, imported_at_utc, is_demo, notes) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (source, kind, stored_name, digest, now_utc_iso(), int(is_demo), notes),
    )
    return cur.lastrowid, True


def log_collection(con, source, status, rows=None, message=None):
    con.execute(
        "INSERT INTO collection_log VALUES (?, ?, ?, ?, ?)",
        (now_utc_iso(), source, status, rows, (message or "")[:500]),
    )
    con.commit()
