import { config } from "./config";
import { audit, one, q } from "./db";
import { randomToken, sha256 } from "./crypto";
import { newsletterConfirm } from "./email/templates";
import { sendMail } from "./email/send";
import { trackEvent } from "./tracking";

// Double opt-in list, UK GDPR / PECR: explicit unticked consent box, the exact wording and version
// stored with a timestamp, a confirmation email before anything else is sent, one-click unsubscribe,
// and only a salted hash of the IP kept (for abuse handling), never the IP itself.

export const CONSENT_TEXT =
  "Yes, email me the Moodius Aurelius newsletter (about one essay a week). I can unsubscribe at any time with one click. My email is used only for this newsletter and is never sold or shared.";

const EMAIL_RE = /^[^\s@]{1,64}@[^\s@]{1,190}\.[^\s@]{2,}$/;

// Free downloads delivered only AFTER the confirm click. Paths live on the public site (storefront).
export const LEAD_MAGNETS: Record<string, { title: string; path: string }> = {
  "seven-day-reflection-guide": { title: "The free 7-day reflection guide", path: "/downloads/free/seven-day-reflection-guide.pdf" },
};

export function leadMagnetUrl(key: string | null | undefined): { title: string; url: string } | null {
  const m = key ? LEAD_MAGNETS[key] : undefined;
  return m ? { title: m.title, url: `${config().publicSiteUrl}${m.path}` } : null;
}

export type SubscribeResult = { ok: true; status: "pending" | "already_confirmed" } | { ok: false; error: string };

export async function subscribe(input: { email: string; consent: boolean; source?: string | null; ip?: string | null; leadMagnet?: string | null }): Promise<SubscribeResult> {
  const email = input.email.trim().toLowerCase();
  if (!EMAIL_RE.test(email)) return { ok: false, error: "That email address doesn't look right." };
  if (!input.consent) return { ok: false, error: "Please tick the box to confirm you want the newsletter." };
  const existing = await one<{ status: string }>("SELECT status FROM subscribers WHERE lower(email) = $1", [email]);
  if (existing?.status === "confirmed") return { ok: true, status: "already_confirmed" };

  const leadMagnet = input.leadMagnet && LEAD_MAGNETS[input.leadMagnet] ? input.leadMagnet : null;
  const confirmToken = randomToken();
  const unsubToken = randomToken();
  const ipHash = input.ip ? sha256(`${config().sessionSecret}:${input.ip}`).slice(0, 16) : null;
  await q(
    `INSERT INTO subscribers (email, status, consent_text, consent_version, consent_at, source, confirm_token_hash, unsubscribe_token_hash, ip_hash, lead_magnet)
     VALUES ($1, 'pending', $2, $3, now(), $4, $5, $6, $7, $8)
     ON CONFLICT (lower(email)) DO UPDATE SET status = 'pending', consent_text = EXCLUDED.consent_text, consent_version = EXCLUDED.consent_version,
       consent_at = now(), source = EXCLUDED.source, confirm_token_hash = EXCLUDED.confirm_token_hash,
       unsubscribe_token_hash = EXCLUDED.unsubscribe_token_hash, ip_hash = EXCLUDED.ip_hash, unsubscribed_at = NULL,
       lead_magnet = coalesce(EXCLUDED.lead_magnet, subscribers.lead_magnet)`,
    [email, CONSENT_TEXT, config().newsletter.consentVersion, input.source ?? null, sha256(confirmToken), sha256(unsubToken), ipHash, leadMagnet],
  );
  const base = config().baseUrl;
  const mail = newsletterConfirm(`${base}/newsletter/confirm?t=${confirmToken}`, `${base}/newsletter/unsubscribe?t=${unsubToken}`);
  await sendMail({ kind: "newsletter_confirm", dedupeKey: `confirm:${sha256(confirmToken)}`, to: email, ...mail });
  await trackEvent("signup_pending", { src: input.source ?? undefined });
  return { ok: true, status: "pending" };
}

export async function confirm(token: string): Promise<{ ok: boolean; leadMagnet: { title: string; url: string } | null }> {
  const row = await one<{ id: number; email: string; source: string | null; lead_magnet: string | null }>(
    `UPDATE subscribers SET status = 'confirmed', confirmed_at = now(), confirm_token_hash = NULL
      WHERE confirm_token_hash = $1 AND status = 'pending' RETURNING id, email, source, lead_magnet`, [sha256(token)]);
  if (!row) return { ok: false, leadMagnet: null };
  await trackEvent("signup_confirmed", { src: row.source ?? undefined });
  const lm = leadMagnetUrl(row.lead_magnet);
  if (lm) {
    // Fresh unsubscribe token (only its hash is stored) so this email carries a working link.
    const unsub = randomToken();
    await q("UPDATE subscribers SET unsubscribe_token_hash = $2 WHERE id = $1", [row.id, sha256(unsub)]);
    const unsubUrl = `${config().baseUrl}/newsletter/unsubscribe?t=${unsub}`;
    await sendMail({
      kind: "lead_magnet", dedupeKey: `lead:${row.id}:${row.lead_magnet}`, to: row.email,
      subject: `${lm.title} (as promised)`,
      html: `<p>Thank you for confirming. Here it is: <a href="${lm.url}">${lm.title}</a>.</p><p>The newsletter itself starts with the next essay.</p><p style="font-size:12px;color:#6b6760"><a href="${unsubUrl}">Unsubscribe</a></p>`,
      headers: { "List-Unsubscribe": `<${config().baseUrl}/api/newsletter/unsubscribe?t=${unsub}>`, "List-Unsubscribe-Post": "List-Unsubscribe=One-Click" },
    });
  }
  return { ok: true, leadMagnet: lm };
}

export async function unsubscribe(token: string): Promise<boolean> {
  const row = await one<{ id: number; source: string | null }>(
    `UPDATE subscribers SET status = 'unsubscribed', unsubscribed_at = now()
      WHERE unsubscribe_token_hash = $1 AND status <> 'unsubscribed' RETURNING id, source`, [sha256(token)]);
  if (!row) return false;
  await trackEvent("unsubscribe", { src: row.source ?? undefined });
  return true;
}

// Retention promised in the privacy notice: unconfirmed sign-ups go after 30 days.
export async function purgeUnconfirmed(): Promise<number> {
  const r = await q<{ id: number }>("DELETE FROM subscribers WHERE status = 'pending' AND consent_at < now() - interval '30 days' RETURNING id");
  return r.length;
}

// Erasure request (UK GDPR art. 17): removes the row entirely.
export async function erase(email: string, actor = "surafel") {
  await q("DELETE FROM subscribers WHERE lower(email) = lower($1)", [email]);
  await audit(actor, "erase_subscriber", sha256(email.toLowerCase()).slice(0, 12));
}

// CSV for importing confirmed subscribers into Substack, with consent evidence columns.
export async function exportConfirmedCsv(): Promise<string> {
  const rows = await q<{ email: string; consent_at: Date; consent_version: string; confirmed_at: Date; source: string | null }>(
    "SELECT email, consent_at, consent_version, confirmed_at, source FROM subscribers WHERE status = 'confirmed' ORDER BY confirmed_at");
  const esc = (v: unknown) => `"${String(v ?? "").replace(/"/g, '""')}"`;
  return ["email,consent_at,consent_version,confirmed_at,source", ...rows.map((r) =>
    [r.email, r.consent_at?.toISOString(), r.consent_version, r.confirmed_at?.toISOString(), r.source].map(esc).join(","))].join("\n");
}
