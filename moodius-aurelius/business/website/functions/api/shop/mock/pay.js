// POST /api/shop/mock/pay — the fake card form on /mock-checkout/ posts here.
// Builds a Stripe-shaped checkout.session.completed and runs the real fulfilment code.
// Disabled unless PAYMENT_PROVIDER=mock and ALLOW_MOCK_PAYMENTS=true (never in production).
import { config, paymentGuard } from "../../../../src/config.js";
import { getProduct } from "../../../../src/catalog.js";
import { fulfil } from "../../../../src/orders.js";
import * as stripe from "../../../../src/providers/stripe.js";
import { json, normalizeEmail, randomId } from "../../../../src/util.js";

export async function onRequestPost({ request, env, waitUntil }) {
  const c = config(env);
  if (c.provider !== "mock" || paymentGuard(c)) return json({ ok: false, error: "mock payments disabled" }, 404);
  const isJson = (request.headers.get("content-type") || "").includes("application/json");
  const input = isJson ? await request.json().catch(() => ({})) : Object.fromEntries(await request.formData());
  const checkout = await env.DB.prepare("SELECT * FROM checkouts WHERE id = ?").bind(input.ref || "").first();
  const email = normalizeEmail(input.email);
  if (!checkout || !email) return json({ ok: false, error: "unknown checkout or bad email" }, 400);
  const product = getProduct(checkout.product_slug);
  const session = {
    id: `cs_mock_${randomId("x").slice(2)}`,
    object: "checkout.session",
    payment_status: "paid",
    payment_intent: `pi_mock_${randomId("x").slice(2)}`,
    amount_total: product.amountCents,
    currency: product.currency.toLowerCase(),
    customer_details: { email, name: input.name || null },
    client_reference_id: checkout.id,
    metadata: { checkout_id: checkout.id, product: product.slug, src: checkout.src || "" },
    livemode: false,
  };
  const order = { ...stripe.sessionToOrder(session), provider: "mock" };
  const { order: saved } = await fulfil(c, env.DB, order, waitUntil);
  return isJson ? json({ ok: true, order: saved.id, payment_ref: saved.payment_ref }) : Response.redirect(`${c.siteUrl}/thank-you/?ref=${checkout.id}`, 303);
}
