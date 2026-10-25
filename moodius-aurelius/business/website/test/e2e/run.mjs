// End-to-end test: runs the real site on Cloudflare's local runtime (wrangler pages dev,
// local D1 + R2) and walks every money path with sample orders. No real credentials.
//
//   npm run build && npm run test:e2e
//
// Phase A (community agent not deployed): mock purchase -> download, Stripe-signed and
// Lemon Squeezy-signed webhooks, idempotency, refunds, download limits, "find my order",
// fallback newsletter double opt-in, fallback /r/ links, funnel + export, admin auth.
// Phase B (COMMUNITY_AGENT_URL set): one-domain proxy and signed revenue events, checked by
// a stand-in agent that verifies X-Moodius-Signature exactly as the contract specifies.

import { spawn, execFileSync } from "node:child_process";
import { createServer } from "node:http";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { createHmac } from "node:crypto";
import assert from "node:assert/strict";

const root = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const wrangler = join(root, "node_modules", ".bin", "wrangler");
const STRIPE_SECRET = "whsec_e2e_secret";
const LS_SECRET = "ls_e2e_secret";
const REVENUE_SECRET = "rev_e2e_secret";
const ADMIN = "e2e_admin_token";
let passed = 0;
let lastLog = () => "";
const results = [];

async function check(name, fn) {
  try {
    await fn();
    passed++;
    results.push(`  ✓ ${name}`);
  } catch (e) {
    results.push(`  ✗ ${name}\n      ${e.message}`);
    throw Object.assign(e, { testName: name });
  }
}

function startSite(port, persist, vars) {
  const args = ["pages", "dev", "public", "--port", String(port), "--persist-to", persist];
  for (const [k, v] of Object.entries(vars)) args.push("--binding", `${k}=${v}`);
  const proc = spawn(wrangler, args, { cwd: root, env: { ...process.env, CI: "1", WRANGLER_SEND_METRICS: "false" }, stdio: ["ignore", "pipe", "pipe"] });
  let log = "";
  proc.stdout.on("data", (d) => (log += d));
  proc.stderr.on("data", (d) => (log += d));
  lastLog = () => log;
  return { proc, log: () => log };
}

async function waitFor(url, ms = 60000) {
  const end = Date.now() + ms;
  while (Date.now() < end) {
    try { if ((await fetch(url)).status < 500) return; } catch {}
    await new Promise((r) => setTimeout(r, 500));
  }
  throw new Error(`site did not start at ${url}`);
}

function prepareState(persist) {
  const run = (args) => execFileSync(wrangler, args, { cwd: root, env: { ...process.env, CI: "1", WRANGLER_SEND_METRICS: "false" }, stdio: "pipe" });
  run(["d1", "migrations", "apply", "moodius", "--local", "--persist-to", persist]);
  for (const f of ["A5-digital", "A4-print"]) {
    run(["r2", "object", "put", `moodius-products/products/the-unexamined-self/v1/The-Unexamined-Self-${f}.pdf`, "--file", join(root, "..", "journal", "out", `The-Unexamined-Self-${f}.pdf`), "--local", "--persist-to", persist]);
  }
}

const stripeSig = (body, secret = STRIPE_SECRET, t = Math.floor(Date.now() / 1000)) => `t=${t},v1=${createHmac("sha256", secret).update(`${t}.${body}`).digest("hex")}`;
const json = (r) => r.json();
const post = (url, body, headers = {}) => fetch(url, { method: "POST", headers: { "content-type": "application/json", ...headers }, body: typeof body === "string" ? body : JSON.stringify(body), redirect: "manual" });
const admin = (B, path, method = "GET") => fetch(`${B}/api/shop/admin/${path}`, { method, headers: { authorization: `Bearer ${ADMIN}` } }).then(json);

async function startCheckout(B, src) {
  const r = await post(`${B}/api/shop/checkout`, { product: "the-unexamined-self", src, consent: true }).then(json);
  assert.equal(r.ok, true, JSON.stringify(r));
  return new URL(r.url).searchParams.get("ref");
}

async function phaseA() {
  const port = 8791;
  const B = `http://localhost:${port}`;
  const persist = mkdtempSync(join(tmpdir(), "moodius-e2e-a-"));
  prepareState(persist);
  const site = startSite(port, persist, {
    SITE_URL: B, PAYMENT_PROVIDER: "mock", ALLOW_MOCK_PAYMENTS: "true", EMAIL_PROVIDER: "log", ADMIN_TOKEN: ADMIN,
    STRIPE_WEBHOOK_SECRET: STRIPE_SECRET, LEMONSQUEEZY_WEBHOOK_SECRET: LS_SECRET, IP_HASH_SALT: "salt", DOWNLOAD_MAX_USES: "3", SUPPORT_EMAIL: "shop@example.com",
  });
  try {
    await waitFor(`${B}/`);
    results.push("Phase A: shop on its own (community agent not deployed)");

    await check("static pages render (home, product, guide, legal, 404)", async () => {
      for (const p of ["/", "/shop/", "/shop/the-unexamined-self/", "/guide/", "/legal/privacy/", "/legal/terms/", "/legal/refunds/", "/orders/", "/thank-you/"]) {
        const r = await fetch(B + p);
        assert.equal(r.status, 200, p);
      }
      const html = await (await fetch(`${B}/shop/the-unexamined-self/`)).text();
      assert.match(html, /Buy for £14/);
      assert.match(html, /lose the legal 14-day right to cancel/);
      assert.equal((await fetch(`${B}/no-such-page`)).status, 404);
    });

    await check("checkout refuses without the digital-content consent tick", async () => {
      const r = await post(`${B}/api/shop/checkout`, { product: "the-unexamined-self" });
      assert.equal(r.status, 400);
      const f = await fetch(`${B}/api/shop/checkout`, { method: "POST", body: new URLSearchParams({ product: "the-unexamined-self" }), redirect: "manual" });
      assert.equal(f.status, 303);
      assert.match(f.headers.get("location"), /error=/);
    });

    await check("coming-soon bundle can't be bought", async () => {
      const r = await post(`${B}/api/shop/checkout`, { product: "the-examined-life-bundle", consent: true });
      assert.equal(r.status, 400);
    });

    let downloadUrl, mockPaymentRef;
    await check("mock purchase: checkout -> pay -> thank-you shows a download link", async () => {
      const ref = await startCheckout(B, "reel_r012");
      assert.equal((await fetch(`${B}/api/shop/order-status?ref=${ref}`).then(json)).status, "pending");
      const paid = await post(`${B}/api/shop/mock/pay`, { ref, email: "Buyer@Example.com", name: "Test Buyer" }).then(json);
      assert.equal(paid.ok, true);
      mockPaymentRef = paid.payment_ref;
      const s = await fetch(`${B}/api/shop/order-status?ref=${ref}`).then(json);
      assert.equal(s.status, "paid");
      assert.equal(s.email, "bu•••@example.com");
      assert.equal(s.testMode, true);
      assert.match(s.downloadUrl, /\/download\/[A-Za-z0-9_-]{43}$/);
      downloadUrl = s.downloadUrl;
    });

    await check("purchase email sent with a working link (outbox)", async () => {
      const { outbox } = await admin(B, "outbox");
      const mail = outbox.find((m) => m.kind === "purchase");
      assert.ok(mail, "no purchase email");
      assert.equal(mail.to_addr, "buyer@example.com");
      assert.match(mail.body_text, /\/download\/[A-Za-z0-9_-]{43}/);
      assert.match(mail.body_text, /TEST ORDER/);
    });

    await check("download page: GET doesn't count a use; POST streams the real PDF", async () => {
      const page = await (await fetch(downloadUrl)).text();
      assert.match(page, /3 downloads left/);
      assert.match((await (await fetch(downloadUrl)).text()), /3 downloads left/, "GET must not use up downloads");
      const r = await fetch(downloadUrl, { method: "POST", body: new URLSearchParams({ f: "0" }) });
      assert.equal(r.status, 200);
      assert.equal(r.headers.get("content-type"), "application/pdf");
      assert.match(r.headers.get("content-disposition"), /The-Unexamined-Self-A5-digital\.pdf/);
      assert.match(r.headers.get("cache-control"), /no-store/);
      const buf = Buffer.from(await r.arrayBuffer());
      assert.equal(buf.subarray(0, 5).toString(), "%PDF-");
      assert.ok(buf.length > 100000, "PDF too small");
      const r2 = await fetch(downloadUrl, { method: "POST", body: new URLSearchParams({ f: "1" }) });
      assert.match(r2.headers.get("content-disposition"), /A4-print/);
      await r2.arrayBuffer();
    });

    await check("download limit enforced (3rd use ok, 4th refused with 410)", async () => {
      const ok = await fetch(downloadUrl, { method: "POST", body: new URLSearchParams({ f: "0" }) });
      assert.equal(ok.status, 200); await ok.arrayBuffer();
      assert.equal((await fetch(downloadUrl, { method: "POST", body: new URLSearchParams({ f: "0" }) })).status, 410);
      assert.equal((await fetch(downloadUrl)).status, 410);
    });

    await check("bad and guessed tokens get 404", async () => {
      assert.equal((await fetch(`${B}/download/notatoken`)).status, 404);
      assert.equal((await fetch(`${B}/download/${"A".repeat(43)}`)).status, 404);
    });

    let stripeOrder;
    await check("Stripe-signed checkout.session.completed fulfils once (retries ignored)", async () => {
      const ref = await startCheckout(B, "pin_journal");
      const event = {
        id: "evt_e2e_1", type: "checkout.session.completed", livemode: false,
        data: { object: { id: "cs_test_e2e_1", payment_status: "paid", payment_intent: "pi_test_e2e_1", amount_total: 1400, currency: "gbp", customer_details: { email: "stripe.buyer@example.com", name: "S B" }, client_reference_id: ref, metadata: { checkout_id: ref, product: "the-unexamined-self", src: "pin_journal" }, livemode: false } },
      };
      const body = JSON.stringify(event);
      const r = await post(`${B}/api/shop/webhooks/stripe`, body, { "stripe-signature": stripeSig(body) }).then(json);
      assert.equal(r.created, true);
      stripeOrder = r.order;
      const again = await post(`${B}/api/shop/webhooks/stripe`, body, { "stripe-signature": stripeSig(body) }).then(json);
      assert.equal(again.duplicate, true);
      // Same session in a different event id (Stripe can send both completed + async_succeeded)
      const ev2 = JSON.stringify({ ...event, id: "evt_e2e_2", type: "checkout.session.async_payment_succeeded" });
      const r3 = await post(`${B}/api/shop/webhooks/stripe`, ev2, { "stripe-signature": stripeSig(ev2) }).then(json);
      assert.equal(r3.created, false);
      assert.equal(r3.order, stripeOrder);
      const s = await fetch(`${B}/api/shop/order-status?ref=${ref}`).then(json);
      assert.equal(s.status, "paid");
    });

    await check("Stripe webhook rejects bad / stale signatures", async () => {
      const body = JSON.stringify({ id: "evt_forged", type: "checkout.session.completed", data: { object: {} } });
      assert.equal((await post(`${B}/api/shop/webhooks/stripe`, body, { "stripe-signature": stripeSig(body, "whsec_wrong") })).status, 400);
      assert.equal((await post(`${B}/api/shop/webhooks/stripe`, body, { "stripe-signature": stripeSig(body, STRIPE_SECRET, 1000) })).status, 400);
      assert.equal((await post(`${B}/api/shop/webhooks/stripe`, body)).status, 400);
    });

    await check("Stripe charge.refunded marks the order refunded and closes its downloads", async () => {
      const body = JSON.stringify({ id: "evt_e2e_refund", type: "charge.refunded", livemode: false, data: { object: { refunded: true, payment_intent: "pi_test_e2e_1" } } });
      const r = await post(`${B}/api/shop/webhooks/stripe`, body, { "stripe-signature": stripeSig(body) }).then(json);
      assert.equal(r.refunded, stripeOrder);
      const { orders } = await admin(B, "orders");
      assert.equal(orders.find((o) => o.id === stripeOrder).status, "refunded");
    });

    await check("Lemon Squeezy-signed order_created fulfils; bad signature rejected", async () => {
      const ref = await startCheckout(B, "dm_journal");
      const body = JSON.stringify({ meta: { event_name: "order_created", custom_data: { checkout_id: ref, product: "the-unexamined-self", src: "dm_journal" } }, data: { id: "4242", attributes: { status: "paid", total: 1400, currency: "GBP", user_email: "ls.buyer@example.com", user_name: "L B", test_mode: true } } });
      const sig = createHmac("sha256", LS_SECRET).update(body).digest("hex");
      const r = await post(`${B}/api/shop/webhooks/lemonsqueezy`, body, { "x-signature": sig }).then(json);
      assert.equal(r.created, true);
      assert.equal((await post(`${B}/api/shop/webhooks/lemonsqueezy`, body, { "x-signature": "00" })).status, 400);
    });

    await check("mock refund closes the mock order", async () => {
      const r = await post(`${B}/api/shop/mock/refund`, { payment_ref: mockPaymentRef }).then(json);
      assert.equal(r.changed, true);
    });

    await check("find my order: same answer for any address, links only to buyers", async () => {
      const a = await post(`${B}/api/shop/resend-links`, { email: "ls.buyer@example.com" }).then(json);
      const b = await post(`${B}/api/shop/resend-links`, { email: "nobody@example.com" }).then(json);
      assert.equal(a.message, b.message);
      const { outbox } = await admin(B, "outbox");
      assert.ok(outbox.some((m) => m.kind === "resend" && m.to_addr === "ls.buyer@example.com"));
      assert.ok(!outbox.some((m) => m.to_addr === "nobody@example.com"));
    });

    await check("fallback newsletter: consent required, double opt-in, confirm, one-click unsubscribe", async () => {
      assert.equal((await post(`${B}/api/newsletter/subscribe`, { email: "reader@example.com" })).status, 400);
      const r = await post(`${B}/api/newsletter/subscribe`, { email: "reader@example.com", consent: true, source: "guide_landing", lead_magnet: "seven-day-reflection-guide" }).then(json);
      assert.equal(r.pending, true);
      let { outbox } = await admin(B, "outbox");
      const confirmMail = outbox.find((m) => m.kind === "confirm" && m.to_addr === "reader@example.com");
      const confirmUrl = confirmMail.body_text.match(/https?:\/\/\S+confirm\?token=\S+/)[0];
      const page = await (await fetch(confirmUrl)).text();
      assert.match(page, /seven-day-reflection-guide\.pdf/);
      assert.equal((await fetch(confirmUrl)).status, 404, "confirm link is single-use");
      ({ outbox } = await admin(B, "outbox"));
      const welcome = outbox.find((m) => m.kind === "welcome" && m.to_addr === "reader@example.com");
      const unsub = welcome.body_text.match(/https?:\/\/\S+unsubscribe\?token=\S+/)[0];
      assert.equal((await fetch(unsub, { method: "POST" })).status, 200);
      const exp = await admin(B, "export");
      const sub = exp.subscribers.find((s) => s.email === "reader@example.com");
      assert.equal(sub.status, "unsubscribed");
      assert.equal(sub.consent_version, "2026-10-21");
      assert.match(sub.consent_text, /never sold or shared/);
      assert.match(sub.ip_hash || "", /^[0-9a-f]{64}$|^$/);
    });

    await check("free guide PDF is served", async () => {
      const r = await fetch(`${B}/downloads/free/seven-day-reflection-guide.pdf`);
      assert.equal(r.status, 200);
      assert.equal(Buffer.from(await r.arrayBuffer()).subarray(0, 5).toString(), "%PDF-");
    });

    await check("fallback /r/ links log a cookieless click and carry src to the product", async () => {
      const r = await fetch(`${B}/r/shop?src=Reel_R012`, { redirect: "manual" });
      assert.equal(r.status, 302);
      assert.equal(r.headers.get("location"), `${B}/shop/the-unexamined-self/?src=reel_r012`);
      assert.equal(r.headers.get("set-cookie"), null);
      assert.equal((await fetch(`${B}/r/unknown`, { redirect: "manual" })).headers.get("location"), `${B}/`);
    });

    await check("page-view beacon counts only known pages", async () => {
      assert.equal((await post(`${B}/api/shop/event`, { kind: "page_view", slug: "the-unexamined-self", src: "reel_r012" })).status, 204);
      assert.equal((await post(`${B}/api/shop/event`, { kind: "purchase", slug: "the-unexamined-self" })).status, 204);
    });

    await check("funnel summary attributes clicks -> views -> checkouts -> purchases by source", async () => {
      await new Promise((r) => setTimeout(r, 300));
      const s = await admin(B, "summary?days=30");
      const reel = s.by_source.find((x) => x.src === "reel_r012");
      assert.ok(reel, JSON.stringify(s.by_source));
      assert.equal(reel.clicks, 1);
      assert.equal(reel.product_views, 1);
      assert.ok(reel.checkouts >= 1);
      assert.equal(reel.purchases, 1);
      assert.equal(s.totals.purchase, 3, "client-sent 'purchase' events must be ignored");
      const test = s.revenue.find((x) => x.test_mode === 1);
      assert.equal(test.orders, 3);
      assert.equal(test.net_cents, 1400, "two refunds leave one paid £14 order");
    });

    let personalOrder;
    await check("personal edition: choices validated, stored on the order, queued, buyer and shop emailed", async () => {
      const base = { product: "the-unexamined-self-personal", consent: true, src: "reel_p001" };
      const noName = await post(`${B}/api/shop/checkout`, base);
      assert.equal(noName.status, 400);
      assert.match((await noName.json()).error, /name/);
      assert.equal((await post(`${B}/api/shop/checkout`, { ...base, p_name: "Amara", p_accent: "neon" })).status, 400);
      assert.equal((await post(`${B}/api/shop/checkout`, { ...base, p_name: "x".repeat(41) })).status, 400);
      const r = await post(`${B}/api/shop/checkout`, { ...base, p_name: "Amara Okafor", p_monogram: "a.o", p_highlight: "manifesto", p_dedication: "For the year you stopped running.", p_start_date: "2026-11-02" }).then(json);
      assert.equal(r.ok, true, JSON.stringify(r));
      const ref = new URL(r.url).searchParams.get("ref");
      await post(`${B}/api/shop/mock/pay`, { ref, email: "amara@example.com" });
      const s = await fetch(`${B}/api/shop/order-status?ref=${ref}`).then(json);
      assert.equal(s.status, "paid");
      assert.equal(s.personal, "queued");
      personalOrder = s.orderId;
      const { queue } = await admin(B, "personal-queue");
      const q = queue.find((o) => o.id === personalOrder);
      assert.deepEqual(q.personal, { name: "Amara Okafor", monogram: "AO", accent: "ember", cover: "dark", highlight: "manifesto", start_date: "2026-11-02", dedication: "For the year you stopped running." });
      const { outbox } = await admin(B, "outbox");
      assert.match(outbox.find((m) => m.kind === "purchase" && m.to_addr === "amara@example.com").body_text, /personal edition now[\s\S]*Name on the cover: Amara Okafor/);
      assert.match(outbox.find((m) => m.kind === "admin").body_text, new RegExp(`personalise\\.py ${personalOrder} --deliver`));
      const page = await (await fetch(s.downloadUrl)).text();
      assert.match(page, /being made/);
    });

    await check("personalise.py builds both editions, uploads them, and delivers the link", async () => {
      assert.equal((await fetch(`${B}/api/shop/admin/orders/${personalOrder}/personal-deliver`, { method: "POST", headers: { authorization: `Bearer ${ADMIN}` } })).status, 409, "no files yet");
      const notPdf = await fetch(`${B}/api/shop/admin/orders/${personalOrder}/personal-file?edition=digital`, { method: "PUT", headers: { authorization: `Bearer ${ADMIN}` }, body: "hello" });
      assert.equal(notPdf.status, 400);
      const out = execFileSync("python3", [join(root, "..", "journal", "personalise.py"), personalOrder, "--deliver"], { env: { ...process.env, SITE_URL: B, ADMIN_TOKEN: ADMIN }, encoding: "utf8", timeout: 240000 });
      assert.match(out, /uploaded digital/); assert.match(out, /uploaded print/); assert.match(out, /delivered/);
      const { outbox } = await admin(B, "outbox");
      const mail = outbox.find((m) => m.kind === "personal" && m.to_addr === "amara@example.com");
      const link = mail.body_text.match(/https?:\/\/\S+\/download\/[A-Za-z0-9_-]{43}/)[0];
      const page = await (await fetch(link)).text();
      assert.match(page, /Your personal edition, digital/);
      assert.doesNotMatch(page, /being made/);
      const r = await fetch(link, { method: "POST", body: new URLSearchParams({ f: "0" }) });
      assert.match(r.headers.get("content-disposition"), /Personal-A5-digital/);
      const pdf = Buffer.from(await r.arrayBuffer()).toString("latin1");
      assert.ok(pdf.includes("%PDF-"));
    });

    await check("gift edition: send date in the past refused; recipient emailed once on delivery", async () => {
      const base = { product: "the-unexamined-self-gift", consent: true, p_name: "Leo", p_from_name: "Sam" };
      assert.equal((await post(`${B}/api/shop/checkout`, { ...base, p_send_date: "2020-01-01" })).status, 400);
      assert.equal((await post(`${B}/api/shop/checkout`, { product: "the-unexamined-self-gift", consent: true, p_name: "Leo" })).status, 400, "gift needs a from name");
      const r = await post(`${B}/api/shop/checkout`, { ...base, p_recipient_email: "Leo@Example.com", p_send_date: "2099-12-25" }).then(json);
      const ref = new URL(r.url).searchParams.get("ref");
      await post(`${B}/api/shop/mock/pay`, { ref, email: "sam@example.com" });
      const id = (await fetch(`${B}/api/shop/order-status?ref=${ref}`).then(json)).orderId;
      const pdf = readFileSync(join(root, "..", "journal", "out", "The-Unexamined-Self-A5-digital.pdf"));
      const up = await fetch(`${B}/api/shop/admin/orders/${id}/personal-file?edition=digital`, { method: "PUT", headers: { authorization: `Bearer ${ADMIN}`, "content-type": "application/pdf" }, body: pdf }).then(json);
      assert.equal(up.ok, true);
      const d = await fetch(`${B}/api/shop/admin/orders/${id}/personal-deliver`, { method: "POST", headers: { authorization: `Bearer ${ADMIN}` } }).then(json);
      assert.equal(d.personal_status, "delivered");
      const { outbox } = await admin(B, "outbox");
      const gift = outbox.filter((m) => m.kind === "gift");
      assert.equal(gift.length, 1);
      assert.equal(gift[0].to_addr, "leo@example.com");
      assert.match(gift[0].body_text, /Sam has given you[\s\S]*haven't added you to any list/);
      assert.match(outbox.find((m) => m.kind === "personal" && m.to_addr === "sam@example.com").body_text, /emailed the gift edition to leo@example\.com/);
    });

    await check("admin API needs the token", async () => {
      assert.equal((await fetch(`${B}/api/shop/admin/orders`)).status, 401);
      assert.equal((await fetch(`${B}/api/shop/admin/orders`, { headers: { authorization: "Bearer wrong" } })).status, 401);
    });

    await check("security headers on static pages", async () => {
      const r = await fetch(`${B}/`);
      assert.match(r.headers.get("content-security-policy") || "", /default-src 'self'/);
      assert.equal(r.headers.get("x-frame-options"), "DENY");
    });
  } finally {
    site.proc.kill();
    rmSync(persist, { recursive: true, force: true });
  }
}

async function phaseB() {
  const port = 8792;
  const B = `http://localhost:${port}`;
  const received = [];
  const agent = createServer((req, res) => {
    let body = "";
    req.on("data", (d) => (body += d));
    req.on("end", () => {
      if (req.url === "/api/integrations/revenue") {
        const [t, v1] = (req.headers["x-moodius-signature"] || "").split(",").map((p) => p.split("=")[1]);
        const ok = v1 === createHmac("sha256", REVENUE_SECRET).update(`${t}.${body}`).digest("hex") && Math.abs(Date.now() / 1000 - Number(t)) < 300;
        received.push({ ok, body: JSON.parse(body) });
        res.writeHead(ok ? 200 : 401, { "content-type": "application/json" }).end(JSON.stringify({ ok, duplicate: false }));
        return;
      }
      res.writeHead(200, { "content-type": "text/plain", "x-agent": "yes" }).end(`agent saw ${req.method} ${req.url} host=${req.headers["x-forwarded-host"]}`);
    });
  });
  await new Promise((r) => agent.listen(9917, r));
  const persist = mkdtempSync(join(tmpdir(), "moodius-e2e-b-"));
  prepareState(persist);
  const site = startSite(port, persist, {
    SITE_URL: B, PAYMENT_PROVIDER: "mock", ALLOW_MOCK_PAYMENTS: "true", EMAIL_PROVIDER: "log", ADMIN_TOKEN: ADMIN,
    COMMUNITY_AGENT_URL: "http://localhost:9917", REVENUE_WEBHOOK_SECRET: REVENUE_SECRET,
  });
  try {
    await waitFor(`${B}/`);
    results.push("Phase B: community agent deployed (one domain + revenue sync)");

    await check("agent paths are proxied; shop paths are not", async () => {
      for (const p of ["/links", "/r/shop?src=reel_r012", "/newsletter", "/api/newsletter/subscribe", "/admin"]) {
        const r = await fetch(B + p, { redirect: "manual" });
        assert.equal(r.headers.get("x-agent"), "yes", p);
        assert.match(await r.text(), new RegExp(`host=localhost:${port}`));
      }
      const shop = await fetch(`${B}/api/shop/admin/orders`);
      assert.equal(shop.headers.get("x-agent"), null);
    });

    await check("paid and refunded orders reach the revenue dashboard with a valid signature and src", async () => {
      const ref = await startCheckout(B, "reel_r020");
      const paid = await post(`${B}/api/shop/mock/pay`, { ref, email: "rev@example.com" }).then(json);
      await post(`${B}/api/shop/mock/refund`, { payment_ref: paid.payment_ref });
      const end = Date.now() + 5000;
      while (received.length < 2 && Date.now() < end) await new Promise((r) => setTimeout(r, 200));
      assert.equal(received.length, 2, JSON.stringify(received));
      assert.ok(received.every((x) => x.ok), "signature check failed");
      const [p, r] = received.map((x) => x.body);
      assert.equal(p.event, "order.paid"); assert.equal(p.amount_cents, 1400); assert.equal(p.src, "reel_r020"); assert.equal(p.stream, "digital_product");
      assert.equal(r.event, "order.refunded"); assert.equal(r.id, `${p.id}_refund`);
      const { orders } = await admin(B, "orders");
      assert.ok(orders[0].revenue_sent_at, "revenue_sent_at not recorded");
    });
  } finally {
    site.proc.kill();
    agent.close();
    rmSync(persist, { recursive: true, force: true });
  }
}

let failed = false;
try {
  await phaseA();
  await phaseB();
} catch (e) {
  failed = true;
  if (!e.testName) results.push(`  ✗ setup: ${e.message}`);
  if (process.env.E2E_DEBUG) console.log(lastLog());
}
console.log(results.join("\n"));
console.log(failed ? `\nFAILED (${passed} passed before the failure)` : `\nall ${passed} end-to-end checks passed`);
process.exit(failed ? 1 : 0);
