// Runs before every Function route (see public/_routes.json).
// 1. One domain: paths owned by the community agent are proxied to it when COMMUNITY_AGENT_URL
//    is set (contract: community-agent/INTEGRATION-CONTRACT.md section 4).
// 2. Uniform error handling so a crash never leaks a stack trace.
import { config } from "../src/config.js";
import { json } from "../src/util.js";

const AGENT_PATHS = [/^\/r\//, /^\/links\/?$/, /^\/newsletter/, /^\/free\//, /^\/privacy-newsletter\/?$/, /^\/api\/newsletter\//, /^\/api\/webhooks\//, /^\/api\/integrations\//, /^\/api\/cron\//, /^\/api\/admin\//, /^\/admin/, /^\/_agent\//];

export const isAgentPath = (pathname) => AGENT_PATHS.some((re) => re.test(pathname));

export async function onRequest(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  const c = config(env);
  if (c.communityAgentUrl && isAgentPath(url.pathname)) {
    const target = new URL(url.pathname + url.search, c.communityAgentUrl);
    const headers = new Headers(request.headers);
    headers.set("x-forwarded-host", url.host);
    headers.set("x-forwarded-proto", url.protocol.replace(":", ""));
    return fetch(target.toString(), {
      method: request.method,
      headers,
      body: ["GET", "HEAD"].includes(request.method) ? undefined : request.body,
      redirect: "manual",
    });
  }
  try {
    return await context.next();
  } catch (err) {
    console.error(`${request.method} ${url.pathname} failed:`, err?.stack || err);
    const status = err?.status && err.status < 500 ? err.status : 500;
    return json({ ok: false, error: status === 500 ? "Something went wrong. Please try again." : err.message }, status);
  }
}
