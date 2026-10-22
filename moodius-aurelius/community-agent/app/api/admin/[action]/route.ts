import { NextResponse, type NextRequest } from "next/server";
import { cookies } from "next/headers";
import { config } from "../../../../src/lib/config";
import { makeSession, passwordOk, SESSION_COOKIE, sessionMaxAge, sessionValid } from "../../../../src/lib/auth";
import { audit, q, setSetting } from "../../../../src/lib/db";
import { allow, clientIp } from "../../../../src/lib/ratelimit";
import { approveAndPublish, markRepliedManually, rejectComment, sendKeywordDm } from "../../../../src/lib/pipeline";
import type { Keyword } from "../../../../src/lib/safety";
import { exportConfirmedCsv, erase } from "../../../../src/lib/newsletter";
import { addExpense, addManualRevenue } from "../../../../src/lib/revenue";
import { moveStage, optOut, type Stage } from "../../../../src/lib/sponsors/crm";
import { approveOutreach, draft, research, sendApproved, setScores } from "../../../../src/lib/sponsors/outreach";
import { DIMENSIONS, type Dimension, type Scores } from "../../../../src/lib/sponsors/scoring";
import { runScheduled } from "../../../../src/lib/jobs";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

const back = (path: string, msg?: string) => {
  const u = new URL(path, config().baseUrl);
  if (msg) u.searchParams.set("msg", msg.slice(0, 300));
  return NextResponse.redirect(u, 303);
};
const s = (f: FormData, k: string) => String(f.get(k) ?? "").trim();
const cents = (v: string) => Math.round(Number(v.replace(/[£€,\s]/g, "")) * 100);

export async function POST(req: NextRequest, ctx: { params: Promise<{ action: string }> }) {
  const { action } = await ctx.params;
  const f = await req.formData();
  const jar = await cookies();

  if (action === "login") {
    if (!allow(`login:${clientIp(req.headers)}`, 5)) return back("/admin/login", "Too many attempts. Wait a minute.");
    if (!passwordOk(s(f, "password"))) return back("/admin/login", "Wrong password (or ADMIN_PASSWORD not set / shorter than 12 characters).");
    jar.set(SESSION_COOKIE, makeSession(), { httpOnly: true, sameSite: "strict", secure: config().baseUrl.startsWith("https"), path: "/", maxAge: sessionMaxAge });
    return back("/admin");
  }
  if (!sessionValid(jar.get(SESSION_COOKIE)?.value)) return back("/admin/login");
  // CSRF: same-site strict cookie + origin check.
  const origin = req.headers.get("origin");
  if (origin && new URL(origin).host !== new URL(config().baseUrl).host && new URL(origin).host !== req.nextUrl.host) return new NextResponse("bad origin", { status: 403 });

  const ret = s(f, "return") || "/admin";
  try {
    switch (action) {
      case "logout": jar.delete(SESSION_COOKIE); return back("/admin/login");
      case "approve": await approveAndPublish(s(f, "comment_id"), s(f, "text")); return back(ret, "Published.");
      case "reject": await rejectComment(s(f, "comment_id")); return back(ret, "Rejected.");
      case "manual": await markRepliedManually(s(f, "comment_id"), s(f, "text") || null); return back(ret, "Marked as answered.");
      case "dm": await sendKeywordDm(s(f, "comment_id"), s(f, "keyword") as Keyword, "surafel"); return back(ret, "DM sent (or already sent).");
      case "mode": {
        const mode = s(f, "mode");
        if (!["draft_only", "assisted", "controlled"].includes(mode)) throw new Error("bad mode");
        await setSetting("agent_mode", mode); await audit("surafel", "set_mode", mode); return back(ret, `Mode: ${mode}`);
      }
      case "kill": await setSetting("kill_switch", s(f, "on") === "1"); await audit("surafel", "kill_switch", s(f, "on")); return back(ret, "Kill switch updated.");
      case "run-job": return back(ret, `Ran ${s(f, "job")}: ${JSON.stringify(await runScheduled(s(f, "job"))).slice(0, 200)}`);
      case "link": {
        await q(`INSERT INTO links (slug, label, destination, kind, disclosure, position, active) VALUES ($1,$2,$3,$4,$5,$6,$7)
                 ON CONFLICT (slug) DO UPDATE SET label=EXCLUDED.label, destination=EXCLUDED.destination, kind=EXCLUDED.kind,
                 disclosure=EXCLUDED.disclosure, position=EXCLUDED.position, active=EXCLUDED.active`,
          [s(f, "slug").toLowerCase().replace(/[^a-z0-9-]/g, "-"), s(f, "label"), s(f, "destination"), s(f, "kind"), s(f, "disclosure") || null, Number(s(f, "position") || 100), s(f, "active") !== "0"]);
        return back(ret, "Link saved.");
      }
      case "revenue": await addManualRevenue({ stream: s(f, "stream"), amount_cents: cents(s(f, "amount")), currency: s(f, "currency") || "GBP", occurred_on: s(f, "date"), note: s(f, "note") }); return back(ret, "Revenue added.");
      case "expense": await addExpense({ item: s(f, "item"), amount_cents: cents(s(f, "amount")), currency: s(f, "currency") || "GBP", occurred_on: s(f, "date"), recurring: s(f, "recurring") === "on" }); return back(ret, "Expense added.");
      case "sponsor-add": {
        await q("INSERT INTO sponsors (name, website, category, country, entity_type, notes) VALUES ($1,$2,$3,$4,$5,$6) ON CONFLICT (website) DO NOTHING",
          [s(f, "name"), s(f, "website"), s(f, "category"), s(f, "country") || null, s(f, "entity_type") || "unknown", s(f, "notes") || null]);
        return back(ret, "Prospect added.");
      }
      case "sponsor-research": { const r = await research(Number(s(f, "id"))); return back(ret, `Checked ${r.pagesChecked.length} pages, ${r.evidence.length} evidence items.`); }
      case "sponsor-scores": {
        const scores: Scores = {};
        for (const k of Object.keys(DIMENSIONS) as Dimension[]) {
          const v = s(f, `score_${k}`); const reason = s(f, `reason_${k}`);
          scores[k] = v !== "" && reason ? { score: Number(v), reason, evidence_url: s(f, `url_${k}`) || undefined } : null;
        }
        await q("UPDATE sponsors SET entity_type = $2, public_contact_email = nullif($3,''), contact_source_url = nullif($4,'') WHERE id = $1",
          [Number(s(f, "id")), s(f, "entity_type") || "unknown", s(f, "contact_email"), s(f, "contact_source")]);
        const r = await setScores(Number(s(f, "id")), scores);
        return back(ret, `Score ${r.total}. ${r.qualified.ok ? "Qualified." : `Not qualified: ${r.qualified.why}`}`);
      }
      case "sponsor-draft": await draft(Number(s(f, "id"))); return back(ret, "Dossier and drafts ready.");
      case "outreach-approve": await approveOutreach(Number(s(f, "outreach_id")), { subject: s(f, "subject"), body: s(f, "body") }); return back(ret, "Approved. Not sent yet.");
      case "outreach-send": { const r = await sendApproved(Number(s(f, "outreach_id"))); return back(ret, r.sent ? (r.logged ? "Logged (email in mock mode)." : "Sent.") : `Blocked: ${r.errors.join("; ")}`); }
      case "sponsor-stage": await moveStage(Number(s(f, "id")), s(f, "stage") as Stage, "surafel", s(f, "note") || undefined); return back(ret, "Stage updated.");
      case "sponsor-optout": await optOut(Number(s(f, "id"))); return back(ret, "Opted out and suppressed.");
      case "task-done": await q("UPDATE sponsor_tasks SET done = true, done_at = now() WHERE id = $1", [Number(s(f, "task_id"))]); return back(ret);
      case "suppress": await q("INSERT INTO suppression (entry, reason) VALUES (lower($1), $2) ON CONFLICT DO NOTHING", [s(f, "entry"), s(f, "reason") || "manual"]); return back(ret, "Suppressed.");
      case "erase-subscriber": await erase(s(f, "email")); return back(ret, "Erased.");
      case "export-subscribers": return new NextResponse(await exportConfirmedCsv(), { headers: { "Content-Type": "text/csv", "Content-Disposition": "attachment; filename=moodius-subscribers.csv" } });
      default: return new NextResponse("unknown action", { status: 404 });
    }
  } catch (e) {
    return back(ret, `Error: ${(e as Error).message}`);
  }
}
