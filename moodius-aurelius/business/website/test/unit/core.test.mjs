// Unit tests for the pure parts of the shop: signatures, Stripe params, event parsing,
// attribution cleaning, payment guards, revenue payloads. Run: npm test
import { test } from "node:test";
import assert from "node:assert/strict";
import * as stripe from "../../src/providers/stripe.js";
import * as ls from "../../src/providers/lemonsqueezy.js";
import { config, paymentGuard } from "../../src/config.js";
import { cleanSrc, normalizeEmail, safeEqual, hmacSha256Hex, randomId, randomToken } from "../../src/util.js";
import { maskEmail } from "../../src/orders.js";
import { revenueEvent } from "../../src/revenue.js";
import { resolveLink } from "../../src/links.js";
import { getProduct } from "../../src/catalog.js";
import { isAgentPath } from "../../functions/_middleware.js";

test("Stripe signature: valid, tampered, stale, wrong secret", async () => {
  const body = JSON.stringify({ id: "evt_1", type: "checkout.session.completed" });
  const header = await stripe.signPayload(body, "whsec_x");
  assert.equal(await stripe.verifySignature(body, header, "whsec_x"), true);
  assert.equal(await stripe.verifySignature(body + " ", header, "whsec_x"), false);
  assert.equal(await stripe.verifySignature(body, header, "whsec_y"), false);
  const old = await stripe.signPayload(body, "whsec_x", Math.floor(Date.now() / 1000) - 3600);
  assert.equal(await stripe.verifySignature(body, old, "whsec_x"), false);
  assert.equal(await stripe.verifySignature(body, null, "whsec_x"), false);
});

test("Stripe signature matches Stripe's documented scheme (HMAC-SHA256 of t.payload)", async () => {
  const t = 1700000000;
  const sig = await hmacSha256Hex("secret", `${t}.payload`);
  assert.equal(await stripe.verifySignature("payload", `t=${t},v1=${sig}`, "secret", 300, t + 10), true);
  assert.equal(await stripe.verifySignature("payload", `t=${t},v0=abc,v1=${sig}`, "secret", 300, t + 10), true);
});

test("Lemon Squeezy signature", async () => {
  const body = '{"meta":{"event_name":"order_created"}}';
  const sig = await hmacSha256Hex("ls_secret", body);
  assert.equal(await ls.verifySignature(body, sig, "ls_secret"), true);
  assert.equal(await ls.verifySignature(body, sig, "other"), false);
});

test("Stripe checkout params: Managed Payments on by default, tax-inclusive inline price", () => {
  const c = config({ PAYMENT_PROVIDER: "stripe", STRIPE_SECRET_KEY: "sk_test_1", SITE_URL: "https://shop.test" });
  const p = stripe.checkoutParams(c, { product: getProduct("the-unexamined-self"), checkoutId: "chk_abc", src: "reel_r012" });
  assert.deepEqual(p.managed_payments, { enabled: true });
  assert.equal(p.automatic_tax, undefined, "automatic_tax must not be sent with Managed Payments");
  assert.equal(p.line_items[0].price_data.unit_amount, 1400);
  assert.equal(p.line_items[0].price_data.currency, "gbp");
  assert.equal(p.line_items[0].price_data.tax_behavior, "inclusive");
  assert.equal(p.line_items[0].price_data.product_data.tax_code, "txcd_10302000");
  assert.equal(p.client_reference_id, "chk_abc");
  assert.equal(p.metadata.src, "reel_r012");
  assert.equal(p.success_url, "https://shop.test/thank-you/?ref=chk_abc");
  const form = stripe.formEncode(p).toString();
  assert.match(form, /managed_payments%5Benabled%5D=true/);
  assert.match(form, /line_items%5B0%5D%5Bprice_data%5D%5Bproduct_data%5D%5Btax_code%5D=txcd_10302000/);
});

test("Stripe checkout params: direct mode and Dashboard price override", () => {
  const c = config({ STRIPE_MANAGED_PAYMENTS: "false", STRIPE_AUTOMATIC_TAX: "true", STRIPE_PRICE_THE_UNEXAMINED_SELF: "price_123" });
  const p = stripe.checkoutParams(c, { product: getProduct("the-unexamined-self"), checkoutId: "chk_x" });
  assert.equal(p.managed_payments, undefined);
  assert.deepEqual(p.automatic_tax, { enabled: true });
  assert.deepEqual(p.line_items[0], { price: "price_123", quantity: 1 });
});

test("Stripe events are normalised", () => {
  const session = { id: "cs_1", payment_status: "paid", payment_intent: "pi_1", amount_total: 1400, currency: "gbp", customer_details: { email: "a@b.co", name: "A" }, client_reference_id: "chk_1", metadata: { product: "the-unexamined-self", src: "x" }, livemode: false };
  const paid = stripe.parseEvent({ type: "checkout.session.completed", data: { object: session } });
  assert.equal(paid.type, "paid");
  assert.equal(paid.order.paymentRef, "pi_1");
  assert.equal(paid.order.currency, "GBP");
  assert.equal(paid.order.testMode, true);
  assert.equal(stripe.parseEvent({ type: "checkout.session.completed", data: { object: { ...session, payment_status: "unpaid" } } }).type, "ignore");
  assert.equal(stripe.parseEvent({ type: "charge.refunded", data: { object: { refunded: true, payment_intent: "pi_1" } } }).type, "refund");
  assert.equal(stripe.parseEvent({ type: "charge.refunded", data: { object: { refunded: false } } }).type, "ignore");
  assert.equal(stripe.parseEvent({ type: "invoice.paid", data: { object: {} } }).type, "ignore");
});

test("Lemon Squeezy events are normalised", () => {
  const p = ls.parseEvent({ meta: { event_name: "order_created", custom_data: { checkout_id: "chk_1", src: "dm_journal" } }, data: { id: 99, attributes: { status: "paid", total: 1400, currency: "GBP", user_email: "a@b.co", test_mode: true } } });
  assert.equal(p.type, "paid");
  assert.equal(p.order.providerRef, "99");
  assert.equal(p.order.checkoutId, "chk_1");
  assert.equal(ls.parseEvent({ meta: { event_name: "order_refunded" }, data: { id: 99, attributes: {} } }).type, "refund");
});

test("payment guard refuses live keys without LIVE_MODE, and mock in production", () => {
  assert.match(paymentGuard(config({ PAYMENT_PROVIDER: "stripe", STRIPE_SECRET_KEY: "sk_live_x" })), /LIVE_MODE/);
  assert.equal(paymentGuard(config({ PAYMENT_PROVIDER: "stripe", STRIPE_SECRET_KEY: "sk_live_x", LIVE_MODE: "true" })), null);
  assert.match(paymentGuard(config({ PAYMENT_PROVIDER: "stripe", STRIPE_SECRET_KEY: "sk_test_x", LIVE_MODE: "true" })), /test key/);
  assert.match(paymentGuard(config({ PAYMENT_PROVIDER: "mock" })), /disabled/);
  assert.match(paymentGuard(config({ PAYMENT_PROVIDER: "mock", ALLOW_MOCK_PAYMENTS: "true", LIVE_MODE: "true" })), /cannot run/);
  assert.equal(paymentGuard(config({ PAYMENT_PROVIDER: "mock", ALLOW_MOCK_PAYMENTS: "true" })), null);
  assert.match(paymentGuard(config({ PAYMENT_PROVIDER: "stripe" })), /not set/);
});

test("attribution and email cleaning", () => {
  assert.equal(cleanSrc("Reel_R012"), "reel_r012");
  assert.equal(cleanSrc("<script>"), "script");
  assert.equal(cleanSrc("a".repeat(60)).length, 40);
  assert.equal(cleanSrc(""), null);
  assert.equal(normalizeEmail(" A@Example.COM "), "a@example.com");
  assert.equal(normalizeEmail("nope"), null);
  assert.equal(maskEmail("buyer@example.com"), "bu•••@example.com");
});

test("ids and tokens are unguessable shapes", () => {
  assert.match(randomId("chk"), /^chk_[a-z2-9]{16}$/);
  assert.match(randomToken(), /^[A-Za-z0-9_-]{43}$/);
  assert.notEqual(randomToken(), randomToken());
  assert.equal(safeEqual("abc", "abc"), true);
  assert.equal(safeEqual("abc", "abd"), false);
  assert.equal(safeEqual("abc", "abcd"), false);
});

test("revenue event follows the community-agent contract", () => {
  const order = { id: "ord_1", amount_cents: 1400, currency: "GBP", created_at: "2026-10-22T10:00:00Z", product_slug: "the-unexamined-self", src: "reel_r012" };
  assert.deepEqual(revenueEvent(order, "order.paid"), { id: "ord_1", event: "order.paid", stream: "digital_product", amount_cents: 1400, currency: "GBP", occurred_at: "2026-10-22T10:00:00Z", product: "the-unexamined-self", src: "reel_r012" });
  const r = revenueEvent({ ...order, refunded_at: "2026-10-23T00:00:00Z" }, "order.refunded");
  assert.equal(r.id, "ord_1_refund");
  assert.equal(r.amount_cents, 1400, "refunds are sent as positive amounts");
});

test("short links keep src on our pages only", () => {
  const c = config({ SITE_URL: "https://shop.test" });
  assert.equal(resolveLink(c, "shop", "reel_r012"), "https://shop.test/shop/the-unexamined-self/?src=reel_r012");
  assert.equal(resolveLink(c, "instagram", "x"), "https://www.instagram.com/moodiusaurelius/");
  assert.equal(resolveLink(c, "nope", "x"), null);
});

test("one-domain proxy covers exactly the community agent's paths", () => {
  for (const p of ["/r/shop", "/links", "/newsletter", "/newsletter/confirm", "/free/x", "/api/newsletter/subscribe", "/api/integrations/revenue", "/api/admin/x", "/admin", "/_agent/a.js", "/privacy-newsletter"]) assert.equal(isAgentPath(p), true, p);
  for (const p of ["/", "/shop/", "/api/shop/checkout", "/api/shop/admin/orders", "/download/x", "/guide/", "/downloads/free/seven-day-reflection-guide.pdf", "/linksy"]) assert.equal(isAgentPath(p), false, p);
});

test("personalisation choices are cleaned and checked", async () => {
  const { cleanPersonal, describePersonal } = await import("../../src/personal.js");
  const p = cleanPersonal({ p_name: "  Amara \n Okafor ", p_monogram: "a.o", p_highlight: "Manifesto", p_start_date: "2026-11-02" }, "personal");
  assert.deepEqual(p, { name: "Amara Okafor", monogram: "AO", accent: "ember", cover: "dark", highlight: "manifesto", start_date: "2026-11-02" });
  assert.match(describePersonal(p), /Feel everything/);
  assert.throws(() => cleanPersonal({}, "personal"), /name/);
  assert.throws(() => cleanPersonal({ p_name: "A", p_accent: "gold" }, "personal"), /accent/);
  assert.throws(() => cleanPersonal({ p_name: "A", p_start_date: "2026-13-40" }, "personal"), /date/);
  assert.throws(() => cleanPersonal({ p_name: "A" }, "gift"), /your name/);
  assert.throws(() => cleanPersonal({ p_name: "A", p_from_name: "B", p_send_date: "2026-01-01" }, "gift", "2026-10-22"), /past/);
  assert.throws(() => cleanPersonal({ p_name: "A", p_from_name: "B", p_recipient_email: "nope" }, "gift"), /email/);
  const g = cleanPersonal({ p_name: "Leo", p_from_name: "Sam", p_recipient_email: "Leo@Example.com" }, "gift");
  assert.equal(g.recipient_email, "leo@example.com");
  assert.equal(getProduct("the-unexamined-self-personal").amountCents, 1900);
  assert.equal(getProduct("the-unexamined-self-gift").amountCents, 2200);
});
