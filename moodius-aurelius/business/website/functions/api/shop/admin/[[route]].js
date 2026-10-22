// /api/shop/admin/*  — order records, funnel numbers, exports. Bearer ADMIN_TOKEN.
// In production also put /backoffice* and /api/shop/admin/* behind Cloudflare Access (free).
//   GET  orders                 latest orders
//   GET  summary?days=30        funnel: clicks -> product views -> checkouts -> purchases, by source
//   GET  export                 orders + fallback subscribers + fallback clicks (for the community agent import)
//   GET  outbox                 last 50 emails (the test inbox when EMAIL_PROVIDER=log)
//   POST orders/<id>/resend     email the buyer a fresh download link
//   POST forward-pending        retry revenue events the community agent didn't acknowledge
//   GET  personal-queue         personalised and gift orders waiting to be made
//   GET  orders/<id>/personal   the buyer's choices for one order (read by journal/personalise.py)
//   PUT  orders/<id>/personal-file?edition=digital|print   upload a personalised PDF (raw body)
//   POST orders/<id>/personal-deliver                     email the buyer (and gift recipient) the link
import { config } from "../../../../src/config.js";
import { getProduct } from "../../../../src/catalog.js";
import { deliverPersonal, downloadPageUrl, getOrder, mintDownloadToken } from "../../../../src/orders.js";
import { sendEmail } from "../../../../src/email.js";
import { forwardRevenue } from "../../../../src/revenue.js";
import { json, nowIso, safeEqual } from "../../../../src/util.js";

const MAX_PDF_BYTES = 25 * 1024 * 1024;

export async function summary(db, days) {
  const since = new Date(Date.now() - days * 86400000).toISOString();
  const { results: kinds } = await db.prepare("SELECT kind, COUNT(*) AS n FROM conversion_events WHERE at >= ? GROUP BY kind").bind(since).all();
  const { results: bySrc } = await db
    .prepare(
      `SELECT COALESCE(src, '(direct)') AS src,
              SUM(kind = 'link_click') AS clicks,
              SUM(kind = 'page_view' AND slug IN ('the-unexamined-self')) AS product_views,
              SUM(kind = 'checkout_started') AS checkouts,
              SUM(kind = 'purchase') AS purchases,
              SUM(kind = 'subscribe') AS subscribes
       FROM conversion_events WHERE at >= ? GROUP BY COALESCE(src, '(direct)') ORDER BY purchases DESC, clicks DESC LIMIT 50`,
    )
    .bind(since)
    .all();
  const { results: revenue } = await db
    .prepare(
      `SELECT test_mode, currency, COUNT(*) AS orders,
              SUM(CASE WHEN status = 'paid' THEN amount_cents ELSE 0 END) AS net_cents,
              SUM(status = 'refunded') AS refunds
       FROM orders WHERE created_at >= ? GROUP BY test_mode, currency`,
    )
    .bind(since)
    .all();
  const count = Object.fromEntries(kinds.map((k) => [k.kind, k.n]));
  const views = count.page_view || 0;
  return {
    days,
    since,
    totals: count,
    conversion: {
      product_view_to_checkout: views ? +(100 * (count.checkout_started || 0) / views).toFixed(1) : null,
      checkout_to_purchase: count.checkout_started ? +(100 * (count.purchase || 0) / count.checkout_started).toFixed(1) : null,
    },
    by_source: bySrc,
    revenue,
  };
}

export async function onRequest({ request, env, params, waitUntil }) {
  const c = config(env);
  if (!c.adminToken) return json({ ok: false, error: "admin disabled: set ADMIN_TOKEN" }, 503);
  const auth = request.headers.get("authorization") || "";
  if (!safeEqual(auth, `Bearer ${c.adminToken}`)) return json({ ok: false, error: "unauthorised" }, 401);

  const route = (params.route || []).join("/");
  const db = env.DB;
  const url = new URL(request.url);

  if (request.method === "GET" && route === "orders") {
    const { results } = await db
      .prepare("SELECT id, created_at, product_slug, amount_cents, currency, email, name, status, src, provider, test_mode, revenue_sent_at FROM orders ORDER BY created_at DESC LIMIT 200")
      .all();
    return json({ orders: results });
  }
  if (request.method === "GET" && route === "summary") {
    const days = Math.min(365, Math.max(1, parseInt(url.searchParams.get("days") || "30", 10)));
    return json(await summary(db, days));
  }
  if (request.method === "GET" && route === "export") {
    const orders = (await db.prepare("SELECT * FROM orders ORDER BY created_at").all()).results;
    const subscribers = (
      await db.prepare("SELECT email, status, consent_text, consent_version, consent_at, source, lead_magnet, confirmed_at, unsubscribed_at, ip_hash FROM subscribers").all()
    ).results;
    const clicks = (await db.prepare("SELECT kind, slug, src, at FROM conversion_events WHERE kind = 'link_click' ORDER BY at").all()).results;
    return json({ exported_at: new Date().toISOString(), orders, subscribers, conversion_events: clicks });
  }
  if (request.method === "GET" && route === "outbox") {
    const { results } = await db.prepare("SELECT * FROM outbox ORDER BY id DESC LIMIT 50").all();
    return json({ outbox: results });
  }
  const resend = route.match(/^orders\/(ord_[a-z0-9]+)\/resend$/);
  if (request.method === "POST" && resend) {
    const order = await getOrder(db, resend[1]);
    if (!order || order.status !== "paid") return json({ ok: false, error: "no paid order with that id" }, 404);
    const product = getProduct(order.product_slug);
    const token = await mintDownloadToken(c, db, order.id);
    await sendEmail(c, db, {
      to: order.email,
      subject: `Your copy of ${product.name}`,
      text: `Here is a fresh download link for ${product.name} (order ${order.id}):\n${downloadPageUrl(c, token)}\n\nMoodius`,
      kind: "resend",
    });
    return json({ ok: true });
  }
  if (request.method === "POST" && route === "forward-pending") {
    const paid = (await db.prepare("SELECT * FROM orders WHERE revenue_sent_at IS NULL").all()).results;
    const refunds = (await db.prepare("SELECT * FROM orders WHERE status = 'refunded' AND refund_sent_at IS NULL").all()).results;
    const out = [];
    for (const o of paid) out.push([o.id, "order.paid", await forwardRevenue(c, db, o, "order.paid")]);
    for (const o of refunds) out.push([o.id, "order.refunded", await forwardRevenue(c, db, o, "order.refunded")]);
    return json({ ok: true, results: out });
  }
  if (request.method === "GET" && route === "personal-queue") {
    const { results } = await db
      .prepare("SELECT id, created_at, product_slug, email, status, test_mode, personal_status, personal_json, personal_done_at FROM orders WHERE personal_status IS NOT NULL ORDER BY personal_status = 'delivered', created_at LIMIT 200")
      .all();
    return json({ queue: results.map((o) => ({ ...o, personal: JSON.parse(o.personal_json || "{}"), personal_json: undefined })) });
  }
  const personal = route.match(/^orders\/(ord_[a-z0-9]+)\/(personal|personal-file|personal-deliver)$/);
  if (personal) {
    const order = await getOrder(db, personal[1]);
    if (!order || !order.personal_json) return json({ ok: false, error: "no personalised order with that id" }, 404);
    if (request.method === "GET" && personal[2] === "personal") {
      return json({ id: order.id, product_slug: order.product_slug, status: order.status, personal_status: order.personal_status, test_mode: !!order.test_mode, personal: JSON.parse(order.personal_json) });
    }
    if (order.status !== "paid") return json({ ok: false, error: "order is not paid (refunded?)" }, 409);
    if (request.method === "PUT" && personal[2] === "personal-file") {
      const edition = url.searchParams.get("edition");
      if (!["digital", "print"].includes(edition)) return json({ ok: false, error: "edition must be digital or print" }, 400);
      const body = await request.arrayBuffer();
      if (body.byteLength > MAX_PDF_BYTES) return json({ ok: false, error: "file too large" }, 413);
      if (new TextDecoder().decode(body.slice(0, 5)) !== "%PDF-") return json({ ok: false, error: "not a PDF" }, 400);
      const filename = edition === "digital" ? "The-Unexamined-Self-Personal-A5-digital.pdf" : "The-Unexamined-Self-Personal-A4-print.pdf";
      const key = `personal/${order.id}/${filename}`;
      await env.FILES.put(key, body, { httpMetadata: { contentType: "application/pdf" } });
      const label = edition === "digital" ? "Your personal edition, digital (A5, type-in fields)" : "Your personal edition, print (A4)";
      await db
        .prepare("INSERT INTO order_files (order_id, r2_key, filename, label, created_at) VALUES (?,?,?,?,?) ON CONFLICT (order_id, r2_key) DO UPDATE SET created_at = excluded.created_at")
        .bind(order.id, key, filename, label, nowIso())
        .run();
      return json({ ok: true, key, bytes: body.byteLength });
    }
    if (request.method === "POST" && personal[2] === "personal-deliver") {
      const updated = await deliverPersonal(c, db, order).catch((e) => ({ error: e }));
      if (updated.error) return json({ ok: false, error: updated.error.message }, updated.error.status || 500);
      return json({ ok: true, personal_status: updated.personal_status });
    }
  }
  return json({ ok: false, error: "not found" }, 404);
}
