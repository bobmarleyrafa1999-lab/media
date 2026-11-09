// Lemon Squeezy (merchant of record) as the fallback provider, e.g. if Stripe declines
// Managed Payments at its eligibility review. Same order flow: our checkout id travels in
// custom data, the order_created webhook fulfils, our own /download links deliver.

import { hmacSha256Hex, safeEqual } from "../util.js";

export async function createCheckout(c, { product, checkoutId, src, email }) {
  const variantId = c.raw[product.lemonVariantEnv];
  if (!variantId) throw new Error(`${product.lemonVariantEnv} is not set`);
  const body = {
    data: {
      type: "checkouts",
      attributes: {
        checkout_data: { ...(email ? { email } : {}), custom: { checkout_id: checkoutId, product: product.slug, src: src || "" } },
        product_options: { redirect_url: `${c.siteUrl}/thank-you/?ref=${checkoutId}` },
        test_mode: !c.liveMode,
      },
      relationships: {
        store: { data: { type: "stores", id: String(c.lemonsqueezy.storeId) } },
        variant: { data: { type: "variants", id: String(variantId) } },
      },
    },
  };
  const res = await fetch(`${c.lemonsqueezy.apiBase}/v1/checkouts`, {
    method: "POST",
    headers: {
      authorization: `Bearer ${c.lemonsqueezy.apiKey}`,
      accept: "application/vnd.api+json",
      "content-type": "application/vnd.api+json",
    },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(`Lemon Squeezy checkout failed (${res.status}): ${data?.errors?.[0]?.detail || "unknown error"}`);
  return { url: data.data.attributes.url, providerRef: data.data.id };
}

// X-Signature: hex HMAC-SHA256 of the raw body with the webhook signing secret.
export async function verifySignature(rawBody, header, secret) {
  if (!header || !secret) return false;
  return safeEqual(header.trim(), await hmacSha256Hex(secret, rawBody));
}

export function parseEvent(payload) {
  const name = payload?.meta?.event_name;
  const custom = payload?.meta?.custom_data || {};
  const a = payload?.data?.attributes || {};
  const ref = String(payload?.data?.id || "");
  if (name === "order_created" && a.status === "paid") {
    return {
      type: "paid",
      order: {
        provider: "lemonsqueezy",
        providerRef: ref,
        paymentRef: ref,
        amountCents: a.total,
        currency: String(a.currency || "GBP").toUpperCase(),
        email: a.user_email || "",
        name: a.user_name || null,
        checkoutId: custom.checkout_id || null,
        productSlug: custom.product || null,
        src: custom.src || null,
        testMode: Boolean(a.test_mode),
      },
    };
  }
  if (name === "order_refunded") return { type: "refund", paymentRef: ref, testMode: Boolean(a.test_mode) };
  return { type: "ignore", reason: `unhandled ${name}` };
}
