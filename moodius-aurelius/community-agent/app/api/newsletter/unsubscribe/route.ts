import { NextResponse, type NextRequest } from "next/server";
import { config } from "../../../../src/lib/config";
import { unsubscribe } from "../../../../src/lib/newsletter";

export const dynamic = "force-dynamic";

// Handles the page's button and RFC 8058 one-click (List-Unsubscribe-Post) requests.
export async function POST(req: NextRequest) {
  let t = req.nextUrl.searchParams.get("t") ?? "";
  if (!t) { const f = await req.formData().catch(() => null); t = String(f?.get("t") ?? ""); }
  await unsubscribe(t);
  return NextResponse.redirect(new URL("/newsletter/unsubscribe?done=1", config().baseUrl), 303);
}
