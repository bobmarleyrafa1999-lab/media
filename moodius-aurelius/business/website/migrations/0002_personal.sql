-- Personalised and gift editions.
ALTER TABLE checkouts ADD COLUMN personal_json TEXT;   -- buyer's choices, validated by src/personal.js

ALTER TABLE orders ADD COLUMN personal_json TEXT;
ALTER TABLE orders ADD COLUMN personal_status TEXT;    -- NULL (standard) | queued | delivered
ALTER TABLE orders ADD COLUMN personal_done_at TEXT;

-- Files made for one order (the personalised PDFs), shown on that order's download page
-- after the product's standard files. Keys point into the private R2 bucket.
CREATE TABLE order_files (
  order_id    TEXT NOT NULL REFERENCES orders(id),
  r2_key      TEXT NOT NULL,
  filename    TEXT NOT NULL,
  label       TEXT NOT NULL,
  created_at  TEXT NOT NULL,
  PRIMARY KEY (order_id, r2_key)
);
