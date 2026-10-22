import { requireAdmin } from "../../src/lib/admin";
import { overview, recommendations, themes } from "../../src/lib/analytics";
import { currentMode, killSwitchOn } from "../../src/lib/policy";
import { config } from "../../src/lib/config";
import { AdminNav, money, pct } from "./nav";

export const dynamic = "force-dynamic";

function Stat({ n, l }: { n: React.ReactNode; l: string }) {
  return <div className="card stat"><div className="n">{n}</div><div className="l">{l}</div></div>;
}

export default async function Overview({ searchParams }: { searchParams: Promise<{ msg?: string; days?: string }> }) {
  await requireAdmin();
  const sp = await searchParams;
  const days = Math.min(365, Math.max(1, Number(sp.days ?? 30)));
  const [o, t, recs, mode, kill] = await Promise.all([overview(days), themes(days), recommendations(days), currentMode(), killSwitchOn()]);
  const c = config();
  const na = (v: number | null, f: (x: number) => string = String) => (v == null ? <span className="muted">n/a</span> : f(v));
  return (
    <>
      <AdminNav msg={sp.msg} />
      <main className="wide stack">
        <p className="muted small">
          Last {days} days · mode <strong>{mode.replace("_", " ")}</strong>{kill ? " · KILL SWITCH ON" : ""} ·
          Instagram {c.meta.mock ? "mock data" : "live"} · Claude {c.claude.mock ? "offline heuristic" : c.claude.model} · email {c.email.mock ? "log only" : "Resend"} ·
          <a href="?days=7"> 7d</a> <a href="?days=30">30d</a> <a href="?days=90">90d</a>
        </p>
        <h2>Comments</h2>
        <div className="grid">
          <Stat n={o.comments.received} l="received" />
          <Stat n={o.comments.answered} l={`answered (${o.comments.autoAnswered} auto)`} />
          <Stat n={o.comments.waiting} l="waiting for you" />
          <Stat n={na(o.comments.medianDelayMin, (x) => `${x} min`)} l="median response delay" />
          <Stat n={o.comments.conversations} l="conversations started" />
          <Stat n={o.comments.crisis} l="flagged crisis" />
        </div>
        <h2>Newsletter funnel</h2>
        <div className="grid">
          <Stat n={o.funnel.keywordComments} l="keyword comments" />
          <Stat n={o.funnel.dmsSent} l="DMs sent" />
          <Stat n={o.funnel.linkClicks} l="link clicks" />
          <Stat n={o.funnel.signupsConfirmed} l="signups confirmed" />
          <Stat n={o.subscribers.confirmed} l="subscribers (all time)" />
          <Stat n={pct(o.funnel.linkClicks ? o.funnel.signupsConfirmed / o.funnel.linkClicks : null)} l="click → signup" />
        </div>
        <h2>Sponsorship & revenue</h2>
        <div className="grid">
          <Stat n={Object.values(o.sponsors.byStage).reduce((a, b) => a + b, 0)} l="prospects identified" />
          <Stat n={o.sponsors.contacted} l="contacted" />
          <Stat n={pct(o.sponsors.replyRate)} l="reply rate" />
          <Stat n={`${o.money.negotiating} / ${o.money.dealsSigned}`} l="negotiating / signed" />
          <Stat n={money(o.money.revenueCents)} l="revenue" />
          <Stat n={na(o.money.revenuePer1kViews, (x) => `£${x.toFixed(2)}`)} l="revenue per 1,000 views" />
        </div>
        <h2>Which themes start real conversations</h2>
        <div className="card" style={{ overflowX: "auto" }}>
          <table className="t">
            <thead><tr><th>Theme</th><th>Posts</th><th>Comments</th><th>Substantive</th><th>Questions</th><th>Disagreements</th><th>Stories</th><th>Keyword asks</th><th>Saves / reach</th><th>Shares / reach</th></tr></thead>
            <tbody>{t.map((r) => (
              <tr key={r.category}><td>{r.category}</td><td>{r.posts}</td><td>{r.comments}</td><td>{r.substantive}</td><td>{r.questions}</td><td>{r.disagreements}</td><td>{r.stories}</td><td>{r.keyword}</td>
                <td>{r.reach ? pct(Number(r.saves) / Number(r.reach)) : <span className="muted">not measured</span>}</td>
                <td>{r.reach ? pct(Number(r.shares) / Number(r.reach)) : <span className="muted">not measured</span>}</td></tr>
            ))}</tbody>
          </table>
        </div>
        <h2>What to make next</h2>
        <ul>{recs.map((r) => <li key={r}>{r}</li>)}</ul>
      </main>
    </>
  );
}
