import { requireAdmin } from "../../../src/lib/admin";
import { linkClicks, overview, revenueByStream } from "../../../src/lib/analytics";
import { q } from "../../../src/lib/db";
import { AdminNav, money, pct } from "../nav";

export const dynamic = "force-dynamic";

const STREAMS: [string, string][] = [["affiliate", "A. Affiliate"], ["sponsorship", "B. Sponsored content"], ["substack_paid", "C. Paid newsletter"], ["digital_product", "D. Journals, workbooks, ebooks"], ["membership", "E. Subscriptions / membership"], ["other", "Other"]];

export default async function Revenue({ searchParams }: { searchParams: Promise<{ msg?: string }> }) {
  await requireAdmin();
  const sp = await searchParams;
  const [byStream, clicks, o, entries, expenses, links] = await Promise.all([
    revenueByStream(90), linkClicks(30), overview(30),
    q<any>("SELECT * FROM revenue_entries ORDER BY occurred_on DESC, id DESC LIMIT 30"),
    q<any>("SELECT * FROM expenses ORDER BY occurred_on DESC, id DESC LIMIT 30"),
    q<any>("SELECT * FROM links ORDER BY position, slug"),
  ]);
  const totalRev = byStream.reduce((a, r) => a + Number(r.cents), 0);
  const ret = "/admin/revenue";
  const today = new Date().toISOString().slice(0, 10);
  return (
    <>
      <AdminNav msg={sp.msg} />
      <main className="wide stack">
        <h2>Revenue by path (90 days)</h2>
        <div className="grid">
          {STREAMS.map(([k, l]) => <div key={k} className="card stat"><div className="n">{money(byStream.find((r) => r.stream === k)?.cents ?? 0)}</div><div className="l">{l}</div></div>)}
          <div className="card stat"><div className="n">{money(totalRev)}</div><div className="l">total</div></div>
          <div className="card stat"><div className="n">{money(o.money.expensesCents)}</div><div className="l">expenses (30d)</div></div>
        </div>
        <h2>Links and conversions (30 days)</h2>
        <table className="t"><thead><tr><th>Link</th><th>Path</th><th>Clicks</th><th>Signups</th><th>Rate</th></tr></thead>
          <tbody>{clicks.map((c) => <tr key={c.slug}><td>{c.label} <span className="muted small">/r/{c.slug}</span></td><td>{c.kind}</td><td>{c.clicks}</td><td>{c.signups}</td><td>{pct(Number(c.clicks) ? Number(c.signups) / Number(c.clicks) : null)}</td></tr>)}</tbody></table>
        <div style={{ display: "grid", gap: 16, gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))" }}>
          <form method="post" action="/api/admin/revenue" className="card stack"><input type="hidden" name="return" value={ret} />
            <h3 style={{ margin: 0 }}>Add revenue</h3>
            <select name="stream">{STREAMS.map(([k, l]) => <option key={k} value={k}>{l}</option>)}</select>
            <input name="amount" placeholder="Amount, e.g. 14.00" required inputMode="decimal" />
            <input name="currency" defaultValue="GBP" />
            <input name="date" type="date" defaultValue={today} required />
            <input name="note" placeholder="Note (e.g. Bookshop.org October payout)" />
            <button className="btn">Add</button>
          </form>
          <form method="post" action="/api/admin/expense" className="card stack"><input type="hidden" name="return" value={ret} />
            <h3 style={{ margin: 0 }}>Add expense</h3>
            <input name="item" placeholder="e.g. Metricool Starter" required />
            <input name="amount" placeholder="Amount" required inputMode="decimal" />
            <input name="currency" defaultValue="GBP" />
            <input name="date" type="date" defaultValue={today} required />
            <label className="check"><input type="checkbox" name="recurring" /> monthly</label>
            <button className="btn">Add</button>
          </form>
        </div>
        <h3>Recent entries</h3>
        <table className="t"><tbody>
          {entries.map((e) => <tr key={`r${e.id}`}><td>{new Date(e.occurred_on).toLocaleDateString("en-GB")}</td><td>{e.stream}</td><td>{money(e.amount_cents)} {e.currency}</td><td className="small muted">{e.source} {e.note}</td></tr>)}
          {expenses.map((e) => <tr key={`e${e.id}`}><td>{new Date(e.occurred_on).toLocaleDateString("en-GB")}</td><td>expense</td><td>−{money(e.amount_cents)} {e.currency}</td><td className="small muted">{e.item}{e.recurring ? " (monthly)" : ""}</td></tr>)}
        </tbody></table>
        <h2>Link-in-bio editor</h2>
        <p className="small muted">Kinds map to the five money paths. Affiliate and sponsor links must carry a disclosure.</p>
        <table className="t"><tbody>{links.map((l) => <tr key={l.slug}><td>{l.position}</td><td>{l.label}</td><td className="small">/r/{l.slug} → {l.destination}</td><td>{l.kind}</td><td>{l.active ? "on" : "off"}</td></tr>)}</tbody></table>
        <form method="post" action="/api/admin/link" className="card stack" style={{ maxWidth: 560 }}><input type="hidden" name="return" value={ret} />
          <input name="slug" placeholder="slug (e.g. bookshop-meditations)" required />
          <input name="label" placeholder="Button text" required />
          <input name="destination" placeholder="https://… or /path on the public site" required />
          <select name="kind">{["newsletter", "resource", "product", "membership", "affiliate", "sponsor"].map((k) => <option key={k}>{k}</option>)}</select>
          <input name="disclosure" placeholder="Disclosure (required for affiliate/sponsor), e.g. Affiliate link: I earn a small commission" />
          <input name="position" type="number" defaultValue={100} />
          <select name="active" defaultValue="1"><option value="1">active</option><option value="0">hidden</option></select>
          <button className="btn">Save link</button>
        </form>
        <form method="post" action="/api/admin/export-subscribers"><button className="btn ghost">Export confirmed subscribers (CSV for Substack import)</button></form>
      </main>
    </>
  );
}
