// POST /api/shop/webhooks/lemonsqueezy — order_created and order_refunded.
import { config } from "../../../../src/config.js";
import { fulfil, refund } from "../../../../src/orders.js";
import * as ls from "../../../../src/providers/lemonsqueezy.js";
import { json, nowIso, sha256Hex } from "../../../../src/util.js";

export async function onRequestPost({ request, env, waitUntil }) {
  const c = config(env);
  const raw = await request.text();
  if (!(await ls.verifySignature(raw, request.headers.get("x-signature"), c.lemonsqueezy.webhookSecret))) {
    return json({ ok: false, error: "bad signature" }, 400);
  }
  const payload = JSON.parse(raw);
  // Lemon Squeezy has no event id header; the body hash identifies a delivery.
  const eventId = `${payload?.meta?.event_name}:${payload?.data?.id}:${(await sha256Hex(raw)).slice(0, 16)}`;
  const seen = await env.DB.prepare("SELECT 1 FROM webhook_events WHERE provider='lemonsqueezy' AND event_id=?").bind(eventId).first();
  if (seen) return json({ ok: true, duplicate: true });
  const parsed = ls.parseEvent(payload);
  let result = { ignored: parsed.reason };
  if (parsed.type === "paid") {
    const { order, created } = await fulfil(c, env.DB, parsed.order, waitUntil);
    result = { order: order.id, created };
  } else if (parsed.type === "refund") {
    const r = await refund(c, env.DB, "lemonsqueezy", parsed.paymentRef, waitUntil);
    result = { refunded: r.found ? r.order.id : null };
  }
  await env.DB.prepare("INSERT OR IGNORE INTO webhook_events (provider, event_id, received_at) VALUES ('lemonsqueezy', ?, ?)").bind(eventId, nowIso()).run();
  return json({ ok: true, ...result });
}
