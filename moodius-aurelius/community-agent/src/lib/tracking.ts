import { q, one } from "./db";

// First-party, cookieless funnel tracking. No IP address or user agent is stored.
export async function trackEvent(kind: string, f: { slug?: string; src?: string; ref?: string; valueCents?: number } = {}) {
  await q("INSERT INTO conversion_events (kind, slug, src, ref, value_cents) VALUES ($1,$2,$3,$4,$5)", [
    kind, f.slug ?? null, f.src?.slice(0, 60) ?? null, f.ref?.slice(0, 120) ?? null, f.valueCents ?? null,
  ]);
}

export async function resolveLink(slug: string) {
  return one<{ slug: string; destination: string; kind: string }>(
    "SELECT slug, destination, kind FROM links WHERE slug = $1 AND active", [slug]);
}

export function cleanSrc(src: string | null): string | null {
  if (!src) return null;
  const s = src.toLowerCase().replace(/[^a-z0-9_\-]/g, "").slice(0, 40);
  return s || null;
}
