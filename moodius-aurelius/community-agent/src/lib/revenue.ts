import crypto from "node:crypto";
import { one, q } from "./db";
import { trackEvent } from "./tracking";

// Store → revenue dashboard. Two receivers share one signature scheme (t=<unix>,v1=<hex HMAC of "t.body">):
//   /api/integrations/revenue  (our own contract, docs/INTEGRATION-CONTRACT.md)
//   /api/integrations/sellf    (Sellf's X-Sellf-Signature, same format)

export function verifyTimestampedSignature(secret: string, rawBody: string, header: string | null, toleranceS = 300, nowS = Math.floor(Date.now() / 1000)): boolean {
  if (!secret || !header) return false;
  let t: number | null = null;
  let v1: string | null = null;
  for (const part of header.split(",")) {
    const i = part.indexOf("=");
    if (i < 0) continue;
    const k = part.slice(0, i).trim();
    const v = part.slice(i + 1).trim();
    if (k === "t" && /^\d+$/.test(v)) t = Number(v);
    if (k === "v1") v1 = v;
  }
  if (t === null || !v1 || Math.abs(nowS - t) > toleranceS) return false;
  const mac = crypto.createHmac("sha256", secret).update(`${t}.${rawBody}`).digest("hex");
  return v1.length === mac.length && crypto.timingSafeEqual(Buffer.from(v1), Buffer.from(mac));
}

export function signTimestamped(secret: string, rawBody: string, t = Math.floor(Date.now() / 1000)) {
  return `t=${t},v1=${crypto.createHmac("sha256", secret).update(`${t}.${rawBody}`).digest("hex")}`;
}

const STREAMS = new Set(["affiliate", "sponsorship", "substack_paid", "digital_product", "membership", "other"]);

export interface RevenueEvent {
  id: string; event: "order.paid" | "order.refunded"; stream: string; amount_cents: number; currency: string;
  occurred_at?: string; product?: string; src?: string;
}

export function validateRevenueEvent(b: any): RevenueEvent | string {
  if (!b || typeof b !== "object") return "body must be JSON";
  if (typeof b.id !== "string" || !b.id) return "id required";
  if (b.event !== "order.paid" && b.event !== "order.refunded") return "event must be order.paid or order.refunded";
  if (!STREAMS.has(b.stream)) return "unknown stream";
  if (!Number.isInteger(b.amount_cents) || b.amount_cents < 0) return "amount_cents must be a non-negative integer";
  if (typeof b.currency !== "string" || !/^[A-Za-z]{3}$/.test(b.currency)) return "currency must be ISO 4217";
  return b as RevenueEvent;
}

export async function recordRevenue(e: RevenueEvent, source: string): Promise<{ duplicate: boolean }> {
  const amount = e.event === "order.refunded" ? -Math.abs(e.amount_cents) : e.amount_cents;
  const on = e.occurred_at ? new Date(e.occurred_at) : new Date();
  const row = await one<{ id: number }>(
    `INSERT INTO revenue_entries (stream, amount_cents, currency, occurred_on, source, note, external_id)
     VALUES ($1,$2,$3,$4::date,$5,$6,$7) ON CONFLICT (external_id) DO NOTHING RETURNING id`,
    [e.stream, amount, e.currency.toUpperCase(), on.toISOString().slice(0, 10), source, [e.product, e.src ? `src=${e.src}` : null].filter(Boolean).join(" · ") || null, `${source}:${e.event}:${e.id}`]);
  if (!row) return { duplicate: true };
  if (e.event === "order.paid") await trackEvent("purchase", { src: e.src, ref: e.product, valueCents: amount });
  return { duplicate: false };
}

// Sellf → RevenueEvent. purchase.completed amounts are minor units; invoice.paid amounts are MAJOR units.
export function fromSellf(deliveryId: string, body: any): RevenueEvent | null {
  const d = body?.data ?? body;
  switch (body?.event) {
    case "purchase.completed":
      return { id: deliveryId, event: "order.paid", stream: "digital_product", amount_cents: Math.round(Number(d?.order?.amount ?? d?.product?.gross ?? 0)),
        currency: String(d?.product?.currency ?? "GBP"), occurred_at: body.timestamp, product: d?.product?.slug };
    case "invoice.paid":
      return { id: deliveryId, event: "order.paid", stream: "membership", amount_cents: Math.round(Number(d?.invoice?.amountPaid ?? 0) * 100),
        currency: String(d?.invoice?.currency ?? "GBP"), occurred_at: body.timestamp };
    case "refund.issued":
      return { id: deliveryId, event: "order.refunded", stream: "digital_product", amount_cents: Math.round(Number(d?.payment?.amount ?? 0)),
        currency: String(d?.payment?.currency ?? "GBP"), occurred_at: body.timestamp };
    default:
      return null;
  }
}

export async function addManualRevenue(r: { stream: string; amount_cents: number; currency?: string; occurred_on: string; source?: string; note?: string }) {
  if (!STREAMS.has(r.stream)) throw new Error("unknown stream");
  await q("INSERT INTO revenue_entries (stream, amount_cents, currency, occurred_on, source, note) VALUES ($1,$2,$3,$4,$5,$6)",
    [r.stream, r.amount_cents, (r.currency ?? "GBP").toUpperCase(), r.occurred_on, r.source ?? "manual", r.note ?? null]);
}

export async function addExpense(e: { item: string; amount_cents: number; currency?: string; occurred_on: string; recurring?: boolean }) {
  await q("INSERT INTO expenses (item, amount_cents, currency, occurred_on, recurring) VALUES ($1,$2,$3,$4,$5)",
    [e.item, e.amount_cents, (e.currency ?? "GBP").toUpperCase(), e.occurred_on, !!e.recurring]);
}
