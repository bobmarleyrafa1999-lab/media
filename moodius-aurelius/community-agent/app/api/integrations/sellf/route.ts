import { NextResponse, type NextRequest } from "next/server";
import { fromSellf, recordRevenue, verifyTimestampedSignature } from "../../../../src/lib/revenue";

export const dynamic = "force-dynamic";

// Sellf outgoing webhook: X-Sellf-Signature (t=…,v1=…), X-Sellf-Delivery-Id for dedupe.
export async function POST(req: NextRequest) {
  const raw = await req.text();
  if (!verifyTimestampedSignature(process.env.SELLF_WEBHOOK_SECRET ?? "", raw, req.headers.get("x-sellf-signature")))
    return NextResponse.json({ ok: false, error: "invalid signature" }, { status: 401 });
  const body = JSON.parse(raw);
  const id = req.headers.get("x-sellf-delivery-id") ?? body?.id;
  if (!id || (body?.id && body.id !== id)) return NextResponse.json({ ok: false, error: "delivery id mismatch" }, { status: 400 });
  const ev = fromSellf(String(id), body);
  if (!ev) return NextResponse.json({ ok: true, ignored: body?.event ?? "unknown" });
  return NextResponse.json({ ok: true, ...(await recordRevenue(ev, "sellf")) });
}
