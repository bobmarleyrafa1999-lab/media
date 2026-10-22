// Transactional email. EMAIL_PROVIDER=resend sends through Resend's HTTP API (free tier:
// 3,000 emails/month); EMAIL_PROVIDER=log sends nothing and keeps the message in the
// outbox table, which is how tests and local runs read "sent" mail.

import { nowIso } from "./util.js";

export async function sendEmail(c, db, { to, subject, text, kind, headers = {} }) {
  const footer = c.email.postalAddress ? `\n\n—\nMoodius Aurelius · ${c.email.postalAddress}` : "\n\n—\nMoodius Aurelius";
  const body = text + footer;
  let providerId = null;
  let error = null;
  if (c.email.provider === "resend") {
    try {
      const res = await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: { authorization: `Bearer ${c.email.resendKey}`, "content-type": "application/json" },
        body: JSON.stringify({
          from: c.email.from,
          to: [to],
          subject,
          text: body,
          ...(c.email.replyTo ? { reply_to: c.email.replyTo } : {}),
          ...(Object.keys(headers).length ? { headers } : {}),
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok) providerId = data.id || null;
      else error = `resend ${res.status}: ${data.message || "error"}`;
    } catch (e) {
      error = String(e.message || e);
    }
  }
  await db
    .prepare("INSERT INTO outbox (to_addr, subject, body_text, kind, created_at, provider, provider_id, error) VALUES (?,?,?,?,?,?,?,?)")
    .bind(to, subject, body, kind, nowIso(), c.email.provider, providerId, error)
    .run();
  return { ok: !error, providerId, error };
}
