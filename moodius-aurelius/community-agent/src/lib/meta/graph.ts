import { config } from "../config";
import { decrypt, encrypt } from "../crypto";
import { one, q } from "../db";
import { log } from "../log";
import { mockGraph } from "./mock";

// Thin client for the official Instagram Platform API. Only documented endpoints:
//   GET  /{comment-id}, GET /{media-id}, GET /{ig-user-id}/media, GET /{media-id}/comments
//   POST /{comment-id}/replies                     (public reply)
//   POST /{ig-user-id}/messages {recipient:{comment_id}}   (private reply, once per comment, within 7 days)
//   GET  /{media-id}/insights                      (reach, saved, shares, views, ...)
//   GET  /refresh_access_token                     (Instagram Login long-lived token, 60 days)
// Retry rules adapted from devgine/n8n-ig-comments-management (MIT): 429 / 5xx / network = retry with
// backoff and Retry-After; other 4xx = permanent.

export interface IgComment {
  id: string; text: string; timestamp?: string; username?: string;
  from?: { id: string; username?: string }; media?: { id: string }; parent_id?: string; like_count?: number;
}
export interface IgMedia {
  id: string; caption?: string; media_type?: string; media_product_type?: string; permalink?: string; timestamp?: string;
}

export class GraphError extends Error {
  constructor(message: string, public status: number, public code?: number, public retryable = false, public retryAfterMs?: number) {
    super(message);
  }
}

// Meta error codes that mean "slow down": 4 app limit, 17 user limit, 32 page limit, 613 call rate.
const RATE_CODES = new Set([4, 17, 32, 613]);

export function classifyGraphError(status: number, body: any, retryAfterHeader?: string | null): GraphError {
  const err = body?.error ?? {};
  const code: number | undefined = err.code;
  const msg = `${err.type ?? "GraphError"} ${code ?? ""}: ${err.message ?? `HTTP ${status}`}`.trim();
  const retryAfterMs = retryAfterHeader && /^\d+$/.test(retryAfterHeader) ? Number(retryAfterHeader) * 1000 : undefined;
  const retryable = status === 429 || status >= 500 || (code !== undefined && RATE_CODES.has(code)) || err.is_transient === true;
  return new GraphError(msg, status, code, retryable, retryAfterMs);
}

async function token(): Promise<string> {
  const row = await one<{ ciphertext: string }>("SELECT ciphertext FROM secrets WHERE name = 'ig_access_token'").catch(() => null);
  if (row) return decrypt(row.ciphertext);
  return config().meta.accessToken;
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

async function call<T>(method: "GET" | "POST", path: string, params: Record<string, string> = {}, body?: unknown, attempts = 3): Promise<T> {
  const c = config().meta;
  const url = new URL(`https://${c.host}/${c.version}/${path.replace(/^\//, "")}`);
  for (const [k, v] of Object.entries(params)) url.searchParams.set(k, v);
  const tk = await token();
  let lastErr: GraphError | undefined;
  for (let i = 0; i < attempts; i++) {
    try {
      const res = await fetch(url, {
        method,
        headers: { Authorization: `Bearer ${tk}`, ...(body ? { "Content-Type": "application/json" } : {}) },
        body: body ? JSON.stringify(body) : undefined,
        signal: AbortSignal.timeout(15000),
      });
      const json = await res.json().catch(() => ({}));
      if (res.ok) return json as T;
      lastErr = classifyGraphError(res.status, json, res.headers.get("retry-after"));
    } catch (e) {
      lastErr = new GraphError(`network: ${(e as Error).message}`, 0, undefined, true);
    }
    if (!lastErr.retryable || i === attempts - 1) break;
    const wait = lastErr.retryAfterMs ?? 1000 * 2 ** i + Math.floor(Math.random() * 300);
    log.warn("graph retry", { path, attempt: i + 1, wait, error: lastErr.message });
    await sleep(Math.min(wait, 30000));
  }
  throw lastErr!;
}

export const graph = {
  async getComment(id: string): Promise<IgComment> {
    if (config().meta.mock) return mockGraph.getComment(id);
    return call<IgComment>("GET", id, { fields: "id,text,timestamp,username,from,media,parent_id,like_count" });
  },
  async getMedia(id: string): Promise<IgMedia> {
    if (config().meta.mock) return mockGraph.getMedia(id);
    return call<IgMedia>("GET", id, { fields: "id,caption,media_type,media_product_type,permalink,timestamp" });
  },
  async recentMedia(limit: number): Promise<IgMedia[]> {
    if (config().meta.mock) return mockGraph.recentMedia(limit);
    const r = await call<{ data: IgMedia[] }>("GET", `${config().meta.igUserId}/media`, {
      fields: "id,caption,media_type,media_product_type,permalink,timestamp", limit: String(limit),
    });
    return r.data ?? [];
  },
  async listComments(mediaId: string): Promise<IgComment[]> {
    if (config().meta.mock) return mockGraph.listComments(mediaId);
    const r = await call<{ data: IgComment[] }>("GET", `${mediaId}/comments`, {
      fields: "id,text,timestamp,username,from,parent_id", limit: "50",
    });
    return r.data ?? [];
  },
  async replyToComment(commentId: string, message: string): Promise<{ id: string }> {
    if (config().meta.mock) return mockGraph.replyToComment(commentId, message);
    return call<{ id: string }>("POST", `${commentId}/replies`, {}, { message });
  },
  async privateReply(commentId: string, text: string): Promise<{ recipient_id?: string; message_id?: string }> {
    if (config().meta.mock) return mockGraph.privateReply(commentId, text);
    return call("POST", `${config().meta.igUserId}/messages`, {}, { recipient: { comment_id: commentId }, message: { text } });
  },
  async mediaInsights(media: IgMedia): Promise<Record<string, number>> {
    if (config().meta.mock) return mockGraph.mediaInsights(media.id);
    // Metric availability differs by media type and changes between versions; ask one by one so
    // a retired metric only blanks itself instead of failing the whole call.
    const metrics = ["reach", "views", "saved", "shares", "comments", "likes", "total_interactions"];
    const out: Record<string, number> = {};
    for (const m of metrics) {
      try {
        const r = await call<{ data: { name: string; values?: { value: number }[]; total_value?: { value: number } }[] }>(
          "GET", `${media.id}/insights`, { metric: m }, undefined, 1);
        const d = r.data?.[0];
        const v = d?.values?.[0]?.value ?? d?.total_value?.value;
        if (typeof v === "number") out[m] = v;
      } catch (e) {
        log.debug("insight metric unavailable", { media: media.id, metric: m, error: (e as Error).message });
      }
    }
    return out;
  },
  // Instagram Login tokens last 60 days and can be refreshed once they are 24h old.
  // Facebook Login page tokens derived from a long-lived user token do not expire: nothing to do.
  async refreshToken(): Promise<{ refreshed: boolean; expiresAt?: Date; reason?: string }> {
    const c = config().meta;
    if (c.mock) return { refreshed: false, reason: "mock mode" };
    if (c.host !== "graph.instagram.com") return { refreshed: false, reason: "Facebook Login page token does not expire" };
    const url = new URL("https://graph.instagram.com/refresh_access_token");
    url.searchParams.set("grant_type", "ig_refresh_token");
    url.searchParams.set("access_token", await token());
    const res = await fetch(url, { signal: AbortSignal.timeout(15000) });
    const json: any = await res.json().catch(() => ({}));
    if (!res.ok || !json.access_token) throw classifyGraphError(res.status, json);
    const expiresAt = new Date(Date.now() + Number(json.expires_in ?? 5184000) * 1000);
    await q(
      `INSERT INTO secrets (name, ciphertext, expires_at, updated_at) VALUES ('ig_access_token', $1, $2, now())
       ON CONFLICT (name) DO UPDATE SET ciphertext = EXCLUDED.ciphertext, expires_at = EXCLUDED.expires_at, updated_at = now()`,
      [encrypt(json.access_token), expiresAt],
    );
    return { refreshed: true, expiresAt };
  },
  async subscribeWebhooks(): Promise<unknown> {
    if (config().meta.mock) return { success: true, mock: true };
    return call("POST", "me/subscribed_apps", { subscribed_fields: "comments" });
  },
};

// Instagram has no comment permalink field; the web app links comments as <post permalink>c/<comment id>/.
// Best effort: falls back to the post itself.
export function commentPermalink(mediaPermalink: string | null | undefined, commentId: string): string | null {
  if (!mediaPermalink) return null;
  return `${mediaPermalink.replace(/\/?$/, "/")}c/${commentId}/`;
}
