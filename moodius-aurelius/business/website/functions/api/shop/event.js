// POST /api/shop/event  {kind:"page_view", slug, src}  — cookieless page counter.
// Stores kind, page slug, campaign source and time. No IP, user agent, cookie or id.
import { logEvent } from "../../../src/orders.js";

const PAGES = new Set(["home", "shop", "the-unexamined-self", "the-examined-life-bundle", "guide", "links", "about", "thank-you", "orders"]);

export async function onRequestPost({ request, env }) {
  const body = await request.json().catch(() => null);
  if (body?.kind === "page_view" && PAGES.has(body.slug)) await logEvent(env.DB, "page_view", body.slug, body.src);
  return new Response(null, { status: 204 });
}
