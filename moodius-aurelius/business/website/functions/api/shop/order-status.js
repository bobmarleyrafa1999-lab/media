// GET /api/shop/order-status?ref=chk_...  — polled by the thank-you page.
// If the webhook hasn't arrived yet, asks Stripe directly and fulfils (idempotently).
import { config } from "../../../src/config.js";
import { claimByCheckout, fulfil } from "../../../src/orders.js";
import * as stripe from "../../../src/providers/stripe.js";
import { json } from "../../../src/util.js";

export async function onRequestGet({ request, env, waitUntil }) {
  const c = config(env);
  const ref = new URL(request.url).searchParams.get("ref") || "";
  if (!/^chk_[a-z0-9]{16}$/.test(ref)) return json({ status: "unknown" }, 404);
  let result = await claimByCheckout(c, env.DB, ref);
  if (result.status === "pending" && result.checkout.provider === "stripe" && c.stripe.secretKey && result.checkout.provider_ref) {
    const session = await stripe.retrieveSession(c, result.checkout.provider_ref).catch(() => null);
    if (session?.payment_status === "paid") {
      await fulfil(c, env.DB, stripe.sessionToOrder(session), waitUntil);
      result = await claimByCheckout(c, env.DB, ref);
    }
  }
  delete result.checkout;
  return json(result, result.status === "unknown" ? 404 : 200);
}
