"""SQLite store for the Hook Library. One file, no server. Full-text search through FTS5."""
import json, os, sqlite3

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS creators (
  id TEXT PRIMARY KEY,            -- platform:native id
  platform TEXT, name TEXT, handle TEXT, url TEXT,
  followers INTEGER,
  baseline_median_views REAL,     -- median views of recent short-form uploads
  baseline_n INTEGER, baseline_source TEXT, fetched_at TEXT
);
CREATE TABLE IF NOT EXISTS videos (
  id TEXT PRIMARY KEY,            -- platform:native id
  platform TEXT NOT NULL, url TEXT NOT NULL, creator_id TEXT, creator TEXT,
  title TEXT, published TEXT, duration_s REAL,
  views INTEGER, likes INTEGER, likes_source TEXT, comments INTEGER,
  followers INTEGER, creator_median_views REAL, outlier_ratio REAL,
  first_spoken TEXT, first_onscreen TEXT, cover_text TEXT, visual_opening TEXT,
  subject TEXT, emotional_trigger TEXT, narrative_format TEXT,
  route TEXT, query TEXT, fetched_at TEXT, cycle TEXT,
  in_window INTEGER,              -- 1 published within RESEARCH_WINDOW_DAYS, 0 older, NULL unknown
  short_form INTEGER,
  missing TEXT,                   -- JSON list of fields that could not be collected
  notes TEXT
);
CREATE TABLE IF NOT EXISTS hooks (
  video_id TEXT PRIMARY KEY REFERENCES videos(id),
  hook_text TEXT, hook_text_source TEXT,
  category TEXT, secondary TEXT, structure TEXT, classifier_confidence REAL, cues TEXT,
  specificity REAL, clarity REAL, originality REAL, emotional REAL, visual REAL, alignment REAL,
  hook_score REAL,                -- 0-100 text score: a judgement, not retention
  priority REAL,                  -- ranking: outlier evidence first, text score second
  pillar TEXT, tone TEXT, visual_style TEXT, flags TEXT,
  why TEXT, adaptation TEXT, first_frame TEXT, music TEXT, length_s TEXT,
  confidence TEXT, evidence TEXT, strong INTEGER DEFAULT 0, relevant INTEGER,
  pick INTEGER                    -- rank in the cycle's hand-checked sample (editorial)
);
CREATE TABLE IF NOT EXISTS patterns (
  id TEXT PRIMARY KEY, cycle TEXT, category TEXT, structure TEXT, name TEXT, description TEXT,
  n INTEGER, n_with_baseline INTEGER, median_outlier REAL, best_outlier REAL, own_evidence TEXT,
  score REAL, rank INTEGER, examples TEXT, template TEXT
);
CREATE TABLE IF NOT EXISTS concepts (
  id TEXT PRIMARY KEY, batch TEXT, pattern_id TEXT, title TEXT, pillar TEXT, status TEXT,
  qc TEXT, data TEXT
);
CREATE TABLE IF NOT EXISTS own_posts (
  id TEXT PRIMARY KEY, url TEXT, published TEXT, kind TEXT, hook TEXT, caption TEXT,
  reach INTEGER, views INTEGER, avg_watch_s REAL, view_rate_3s REAL, duration_s REAL,
  likes INTEGER, comments INTEGER, saves INTEGER, shares INTEGER, follows INTEGER, reposts INTEGER,
  source TEXT, imported_at TEXT
);
CREATE TABLE IF NOT EXISTS experiments (
  id TEXT PRIMARY KEY,            -- e.g. HI01
  concept_id TEXT, hypothesis TEXT, metric TEXT, status TEXT, created TEXT, notes TEXT
);
CREATE TABLE IF NOT EXISTS variants (
  experiment_id TEXT, variant TEXT, hook TEXT, post_url TEXT, slot TEXT, published TEXT,
  PRIMARY KEY (experiment_id, variant)
);
CREATE VIRTUAL TABLE IF NOT EXISTS library_fts USING fts5(
  video_id UNINDEXED, text, tokenize = 'porter unicode61'
);
"""


def connect(path=None):
    path = path or config.DB_PATH
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


def upsert(con, table, row, key="id"):
    """Insert or update by primary key, never overwriting a stored value with NULL."""
    keys = list(row)
    cols = ",".join(keys)
    marks = ",".join("?" for _ in keys)
    keyset = [key] if isinstance(key, str) else list(key)
    updates = ",".join(f"{k}=COALESCE(excluded.{k}, {table}.{k})" for k in keys if k not in keyset)
    sql = f"INSERT INTO {table} ({cols}) VALUES ({marks}) ON CONFLICT({','.join(keyset)}) DO "
    sql += f"UPDATE SET {updates}" if updates else "NOTHING"
    con.execute(sql, [json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v for v in row.values()])


def rows(con, sql, args=()):
    return [dict(r) for r in con.execute(sql, args)]


def reindex_fts(con):
    con.execute("DELETE FROM library_fts")
    for r in rows(con, """SELECT v.id, v.title, v.creator, v.platform, v.first_spoken, v.first_onscreen, v.cover_text,
                                 v.subject, h.hook_text, h.category, h.pillar, h.tone, h.visual_style, h.adaptation, h.why
                          FROM videos v LEFT JOIN hooks h ON h.video_id = v.id"""):
        text = " ".join(str(x) for k, x in r.items() if k != "id" and x)
        con.execute("INSERT INTO library_fts (video_id, text) VALUES (?, ?)", (r["id"], text))


def search(con, query, limit=50):
    """Full-text search across title, hook, adaptation, tags. Falls back to LIKE for odd queries."""
    try:
        ids = [r["video_id"] for r in con.execute(
            "SELECT video_id FROM library_fts WHERE library_fts MATCH ? ORDER BY rank LIMIT ?", (query, limit))]
    except sqlite3.OperationalError:
        like = f"%{query}%"
        ids = [r["video_id"] for r in con.execute(
            "SELECT video_id FROM library_fts WHERE text LIKE ? LIMIT ?", (like, limit))]
    if not ids:
        return []
    marks = ",".join("?" for _ in ids)
    found = {r["id"]: r for r in rows(con, f"""SELECT v.*, h.* FROM videos v LEFT JOIN hooks h ON h.video_id=v.id
                                                WHERE v.id IN ({marks})""", ids)}
    return [found[i] for i in ids if i in found]
