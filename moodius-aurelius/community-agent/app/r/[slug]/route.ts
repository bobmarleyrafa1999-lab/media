import { NextResponse, type NextRequest } from "next/server";
import { config } from "../../../src/lib/config";
import { cleanSrc, resolveLink, trackEvent } from "../../../src/lib/tracking";
import { allow, clientIp } from "../../../src/lib/ratelimit";

export const dynamic = "force-dynamic";

// First-party redirect: logs one cookieless click (slug + source only), then 302s to the destination
// with ?src= carried along so the storefront can attribute the purchase.
export async function GET(req: NextRequest, ctx: { params: Promise<{ slug: string }> }) {
  const { slug } = await ctx.params;
  const link = await resolveLink(slug.toLowerCase());
  if (!link) return NextResponse.redirect(new URL("/links", config().baseUrl), 302);
  const src = cleanSrc(req.nextUrl.searchParams.get("src"));
  const isBot = /bot|crawler|spider|preview|facebookexternalhit|slurp/i.test(req.headers.get("user-agent") ?? "");
  if (!isBot && allow(`r:${clientIp(req.headers)}:${slug}`, 20)) await trackEvent("link_click", { slug: link.slug, src: src ?? "direct" });
  const dest = new URL(link.destination, config().publicSiteUrl);
  // The visitor's own source (ig_bio, dm_journal...) wins over a default baked into the destination.
  if (src) dest.searchParams.set("src", src);
  if (link.kind === "newsletter" && dest.origin === new URL(config().baseUrl).origin && !dest.searchParams.has("src")) dest.searchParams.set("src", `link_${link.slug}`);
  const res = NextResponse.redirect(dest, 302);
  res.headers.set("Cache-Control", "no-store");
  res.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  return res;
}
