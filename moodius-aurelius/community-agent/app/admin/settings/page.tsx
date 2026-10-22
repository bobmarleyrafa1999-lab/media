import { requireAdmin } from "../../../src/lib/admin";
import { config } from "../../../src/lib/config";
import { q } from "../../../src/lib/db";
import { currentMode, killSwitchOn } from "../../../src/lib/policy";
import { health } from "../../../src/lib/jobs";
import { AdminNav } from "../nav";

export const dynamic = "force-dynamic";

export default async function Settings({ searchParams }: { searchParams: Promise<{ msg?: string }> }) {
  await requireAdmin();
  const sp = await searchParams;
  const [mode, kill, h, mails, jobs] = await Promise.all([
    currentMode(), killSwitchOn(), health(),
    q<any>("SELECT kind, to_address, subject, status, created_at FROM email_log ORDER BY id DESC LIMIT 15"),
    q<any>("SELECT kind, status, attempts, last_error, updated_at FROM jobs WHERE status = 'failed' ORDER BY id DESC LIMIT 10"),
  ]);
  const a = config().agent;
  const ret = "/admin/settings";
  return (
    <>
      <AdminNav msg={sp.msg} />
      <main className="wide stack">
        <h2>Reply mode</h2>
        <form method="post" action="/api/admin/mode" className="card stack" style={{ maxWidth: 640 }}><input type="hidden" name="return" value={ret} />
          {[
            ["draft_only", "A. Draft only", "Nothing is published without your click. Default; keep it until you've reviewed at least 100 drafts."],
            ["assisted", "B. Assisted", `Auto-publishes only: ${a.assistedCategories.join(", ")}; confidence ≥ ${a.minConfidence}; max ${a.maxAutoPerHour}/hour, ${a.maxAutoPerDay}/day.`],
            ["controlled", "C. Controlled automatic", `Auto-publishes: ${a.controlledCategories.join(", ")}; same caps. Crisis, sensitive, commercial, sponsorship and criticism always come to you.`],
          ].map(([v, l, d]) => (
            <label key={v} className="check"><input type="radio" name="mode" value={v} defaultChecked={mode === v} /> <span><strong>{l}</strong><br /><span className="small muted">{d}</span></span></label>
          ))}
          <button className="btn">Save mode</button>
        </form>
        <form method="post" action="/api/admin/kill" className="card" style={{ maxWidth: 640 }}><input type="hidden" name="return" value={ret} /><input type="hidden" name="on" value={kill ? "0" : "1"} />
          <strong>Kill switch is {kill ? "ON: no automatic replies" : "off"}.</strong> <button className="btn ghost" style={{ marginLeft: 8 }}>{kill ? "Turn off" : "Turn on"}</button>
        </form>
        <h2>Integrations</h2>
        <pre className="card small" style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(h, null, 2)}</pre>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {["poll-comments", "process-queue", "sync-insights", "daily-digest", "weekly-report", "refresh-token", "retention", "sponsor-followups", "subscribe-webhooks"].map((j) => (
            <form key={j} method="post" action="/api/admin/run-job"><input type="hidden" name="job" value={j} /><input type="hidden" name="return" value={ret} /><button className="btn ghost">Run {j}</button></form>
          ))}
        </div>
        <h2>Failed jobs</h2>
        {jobs.length ? <table className="t"><tbody>{jobs.map((j, i) => <tr key={i}><td>{j.kind}</td><td>{j.attempts}</td><td className="small">{j.last_error}</td></tr>)}</tbody></table> : <p className="muted">None.</p>}
        <h2>Recent emails</h2>
        <table className="t"><tbody>{mails.map((m, i) => <tr key={i}><td className="small">{new Date(m.created_at).toLocaleString("en-GB")}</td><td>{m.kind}</td><td>{m.status}</td><td className="small">{m.subject}</td></tr>)}</tbody></table>
        <h2>Privacy tools</h2>
        <form method="post" action="/api/admin/erase-subscriber" className="card stack" style={{ maxWidth: 560 }}><input type="hidden" name="return" value={ret} />
          <input name="email" type="email" placeholder="Subscriber email to erase completely" required /><button className="btn ghost">Erase subscriber</button></form>
        <form method="post" action="/api/admin/suppress" className="card stack" style={{ maxWidth: 560 }}><input type="hidden" name="return" value={ret} />
          <input name="entry" placeholder="email or domain never to contact" required /><input name="reason" placeholder="reason" /><button className="btn ghost">Add to suppression list</button></form>
      </main>
    </>
  );
}
