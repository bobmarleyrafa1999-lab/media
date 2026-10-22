import { NextResponse, type NextRequest } from "next/server";
import { recordRevenue, validateRevenueEvent, verifyTimestampedSignature } from "../../../../src/lib/revenue";

export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  const raw = await req.text();
  if (!verifyTimestampedSignature(process.env.REVENUE_WEBHOOK_SECRET ?? "", raw, req.headers.get("x-moodius-signature")))
    return NextResponse.json({ ok: false, error: "invalid signature" }, { status: 401 });
  let body: unknown;
  try { body = JSON.parse(raw); } catch { return NextResponse.json({ ok: false, error: "bad json" }, { status: 400 }); }
  const ev = validateRevenueEvent(body);
  if (typeof ev === "string") return NextResponse.json({ ok: false, error: ev }, { status: 400 });
  const r = await recordRevenue(ev, "storefront");
  return NextResponse.json({ ok: true, ...r });
}
