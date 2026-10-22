import crypto from "node:crypto";
import { config } from "./config";

// AES-256-GCM for secrets stored in Postgres. Wire format enc:v1:<iv>:<tag>:<ciphertext> (base64url).
// Format borrowed from oratis/influencex server/encryption.js (MIT); this is a fresh, smaller implementation.
const PREFIX = "enc:v1:";

function key(): Buffer {
  const raw = config().encryptionKey;
  if (raw) {
    const k = Buffer.from(raw, "base64");
    if (k.length !== 32) throw new Error("ENCRYPTION_KEY must be 32 bytes, base64 (openssl rand -base64 32)");
    return k;
  }
  if (config().env === "production") throw new Error("ENCRYPTION_KEY is required in production");
  return crypto.createHash("sha256").update("moodius-dev-only-key").digest();
}

export function encrypt(plain: string): string {
  const iv = crypto.randomBytes(12);
  const c = crypto.createCipheriv("aes-256-gcm", key(), iv);
  const ct = Buffer.concat([c.update(plain, "utf8"), c.final()]);
  return PREFIX + [iv, c.getAuthTag(), ct].map((b) => b.toString("base64url")).join(":");
}

export function decrypt(blob: string): string {
  if (!blob.startsWith(PREFIX)) throw new Error("not an encrypted value");
  const [iv, tag, ct] = blob.slice(PREFIX.length).split(":").map((s) => Buffer.from(s, "base64url"));
  const d = crypto.createDecipheriv("aes-256-gcm", key(), iv);
  d.setAuthTag(tag);
  return Buffer.concat([d.update(ct), d.final()]).toString("utf8");
}

export function sha256(s: string | Buffer): string {
  return crypto.createHash("sha256").update(s).digest("hex");
}

export function randomToken(bytes = 24): string {
  return crypto.randomBytes(bytes).toString("base64url");
}

export function safeEqual(a: string, b: string): boolean {
  const ab = Buffer.from(a);
  const bb = Buffer.from(b);
  return ab.length === bb.length && crypto.timingSafeEqual(ab, bb);
}

export function hmac(secret: string, data: string): string {
  return crypto.createHmac("sha256", secret).update(data).digest("base64url");
}
