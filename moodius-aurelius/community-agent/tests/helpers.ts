import { migrate, q } from "../src/lib/db";

// Tests run against a real Postgres (TEST_DATABASE_URL, default local moodius_test) in mock mode:
// no Instagram token, no Anthropic key, no Resend key.
export function testEnv() {
  process.env.DATABASE_URL = process.env.TEST_DATABASE_URL ?? "postgres://moodius@localhost:5432/moodius_test";
  for (const k of ["IG_ACCESS_TOKEN", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "RESEND_API_KEY", "AGENT_MODE", "DM_KEYWORDS_ENABLED"]) delete process.env[k];
  process.env.IG_USER_ID = "17841400000000001";
  process.env.META_APP_SECRET = "test-app-secret";
  process.env.META_VERIFY_TOKEN = "test-verify";
  process.env.SESSION_SECRET = "test-session-secret-0123456789";
  process.env.ADMIN_PASSWORD = "correct horse battery";
  process.env.CRON_SECRET = "cron-secret";
  process.env.OWNER_EMAIL = "owner@example.org";
  process.env.APP_BASE_URL = "https://agent.example.org";
}

let migrated = false;
export async function resetDb() {
  if (!migrated) { await migrate(); migrated = true; }
  const tables = ["comments", "media_insights", "media", "jobs", "webhook_events", "outbound_actions", "email_log", "subscribers", "links",
    "conversion_events", "sponsor_activities", "sponsor_tasks", "outreach", "suppression", "revenue_entries", "deals", "sponsors", "expenses", "settings", "audit_log", "secrets"];
  await q(`TRUNCATE ${tables.join(", ")} RESTART IDENTITY CASCADE`);
}
