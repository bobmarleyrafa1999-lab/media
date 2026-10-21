import { NextResponse, type NextRequest } from "next/server";
import { cronAuthorized } from "../../../../src/lib/auth";
import { runScheduled } from "../../../../src/lib/jobs";
import { log } from "../../../../src/lib/log";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

// Called by n8n schedules (n8n/workflows/00-scheduler.json) with Authorization: Bearer $CRON_SECRET.
export async function POST(req: NextRequest, ctx: { params: Promise<{ job: string }> }) {
  if (!cronAuthorized(req.headers.get("authorization"))) return new NextResponse("unauthorized", { status: 401 });
  const { job } = await ctx.params;
  try {
    const result = await runScheduled(job);
    return NextResponse.json({ ok: true, job, result });
  } catch (e) {
    log.error("cron job failed", { job, error: (e as Error).message });
    return NextResponse.json({ ok: false, job, error: (e as Error).message }, { status: 500 });
  }
}
