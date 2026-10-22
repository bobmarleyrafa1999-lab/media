import { requireAdmin } from "../../../src/lib/admin";
import { q } from "../../../src/lib/db";
import { STAGES } from "../../../src/lib/sponsors/crm";
import { AdminNav } from "../nav";

export const dynamic = "force-dynamic";

export default async function Sponsors({ searchParams }: { searchParams: Promise<{ msg?: string }> }) {
  await requireAdmin();
  const sp = await searchParams;
  const rows = await q<{ id: number; name: string; category: string; stage: string; total_score: string | null; opted_out: boolean }>(
    "SELECT id, name, category, stage, total_score, opted_out FROM sponsors ORDER BY total_score DESC NULLS LAST, name");
  const tasks = await q<{ id: number; sponsor_id: number; title: string; due_at: Date; name: string }>(
    "SELECT t.id, t.sponsor_id, t.title, t.due_at, s.name FROM sponsor_tasks t JOIN sponsors s ON s.id = t.sponsor_id WHERE NOT t.done ORDER BY t.due_at LIMIT 30");
  return (
    <>
      <AdminNav msg={sp.msg} />
      <main className="wide stack">
        <h2>Sponsorship pipeline</h2>
        <p className="muted small">Nothing is ever sent without your approval. Prospects start with no contact details; research reads only the brand's own public pages.</p>
        <div className="kanban">
          {STAGES.map((st) => (
            <div key={st} className="card" style={{ minHeight: 120 }}>
              <div className="small muted" style={{ textTransform: "uppercase", letterSpacing: ".06em" }}>{st} · {rows.filter((r) => r.stage === st).length}</div>
              {rows.filter((r) => r.stage === st).map((r) => (
                <a key={r.id} href={`/admin/sponsors/${r.id}`} style={{ display: "block", margin: "8px 0", color: "var(--fg)", textDecoration: r.opted_out ? "line-through" : "none" }}>
                  {r.name}<br /><span className="small muted">{r.category} · {r.total_score ?? "unscored"}</span>
                </a>
              ))}
            </div>
          ))}
        </div>
        <h2>Due tasks</h2>
        {tasks.length ? <table className="t"><tbody>{tasks.map((t) => (
          <tr key={t.id}><td>{new Date(t.due_at).toLocaleDateString("en-GB")}</td><td><a href={`/admin/sponsors/${t.sponsor_id}`}>{t.name}</a></td><td>{t.title}</td>
            <td><form method="post" action="/api/admin/task-done"><input type="hidden" name="task_id" value={t.id} /><input type="hidden" name="return" value="/admin/sponsors" /><button className="btn ghost">Done</button></form></td></tr>
        ))}</tbody></table> : <p className="muted">No open tasks.</p>}
        <h2>Add a prospect</h2>
        <form method="post" action="/api/admin/sponsor-add" className="card stack" style={{ maxWidth: 560 }}>
          <input type="hidden" name="return" value="/admin/sponsors" />
          <input name="name" placeholder="Company name" required />
          <input name="website" placeholder="https://brand.example" required />
          <select name="category" required defaultValue="">
            <option value="" disabled>Category</option>
            {["Stationery and journals", "Books and reading", "Educational products", "Mindfulness and meditation", "Productivity software", "Men's grooming and lifestyle", "Everyday accessories", "Professional development"].map((c) => <option key={c}>{c}</option>)}
          </select>
          <input name="country" placeholder="Country (e.g. UK)" />
          <select name="entity_type" defaultValue="unknown"><option value="unknown">Entity type unknown</option><option value="corporate">Company (Ltd / LLP / plc / Inc)</option><option value="sole_trader">Sole trader / partnership</option></select>
          <textarea name="notes" placeholder="Why them (optional)" />
          <button className="btn">Add</button>
        </form>
      </main>
    </>
  );
}
