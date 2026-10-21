// Structured JSON logs (one line per event) so Docker / any log shipper can parse them.
type Level = "debug" | "info" | "warn" | "error";

const SECRET_KEYS = /token|secret|password|authorization|api[_-]?key/i;

function scrub(value: unknown, depth = 0): unknown {
  if (depth > 4 || value === null || typeof value !== "object") return value;
  if (Array.isArray(value)) return value.map((v) => scrub(v, depth + 1));
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(value as Record<string, unknown>)) {
    out[k] = SECRET_KEYS.test(k) ? "[redacted]" : scrub(v, depth + 1);
  }
  return out;
}

function emit(level: Level, msg: string, fields?: Record<string, unknown>) {
  if (level === "debug" && process.env.LOG_LEVEL !== "debug") return;
  const line = JSON.stringify({ t: new Date().toISOString(), level, msg, ...(scrub(fields ?? {}) as object) });
  if (level === "error" || level === "warn") console.error(line);
  else console.log(line);
}

export const log = {
  debug: (m: string, f?: Record<string, unknown>) => emit("debug", m, f),
  info: (m: string, f?: Record<string, unknown>) => emit("info", m, f),
  warn: (m: string, f?: Record<string, unknown>) => emit("warn", m, f),
  error: (m: string, f?: Record<string, unknown>) => emit("error", m, f),
};
