-- Moodius Aurelius storefront schema (Cloudflare D1 / SQLite).
-- Personal data kept to the minimum needed to deliver a purchase and answer a support request.

-- One row per "Buy" click that reached a payment provider. The id doubles as the
-- unguessable reference the thank-you page uses to find the order.
CREATE TABLE checkouts (
  id            TEXT PRIMARY KEY,            -- chk_<random>
  product_slug  TEXT NOT NULL,
  provider      TEXT NOT NULL,               -- stripe | lemonsqueezy | mock
  provider_ref  TEXT,                        -- Stripe session id / Lemon Squeezy checkout id
  src           TEXT,                        -- attribution, e.g. reel_r012
  digital_consent_at TEXT,                   -- buyer ticked "start access now, I lose the 14-day cancellation right"
  created_at    TEXT NOT NULL
);

CREATE TABLE orders (
  id               TEXT PRIMARY KEY,         -- ord_<random>
  checkout_id      TEXT REFERENCES checkouts(id),
  provider         TEXT NOT NULL,
  provider_ref     TEXT NOT NULL,            -- Stripe session id / LS order id
  payment_ref      TEXT,                     -- Stripe payment_intent (for refunds)
  product_slug     TEXT NOT NULL,
  amount_cents     INTEGER NOT NULL,         -- what the buyer paid, incl. tax
  currency         TEXT NOT NULL,
  email            TEXT NOT NULL,
  name             TEXT,
  status           TEXT NOT NULL,            -- paid | refunded
  src              TEXT,
  test_mode        INTEGER NOT NULL DEFAULT 1,
  page_claims      INTEGER NOT NULL DEFAULT 0,
  created_at       TEXT NOT NULL,
  refunded_at      TEXT,
  revenue_sent_at  TEXT,                     -- forwarded to the community agent
  refund_sent_at   TEXT,
  UNIQUE (provider, provider_ref)
);
CREATE INDEX orders_email ON orders(email);
CREATE INDEX orders_payment_ref ON orders(payment_ref);
CREATE INDEX orders_created ON orders(created_at);

-- Download links. Only a SHA-256 of the token is stored, so a leaked database
-- does not leak working links.
CREATE TABLE download_tokens (
  token_hash    TEXT PRIMARY KEY,
  order_id      TEXT NOT NULL REFERENCES orders(id),
  created_at    TEXT NOT NULL,
  expires_at    TEXT NOT NULL,
  max_uses      INTEGER NOT NULL,
  uses          INTEGER NOT NULL DEFAULT 0,
  last_used_at  TEXT
);
CREATE INDEX download_tokens_order ON download_tokens(order_id);

-- Webhook idempotency: providers retry, we fulfil once.
CREATE TABLE webhook_events (
  provider     TEXT NOT NULL,
  event_id     TEXT NOT NULL,
  received_at  TEXT NOT NULL,
  PRIMARY KEY (provider, event_id)
);

-- Cookieless funnel events. No IP, no user agent, no cookie, no identifier.
-- kind: link_click | page_view | checkout_started | purchase | subscribe
-- Column names match the community agent's conversion_events so exports import cleanly.
CREATE TABLE conversion_events (
  id       INTEGER PRIMARY KEY AUTOINCREMENT,
  kind     TEXT NOT NULL,
  slug     TEXT,              -- link slug or page/product slug
  src      TEXT,
  at       TEXT NOT NULL
);
CREATE INDEX conversion_events_at ON conversion_events(at);

-- Fallback newsletter list, used only while COMMUNITY_AGENT_URL is unset.
-- Same columns as the community agent's subscribers table, exported for import.
CREATE TABLE subscribers (
  email              TEXT PRIMARY KEY,
  status             TEXT NOT NULL,          -- pending | confirmed | unsubscribed
  consent_text       TEXT NOT NULL,
  consent_version    TEXT NOT NULL,
  consent_at         TEXT NOT NULL,
  source             TEXT,
  lead_magnet        TEXT,
  confirmed_at       TEXT,
  unsubscribed_at    TEXT,
  ip_hash            TEXT,                   -- salted hash, never the raw IP
  confirm_token_hash TEXT,
  unsub_token_hash   TEXT,
  last_email_at      TEXT
);

-- Every email the site sends. With EMAIL_PROVIDER=log nothing leaves the
-- server and this table is the test inbox.
CREATE TABLE outbox (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  to_addr      TEXT NOT NULL,
  subject      TEXT NOT NULL,
  body_text    TEXT NOT NULL,
  kind         TEXT NOT NULL,
  created_at   TEXT NOT NULL,
  provider     TEXT NOT NULL,
  provider_id  TEXT,
  error        TEXT
);
