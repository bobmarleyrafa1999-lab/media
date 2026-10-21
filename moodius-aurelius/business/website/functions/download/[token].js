// /download/<token>
// GET shows the buyer's download page (no use is counted, safe for link scanners).
// POST f=<index> streams that file from the private R2 bucket and counts one use.
import { config } from "../../src/config.js";
import { getProduct } from "../../src/catalog.js";
import { page } from "../../src/html.js";
import { escapeHtml, nowIso, sha256Hex } from "../../src/util.js";

async function lookup(db, token) {
  if (!/^[A-Za-z0-9_-]{43}$/.test(token || "")) return null;
  const hash = await sha256Hex(token);
  const row = await db
    .prepare("SELECT t.*, o.product_slug, o.status, o.id AS oid, o.test_mode FROM download_tokens t JOIN orders o ON o.id = t.order_id WHERE t.token_hash = ?")
    .bind(hash)
    .first();
  return row ? { ...row, hash } : null;
}

const gone = (why) =>
  page("Link expired", `<h1>This link has expired</h1><p>${why}</p><p><a class="btn" href="/orders/">Send me a fresh link</a></p>`, { status: 410 });

export async function onRequestGet({ env, params }) {
  const row = await lookup(env.DB, params.token);
  if (!row) return page("Link not found", `<h1>We couldn't find that link</h1><p>Check it was copied in full, or ask for a fresh one.</p><p><a class="btn" href="/orders/">Find my order</a></p>`, { status: 404 });
  if (row.status !== "paid") return gone("This order was refunded, so its downloads are closed.");
  if (row.expires_at <= nowIso()) return gone("Download links last a limited time to keep your files private.");
  if (row.uses >= row.max_uses) return gone("This link has been used the maximum number of times.");
  const product = getProduct(row.product_slug);
  const left = row.max_uses - row.uses;
  const files = product.files
    .map(
      (f, i) => `<form method="post" class="dl"><input type="hidden" name="f" value="${i}"><button class="btn" type="submit">Download ${escapeHtml(f.label)}</button></form>`,
    )
    .join("");
  return page(
    `Your downloads`,
    `<p class="kicker">Order ${escapeHtml(row.oid)}${row.test_mode ? " · test order" : ""}</p>
     <h1>${escapeHtml(product.name)}</h1>
     <p>${escapeHtml(product.subtitle)}. Both editions hold the same 30 days: use the digital one on a tablet or computer, print the A4 one if you prefer pen.</p>
     ${files}
     <p class="muted">${left} download${left === 1 ? "" : "s"} left on this link · expires ${new Date(row.expires_at).toUTCString().slice(5, 16)}.<br>Please don't share it. It's tied to your order.</p>`,
  );
}

export async function onRequestPost({ request, env, params }) {
  const c = config(env);
  const row = await lookup(env.DB, params.token);
  if (!row || row.status !== "paid") return gone("This link isn't active.");
  const form = await request.formData();
  const product = getProduct(row.product_slug);
  const file = product.files[parseInt(form.get("f"), 10)];
  if (!file) return page("Not found", "<h1>That file doesn't exist</h1>", { status: 404 });
  const object = await env.FILES.get(file.key);
  if (!object) {
    console.error("missing R2 object", file.key);
    return page("Temporarily unavailable", `<h1>The file isn't available right now</h1><p>Nothing was used up. Please try again in a few minutes or reply to your order email.</p>`, { status: 503 });
  }
  // Count the use atomically, only while the link is still valid.
  const res = await env.DB
    .prepare("UPDATE download_tokens SET uses = uses + 1, last_used_at = ? WHERE token_hash = ? AND uses < max_uses AND expires_at > ?")
    .bind(nowIso(), row.hash, nowIso())
    .run();
  if (!res.meta?.changes) return gone("This link has expired or reached its download limit.");
  return new Response(object.body, {
    headers: {
      "content-type": "application/pdf",
      "content-disposition": `attachment; filename="${file.filename}"`,
      "cache-control": "private, no-store",
      "x-robots-tag": "noindex",
      "x-content-type-options": "nosniff",
      ...(object.size ? { "content-length": String(object.size) } : {}),
    },
  });
}
