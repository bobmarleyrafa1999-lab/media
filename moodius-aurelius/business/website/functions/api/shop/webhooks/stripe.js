// POST /api/shop/webhooks/stripe — Stripe sends checkout.session.completed,
// checkout.session.async_payment_succeeded and charge.refunded here.
import { config } from "../../../../src/config.js";
import { fulfil, refund } from "../../../../src/orders.js";
import * as stripe from "../../../../src/providers/stripe.js";
import { json, nowIso } from "../../../../src/util.js";

export async function onRequestPost({ request, env, waitUntil }) {
  const c = config(env);
  const raw = await request.text();
  if (!(await stripe.verifySignature(raw, request.headers.get("stripe-signature"), c.stripe.webhookSecret))) {
    return json({ ok: false, error: "bad signature" }, 400);
  }
  const event = JSON.parse(raw);
  const seen = await env.DB.prepare("SELECT 1 FROM webhook_events WHERE provider='stripe' AND event_id=?").bind(event.id).first();
  if (seen) return json({ ok: true, duplicate: true });

  const parsed = stripe.parseEvent(event);
  let result = { ignored: parsed.reason };
  if (parsed.type === "paid") {
    const { order, created } = await fulfil(c, env.DB, parsed.order, waitUntil);
    result = { order: order.id, created };
  } else if (parsed.type === "refund") {
    const r = await refund(c, env.DB, "stripe", parsed.paymentRef, waitUntil);
    result = { refunded: r.found ? r.order.id : null };
  }
  // Recorded only after processing succeeded, so a failed attempt is retried by Stripe.
  await env.DB.prepare("INSERT OR IGNORE INTO webhook_events (provider, event_id, received_at) VALUES ('stripe', ?, ?)").bind(event.id, nowIso()).run();
  return json({ ok: true, ...result });
}
