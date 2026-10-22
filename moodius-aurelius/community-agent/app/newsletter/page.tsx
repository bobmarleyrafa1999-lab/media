import type { Metadata } from "next";
import { CONSENT_TEXT } from "../../src/lib/newsletter";
import { config } from "../../src/lib/config";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "The newsletter", description: "One considered essay a week on Stoicism, psychology and the inner life." };

export default async function Newsletter({ searchParams }: { searchParams: Promise<Record<string, string | undefined>> }) {
  const sp = await searchParams;
  const src = (sp.src ?? "newsletter_page").replace(/[^a-z0-9_\-]/gi, "").slice(0, 40);
  const lm = (sp.lm ?? "").replace(/[^a-z0-9\-]/gi, "").slice(0, 60);
  return (
    <main className="wrap">
      <p className="muted small" style={{ textTransform: "uppercase", letterSpacing: ".08em" }}>Moodius Aurelius · Newsletter</p>
      <h1 style={{ fontSize: 34, margin: "8px 0 12px" }}>Fewer, better thoughts.</h1>
      <p style={{ fontSize: 18 }}>One essay a week on the quiet problems: the 2am argument in your head, the trait you can't stand in other people, the loneliness of being fine. Stoicism, Jung and modern psychology, read slowly and cited properly.</p>
      <ul className="muted">
        <li>About one email a week. No daily blasts.</li>
        <li>Every quotation sourced; research labelled as research, opinion as opinion.</li>
        <li>Unsubscribe with one click, any time.</li>
      </ul>
      {sp.status === "check" && <div className="card" role="status"><strong>Check your inbox.</strong> Click the link in the email to confirm. Nothing is sent until you do.</div>}
      {sp.status === "already" && <div className="card" role="status">You're already subscribed. Thank you.</div>}
      {sp.error && <div className="card" role="alert" style={{ borderColor: "var(--ember)" }}>{sp.error}</div>}
      <form method="post" action="/api/newsletter/subscribe" className="card stack" style={{ marginTop: 18 }}>
        <input type="hidden" name="source" value={src} />
        {lm && <input type="hidden" name="lead_magnet" value={lm} />}
        <label htmlFor="email" className="small muted">Email</label>
        <input id="email" name="email" type="email" required autoComplete="email" placeholder="you@example.com" />
        <label className="check"><input type="checkbox" name="consent" value="yes" required /> <span>{CONSENT_TEXT}</span></label>
        <div style={{ position: "absolute", left: -9999 }} aria-hidden><label>Leave empty<input name="website" tabIndex={-1} autoComplete="off" /></label></div>
        <button className="btn ember" type="submit">Subscribe</button>
        <p className="muted small" style={{ margin: 0 }}>
          We'll send one confirmation email first. Your address is stored on our own server and, once confirmed, imported into our newsletter platform (Substack) to deliver the essays. <a href="/privacy-newsletter">Privacy notice</a>.
        </p>
      </form>
      <p className="muted small" style={{ marginTop: 24 }}>Prefer to read first? <a href={`/r/substack?src=${src}`}>Browse the essays</a>{config().newsletter.substackUrl ? "" : ""}.</p>
    </main>
  );
}
