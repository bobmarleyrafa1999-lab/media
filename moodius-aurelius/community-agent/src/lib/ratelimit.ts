// In-process token bucket per key (IP or route). Enough for one small server; behind several
// instances, put the limit in the reverse proxy instead.
const buckets = new Map<string, { tokens: number; at: number }>();

export function allow(key: string, perMinute: number): boolean {
  const now = Date.now();
  const b = buckets.get(key) ?? { tokens: perMinute, at: now };
  b.tokens = Math.min(perMinute, b.tokens + ((now - b.at) / 60000) * perMinute);
  b.at = now;
  if (b.tokens < 1) { buckets.set(key, b); return false; }
  b.tokens -= 1;
  buckets.set(key, b);
  if (buckets.size > 5000) for (const [k, v] of buckets) if (now - v.at > 600000) buckets.delete(k);
  return true;
}

export function clientIp(h: Headers): string {
  return (h.get("cf-connecting-ip") ?? h.get("x-forwarded-for")?.split(",")[0] ?? h.get("x-real-ip") ?? "unknown").trim();
}
