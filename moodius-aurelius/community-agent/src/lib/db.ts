import { Pool, type PoolClient, type QueryResultRow } from "pg";
import fs from "node:fs";
import path from "node:path";
import { config } from "./config";

declare global {
  // eslint-disable-next-line no-var
  var __moodiusPool: Pool | undefined;
}

export function pool(): Pool {
  if (!globalThis.__moodiusPool) {
    globalThis.__moodiusPool = new Pool({ connectionString: config().databaseUrl, max: 8 });
  }
  return globalThis.__moodiusPool;
}

export async function q<T extends QueryResultRow = QueryResultRow>(sql: string, params: unknown[] = []): Promise<T[]> {
  const res = await pool().query<T>(sql, params as unknown[]);
  return res.rows;
}

export async function one<T extends QueryResultRow = QueryResultRow>(sql: string, params: unknown[] = []): Promise<T | null> {
  const rows = await q<T>(sql, params);
  return rows[0] ?? null;
}

export async function tx<T>(fn: (c: PoolClient) => Promise<T>): Promise<T> {
  const c = await pool().connect();
  try {
    await c.query("BEGIN");
    const out = await fn(c);
    await c.query("COMMIT");
    return out;
  } catch (e) {
    await c.query("ROLLBACK");
    throw e;
  } finally {
    c.release();
  }
}

export async function migrate(dir = path.join(process.cwd(), "db", "migrations")): Promise<string[]> {
  const files = fs.readdirSync(dir).filter((f) => f.endsWith(".sql")).sort();
  const applied: string[] = [];
  await q("CREATE TABLE IF NOT EXISTS schema_migrations (name TEXT PRIMARY KEY, applied_at TIMESTAMPTZ NOT NULL DEFAULT now())");
  for (const f of files) {
    const done = await one("SELECT 1 FROM schema_migrations WHERE name = $1", [f]);
    if (done) continue;
    await tx(async (c) => {
      await c.query(fs.readFileSync(path.join(dir, f), "utf8"));
      await c.query("INSERT INTO schema_migrations (name) VALUES ($1)", [f]);
    });
    applied.push(f);
  }
  return applied;
}

export async function audit(actor: string, action: string, target?: string, detail?: unknown) {
  await q("INSERT INTO audit_log (actor, action, target, detail) VALUES ($1,$2,$3,$4)", [
    actor, action, target ?? null, detail ? JSON.stringify(detail) : null,
  ]);
}

export async function getSetting<T>(key: string, fallback: T): Promise<T> {
  const row = await one<{ value: T }>("SELECT value FROM settings WHERE key = $1", [key]);
  return row ? row.value : fallback;
}

export async function setSetting(key: string, value: unknown) {
  await q(
    `INSERT INTO settings (key, value, updated_at) VALUES ($1, $2, now())
     ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = now()`,
    [key, JSON.stringify(value)],
  );
}
