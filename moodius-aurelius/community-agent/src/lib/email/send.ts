import { Resend } from "resend";
import { config } from "../config";
import { one, q } from "../db";
import { log } from "../log";

export interface Mail {
  kind: string;            // comment_alert | urgent_alert | daily_digest | weekly_report | error_alert | newsletter_confirm | outreach
  dedupeKey: string;       // stored UNIQUE: the same key never sends twice
  to: string;
  subject: string;
  html: string;
  text?: string;
  from?: string;
  replyTo?: string;
  headers?: Record<string, string>;
}

let resend: Resend | null = null;

// Sends through Resend when RESEND_API_KEY is set; otherwise stores the rendered email in
// email_log with status 'logged' so it can be read in the dashboard (mock mode).
export async function sendMail(m: Mail): Promise<{ status: "sent" | "logged" | "duplicate" | "failed"; id?: string }> {
  const inserted = await one<{ id: number }>(
    `INSERT INTO email_log (kind, dedupe_key, to_address, subject, html) VALUES ($1,$2,$3,$4,$5)
     ON CONFLICT (dedupe_key) DO NOTHING RETURNING id`,
    [m.kind, m.dedupeKey, m.to, m.subject, m.html],
  );
  if (!inserted) return { status: "duplicate" };
  const cfg = config().email;
  if (cfg.mock) {
    await q("UPDATE email_log SET status = 'logged' WHERE id = $1", [inserted.id]);
    log.info("email logged (mock)", { kind: m.kind, to: m.to, subject: m.subject });
    return { status: "logged" };
  }
  try {
    if (!resend) resend = new Resend(cfg.resendKey);
    const { data, error } = await resend.emails.send({
      from: m.from ?? cfg.from, to: [m.to], subject: m.subject, html: m.html, text: m.text,
      replyTo: m.replyTo, headers: m.headers,
    });
    if (error) throw new Error(`${error.name}: ${error.message}`);
    await q("UPDATE email_log SET status = 'sent', provider_id = $2 WHERE id = $1", [inserted.id, data?.id ?? null]);
    return { status: "sent", id: data?.id };
  } catch (e) {
    await q("UPDATE email_log SET status = 'failed', error = $2 WHERE id = $1", [inserted.id, (e as Error).message]);
    // Release the dedupe key so a retry can send it.
    await q("UPDATE email_log SET dedupe_key = dedupe_key || ':failed:' || id WHERE id = $1", [inserted.id]);
    log.error("email failed", { kind: m.kind, error: (e as Error).message });
    return { status: "failed" };
  }
}

// Inbox-overload guard for per-comment emails (urgent alerts bypass it).
export async function underHourlyCap(): Promise<boolean> {
  const r = await one<{ n: string }>(
    `SELECT count(*) AS n FROM email_log WHERE kind = 'comment_alert' AND created_at > now() - interval '1 hour' AND status IN ('sent','logged')`,
  );
  return Number(r?.n ?? 0) < config().email.maxPerHour;
}
