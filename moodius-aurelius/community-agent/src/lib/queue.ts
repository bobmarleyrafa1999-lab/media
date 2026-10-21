import { q, one } from "./db";
import { log } from "./log";

// Postgres-backed job queue: idempotent enqueue (dedupe_key), SKIP LOCKED claiming,
// exponential backoff, and a dead-letter state ('failed') that triggers an error email.

export async function enqueue(kind: string, payload: Record<string, unknown>, opts: { dedupeKey?: string; delaySec?: number; maxAttempts?: number } = {}) {
  await q(
    `INSERT INTO jobs (kind, payload, dedupe_key, run_after, max_attempts)
     VALUES ($1, $2, $3, now() + make_interval(secs => $4), $5)
     ON CONFLICT (dedupe_key) DO NOTHING`,
    [kind, JSON.stringify(payload), opts.dedupeKey ?? null, opts.delaySec ?? 0, opts.maxAttempts ?? 5],
  );
}

interface JobRow { id: number; kind: string; payload: Record<string, unknown>; attempts: number; max_attempts: number }

export type Handler = (payload: Record<string, unknown>) => Promise<void>;

export async function runJobs(handlers: Record<string, Handler>, limit = 20, onDead?: (job: JobRow, err: Error) => Promise<void>) {
  const result = { done: 0, retried: 0, failed: 0 };
  for (let i = 0; i < limit; i++) {
    const job = await one<JobRow>(
      `UPDATE jobs SET status = 'running', attempts = attempts + 1, updated_at = now()
        WHERE id = (SELECT id FROM jobs WHERE status = 'queued' AND run_after <= now()
                    ORDER BY run_after, id FOR UPDATE SKIP LOCKED LIMIT 1)
        RETURNING id, kind, payload, attempts, max_attempts`,
    );
    if (!job) break;
    const h = handlers[job.kind];
    try {
      if (!h) throw new Error(`no handler for ${job.kind}`);
      await h(job.payload);
      await q("UPDATE jobs SET status = 'done', last_error = NULL, updated_at = now() WHERE id = $1", [job.id]);
      result.done++;
    } catch (e) {
      const err = e as Error & { retryable?: boolean };
      const permanent = err.retryable === false || job.attempts >= job.max_attempts;
      const backoff = Math.min(3600, 30 * 2 ** (job.attempts - 1));
      await q(
        `UPDATE jobs SET status = $2, last_error = $3, run_after = now() + make_interval(secs => $4), updated_at = now() WHERE id = $1`,
        [job.id, permanent ? "failed" : "queued", err.message.slice(0, 2000), backoff],
      );
      log.error("job failed", { id: job.id, kind: job.kind, attempt: job.attempts, permanent, error: err.message });
      if (permanent) { result.failed++; if (onDead) await onDead(job, err).catch(() => undefined); }
      else result.retried++;
    }
  }
  // Recover jobs stuck in 'running' after a crash.
  await q(`UPDATE jobs SET status = 'queued', updated_at = now() WHERE status = 'running' AND updated_at < now() - interval '10 minutes'`);
  return result;
}
