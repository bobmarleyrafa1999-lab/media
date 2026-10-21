import { notFound } from "next/navigation";
import { requireAdmin } from "../../../../src/lib/admin";
import { one, q } from "../../../../src/lib/db";
import { STAGES } from "../../../../src/lib/sponsors/crm";
import { DIMENSIONS, type Dimension } from "../../../../src/lib/sponsors/scoring";
import { AdminNav } from "../../nav";

export const dynamic = "force-dynamic";

export default async function Sponsor({ params, searchParams }: { params: Promise<{ id: string }>; searchParams: Promise<{ msg?: string }> }) {
  await requireAdmin();
  const id = Number((await params).id);
  const sp = await searchParams;
  const s = await one<any>("SELECT * FROM sponsors WHERE id = $1", [id]);
  if (!s) notFound();
  const outreach = await q<any>("SELECT * FROM outreach WHERE sponsor_id = $1 ORDER BY sequence", [id]);
  const acts = await q<any>("SELECT * FROM sponsor_activities WHERE sponsor_id = $1 ORDER BY at DESC LIMIT 50", [id]);
  const ret = `/admin/sponsors/${id}`;
  const d = s.dossier ?? {};
  const hidden = <><input type="hidden" name="id" value={id} /><input type="hidden" name="return" value={ret} /></>;
  return (
    <>
      <AdminNav msg={sp.msg} />
      <main className="wide stack">
        <h1 style={{ marginBottom: 0 }}>{s.name}</h1>
        <p className="muted">{s.category} · <a href={s.website} target="_blank" rel="noreferrer">{s.website}</a> · stage <strong>{s.stage}</strong> · score {s.total_score ?? "unscored"} · {s.entity_type}{s.opted_out ? " · OPTED OUT" : ""}</p>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <form method="post" action="/api/admin/sponsor-research">{hidden}<button className="btn ghost">Research public pages</button></form>
          <form method="post" action="/api/admin/sponsor-draft">{hidden}<button className="btn ghost">Generate dossier + drafts</button></form>
          <form method="post" action="/api/admin/sponsor-stage" style={{ display: "flex", gap: 6 }}>{hidden}
            <select name="stage" defaultValue={s.stage}>{STAGES.map((x) => <option key={x}>{x}</option>)}</select><button className="btn ghost">Move</button></form>
          <form method="post" action="/api/admin/sponsor-optout">{hidden}<button className="btn ghost">Opt out / never contact</button></form>
        </div>

        <section className="card stack">
          <h3 style={{ margin: 0 }}>Evidence (from their own public pages)</h3>
          {(s.evidence ?? []).length ? <ul>{s.evidence.map((e: any) => <li key={e.claim + e.url}>{e.claim}: <a href={e.url} target="_blank" rel="noreferrer">{e.url}</a></li>)}</ul> : <p className="muted">None yet. Run research or add notes.</p>}
          {d.site?.emailsSeen?.length ? <p className="small muted">Addresses published on their site: {d.site.emailsSeen.map((e: any) => `${e.email}${e.role ? "" : " (personal: avoid)"}`).join(", ")}</p> : null}
        </section>

        <form method="post" action="/api/admin/sponsor-scores" className="card stack">{hidden}
          <h3 style={{ margin: 0 }}>Score (0–5 each; a score without a reason doesn't count)</h3>
          {(Object.keys(DIMENSIONS) as Dimension[]).map((k) => (
            <div key={k} style={{ display: "grid", gridTemplateColumns: "minmax(140px,1fr) 70px 2fr 1.5fr", gap: 6, alignItems: "center" }}>
              <span className="small">{DIMENSIONS[k].label} ({DIMENSIONS[k].weight})</span>
              <input name={`score_${k}`} type="number" min={0} max={5} step={1} defaultValue={s.scores?.[k]?.score ?? ""} />
              <input name={`reason_${k}`} placeholder="reason" defaultValue={s.scores?.[k]?.reason ?? ""} />
              <input name={`url_${k}`} placeholder="evidence URL" defaultValue={s.scores?.[k]?.evidence_url ?? ""} />
            </div>
          ))}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 6 }}>
            <select name="entity_type" defaultValue={s.entity_type}><option value="unknown">Entity type unknown</option><option value="corporate">Company</option><option value="sole_trader">Sole trader / partnership</option></select>
            <input name="contact_email" placeholder="public business contact" defaultValue={s.public_contact_email ?? ""} />
            <input name="contact_source" placeholder="page where it's published" defaultValue={s.contact_source_url ?? ""} />
          </div>
          <button className="btn">Save score</button>
        </form>

        {d.overview && (
          <section className="card stack">
            <h3 style={{ margin: 0 }}>Dossier</h3>
            <p>{d.overview}</p>
            <strong>Why they fit</strong><ul>{(d.relevance ?? []).map((r: any) => <li key={r.point}>{r.point} (<a href={r.url}>source</a>)</li>)}</ul>
            <strong>Collaboration idea</strong><p>{d.collab_idea}</p>
            <strong>Deliverables</strong><ul>{(d.deliverables ?? []).map((x: string) => <li key={x}>{x}</li>)}</ul>
            <strong>Pricing framework</strong><ul>{(d.pricing ?? []).map((x: string) => <li key={x}>{x}</li>)}</ul>
            <strong>Negotiation</strong><ul>{(d.negotiation ?? []).map((x: string) => <li key={x}>{x}</li>)}</ul>
            <strong>Follow-ups</strong><ul>{(d.followups ?? []).map((x: any) => <li key={x.day}>Day {x.day}: {x.note}</li>)}</ul>
            {d.unknowns?.length ? <p className="small muted">Unknown: {d.unknowns.join("; ")}</p> : null}
          </section>
        )}

        {outreach.map((o) => (
          <section key={o.id} className="card stack">
            <h3 style={{ margin: 0 }}>{o.sequence === 0 ? "First email" : `Follow-up ${o.sequence}`} · {o.status}{o.approved_by ? ` (approved by ${o.approved_by})` : ""}{o.sent_at ? ` · sent ${new Date(o.sent_at).toLocaleString("en-GB")}` : ""}</h3>
            <p className="small muted">To: {o.to_address ?? "no public contact on file"}</p>
            {o.error && <p className="small" style={{ color: "var(--ember)" }}>Blocked: {o.error}</p>}
            {["draft", "approved"].includes(o.status) ? (
              <>
                <form method="post" action="/api/admin/outreach-approve" className="stack">
                  <input type="hidden" name="outreach_id" value={o.id} /><input type="hidden" name="return" value={ret} />
                  <input name="subject" defaultValue={o.subject} />
                  <textarea name="body" defaultValue={o.body} style={{ minHeight: 260 }} />
                  <button className="btn ghost">{o.status === "approved" ? "Save edits (stays approved)" : "Approve (does not send)"}</button>
                </form>
                {o.status === "approved" && <form method="post" action="/api/admin/outreach-send"><input type="hidden" name="outreach_id" value={o.id} /><input type="hidden" name="return" value={ret} /><button className="btn ember">Send now</button></form>}
              </>
            ) : <pre style={{ whiteSpace: "pre-wrap", fontFamily: "inherit" }}>{o.body}</pre>}
          </section>
        ))}

        <section className="card"><h3 style={{ marginTop: 0 }}>Timeline</h3>
          <ul className="small">{acts.map((a) => <li key={a.id}>{new Date(a.at).toLocaleString("en-GB")} · {a.title}{a.body ? ` — ${a.body}` : ""} <span className="muted">({a.actor})</span></li>)}</ul>
        </section>
      </main>
    </>
  );
}
