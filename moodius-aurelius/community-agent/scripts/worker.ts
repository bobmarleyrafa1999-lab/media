import { runScheduled } from "../src/lib/jobs";
import { log } from "../src/lib/log";
import { pool } from "../src/lib/db";

// Optional: runs the schedule without n8n (e.g. `npm run worker` under systemd or a container).
// Same jobs, same intervals as n8n/workflows/00-scheduler.json.
const EVERY: [string, number][] = [["process-queue", 60], ["poll-comments", 300], ["sync-insights", 43200], ["refresh-token", 604800], ["retention", 86400], ["sponsor-followups", 86400]];
const last = new Map<string, number>();

async function tick() {
  const now = Date.now();
  for (const [job, s] of EVERY) {
    if (now - (last.get(job) ?? 0) < s * 1000) continue;
    last.set(job, now);
    await runScheduled(job).catch((e) => log.error("worker job failed", { job, error: (e as Error).message }));
  }
  const hm = new Intl.DateTimeFormat("en-GB", { timeZone: process.env.APP_TIMEZONE ?? "Europe/Madrid", hour: "2-digit", minute: "2-digit", weekday: "short" }).formatToParts(new Date());
  const h = hm.find((p) => p.type === "hour")?.value, m = hm.find((p) => p.type === "minute")?.value, d = hm.find((p) => p.type === "weekday")?.value;
  if (h === "20" && m === "30") await runScheduled("daily-digest").catch(() => undefined);
  if (d === "Mon" && h === "08" && m === "00") await runScheduled("weekly-report").catch(() => undefined);
}

if (process.argv.includes("--once")) {
  Promise.all(["poll-comments", "process-queue"].map((j) => runScheduled(j))).finally(() => pool().end());
} else {
  log.info("worker started");
  setInterval(() => void tick(), 60_000);
  void tick();
}
