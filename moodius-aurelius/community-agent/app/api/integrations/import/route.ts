import { NextResponse, type NextRequest } from "next/server";
import { safeEqual, sha256, randomToken } from "../../../../src/lib/crypto";
import { q } from "../../../../src/lib/db";

export const dynamic = "force-dynamic";

// One-time import of the storefront's fallback tables (subscribers + clicks) collected before this
// service was live. Bearer IMPORT_TOKEN. Consent evidence is kept exactly as recorded there.
export async function POST(req: NextRequest) {
  const token = process.env.IMPORT_TOKEN ?? "";
  const auth = (req.headers.get("authorization") ?? "").replace(/^Bearer /, "");
  if (!token || !safeEqual(auth, token)) return NextResponse.json({ ok: false }, { status: 401 });
  const b = await req.json().catch(() => null) as { subscribers?: any[]; clicks?: any[] } | null;
  if (!b) return NextResponse.json({ ok: false, error: "bad json" }, { status: 400 });
  let subs = 0, clicks = 0;
  for (const s of b.subscribers ?? []) {
    if (!s?.email || !s?.consent_text || !s?.consent_version || !s?.consent_at) continue; // no consent evidence, no import
    const r = await q(
      `INSERT INTO subscribers (email, status, consent_text, consent_version, consent_at, source, confirmed_at, unsubscribed_at, ip_hash, unsubscribe_token_hash)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10) ON CONFLICT (lower(email)) DO NOTHING RETURNING id`,
      [String(s.email).toLowerCase(), ["pending", "confirmed", "unsubscribed"].includes(s.status) ? s.status : "pending", s.consent_text, s.consent_version,
       s.consent_at, s.source ?? "storefront_import", s.confirmed_at ?? null, s.unsubscribed_at ?? null, s.ip_hash ?? null, sha256(randomToken())]);
    subs += r.length;
  }
  for (const c of b.clicks ?? []) {
    if (!c?.slug || !c?.at) continue;
    await q("INSERT INTO conversion_events (kind, slug, src, at) VALUES ('link_click', $1, $2, $3)", [String(c.slug).slice(0, 60), c.src ? String(c.src).slice(0, 40) : null, c.at]);
    clicks++;
  }
  return NextResponse.json({ ok: true, subscribers: subs, clicks });
}
