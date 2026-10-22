import { NextResponse } from "next/server";
import { health } from "../../../src/lib/jobs";

export const dynamic = "force-dynamic";
export async function GET() {
  try { return NextResponse.json(await health()); }
  catch (e) { return NextResponse.json({ ok: false, error: (e as Error).message }, { status: 503 }); }
}
