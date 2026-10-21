import crypto from "node:crypto";

// Meta signs every webhook POST: X-Hub-Signature-256: sha256=<hex HMAC-SHA256(raw body, App Secret)>.
// The HMAC must be computed over the exact raw bytes, before any JSON parsing.
export function verifyMetaSignature(rawBody: string | Buffer, header: string | null, appSecret: string): boolean {
  if (!appSecret || !header || !header.startsWith("sha256=")) return false;
  const expected = crypto.createHmac("sha256", appSecret).update(rawBody).digest("hex");
  const given = header.slice("sha256=".length);
  if (given.length !== expected.length) return false;
  return crypto.timingSafeEqual(Buffer.from(given, "hex"), Buffer.from(expected, "hex"));
}

export function signForTest(rawBody: string, appSecret: string): string {
  return "sha256=" + crypto.createHmac("sha256", appSecret).update(rawBody).digest("hex");
}

// GET handshake when the callback URL is saved in the App Dashboard.
export function verifyHandshake(params: URLSearchParams, verifyToken: string): string | null {
  const mode = params.get("hub.mode");
  const token = params.get("hub.verify_token");
  const challenge = params.get("hub.challenge");
  if (mode === "subscribe" && verifyToken && token === verifyToken && challenge) return challenge;
  return null;
}
