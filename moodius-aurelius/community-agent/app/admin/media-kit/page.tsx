import { requireAdmin } from "../../../src/lib/admin";
import { mediaKitMetrics } from "../../../src/lib/analytics";
import { config } from "../../../src/lib/config";
import { AdminNav, pct } from "../nav";

export const dynamic = "force-dynamic";

// Media kit: every number comes from the API or our own database. Anything unmeasured says so.
// No demographics, testimonials or "affluent audience" claims unless Instagram's own audience
// insights back them (not collected by this version).
export default async function MediaKit() {
  await requireAdmin();
  const m = await mediaKitMetrics();
  const v = (x: number | null, f: (n: number) => string = (n) => n.toLocaleString("en-GB")) => (x == null ? <span className="muted">not yet measured</span> : f(x));
  return (
    <>
      <AdminNav />
      <main className="wrap prose">
        <p className="muted small">Print or save as PDF from your browser. Numbers update live from measured data.</p>
        <h1>Moodius Aurelius</h1>
        <p><em>Stoicism for people who feel things.</em> An anonymous editorial journal on Instagram and email about Stoicism, psychology, emotional intelligence, relationships and identity. Written slowly, cited properly.</p>
        <h2>Measured audience (last 90 days)</h2>
        <table className="t"><tbody>
          <tr><td>Posts with insights</td><td>{m.postsMeasured || <span className="muted">not yet measured</span>}</td></tr>
          <tr><td>Median reach per post</td><td>{v(m.medianReach)}</td></tr>
          <tr><td>Median views per post</td><td>{v(m.medianViews)}</td></tr>
          <tr><td>Saves per reach</td><td>{v(m.savesPerReach, (n) => pct(n))}</td></tr>
          <tr><td>Shares per reach</td><td>{v(m.sharesPerReach, (n) => pct(n))}</td></tr>
          <tr><td>Newsletter subscribers (double opt-in)</td><td>{m.newsletterSubscribers.toLocaleString("en-GB")}</td></tr>
          <tr><td>Substantive comments</td><td>{m.substantiveComments90d.toLocaleString("en-GB")}</td></tr>
        </tbody></table>
        <p className="small muted">Source: Instagram Graph API media insights and our own subscriber records{m.since ? `, posts since ${new Date(m.since).toLocaleDateString("en-GB")}` : ""}. Audience demographics are not included: they are only shown once Instagram's audience insights are connected, and never estimated.</p>
        <h2>Formats</h2>
        <ul>
          <li>Reflective carousel (7 slides), labelled Paid partnership</li>
          <li>Text-led reel (7–20 s), restrained motion, original audio</li>
          <li>Story set with link sticker</li>
          <li>Newsletter mention inside a weekly essay (when the list is large enough to matter)</li>
        </ul>
        <h2>How we work</h2>
        <ul>
          <li>Only products we can honestly recommend. Brands approve facts; we keep the voice.</li>
          <li>Every paid post is disclosed (#ad / Paid partnership), per ASA and CMA guidance.</li>
          <li>Results reported with the same API numbers shown here.</li>
        </ul>
        <p>Contact: {config().outreach.replyTo || <span className="muted">set OUTREACH_REPLY_TO</span>}</p>
      </main>
    </>
  );
}
