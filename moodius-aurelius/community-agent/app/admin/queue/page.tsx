import { requireAdmin } from "../../../src/lib/admin";
import { q } from "../../../src/lib/db";
import { commentPermalink } from "../../../src/lib/meta/graph";
import { AdminNav } from "../nav";

export const dynamic = "force-dynamic";

interface Row {
  comment_id: string; username: string | null; text: string; status: string; intent: string | null; sentiment: string | null; topic: string | null;
  priority: number | null; risk: string | null; flags: string[]; draft_reply: string | null; final_reply: string | null; decision_reason: string | null;
  dm_keyword: string | null; dm_status: string | null; received_at: Date; caption: string | null; permalink: string | null; published_by: string | null;
}

const FILTERS: Record<string, string[]> = {
  waiting: ["needs_approval", "escalated"], published: ["published"], skipped: ["skipped", "rejected"], all: ["new", "needs_approval", "escalated", "approved", "published", "rejected", "skipped", "error"],
};

export default async function Queue({ searchParams }: { searchParams: Promise<{ f?: string; focus?: string; msg?: string }> }) {
  await requireAdmin();
  const sp = await searchParams;
  const f = FILTERS[sp.f ?? "waiting"] ? sp.f ?? "waiting" : "waiting";
  const rows = await q<Row>(
    `SELECT c.*, m.caption, m.permalink FROM comments c LEFT JOIN media m ON m.media_id = c.media_id
      WHERE c.status = ANY($1) ${sp.focus ? "OR c.comment_id = $2" : ""}
      ORDER BY (c.comment_id = $2) DESC, c.priority DESC NULLS LAST, c.received_at DESC LIMIT 100`,
    [FILTERS[f], sp.focus ?? ""]);
  const ret = `/admin/queue?f=${f}`;
  return (
    <>
      <AdminNav msg={sp.msg} />
      <main className="wide stack">
        <p className="small">{Object.keys(FILTERS).map((k) => <a key={k} href={`?f=${k}`} style={{ marginRight: 12, fontWeight: k === f ? 600 : 400 }}>{k}</a>)}</p>
        {!rows.length && <p className="muted">Nothing here.</p>}
        {rows.map((r) => (
          <article key={r.comment_id} className="card stack" id={r.comment_id} style={r.intent === "crisis" ? { borderColor: "var(--ember)" } : undefined}>
            <div className="small muted">
              <span className={`pill ${r.risk === "high" ? "high" : ""}`}>{r.intent ?? "unclassified"}</span>{" "}
              priority {r.priority ?? "–"} · {r.sentiment} · {r.topic} · {r.status}{r.published_by ? ` by ${r.published_by}` : ""} · {new Date(r.received_at).toLocaleString("en-GB")}
            </div>
            <div><strong>@{r.username}</strong>: {r.text}</div>
            <div className="small muted">On: {(r.caption ?? "").slice(0, 140)}{r.permalink && <> · <a href={r.permalink} target="_blank" rel="noreferrer">post</a> · <a href={commentPermalink(r.permalink, r.comment_id)!} target="_blank" rel="noreferrer">comment</a></>}</div>
            {r.intent === "crisis" && <div className="small" style={{ color: "var(--ember)" }}>Possible risk to this person. Answer personally; consider pointing to local help (UK Samaritans 116 123, or findahelpline.com). Nothing was posted.</div>}
            {r.flags?.length ? <div className="small muted">Flags: {r.flags.join(", ")}</div> : null}
            {r.decision_reason && <div className="small muted">Why not automatic: {r.decision_reason}</div>}
            {["needs_approval", "escalated", "approved", "error"].includes(r.status) ? (
              <>
                <form method="post" action="/api/admin/approve" className="stack">
                  <input type="hidden" name="comment_id" value={r.comment_id} /><input type="hidden" name="return" value={ret} />
                  <textarea name="text" defaultValue={r.final_reply ?? r.draft_reply ?? ""} maxLength={2200} aria-label="Reply" />
                  <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                    <button className="btn" type="submit">Approve and publish</button>
                  </div>
                </form>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                  <form method="post" action="/api/admin/manual"><input type="hidden" name="comment_id" value={r.comment_id} /><input type="hidden" name="return" value={ret} /><button className="btn ghost">I replied on Instagram</button></form>
                  <form method="post" action="/api/admin/reject"><input type="hidden" name="comment_id" value={r.comment_id} /><input type="hidden" name="return" value={ret} /><button className="btn ghost">No reply needed</button></form>
                  {r.dm_keyword && !r.dm_status && (
                    <form method="post" action="/api/admin/dm"><input type="hidden" name="comment_id" value={r.comment_id} /><input type="hidden" name="keyword" value={r.dm_keyword} /><input type="hidden" name="return" value={ret} /><button className="btn ember">Send {r.dm_keyword} DM</button></form>
                  )}
                </div>
              </>
            ) : r.final_reply ? <div className="small">Reply: {r.final_reply}</div> : null}
            {r.dm_status && <div className="small muted">DM: {r.dm_status}</div>}
          </article>
        ))}
      </main>
    </>
  );
}
