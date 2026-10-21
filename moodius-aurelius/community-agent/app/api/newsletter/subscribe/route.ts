import { NextResponse, type NextRequest } from "next/server";
import { config } from "../../../../src/lib/config";
import { subscribe } from "../../../../src/lib/newsletter";
import { allow, clientIp } from "../../../../src/lib/ratelimit";

export const dynamic = "force-dynamic";

// Accepts the HTML form (redirects back) or JSON from the storefront (returns JSON).
export async function POST(req: NextRequest) {
  const ip = clientIp(req.headers);
  const isJson = (req.headers.get("content-type") ?? "").includes("application/json");
  let email = "", consent = false, source: string | null = null, leadMagnet: string | null = null, honeypot = "";
  if (isJson) {
    const b = await req.json().catch(() => ({}));
    email = String(b.email ?? ""); consent = b.consent === true; source = b.source ? String(b.source) : null; leadMagnet = b.lead_magnet ? String(b.lead_magnet) : null;
  } else {
    const f = await req.formData();
    email = String(f.get("email") ?? ""); consent = f.get("consent") === "yes"; source = f.get("source") ? String(f.get("source")) : null;
    leadMagnet = f.get("lead_magnet") ? String(f.get("lead_magnet")) : null; honeypot = String(f.get("website") ?? "");
  }
  source = source ? source.toLowerCase().replace(/[^a-z0-9_\-]/g, "").slice(0, 40) : null;
  const back = (params: Record<string, string>) => {
    const u = new URL("/newsletter", config().baseUrl);
    for (const [k, v] of Object.entries(params)) u.searchParams.set(k, v);
    if (source) u.searchParams.set("src", source);
    return NextResponse.redirect(u, 303);
  };
  if (!allow(`sub:${ip}`, 5)) return isJson ? NextResponse.json({ ok: false, error: "Too many attempts, try again in a minute." }, { status: 429 }) : back({ error: "Too many attempts, try again in a minute." });
  if (honeypot) return isJson ? NextResponse.json({ ok: true, status: "pending" }) : back({ status: "check" }); // quietly drop bots
  const r = await subscribe({ email, consent, source, ip, leadMagnet });
  if (isJson) return NextResponse.json(r, { status: r.ok ? 200 : 400 });
  if (!r.ok) return back({ error: r.error });
  return back({ status: r.status === "already_confirmed" ? "already" : "check" });
}
