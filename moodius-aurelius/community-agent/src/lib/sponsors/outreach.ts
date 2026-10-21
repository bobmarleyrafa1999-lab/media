import { config } from "../config";
import { audit, one, q } from "../db";
import { sendMail } from "../email/send";
import { mediaKitMetrics } from "../analytics";
import { checkOutreach, OPT_OUT_LINE } from "./compliance";
import { buildDossier, FOLLOWUPS, signature } from "./drafting";
import { addActivity, moveStage } from "./crm";
import { pickContact, researchBrand, type Fetcher } from "./discovery";
import { qualifies, totalScore, type Scores } from "./scoring";

export async function research(id: number, fetcher?: Fetcher) {
  const s = await one<{ website: string; evidence: { claim: string; url: string }[] }>("SELECT website, evidence FROM sponsors WHERE id = $1", [id]);
  if (!s) throw new Error("sponsor not found");
  const r = await researchBrand(s.website, fetcher, fetcher ? 0 : 1000);
  const contact = pickContact(r);
  const evidence = [...(s.evidence ?? []), ...r.evidence].filter((e, i, a) => a.findIndex((x) => x.claim === e.claim && x.url === e.url) === i);
  await q(
    `UPDATE sponsors SET evidence = $2, public_contact_email = coalesce(public_contact_email, $3), contact_source_url = coalesce(contact_source_url, $4),
       dossier = coalesce(dossier, '{}'::jsonb) || jsonb_build_object('site', $5::jsonb) WHERE id = $1`,
    [id, JSON.stringify(evidence), contact?.email ?? null, contact?.source_url ?? null,
     JSON.stringify({ title: r.title, description: r.description, pagesChecked: r.pagesChecked, blockedByRobots: r.blockedByRobots, emailsSeen: r.emails })]);
  await addActivity(id, "research", `Checked ${r.pagesChecked.length} public pages`, `${r.evidence.length} evidence items; contact ${contact?.email ?? "not found"}`);
  return { ...r, contact };
}

export async function setScores(id: number, scores: Scores, actor = "surafel") {
  const ev = await one<{ evidence: unknown[]; stage: string }>("SELECT evidence, stage FROM sponsors WHERE id = $1", [id]);
  const { total } = totalScore(scores);
  await q("UPDATE sponsors SET scores = $2, total_score = $3 WHERE id = $1", [id, JSON.stringify(scores), total]);
  const qual = qualifies(scores, (ev?.evidence ?? []).length);
  if (qual.ok && ev?.stage === "Prospect") await moveStage(id, "Qualified", actor, qual.why);
  return { total, qualified: qual };
}

export async function draft(id: number, actor = "claude") {
  const s = await one<{ name: string; website: string; category: string; evidence: { claim: string; url: string }[]; dossier: any; stage: string; public_contact_email: string | null }>(
    "SELECT name, website, category, evidence, dossier, stage, public_contact_email FROM sponsors WHERE id = $1", [id]);
  if (!s) throw new Error("sponsor not found");
  if (s.stage !== "Qualified" && s.stage !== "Drafted") throw new Error("only Qualified prospects get drafts");
  const m = await mediaKitMetrics();
  const d = await buildDossier({
    name: s.name, website: s.website, category: s.category, evidence: s.evidence ?? [],
    siteTitle: s.dossier?.site?.title, siteDescription: s.dossier?.site?.description,
    metrics: { medianReach: m.medianReach, subscribers: m.newsletterSubscribers, savesPerReach: m.savesPerReach },
  });
  await q("UPDATE sponsors SET dossier = coalesce(dossier, '{}'::jsonb) || $2::jsonb WHERE id = $1", [id, JSON.stringify({ ...d, generated_at: new Date().toISOString() })]);
  await q(
    `INSERT INTO outreach (sponsor_id, sequence, to_address, subject, body) VALUES ($1, 0, $2, $3, $4)
     ON CONFLICT (sponsor_id, sequence) DO UPDATE SET subject = EXCLUDED.subject, body = EXCLUDED.body, to_address = EXCLUDED.to_address,
       status = 'draft', approved_by = NULL, approved_at = NULL WHERE outreach.status IN ('draft','approved')`,
    [id, s.public_contact_email, d.email.subject, d.email.body]);
  for (const [n, f] of FOLLOWUPS.entries()) {
    await q(`INSERT INTO outreach (sponsor_id, sequence, to_address, subject, body) VALUES ($1,$2,$3,$4,$5) ON CONFLICT (sponsor_id, sequence) DO NOTHING`,
      [id, n + 1, s.public_contact_email, `${d.email.subject} (follow-up)`, `${f.note}\n\n[Write two lines here before approving]${signature()}`]);
  }
  if (s.stage === "Qualified") await moveStage(id, "Drafted", actor);
  return d;
}

export async function approveOutreach(outreachId: number, edits: { subject?: string; body?: string }, actor = "surafel") {
  const o = await one<{ sponsor_id: number; body: string }>("SELECT sponsor_id, body FROM outreach WHERE id = $1 AND status IN ('draft','approved')", [outreachId]);
  if (!o) throw new Error("outreach not found or already sent");
  let body = edits.body ?? o.body;
  if (!body.includes(OPT_OUT_LINE)) body = body.trim() + `\n\n${OPT_OUT_LINE}`;
  await q("UPDATE outreach SET subject = coalesce($2, subject), body = $3, status = 'approved', approved_by = $4, approved_at = now() WHERE id = $1",
    [outreachId, edits.subject ?? null, body, actor]);
  const s = await one<{ stage: string }>("SELECT stage FROM sponsors WHERE id = $1", [o.sponsor_id]);
  if (s?.stage === "Drafted") await moveStage(o.sponsor_id, "Approved", actor);
  await audit(actor, "approve_outreach", String(outreachId));
}

// Sends exactly one approved email, after every compliance check passes. Follow-ups only when the
// previous email was sent, the due day has passed, and the prospect hasn't replied.
export async function sendApproved(outreachId: number, actor = "surafel") {
  const o = await one<{ id: number; sponsor_id: number; sequence: number; to_address: string | null; subject: string; body: string; approved_by: string | null; status: string }>(
    "SELECT * FROM outreach WHERE id = $1", [outreachId]);
  if (!o || o.status !== "approved") throw new Error("outreach must be approved first");
  const s = await one<{ id: number; entity_type: string; opted_out: boolean; public_contact_email: string | null; contact_source_url: string | null; stage: string }>(
    "SELECT id, entity_type, opted_out, public_contact_email, contact_source_url, stage FROM sponsors WHERE id = $1", [o.sponsor_id]);
  if (!s) throw new Error("sponsor missing");
  if (o.sequence > 0) {
    if (s.stage !== "Contacted") throw new Error("follow-ups only while waiting for a first reply");
    const prev = await one<{ sent_at: Date | null }>("SELECT sent_at FROM outreach WHERE sponsor_id = $1 AND sequence = $2 AND status = 'sent'", [o.sponsor_id, o.sequence - 1]);
    if (!prev?.sent_at) throw new Error("previous email not sent");
    // FOLLOWUPS days count from the first email; the gap is measured from the previous send.
    const gapDays = FOLLOWUPS[o.sequence - 1].day - (o.sequence > 1 ? FOLLOWUPS[o.sequence - 2].day : 0);
    if (Date.now() - new Date(prev.sent_at).getTime() < gapDays * 86400_000) throw new Error("follow-up not due yet");
  }
  const check = await checkOutreach({ sponsor: s, email: { to: o.to_address, subject: o.subject, body: o.body, sequence: o.sequence, approved_by: o.approved_by } });
  if (!check.ok) {
    await q("UPDATE outreach SET error = $2 WHERE id = $1", [o.id, check.errors.join("; ")]);
    return { sent: false, errors: check.errors, warnings: check.warnings };
  }
  const cfg = config().outreach;
  const res = await sendMail({
    kind: "outreach", dedupeKey: `outreach:${o.id}`, to: o.to_address!, subject: o.subject,
    html: `<div style="font-family:Georgia,serif;font-size:15px;line-height:1.5;white-space:pre-wrap">${o.body.replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" })[c]!)}</div>`,
    text: o.body, from: cfg.from, replyTo: cfg.replyTo || undefined,
  });
  if (res.status === "failed") return { sent: false, errors: ["email provider error"], warnings: check.warnings };
  await q("UPDATE outreach SET status = 'sent', sent_at = now(), provider_id = $2 WHERE id = $1", [o.id, res.id ?? null]);
  if (s.stage === "Approved") await moveStage(s.id, "Contacted", actor);
  await addActivity(s.id, "email", `Sent: ${o.subject}`, undefined, actor);
  return { sent: true, logged: res.status === "logged", errors: [], warnings: check.warnings };
}
