// POST /api/newsletter/subscribe {email, consent:true, source, lead_magnet}
// Fallback while the community agent isn't deployed (the middleware proxies to it once it is).
import { config } from "../../../src/config.js";
import { subscribe } from "../../../src/newsletter.js";
import { json } from "../../../src/util.js";

export async function onRequestPost({ request, env }) {
  const c = config(env);
  const isJson = (request.headers.get("content-type") || "").includes("application/json");
  const input = isJson ? await request.json().catch(() => ({})) : Object.fromEntries(await request.formData());
  if (input.website) return json({ ok: true, pending: true }); // honeypot
  const consent = input.consent === true || input.consent === "on" || input.consent === "true";
  const r = await subscribe(c, env.DB, {
    email: input.email,
    consent,
    source: input.source || "site",
    leadMagnet: input.lead_magnet,
    ip: request.headers.get("cf-connecting-ip"),
  });
  if (isJson) return json(r.body, r.status);
  const back = new URL(request.headers.get("referer") || `${c.siteUrl}/guide/`);
  back.searchParams.set(r.body.ok ? "sent" : "error", r.body.ok ? "1" : r.body.error);
  return Response.redirect(back.toString(), 303);
}
