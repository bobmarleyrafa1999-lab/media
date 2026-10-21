import type { Metadata } from "next";
import { q } from "../../src/lib/db";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Links", description: "Essays, free reflection tools and the Moodius Aurelius newsletter." };

interface Link { slug: string; label: string; kind: string; disclosure: string | null }

const GROUPS: [string, string[]][] = [
  ["Read and reflect", ["newsletter", "resource"]],
  ["Shop", ["product", "membership"]],
  ["Things I use and recommend", ["affiliate", "sponsor"]],
];

export default async function LinksPage() {
  const links = await q<Link>("SELECT slug, label, kind, disclosure FROM links WHERE active AND position < 1000 ORDER BY position, slug").catch(() => [] as Link[]);
  return (
    <main className="wrap">
      <header style={{ textAlign: "center", marginBottom: 28 }}>
        <div aria-hidden style={{ width: 64, height: 64, borderRadius: 99, margin: "0 auto 12px", background: "var(--slate)", color: "var(--bone)", display: "grid", placeItems: "center", fontFamily: "var(--serif)", fontSize: 26 }}>M</div>
        <h1 style={{ margin: 0, fontSize: 26 }}>Moodius Aurelius</h1>
        <p className="muted" style={{ margin: "6px 0 0" }}>Stoicism for people who feel things. An anonymous journal on philosophy, psychology and the inner life.</p>
      </header>
      {GROUPS.map(([title, kinds]) => {
        const items = links.filter((l) => kinds.includes(l.kind));
        if (!items.length) return null;
        return (
          <section key={title} style={{ marginBottom: 26 }}>
            <h2 className="muted" style={{ fontFamily: "var(--sans)", fontSize: 12, textTransform: "uppercase", letterSpacing: ".08em", margin: "0 0 10px" }}>{title}</h2>
            <div className="stack">
              {items.map((l) => (
                <a key={l.slug} className="linkbtn" href={`/r/${l.slug}?src=link_bio`} rel={l.kind === "affiliate" || l.kind === "sponsor" ? "sponsored noopener" : "noopener"}>
                  {l.label}
                  {l.disclosure ? <span className="sub">{l.disclosure}</span> : null}
                </a>
              ))}
            </div>
          </section>
        );
      })}
      {!links.length && <p className="muted" style={{ textAlign: "center" }}>Links are being set up.</p>}
      <footer className="muted small" style={{ textAlign: "center", marginTop: 36 }}>
        No cookies, no trackers. Clicks are counted on this server without storing who you are. <a href="/privacy-newsletter">Privacy</a>
      </footer>
    </main>
  );
}
