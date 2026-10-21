import { NextResponse, type NextRequest } from "next/server";
import { config } from "../../../../src/lib/config";
import { sha256 } from "../../../../src/lib/crypto";
import { one } from "../../../../src/lib/db";
import { log } from "../../../../src/lib/log";
import { verifyHandshake, verifyMetaSignature } from "../../../../src/lib/meta/signature";
import { parseCommentWebhook } from "../../../../src/lib/meta/webhook";
import { ingestComment } from "../../../../src/lib/pipeline";
import { processQueue } from "../../../../src/lib/jobs";
import { after } from "next/server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

// GET: subscription handshake from the App Dashboard.
export async function GET(req: NextRequest) {
  const challenge = verifyHandshake(req.nextUrl.searchParams, config().meta.verifyToken);
  return challenge ? new NextResponse(challenge, { status: 200 }) : new NextResponse("forbidden", { status: 403 });
}

// POST: verify X-Hub-Signature-256 over the raw body, dedupe the delivery, store comments,
// answer 200 fast, then process in the background (n8n's process-queue run is the safety net).
export async function POST(req: NextRequest) {
  const raw = await req.text();
  if (!verifyMetaSignature(raw, req.headers.get("x-hub-signature-256"), config().meta.appSecret)) {
    log.warn("webhook signature rejected");
    return new NextResponse("invalid signature", { status: 401 });
  }
  let body: unknown;
  try { body = JSON.parse(raw); } catch { return new NextResponse("bad json", { status: 400 }); }
  const fresh = await one("INSERT INTO webhook_events (body_sha256, payload) VALUES ($1, $2) ON CONFLICT DO NOTHING RETURNING id", [sha256(raw), raw]);
  if (!fresh) return NextResponse.json({ ok: true, duplicate: true });
  const parsed = parseCommentWebhook(body, config().meta.igUserId);
  let stored = 0;
  for (const e of parsed.events) if (await ingestComment(e, "webhook")) stored++;
  if (stored) after(() => processQueue(10).then(() => undefined).catch((e) => log.error("background processing failed", { error: (e as Error).message })));
  return NextResponse.json({ ok: true, stored, ignored: parsed.ignored.length });
}
