-- Moodius community agent: initial schema (PostgreSQL 14+ / Supabase).
-- Idempotent: safe to run more than once.

CREATE TABLE IF NOT EXISTS schema_migrations (
  name TEXT PRIMARY KEY,
  applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Runtime switches editable from the dashboard (mode, kill switch, caps).
CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY,
  value JSONB NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Secrets the app rotates itself (the refreshed Instagram token). AES-256-GCM ciphertext only.
CREATE TABLE IF NOT EXISTS secrets (
  name TEXT PRIMARY KEY,
  ciphertext TEXT NOT NULL,
  expires_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Raw webhook deliveries. Meta retries for up to 36h, so the body hash dedupes replays.
CREATE TABLE IF NOT EXISTS webhook_events (
  id BIGSERIAL PRIMARY KEY,
  body_sha256 TEXT NOT NULL UNIQUE,
  payload JSONB NOT NULL,
  received_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Durable job queue (SELECT ... FOR UPDATE SKIP LOCKED). dedupe_key makes enqueue idempotent.
CREATE TABLE IF NOT EXISTS jobs (
  id BIGSERIAL PRIMARY KEY,
  kind TEXT NOT NULL,
  payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  dedupe_key TEXT UNIQUE,
  status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued','running','done','failed')),
  attempts INT NOT NULL DEFAULT 0,
  max_attempts INT NOT NULL DEFAULT 5,
  run_after TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_error TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS jobs_ready_idx ON jobs (status, run_after);

CREATE TABLE IF NOT EXISTS media (
  media_id TEXT PRIMARY KEY,
  caption TEXT,
  media_type TEXT,
  media_product_type TEXT,
  permalink TEXT,
  posted_at TIMESTAMPTZ,
  category TEXT,
  fetched_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- One row per media per day; only metrics the API actually returned are filled.
CREATE TABLE IF NOT EXISTS media_insights (
  media_id TEXT NOT NULL REFERENCES media(media_id) ON DELETE CASCADE,
  captured_on DATE NOT NULL DEFAULT CURRENT_DATE,
  reach INT, views INT, saved INT, shares INT, comments INT, likes INT, total_interactions INT,
  raw JSONB,
  PRIMARY KEY (media_id, captured_on)
);

CREATE TABLE IF NOT EXISTS comments (
  comment_id TEXT PRIMARY KEY,
  media_id TEXT NOT NULL,
  parent_id TEXT,
  from_id TEXT,
  username TEXT,
  text TEXT NOT NULL DEFAULT '',
  commented_at TIMESTAMPTZ,
  received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  source TEXT NOT NULL DEFAULT 'webhook' CHECK (source IN ('webhook','poll','mock')),
  status TEXT NOT NULL DEFAULT 'new' CHECK (status IN
    ('new','needs_approval','escalated','approved','published','rejected','skipped','error')),
  sentiment TEXT,
  intent TEXT,
  topic TEXT,
  flags TEXT[] NOT NULL DEFAULT '{}',
  risk TEXT,
  priority INT,
  substantive BOOLEAN,
  classifier JSONB,
  draft_reply TEXT,
  follow_up_question TEXT,
  final_reply TEXT,
  reply_comment_id TEXT,
  published_at TIMESTAMPTZ,
  published_by TEXT,
  decision_reason TEXT,
  dm_keyword TEXT,
  dm_status TEXT CHECK (dm_status IN ('sent','failed','skipped')),
  dm_sent_at TIMESTAMPTZ,
  email_kind TEXT,
  email_notified_at TIMESTAMPTZ,
  error TEXT,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS comments_status_idx ON comments (status, received_at DESC);
CREATE INDEX IF NOT EXISTS comments_user_idx ON comments (from_id, received_at DESC);

-- Every outbound Instagram write. UNIQUE(kind, comment_id) = never reply or DM twice.
CREATE TABLE IF NOT EXISTS outbound_actions (
  id BIGSERIAL PRIMARY KEY,
  kind TEXT NOT NULL CHECK (kind IN ('public_reply','private_reply')),
  comment_id TEXT NOT NULL,
  actor TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','sent','failed')),
  remote_id TEXT,
  error TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (kind, comment_id)
);

CREATE TABLE IF NOT EXISTS email_log (
  id BIGSERIAL PRIMARY KEY,
  kind TEXT NOT NULL,
  dedupe_key TEXT NOT NULL UNIQUE,
  to_address TEXT NOT NULL,
  subject TEXT NOT NULL,
  html TEXT,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','sent','logged','failed')),
  provider_id TEXT,
  error TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Newsletter list held only for people who ticked the consent box and clicked the confirm link.
CREATE TABLE IF NOT EXISTS subscribers (
  id BIGSERIAL PRIMARY KEY,
  email TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','confirmed','unsubscribed')),
  consent_text TEXT NOT NULL,
  consent_version TEXT NOT NULL,
  consent_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  source TEXT,
  lead_magnet TEXT,
  confirm_token_hash TEXT,
  unsubscribe_token_hash TEXT NOT NULL,
  confirmed_at TIMESTAMPTZ,
  unsubscribed_at TIMESTAMPTZ,
  ip_hash TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS subscribers_email_uq ON subscribers (lower(email));

-- Tracked short links (/r/<slug>). kind separates the five conversion paths.
CREATE TABLE IF NOT EXISTS links (
  slug TEXT PRIMARY KEY,
  label TEXT NOT NULL,
  destination TEXT NOT NULL,
  kind TEXT NOT NULL CHECK (kind IN ('affiliate','sponsor','newsletter','product','membership','resource')),
  disclosure TEXT,
  active BOOLEAN NOT NULL DEFAULT true,
  position INT NOT NULL DEFAULT 100,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Funnel events: comment_keyword -> dm_sent -> link_click -> signup_pending -> signup_confirmed.
CREATE TABLE IF NOT EXISTS conversion_events (
  id BIGSERIAL PRIMARY KEY,
  kind TEXT NOT NULL,
  slug TEXT,
  src TEXT,
  ref TEXT,
  value_cents INT,
  at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS conversion_events_kind_idx ON conversion_events (kind, at);

-- Sponsorship CRM (data model adapted from alongot/creator-crm, MIT).
CREATE TABLE IF NOT EXISTS sponsors (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  website TEXT NOT NULL,
  category TEXT NOT NULL,
  country TEXT,
  -- PECR: 'corporate' (Ltd/LLP/plc, B2B email allowed with opt-out) vs 'sole_trader' (needs prior consent).
  entity_type TEXT NOT NULL DEFAULT 'unknown' CHECK (entity_type IN ('corporate','sole_trader','unknown')),
  stage TEXT NOT NULL DEFAULT 'Prospect',
  stage_changed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  scores JSONB NOT NULL DEFAULT '{}'::jsonb,
  total_score NUMERIC(5,2),
  public_contact_email TEXT,
  contact_source_url TEXT,
  evidence JSONB NOT NULL DEFAULT '[]'::jsonb,
  dossier JSONB,
  notes TEXT,
  opted_out BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (website)
);

CREATE TABLE IF NOT EXISTS sponsor_activities (
  id BIGSERIAL PRIMARY KEY,
  sponsor_id BIGINT NOT NULL REFERENCES sponsors(id) ON DELETE CASCADE,
  type TEXT NOT NULL,
  title TEXT NOT NULL,
  body TEXT,
  actor TEXT NOT NULL DEFAULT 'system',
  at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sponsor_tasks (
  id BIGSERIAL PRIMARY KEY,
  sponsor_id BIGINT NOT NULL REFERENCES sponsors(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  due_at TIMESTAMPTZ NOT NULL,
  done BOOLEAN NOT NULL DEFAULT false,
  done_at TIMESTAMPTZ,
  source TEXT NOT NULL DEFAULT 'auto'
);

CREATE TABLE IF NOT EXISTS outreach (
  id BIGSERIAL PRIMARY KEY,
  sponsor_id BIGINT NOT NULL REFERENCES sponsors(id) ON DELETE CASCADE,
  sequence INT NOT NULL DEFAULT 0,
  to_address TEXT,
  subject TEXT NOT NULL,
  body TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','approved','sent','failed','cancelled')),
  approved_by TEXT,
  approved_at TIMESTAMPTZ,
  sent_at TIMESTAMPTZ,
  provider_id TEXT,
  error TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (sponsor_id, sequence)
);

-- Opt-outs and "never contact" entries: an address or a whole domain.
CREATE TABLE IF NOT EXISTS suppression (
  entry TEXT PRIMARY KEY,
  reason TEXT NOT NULL,
  at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS deals (
  id BIGSERIAL PRIMARY KEY,
  sponsor_id BIGINT REFERENCES sponsors(id) ON DELETE SET NULL,
  title TEXT NOT NULL,
  value_cents INT NOT NULL,
  currency TEXT NOT NULL DEFAULT 'GBP',
  signed_at DATE,
  delivered_at DATE,
  paid_at DATE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS revenue_entries (
  id BIGSERIAL PRIMARY KEY,
  stream TEXT NOT NULL CHECK (stream IN ('affiliate','sponsorship','substack_paid','digital_product','membership','other')),
  amount_cents INT NOT NULL,
  currency TEXT NOT NULL DEFAULT 'GBP',
  occurred_on DATE NOT NULL,
  source TEXT,
  note TEXT,
  deal_id BIGINT REFERENCES deals(id) ON DELETE SET NULL,
  -- Delivery id from a store webhook (e.g. Sellf X-Sellf-Delivery-Id) so a retried webhook is counted once.
  external_id TEXT UNIQUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS expenses (
  id BIGSERIAL PRIMARY KEY,
  item TEXT NOT NULL,
  amount_cents INT NOT NULL,
  currency TEXT NOT NULL DEFAULT 'GBP',
  occurred_on DATE NOT NULL,
  recurring BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS audit_log (
  id BIGSERIAL PRIMARY KEY,
  actor TEXT NOT NULL,
  action TEXT NOT NULL,
  target TEXT,
  detail JSONB,
  at TIMESTAMPTZ NOT NULL DEFAULT now()
);
