// Structured JSON logs (one line per event) so Docker / any log shipper can parse them.
type Level = "debug" | "info" | "warn" | "error";

const SECRET_KEYS = /token|secret|password|authorization|api[_-]?key/i;
// LOG_PUBLIC=true (GitHub Actions on a public repo, where anyone can read the logs): also hide
// people's words, names and addresses.
const PERSONAL_KEYS = /^(subject|text|comment|username|to|email|html|body|caption|reply)$/i;
const ORDER: Record<Level, number> = { debug: 0, info: 1, warn: 2, error: 3 };

function scrub(value: unknown, depth = 0): unknown {
  if (depth > 4 || value === null || typeof value !== "object") return value;
  if (Array.isArray(value)) return value.map((v) => scrub(v, depth + 1));
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(value as Record<string, unknown>)) {
    const hide = SECRET_KEYS.test(k) || (process.env.LOG_PUBLIC === "true" && PERSONAL_KEYS.test(k));
    out[k] = hide ? "[redacted]" : scrub(v, depth + 1);
  }
  return out;
}

function emit(level: Level, msg: string, fields?: Record<string, unknown>) {
  const min = (process.env.LOG_LEVEL as Level) in ORDER ? (process.env.LOG_LEVEL as Level) : "info";
  if (ORDER[level] < ORDER[min]) return;
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
