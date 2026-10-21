import { beforeEach, describe, expect, it } from "vitest";
import { testEnv, resetDb } from "./helpers";
testEnv();
import { q } from "../src/lib/db";
import { verifyTimestampedSignature, signTimestamped, validateRevenueEvent, recordRevenue, fromSellf } from "../src/lib/revenue";
import { makeSession, sessionValid, passwordOk, cronAuthorized } from "../src/lib/auth";

beforeEach(async () => { await resetDb(); });

describe("revenue webhook", () => {
  it("accepts a fresh signature and rejects tampered, stale or missing ones", () => {
    const body = JSON.stringify({ id: "o1" });
    const h = signTimestamped("s3cret", body, 1_000_000);
    expect(verifyTimestampedSignature("s3cret", body, h, 300, 1_000_100)).toBe(true);
    expect(verifyTimestampedSignature("s3cret", body + " ", h, 300, 1_000_100)).toBe(false);
    expect(verifyTimestampedSignature("other", body, h, 300, 1_000_100)).toBe(false);
    expect(verifyTimestampedSignature("s3cret", body, h, 300, 1_000_400)).toBe(false);
    expect(verifyTimestampedSignature("s3cret", body, null)).toBe(false);
  });

  it("validates the contract, records once, and stores refunds as negative", async () => {
    expect(typeof validateRevenueEvent({ id: "x", event: "order.paid", stream: "crypto", amount_cents: 1, currency: "GBP" })).toBe("string");
    const paid = validateRevenueEvent({ id: "o1", event: "order.paid", stream: "digital_product", amount_cents: 1400, currency: "gbp", src: "ig_bio" });
    expect(typeof paid).toBe("object");
    expect(await recordRevenue(paid as any, "store")).toEqual({ duplicate: false });
    expect(await recordRevenue(paid as any, "store")).toEqual({ duplicate: true });
    await recordRevenue({ ...(paid as any), event: "order.refunded" }, "store");
    const rows = await q<{ amount_cents: number; currency: string }>("SELECT amount_cents, currency FROM revenue_entries ORDER BY id");
    expect(rows.map((r) => Number(r.amount_cents))).toEqual([1400, -1400]);
    expect(rows[0].currency).toBe("GBP");
    expect(await q("SELECT 1 FROM conversion_events WHERE kind = 'purchase'")).toHaveLength(1);
  });

  it("maps Sellf events, converting invoice amounts from major units", () => {
    expect(fromSellf("d1", { event: "purchase.completed", data: { order: { amount: 1400 }, product: { currency: "GBP", slug: "journal" } } }))
      .toMatchObject({ event: "order.paid", stream: "digital_product", amount_cents: 1400, product: "journal" });
    expect(fromSellf("d2", { event: "invoice.paid", data: { invoice: { amountPaid: 5, currency: "GBP" } } })).toMatchObject({ stream: "membership", amount_cents: 500 });
    expect(fromSellf("d3", { event: "refund.issued", data: { payment: { amount: 1400 } } })).toMatchObject({ event: "order.refunded" });
    expect(fromSellf("d4", { event: "lead.created" })).toBeNull();
  });
});

describe("admin auth", () => {
  it("signs sessions that expire and can't be forged", () => {
    const now = Date.now();
    const s = makeSession(now);
    expect(sessionValid(s, now + 1000)).toBe(true);
    expect(sessionValid(s, now + 8 * 86400_000)).toBe(false);
    expect(sessionValid(s.replace(/.$/, (c) => (c === "a" ? "b" : "a")), now)).toBe(false);
    expect(sessionValid("9999999999999.deadbeef", now)).toBe(false);
    expect(sessionValid(undefined, now)).toBe(false);
  });
  it("checks the password and the cron bearer token", () => {
    expect(passwordOk("correct horse battery")).toBe(true);
    expect(passwordOk("wrong")).toBe(false);
    expect(cronAuthorized("Bearer cron-secret")).toBe(true);
    expect(cronAuthorized("Bearer nope")).toBe(false);
    expect(cronAuthorized(null)).toBe(false);
  });
});
