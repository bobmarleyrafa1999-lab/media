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

// `--once` runs one pass and exits (used by the free GitHub Actions setup):
//   worker.ts --once                      poll comments, then process the queue
//   worker.ts --once daily-digest retention ...   run those jobs in order
if (process.argv.includes("--once")) {
  const named = process.argv.slice(process.argv.indexOf("--once") + 1);
  const jobs = named.length ? named : ["poll-comments", "process-queue"];
  (async () => {
    let failed = false;
    for (const j of jobs) await runScheduled(j).catch((e) => { failed = true; log.error("job failed", { job: j, error: (e as Error).message }); });
    await pool().end();
    process.exit(failed ? 1 : 0);
  })();
} else {
  log.info("worker started");
  setInterval(() => void tick(), 60_000);
  void tick();
}
