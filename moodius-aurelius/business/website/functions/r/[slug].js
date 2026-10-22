// /r/<slug>?src=<source> — fallback short links (proxied to the community agent once it's live).
// Logs one cookieless link_click (slug, src, time) and redirects.
import { config } from "../../src/config.js";
import { resolveLink } from "../../src/links.js";
import { logEvent } from "../../src/orders.js";
import { cleanSlug, cleanSrc } from "../../src/util.js";

export async function onRequestGet({ request, env, params, waitUntil }) {
  const c = config(env);
  const slug = cleanSlug(params.slug);
  const src = cleanSrc(new URL(request.url).searchParams.get("src"));
  const dest = slug && resolveLink(c, slug, src);
  if (!dest) return Response.redirect(`${c.siteUrl}/`, 302);
  waitUntil(logEvent(env.DB, "link_click", slug, src));
  return new Response(null, { status: 302, headers: { location: dest, "cache-control": "no-store", "referrer-policy": "strict-origin-when-cross-origin" } });
}
