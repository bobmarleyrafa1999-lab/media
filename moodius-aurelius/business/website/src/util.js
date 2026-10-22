// Small helpers shared by every Function. Web-standard APIs only, so the same
// code runs on Cloudflare Workers and on Node 20+ (used by the unit tests).

const enc = new TextEncoder();

export const nowIso = () => new Date().toISOString();

export function randomBytes(n) {
  const b = new Uint8Array(n);
  crypto.getRandomValues(b);
  return b;
}

export function b64url(bytes) {
  let s = "";
  for (const x of bytes) s += String.fromCharCode(x);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

const B32 = "abcdefghijkmnpqrstuvwxyz23456789"; // no l, o, 0, 1
export function randomId(prefix, len = 16) {
  const b = randomBytes(len);
  let s = "";
  for (const x of b) s += B32[x % 32];
  return `${prefix}_${s}`;
}

export const randomToken = () => b64url(randomBytes(32));

const hex = (buf) => [...new Uint8Array(buf)].map((x) => x.toString(16).padStart(2, "0")).join("");

export async function sha256Hex(text) {
  return hex(await crypto.subtle.digest("SHA-256", enc.encode(text)));
}

export async function hmacSha256Hex(secret, message) {
  const key = await crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  return hex(await crypto.subtle.sign("HMAC", key, enc.encode(message)));
}

// Constant-time string comparison (both strings are hex or tokens we control the format of).
export function safeEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string") return false;
  const len = Math.max(a.length, b.length);
  let diff = a.length ^ b.length;
  for (let i = 0; i < len; i++) diff |= (a.charCodeAt(i) || 0) ^ (b.charCodeAt(i) || 0);
  return diff === 0;
}

export function json(data, status = 200, headers = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", ...headers },
  });
}

// Attribution source, same rule as the community agent: lowercase [a-z0-9_-], max 40 chars.
export function cleanSrc(value) {
  if (!value) return null;
  const s = String(value).toLowerCase().replace(/[^a-z0-9_-]/g, "").slice(0, 40);
  return s || null;
}

export const cleanSlug = (value) => (/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(value || "") && value.length <= 60 ? value : null);

export function normalizeEmail(value) {
  const e = String(value || "").trim().toLowerCase();
  return /^[^\s@]{1,64}@[^\s@]+\.[a-z]{2,}$/.test(e) && e.length <= 254 ? e : null;
}

export const escapeHtml = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

export function addDays(iso, days) {
  return new Date(new Date(iso).getTime() + days * 86400000).toISOString();
}
