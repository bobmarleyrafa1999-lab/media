// Fallback newsletter capture, used only while the community agent (which owns the
// real list) isn't deployed. Same request shape and consent record as the agent:
// double opt-in, exact consent wording + version + timestamp, one-click unsubscribe,
// salted IP hash at most. Exported for import the day the agent goes live.

import { sendEmail } from "./email.js";
import { nowIso, normalizeEmail, randomToken, sha256Hex, cleanSrc, cleanSlug } from "./util.js";

export const CONSENT_VERSION = "2026-10-21";
export const CONSENT_TEXT =
  "Yes, email me the Moodius Aurelius newsletter (about one essay a week). I can unsubscribe at any time with one click. My email is used only for this newsletter and is never sold or shared.";

export const LEAD_MAGNETS = {
  "seven-day-reflection-guide": { title: "Seven Days of Honest Reflection", path: "/downloads/free/seven-day-reflection-guide.pdf" },
};

export async function subscribe(c, db, { email, consent, source, leadMagnet, ip }) {
  const addr = normalizeEmail(email);
  if (!addr) return { status: 400, body: { ok: false, error: "Please enter a valid email address." } };
  if (consent !== true) return { status: 400, body: { ok: false, error: "Please tick the consent box to subscribe." } };
  const magnet = leadMagnet && LEAD_MAGNETS[leadMagnet] ? leadMagnet : null;
  const existing = await db.prepare("SELECT * FROM subscribers WHERE email = ?").bind(addr).first();
  // Same answer whether or not the address exists, so the form can't be used to test who's subscribed.
  const okBody = { ok: true, pending: true, message: "Check your inbox and click the link to confirm." };
  if (existing?.status === "confirmed") return { status: 200, body: okBody };
  if (existing?.last_email_at && Date.now() - Date.parse(existing.last_email_at) < 10 * 60000) return { status: 200, body: okBody };

  const confirmToken = randomToken();
  const unsubToken = existing?.unsub_token_hash ? null : randomToken();
  const at = nowIso();
  const ipHash = ip && c.ipHashSalt ? await sha256Hex(`${c.ipHashSalt}:${ip}`) : null;
  if (existing) {
    await db
      .prepare("UPDATE subscribers SET status='pending', consent_text=?, consent_version=?, consent_at=?, source=?, lead_magnet=?, ip_hash=?, confirm_token_hash=?, last_email_at=?, unsubscribed_at=NULL WHERE email=?")
      .bind(CONSENT_TEXT, CONSENT_VERSION, at, cleanSrc(source), magnet, ipHash, await sha256Hex(confirmToken), at, addr)
      .run();
  } else {
    await db
      .prepare(
        "INSERT INTO subscribers (email, status, consent_text, consent_version, consent_at, source, lead_magnet, ip_hash, confirm_token_hash, unsub_token_hash, last_email_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
      )
      .bind(addr, "pending", CONSENT_TEXT, CONSENT_VERSION, at, cleanSrc(source), magnet, ipHash, await sha256Hex(confirmToken), await sha256Hex(unsubToken), at)
      .run();
  }
  const what = magnet ? `your free guide, ${LEAD_MAGNETS[magnet].title}, and ` : "";
  await sendEmail(c, db, {
    to: addr,
    subject: "Confirm your subscription to Moodius Aurelius",
    text: `One click to confirm and you'll get ${what}about one essay a week.\n\nConfirm: ${c.siteUrl}/api/newsletter/confirm?token=${confirmToken}\n\nIf you didn't ask for this, ignore this email and you won't hear from us again.`,
    kind: "confirm",
  });
  return { status: 200, body: okBody, _confirmToken: confirmToken, _unsubToken: unsubToken };
}

export async function confirm(c, db, token) {
  if (!token) return null;
  const row = await db.prepare("SELECT * FROM subscribers WHERE confirm_token_hash = ?").bind(await sha256Hex(token)).first();
  if (!row) return null;
  const at = nowIso();
  // A fresh unsubscribe token is issued at confirmation and goes out in the welcome email.
  const unsub = randomToken();
  await db
    .prepare("UPDATE subscribers SET status='confirmed', confirmed_at=?, confirm_token_hash=NULL, unsub_token_hash=? WHERE email=?")
    .bind(at, await sha256Hex(unsub), row.email)
    .run();
  const magnet = row.lead_magnet ? LEAD_MAGNETS[row.lead_magnet] : null;
  const unsubUrl = `${c.siteUrl}/api/newsletter/unsubscribe?token=${unsub}`;
  await sendEmail(c, db, {
    to: row.email,
    subject: magnet ? `Your guide: ${magnet.title}` : "You're subscribed to Moodius Aurelius",
    text:
      (magnet ? `Here is your guide:\n${c.siteUrl}${magnet.path}\n\nOne day at a time, ten minutes each. Day 1 works best in the evening.\n\n` : "") +
      `You're on the list. Expect about one essay a week, nothing more.\n\nUnsubscribe with one click: ${unsubUrl}`,
    kind: "welcome",
    headers: { "List-Unsubscribe": `<${unsubUrl}>`, "List-Unsubscribe-Post": "List-Unsubscribe=One-Click" },
  });
  await db.prepare("INSERT INTO conversion_events (kind, slug, src, at) VALUES ('subscribe', ?, ?, ?)").bind(cleanSlug(row.lead_magnet) || "newsletter", row.source, at).run();
  return { email: row.email, magnet, unsubToken: unsub };
}

export async function unsubscribe(db, token) {
  if (!token) return false;
  const res = await db
    .prepare("UPDATE subscribers SET status='unsubscribed', unsubscribed_at=? WHERE unsub_token_hash = ? AND status != 'unsubscribed'")
    .bind(nowIso(), await sha256Hex(token))
    .run();
  return (res.meta?.changes || 0) > 0;
}
