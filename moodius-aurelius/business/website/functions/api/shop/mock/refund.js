// POST /api/shop/mock/refund {payment_ref} — test-only refund, mirrors charge.refunded.
import { config, paymentGuard } from "../../../../src/config.js";
import { refund } from "../../../../src/orders.js";
import { json } from "../../../../src/util.js";

export async function onRequestPost({ request, env, waitUntil }) {
  const c = config(env);
  if (c.provider !== "mock" || paymentGuard(c)) return json({ ok: false, error: "mock payments disabled" }, 404);
  const { payment_ref } = await request.json().catch(() => ({}));
  const r = await refund(c, env.DB, "mock", payment_ref, waitUntil);
  return json({ ok: r.found, order: r.order?.id || null, changed: r.changed || false });
}
