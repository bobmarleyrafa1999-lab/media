// The order lifecycle: start a checkout, fulfil a paid order exactly once, mint
// expiring download links, handle refunds. Provider-specific code only parses events;
// everything here is shared by Stripe, Lemon Squeezy and the mock provider.

import { getProduct, formatMoney } from "./catalog.js";
import { sendEmail } from "./email.js";
import { forwardRevenue } from "./revenue.js";
import * as stripe from "./providers/stripe.js";
import * as lemonsqueezy from "./providers/lemonsqueezy.js";
import { addDays, cleanSrc, nowIso, randomId, randomToken, sha256Hex } from "./util.js";

export async function logEvent(db, kind, slug, src) {
  await db.prepare("INSERT INTO conversion_events (kind, slug, src, at) VALUES (?,?,?,?)").bind(kind, slug || null, cleanSrc(src), nowIso()).run();
}

export async function startCheckout(c, db, { productSlug, src, email, digitalConsent }) {
  const product = getProduct(productSlug);
  if (!product) throw Object.assign(new Error("Unknown product"), { status: 404 });
  if (product.status !== "available") throw Object.assign(new Error("This product is not on sale yet"), { status: 409 });
  if (!digitalConsent) throw Object.assign(new Error("Please confirm you want immediate access to the download"), { status: 400 });

  const checkoutId = randomId("chk");
  const at = nowIso();
  await db
    .prepare("INSERT INTO checkouts (id, product_slug, provider, src, digital_consent_at, created_at) VALUES (?,?,?,?,?,?)")
    .bind(checkoutId, product.slug, c.provider, cleanSrc(src), at, at)
    .run();

  let result;
  if (c.provider === "stripe") result = await stripe.createCheckout(c, { product, checkoutId, src: cleanSrc(src) });
  else if (c.provider === "lemonsqueezy") result = await lemonsqueezy.createCheckout(c, { product, checkoutId, src: cleanSrc(src), email });
  else result = { url: `${c.siteUrl}/mock-checkout/?ref=${checkoutId}`, providerRef: `mock_${checkoutId}` };

  await db.prepare("UPDATE checkouts SET provider_ref = ? WHERE id = ?").bind(result.providerRef, checkoutId).run();
  await logEvent(db, "checkout_started", product.slug, src);
  return { checkoutId, url: result.url };
}

export async function mintDownloadToken(c, db, orderId) {
  const token = randomToken();
  const at = nowIso();
  await db
    .prepare("INSERT INTO download_tokens (token_hash, order_id, created_at, expires_at, max_uses) VALUES (?,?,?,?,?)")
    .bind(await sha256Hex(token), orderId, at, addDays(at, c.downloadTtlDays), c.downloadMaxUses)
    .run();
  return token;
}

// One page per token. GET only shows the page; the files themselves need a POST from
// its buttons, so email link scanners that prefetch URLs can't use up the downloads.
export const downloadPageUrl = (c, token) => `${c.siteUrl}/download/${token}`;

export const getOrder = (db, id) => db.prepare("SELECT * FROM orders WHERE id = ?").bind(id).first();

async function sendPurchaseEmail(c, db, order) {
  const product = getProduct(order.product_slug);
  const token = await mintDownloadToken(c, db, order.id);
  const text = [
    `Thank you for buying ${product.name}.`,
    "",
    `Your downloads (${product.files.map((f) => f.label).join(" and ")}):`,
    downloadPageUrl(c, token),
    "",
    `The page allows ${c.downloadMaxUses} downloads and expires in ${c.downloadTtlDays} days. Save the PDFs somewhere you will find them again.`,
    `Lost the links later? Request fresh ones at ${c.siteUrl}/orders/ with this email address.`,
    "",
    `Order ${order.id} · ${formatMoney(order.amount_cents, order.currency)}${order.test_mode ? " · TEST ORDER, no money taken" : ""}`,
    order.provider === "stripe" ? "Your receipt comes separately from Stripe, which processes the payment as the seller of record." : "",
    "",
    "Start with Day 1 on a quiet evening. Ten minutes is enough.",
    "",
    "Moodius",
  ].join("\n");
  return sendEmail(c, db, { to: order.email, subject: `Your copy of ${product.name}`, text, kind: "purchase" });
}

// Idempotent: a second webhook (or the thank-you page racing the webhook) for the same
// provider reference returns the existing order and sends nothing.
export async function fulfil(c, db, input, waitUntil = (p) => p) {
  const existing = await db.prepare("SELECT * FROM orders WHERE provider = ? AND provider_ref = ?").bind(input.provider, input.providerRef).first();
  if (existing) return { order: existing, created: false };

  const checkout = input.checkoutId ? await db.prepare("SELECT * FROM checkouts WHERE id = ?").bind(input.checkoutId).first() : null;
  const productSlug = checkout?.product_slug || input.productSlug;
  const product = getProduct(productSlug);
  if (!product) throw new Error(`Paid event for unknown product "${productSlug}" (${input.provider} ${input.providerRef})`);
  if (!input.email) throw new Error(`Paid event without an email (${input.provider} ${input.providerRef})`);

  const order = {
    id: randomId("ord", 12),
    checkout_id: checkout?.id || null,
    provider: input.provider,
    provider_ref: input.providerRef,
    payment_ref: input.paymentRef || null,
    product_slug: product.slug,
    amount_cents: Number.isFinite(input.amountCents) ? input.amountCents : product.amountCents,
    currency: input.currency || product.currency,
    email: input.email.trim().toLowerCase(),
    name: input.name || null,
    status: "paid",
    src: cleanSrc(checkout?.src || input.src),
    test_mode: input.testMode ? 1 : 0,
    created_at: nowIso(),
  };
  const res = await db
    .prepare(
      `INSERT OR IGNORE INTO orders (id, checkout_id, provider, provider_ref, payment_ref, product_slug, amount_cents, currency, email, name, status, src, test_mode, created_at)
       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)`,
    )
    .bind(order.id, order.checkout_id, order.provider, order.provider_ref, order.payment_ref, order.product_slug, order.amount_cents, order.currency, order.email, order.name, order.status, order.src, order.test_mode, order.created_at)
    .run();
  if (!res.meta?.changes) {
    // Lost a race with a concurrent delivery of the same event.
    const winner = await db.prepare("SELECT * FROM orders WHERE provider = ? AND provider_ref = ?").bind(input.provider, input.providerRef).first();
    return { order: winner, created: false };
  }
  await logEvent(db, "purchase", order.product_slug, order.src);
  await sendPurchaseEmail(c, db, order);
  waitUntil(forwardRevenue(c, db, order, "order.paid"));
  return { order, created: true };
}

export async function refund(c, db, provider, paymentRef, waitUntil = (p) => p) {
  const order = await db.prepare("SELECT * FROM orders WHERE provider = ? AND payment_ref = ?").bind(provider, paymentRef).first();
  if (!order) return { found: false };
  if (order.status === "refunded") return { found: true, order, changed: false };
  const at = nowIso();
  await db.prepare("UPDATE orders SET status = 'refunded', refunded_at = ? WHERE id = ?").bind(at, order.id).run();
  await db.prepare("UPDATE download_tokens SET expires_at = ? WHERE order_id = ?").bind(at, order.id).run();
  const updated = { ...order, status: "refunded", refunded_at: at };
  waitUntil(forwardRevenue(c, db, updated, "order.refunded"));
  return { found: true, order: updated, changed: true };
}

// The thank-you page asks for its order by checkout reference. Each successful call
// mints a fresh link (the stored hash can't be turned back into the emailed one),
// capped at PAGE_CLAIM_LIMIT so a leaked thank-you URL can't hand out unlimited links.
export async function claimByCheckout(c, db, checkoutId) {
  const checkout = await db.prepare("SELECT * FROM checkouts WHERE id = ?").bind(checkoutId).first();
  if (!checkout) return { status: "unknown" };
  const order = await db.prepare("SELECT * FROM orders WHERE checkout_id = ? ORDER BY created_at LIMIT 1").bind(checkoutId).first();
  if (!order) return { status: "pending", checkout };
  const product = getProduct(order.product_slug);
  const base = { status: order.status, orderId: order.id, product: product.name, email: maskEmail(order.email), testMode: Boolean(order.test_mode) };
  if (order.status !== "paid") return base;
  if (order.page_claims >= c.pageClaimLimit) return { ...base, note: "Your download link is in your email." };
  await db.prepare("UPDATE orders SET page_claims = page_claims + 1 WHERE id = ?").bind(order.id).run();
  const token = await mintDownloadToken(c, db, order.id);
  return { ...base, downloadUrl: downloadPageUrl(c, token), files: product.files.map((f) => f.label) };
}

export function maskEmail(email) {
  const [u, d] = String(email).split("@");
  if (!d) return "";
  return `${u.slice(0, 2)}${"•".repeat(Math.max(1, Math.min(6, u.length - 2)))}@${d}`;
}

// "Lost your link?" Sends fresh links for every paid order on that address. The
// response never says whether the address had orders.
export async function resendLinks(c, db, email) {
  const { results } = await db.prepare("SELECT * FROM orders WHERE email = ? AND status = 'paid' ORDER BY created_at DESC LIMIT 10").bind(email).all();
  if (!results.length) return 0;
  const recent = await db
    .prepare("SELECT COUNT(*) AS n FROM outbox WHERE to_addr = ? AND kind = 'resend' AND created_at > ?")
    .bind(email, new Date(Date.now() - 3600000).toISOString())
    .first();
  if ((recent?.n || 0) >= 3) return 0; // at most three resends an hour per address
  const blocks = [];
  for (const o of results) {
    const product = getProduct(o.product_slug);
    const token = await mintDownloadToken(c, db, o.id);
    blocks.push(`${product.name} (order ${o.id}):\n${downloadPageUrl(c, token)}`);
  }
  await sendEmail(c, db, {
    to: email,
    subject: "Your Moodius Aurelius downloads",
    text: `Here are fresh download links for your purchases.\n\n${blocks.join("\n\n")}\n\nEach page allows ${c.downloadMaxUses} downloads and expires in ${c.downloadTtlDays} days. If you didn't ask for this, you can ignore it.\n\nMoodius`,
    kind: "resend",
  });
  return results.length;
}
