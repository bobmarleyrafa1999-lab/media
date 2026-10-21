import { config } from "../config";
import { one } from "../db";

// Sending floor for 1:1 B2B outreach under UK GDPR + PECR. Rules adapted from oratis/influencex
// packages/social-ops/edm/compliance.js and suppression.js (MIT), reduced to what a one-person,
// human-approved outreach programme needs. Nothing here sends; it only says yes or no and why.

const CONSUMER_DOMAINS = new Set(["gmail.com", "googlemail.com", "outlook.com", "hotmail.com", "live.com", "yahoo.com", "icloud.com", "me.com", "aol.com", "proton.me", "protonmail.com", "gmx.com"]);
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
export const OPT_OUT_LINE = "If you'd rather not hear from me again, just reply \"no thanks\" and I won't contact you again.";

export interface OutreachCheckInput {
  sponsor: { id: number; entity_type: string; opted_out: boolean; public_contact_email: string | null; contact_source_url: string | null; stage: string };
  email: { to: string | null; subject: string; body: string; sequence: number; approved_by: string | null };
}

export async function checkOutreach(i: OutreachCheckInput): Promise<{ ok: boolean; errors: string[]; warnings: string[] }> {
  const errors: string[] = [];
  const warnings: string[] = [];
  const o = config().outreach;
  const to = (i.email.to ?? "").toLowerCase();

  if (!i.email.approved_by) errors.push("not approved by a human");
  if (!EMAIL_RE.test(to)) errors.push("no valid recipient address");
  if (to && to !== (i.sponsor.public_contact_email ?? "").toLowerCase()) errors.push("recipient is not the publicly listed business contact on file");
  if (!i.sponsor.contact_source_url) errors.push("no source URL recorded for the contact address (we never guess addresses)");
  if (i.sponsor.opted_out) errors.push("this company opted out");
  if (i.sponsor.entity_type === "sole_trader") errors.push("sole traders/partnerships count as individuals under PECR: prior consent needed");
  if (i.sponsor.entity_type === "unknown") errors.push("set entity type (corporate vs sole trader) before sending");
  if (i.email.sequence > 2) errors.push("max two follow-ups");

  const domain = to.split("@")[1] ?? "";
  const sup = await one("SELECT 1 FROM suppression WHERE entry = $1 OR entry = $2", [to, domain]);
  if (sup) errors.push("address or domain is on the suppression list");

  if (!o.from || !EMAIL_RE.test(o.from.replace(/^.*<|>$/g, ""))) errors.push("OUTREACH_FROM not configured");
  else if (CONSUMER_DOMAINS.has(o.from.replace(/^.*<|>$/g, "").split("@")[1] ?? "")) errors.push("send from an owned domain with SPF/DKIM/DMARC, not a consumer mailbox");
  if (!o.postalAddress) errors.push("OUTREACH_POSTAL_ADDRESS not set (a PO box or virtual office keeps the brand anonymous)");
  else if (!i.email.body.includes(o.postalAddress)) errors.push("postal/contact address missing from the body");
  if (!i.email.body.includes(OPT_OUT_LINE)) errors.push("opt-out line missing from the body");
  if (/^\s*(re|fw|fwd)\s*:/i.test(i.email.subject)) errors.push("subject imitates a reply/forward");
  if (i.email.body.split(/\s+/).length > 260) warnings.push("long email; under 180 words gets more replies");

  const sentToday = await one<{ n: string }>("SELECT count(*) AS n FROM outreach WHERE status = 'sent' AND sent_at > now() - interval '24 hours'");
  if (Number(sentToday?.n ?? 0) >= o.dailyCap) errors.push(`daily cap of ${o.dailyCap} reached`);

  return { ok: errors.length === 0, errors, warnings };
}
