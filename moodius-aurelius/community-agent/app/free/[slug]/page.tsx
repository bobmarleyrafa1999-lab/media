import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { RESOURCES } from "../../../src/lib/resources";

export function generateStaticParams() { return Object.keys(RESOURCES).map((slug) => ({ slug })); }

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const r = RESOURCES[(await params).slug];
  return r ? { title: r.title, description: r.intro.slice(0, 150) } : {};
}

export default async function Resource({ params }: { params: Promise<{ slug: string }> }) {
  const r = RESOURCES[(await params).slug];
  if (!r) notFound();
  return (
    <main className="wrap prose">
      <p className="muted small" style={{ textTransform: "uppercase", letterSpacing: ".08em" }}>Moodius Aurelius · Free</p>
      <h1 style={{ fontSize: 32 }}>{r.title}</h1>
      <p>{r.intro}</p>
      {r.sections.map((s) => (
        <section key={s.h}>
          <h2 style={{ fontSize: 22 }}>{s.h}</h2>
          <ul>{s.items.map((i) => <li key={i}>{i}</li>)}</ul>
        </section>
      ))}
      {r.note && <p className="muted small">{r.note}</p>}
      <hr />
      <p>If this was useful, the newsletter goes deeper once a week. <a href={`/newsletter?src=free_${r.slug}`}>Read about it</a>; nothing is signed up automatically.</p>
    </main>
  );
}
