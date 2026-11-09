// Sends order.paid / order.refunded to the community agent's revenue dashboard,
// following moodius-aurelius/community-agent/INTEGRATION-CONTRACT.md section 1.

import { hmacSha256Hex, nowIso } from "./util.js";

export function revenueEvent(order, event) {
  return {
    id: event === "order.refunded" ? `${order.id}_refund` : order.id,
    event,
    stream: "digital_product",
    amount_cents: order.amount_cents,
    currency: order.currency,
    occurred_at: event === "order.refunded" ? order.refunded_at || nowIso() : order.created_at,
    product: order.product_slug,
    ...(order.src ? { src: order.src } : {}),
  };
}

export async function forwardRevenue(c, db, order, event) {
  if (!c.communityAgentUrl || !c.revenueSecret) return "skipped";
  const body = JSON.stringify(revenueEvent(order, event));
  const t = Math.floor(Date.now() / 1000);
  const sig = await hmacSha256Hex(c.revenueSecret, `${t}.${body}`);
  try {
    const res = await fetch(`${c.communityAgentUrl}/api/integrations/revenue`, {
      method: "POST",
      headers: { "content-type": "application/json", "x-moodius-signature": `t=${t},v1=${sig}` },
      body,
    });
    if (!res.ok) return `failed ${res.status}`;
    const col = event === "order.refunded" ? "refund_sent_at" : "revenue_sent_at";
    await db.prepare(`UPDATE orders SET ${col} = ? WHERE id = ?`).bind(nowIso(), order.id).run();
    return "sent";
  } catch (e) {
    return `failed ${e.message || e}`;
  }
}
