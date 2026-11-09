// POST /api/shop/resend-links  {email}  — "Find my order". Always answers the same way.
import { config } from "../../../src/config.js";
import { resendLinks } from "../../../src/orders.js";
import { json, normalizeEmail } from "../../../src/util.js";

export async function onRequestPost({ request, env }) {
  const c = config(env);
  const isJson = (request.headers.get("content-type") || "").includes("application/json");
  const input = isJson ? await request.json().catch(() => ({})) : Object.fromEntries(await request.formData());
  const email = normalizeEmail(input.email);
  if (email && !input.website) await resendLinks(c, env.DB, email);
  const message = "If that address has orders, fresh download links are on their way. Check your spam folder too.";
  return isJson ? json({ ok: true, message }) : Response.redirect(`${c.siteUrl}/orders/?sent=1`, 303);
}
