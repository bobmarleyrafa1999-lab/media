import { config } from "../config";
import { log } from "../log";

// Brand research from the brand's OWN public pages only: homepage plus a few standard paths,
// robots.txt respected, one request per second, an honest user agent. No scraping of social
// platforms, no email-guessing services, no personal profiles.

const UA = "MoodiusResearchBot/0.1 (+manual review; contact via site)";
const PATHS = ["/", "/contact", "/pages/contact", "/partners", "/affiliates", "/affiliate", "/creators", "/collaborations", "/press", "/about"];
const SIGNALS: [string, RegExp][] = [
  ["affiliate programme", /\baffiliate (program|programme|partners?)\b/i],
  ["creator / ambassador programme", /\b(creator|ambassador|influencer) (program|programme|partnerships?|collective)\b/i],
  ["partnerships contact", /\b(partnerships?|collaborations?|collabs?)@/i],
  ["press / PR contact", /\b(press|pr|media)@/i],
  ["ships to UK", /\b(ships? to (the )?uk|uk shipping|united kingdom delivery|free uk delivery)\b/i],
  ["B Corp / sustainability claim", /\b(b ?corp|certified b corporation)\b/i],
];
const ROLE = /^(partnerships?|partners|collabs?|collaborations?|press|pr|media|marketing|hello|info|contact|creators?|affiliates?|influencers?)@/i;

export interface PageFetch { url: string; status: number; html: string }
export type Fetcher = (url: string) => Promise<PageFetch>;

const defaultFetcher: Fetcher = async (url) => {
  const res = await fetch(url, { headers: { "User-Agent": UA, Accept: "text/html" }, redirect: "follow", signal: AbortSignal.timeout(12000) });
  const html = res.ok ? (await res.text()).slice(0, 600_000) : "";
  return { url: res.url || url, status: res.status, html };
};

export function robotsAllows(robots: string, path: string): boolean {
  let applies = false;
  const disallow: string[] = [];
  for (const raw of robots.split(/\r?\n/)) {
    const line = raw.replace(/#.*/, "").trim();
    const [k, ...rest] = line.split(":");
    const v = rest.join(":").trim();
    if (/^user-agent$/i.test(k)) applies = v === "*" || /moodius/i.test(v);
    else if (applies && /^disallow$/i.test(k) && v) disallow.push(v);
  }
  return !disallow.some((d) => path.startsWith(d));
}

export function textOf(html: string): string {
  return html.replace(/<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>/gi, " ").replace(/<[^>]+>/g, " ").replace(/&nbsp;|&amp;/g, " ").replace(/\s+/g, " ").trim();
}

export interface DiscoveryResult {
  website: string; title: string | null; description: string | null;
  emails: { email: string; role: boolean; source_url: string }[];
  evidence: { claim: string; url: string }[];
  pagesChecked: string[]; blockedByRobots: string[];
}

export async function researchBrand(website: string, fetcher: Fetcher = defaultFetcher, delayMs = 1000): Promise<DiscoveryResult> {
  const base = new URL(website.startsWith("http") ? website : `https://${website}`);
  const origin = base.origin;
  const out: DiscoveryResult = { website: origin, title: null, description: null, emails: [], evidence: [], pagesChecked: [], blockedByRobots: [] };
  let robots = "";
  try { const r = await fetcher(`${origin}/robots.txt`); robots = r.status === 200 ? r.html : ""; } catch { /* no robots = allowed */ }
  const seen = new Set<string>();
  for (const p of PATHS) {
    if (!robotsAllows(robots, p)) { out.blockedByRobots.push(p); continue; }
    let page: PageFetch;
    try { page = await fetcher(origin + p); } catch (e) { log.debug("discovery fetch failed", { url: origin + p, error: (e as Error).message }); continue; }
    if (page.status !== 200 || !page.html || seen.has(page.url)) continue;
    seen.add(page.url);
    out.pagesChecked.push(page.url);
    if (p === "/") {
      out.title = page.html.match(/<title[^>]*>([^<]{1,160})<\/title>/i)?.[1]?.trim() ?? null;
      out.description = page.html.match(/<meta[^>]+name=["']description["'][^>]+content=["']([^"']{1,300})/i)?.[1]?.trim() ?? null;
    }
    const text = textOf(page.html) + " " + [...page.html.matchAll(/mailto:([^"'?\s>]+)/gi)].map((m) => m[1]).join(" ");
    for (const m of text.matchAll(/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g)) {
      const email = m[0].toLowerCase().replace(/\.$/, "");
      if (/\.(png|jpg|svg|webp)$/.test(email) || /example\.|sentry|wixpress/.test(email)) continue;
      if (!out.emails.some((e) => e.email === email)) out.emails.push({ email, role: ROLE.test(email), source_url: page.url });
    }
    for (const [claim, re] of SIGNALS) if (re.test(text) && !out.evidence.some((e) => e.claim === claim)) out.evidence.push({ claim, url: page.url });
    if (delayMs) await new Promise((r) => setTimeout(r, delayMs));
  }
  return out;
}

// Best public contact = a role address on the brand's own domain. Personal-name addresses are
// returned but never auto-selected.
export function pickContact(r: DiscoveryResult): { email: string; source_url: string } | null {
  const host = new URL(r.website).hostname.replace(/^www\./, "");
  const own = r.emails.filter((e) => e.email.endsWith(`@${host}`) || e.email.split("@")[1]?.endsWith(`.${host}`));
  const order = ["partnerships", "partners", "collab", "creators", "affiliate", "influencer", "press", "pr", "media", "marketing", "hello", "contact", "info"];
  const roles = own.filter((e) => e.role).sort((a, b) => order.findIndex((o) => a.email.startsWith(o)) - order.findIndex((o) => b.email.startsWith(o)));
  return roles[0] ? { email: roles[0].email, source_url: roles[0].source_url } : null;
}

