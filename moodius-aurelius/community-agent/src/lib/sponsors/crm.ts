import { audit, one, q, tx } from "../db";

// Stages from the brief. Stage-change auto-tasks follow alongot/creator-crm lib/stage-automations.ts (MIT),
// rewritten for a creator pitching brands instead of a brand hiring creators.
export const STAGES = ["Prospect", "Qualified", "Drafted", "Approved", "Contacted", "Replied", "Negotiating", "Contracted", "Delivered", "Paid", "Lost"] as const;
export type Stage = (typeof STAGES)[number];

const NEXT: Record<Stage, Stage[]> = {
  Prospect: ["Qualified", "Lost"],
  Qualified: ["Drafted", "Lost"],
  Drafted: ["Approved", "Qualified", "Lost"],
  Approved: ["Contacted", "Drafted", "Lost"],
  Contacted: ["Replied", "Lost"],
  Replied: ["Negotiating", "Lost"],
  Negotiating: ["Contracted", "Lost"],
  Contracted: ["Delivered", "Lost"],
  Delivered: ["Paid"],
  Paid: [],
  Lost: ["Prospect"],
};

export function canMove(from: Stage, to: Stage) { return NEXT[from]?.includes(to) ?? false; }

export function autoTask(to: Stage): { title: string; days: number } | null {
  switch (to) {
    case "Qualified": return { title: "Generate dossier and outreach draft", days: 0 };
    case "Drafted": return { title: "Review, edit and approve the outreach email", days: 1 };
    case "Contacted": return { title: "Follow-up 1 if no reply (stop if they opt out)", days: 5 };
    case "Replied": return { title: "Answer within one working day", days: 1 };
    case "Negotiating": return { title: "Send written terms: deliverables, dates, usage rights, #ad disclosure, fee, payment terms", days: 2 };
    case "Contracted": return { title: "Send content draft to the brand for approval", days: 7 };
    case "Delivered": return { title: "Send invoice and performance recap (real numbers only)", days: 1 };
    case "Paid": return { title: "Thank-you note; record revenue entry", days: 2 };
    default: return null;
  }
}

export async function moveStage(id: number, to: Stage, actor: string, note?: string) {
  return tx(async (c) => {
    const { rows } = await c.query<{ stage: Stage }>("SELECT stage FROM sponsors WHERE id = $1 FOR UPDATE", [id]);
    if (!rows[0]) throw new Error("sponsor not found");
    const from = rows[0].stage;
    if (from === to) return;
    if (!canMove(from, to)) throw new Error(`cannot move ${from} → ${to}`);
    await c.query("UPDATE sponsors SET stage = $2, stage_changed_at = now() WHERE id = $1", [id, to]);
    await c.query("INSERT INTO sponsor_activities (sponsor_id, type, title, body, actor) VALUES ($1,'stage',$2,$3,$4)", [id, `${from} → ${to}`, note ?? null, actor]);
    const t = autoTask(to);
    if (t) await c.query("INSERT INTO sponsor_tasks (sponsor_id, title, due_at) VALUES ($1, $2, now() + make_interval(days => $3))", [id, t.title, t.days]);
    // Leaving the outreach path closes any open follow-up tasks.
    if (["Replied", "Lost", "Negotiating"].includes(to)) {
      await c.query("UPDATE sponsor_tasks SET done = true, done_at = now() WHERE sponsor_id = $1 AND NOT done AND title LIKE 'Follow-up%'", [id]);
      await c.query("UPDATE outreach SET status = 'cancelled' WHERE sponsor_id = $1 AND status IN ('draft','approved') AND sequence > 0", [id]);
    }
  });
}

export async function addActivity(id: number, type: string, title: string, body?: string, actor = "system") {
  await q("INSERT INTO sponsor_activities (sponsor_id, type, title, body, actor) VALUES ($1,$2,$3,$4,$5)", [id, type, title, body ?? null, actor]);
}

export async function dueFollowUps() {
  return q<{ id: number; sponsor_id: number; title: string; due_at: Date; name: string }>(
    `SELECT t.id, t.sponsor_id, t.title, t.due_at, s.name FROM sponsor_tasks t JOIN sponsors s ON s.id = t.sponsor_id
      WHERE NOT t.done AND t.due_at <= now() ORDER BY t.due_at`);
}

export async function optOut(id: number, actor = "surafel") {
  const s = await one<{ public_contact_email: string | null; website: string }>("SELECT public_contact_email, website FROM sponsors WHERE id = $1", [id]);
  await q("UPDATE sponsors SET opted_out = true WHERE id = $1", [id]);
  if (s?.public_contact_email) await q("INSERT INTO suppression (entry, reason) VALUES (lower($1), 'opted out') ON CONFLICT DO NOTHING", [s.public_contact_email]);
  await q("UPDATE outreach SET status = 'cancelled' WHERE sponsor_id = $1 AND status IN ('draft','approved')", [id]);
  await addActivity(id, "opt_out", "Opted out: never contact again", undefined, actor);
  await audit(actor, "sponsor_opt_out", String(id));
}
