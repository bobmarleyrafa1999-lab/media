// Stripe Checkout over the REST API (no SDK, so it runs on Workers without Node shims).
// Default: Managed Payments on, which makes Stripe the merchant of record (Stripe collects
// and remits UK VAT / EU VAT, handles disputes and receipts). STRIPE_MANAGED_PAYMENTS=false
// switches to plain Stripe, where Surafel is the seller of record and owns VAT.

import { hmacSha256Hex, safeEqual } from "../util.js";

// Flattens {a:{b:[{c:1}]}} into a=..., a[b][0][c]=1 form fields, the way Stripe expects.
export function formEncode(obj, prefix = "", out = new URLSearchParams()) {
  for (const [k, v] of Object.entries(obj)) {
    if (v === undefined || v === null) continue;
    const key = prefix ? `${prefix}[${k}]` : k;
    if (typeof v === "object") formEncode(v, key, out);
    else out.append(key, String(v));
  }
  return out;
}

async function stripeFetch(c, method, path, params) {
  const res = await fetch(`${c.stripe.apiBase}${path}`, {
    method,
    headers: {
      authorization: `Bearer ${c.stripe.secretKey}`,
      "stripe-version": c.stripe.apiVersion,
      ...(params ? { "content-type": "application/x-www-form-urlencoded" } : {}),
    },
    body: params ? formEncode(params).toString() : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(`Stripe ${method} ${path} failed (${res.status}): ${data?.error?.message || "unknown error"}`);
  return data;
}

export function checkoutParams(c, { product, checkoutId, src }) {
  const priceId = c.raw[product.stripePriceEnv];
  const lineItem = priceId
    ? { price: priceId, quantity: 1 }
    : {
        quantity: 1,
        price_data: {
          currency: product.currency.toLowerCase(),
          unit_amount: product.amountCents,
          tax_behavior: "inclusive",
          product_data: { name: product.name, description: product.subtitle, tax_code: product.stripeTaxCode },
        },
      };
  const params = {
    mode: "payment",
    line_items: [lineItem],
    client_reference_id: checkoutId,
    success_url: `${c.siteUrl}/thank-you/?ref=${checkoutId}`,
    cancel_url: `${c.siteUrl}/shop/${product.slug}/?cancelled=1`,
    metadata: { checkout_id: checkoutId, product: product.slug, src: src || "" },
  };
  if (c.stripe.managedPayments) {
    params.managed_payments = { enabled: true };
  } else if (c.raw.STRIPE_AUTOMATIC_TAX === "true") {
    params.automatic_tax = { enabled: true };
  }
  if (c.raw.STRIPE_TOS_CONSENT === "true") {
    // Needs a Terms URL saved in the Stripe Dashboard (Settings > Public details).
    params.consent_collection = { terms_of_service: "required" };
  }
  return params;
}

export async function createCheckout(c, args) {
  const session = await stripeFetch(c, "POST", "/v1/checkout/sessions", checkoutParams(c, args));
  return { url: session.url, providerRef: session.id };
}

export const retrieveSession = (c, id) => stripeFetch(c, "GET", `/v1/checkout/sessions/${encodeURIComponent(id)}`);

// Stripe-Signature: t=<ts>,v1=<hex hmac of "<ts>.<raw body>">[,v1=...]
export async function verifySignature(rawBody, header, secret, toleranceSec = 300, nowSec = Math.floor(Date.now() / 1000)) {
  if (!header || !secret) return false;
  const parts = header.split(",").map((p) => p.trim().split("="));
  const t = parts.find(([k]) => k === "t")?.[1];
  const sigs = parts.filter(([k]) => k === "v1").map(([, v]) => v);
  if (!t || !sigs.length || Math.abs(nowSec - Number(t)) > toleranceSec) return false;
  const expected = await hmacSha256Hex(secret, `${t}.${rawBody}`);
  return sigs.some((s) => safeEqual(s, expected));
}

export async function signPayload(rawBody, secret, t = Math.floor(Date.now() / 1000)) {
  return `t=${t},v1=${await hmacSha256Hex(secret, `${t}.${rawBody}`)}`;
}

export function sessionToOrder(session) {
  return {
    provider: "stripe",
    providerRef: session.id,
    paymentRef: typeof session.payment_intent === "string" ? session.payment_intent : session.payment_intent?.id || null,
    amountCents: session.amount_total,
    currency: String(session.currency || "gbp").toUpperCase(),
    email: session.customer_details?.email || session.customer_email || "",
    name: session.customer_details?.name || null,
    checkoutId: session.client_reference_id || session.metadata?.checkout_id || null,
    productSlug: session.metadata?.product || null,
    src: session.metadata?.src || null,
    testMode: !session.livemode,
  };
}

// Turns a verified Stripe event into one of: {type:"paid", order}, {type:"refund", paymentRef}, {type:"ignore"}.
export function parseEvent(event) {
  const obj = event?.data?.object || {};
  switch (event?.type) {
    case "checkout.session.completed":
      return obj.payment_status === "paid" ? { type: "paid", order: sessionToOrder(obj) } : { type: "ignore", reason: "awaiting async payment" };
    case "checkout.session.async_payment_succeeded":
      return { type: "paid", order: sessionToOrder(obj) };
    case "charge.refunded":
      return obj.refunded ? { type: "refund", paymentRef: obj.payment_intent, testMode: !event.livemode } : { type: "ignore", reason: "partial refund" };
    default:
      return { type: "ignore", reason: `unhandled ${event?.type}` };
  }
}
