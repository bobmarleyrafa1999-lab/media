import { config } from "./config";
import { one, q } from "./db";
import { dailyDigest as digestTpl, errorAlert, weeklyReport as weeklyTpl } from "./email/templates";
import { sendMail } from "./email/send";
import { log } from "./log";
import { graph } from "./meta/graph";
import { categoryFromCaption, ingestComment, processComment } from "./pipeline";
import { runJobs } from "./queue";
import { overview, recommendations, themes } from "./analytics";
import { dueFollowUps } from "./sponsors/crm";
import { purgeUnconfirmed } from "./newsletter";

const handlers = {
  process_comment: async (p: Record<string, unknown>) => processComment(String(p.commentId)),
};

export async function processQueue(limit = 25) {
  return runJobs(handlers, limit, async (job, err) => {
    const m = errorAlert(`job ${job.kind} failed ${job.attempts} times`, `${err.message}\npayload: ${JSON.stringify(job.payload)}`);
    await sendMail({ kind: "error_alert", dedupeKey: `job-dead:${job.id}`, to: config().email.owner, ...m });
  });
}

// Fallback for missed webhooks (and the only source until Meta grants Advanced Access for the
// comments webhook): reads comments on the latest posts and ingests any not seen yet.
export async function pollComments() {
  const media = await graph.recentMedia(config().meta.pollLookbackMedia);
  let found = 0;
  for (const m of media) {
    await q(
      `INSERT INTO media (media_id, caption, media_type, media_product_type, permalink, posted_at, category)
       VALUES ($1,$2,$3,$4,$5,$6,$7)
       ON CONFLICT (media_id) DO UPDATE SET caption = EXCLUDED.caption, permalink = EXCLUDED.permalink, fetched_at = now()`,
      [m.id, m.caption ?? null, m.media_type ?? null, m.media_product_type ?? null, m.permalink ?? null, m.timestamp ?? null, categoryFromCaption(m.caption)],
    );
    const comments = await graph.listComments(m.id);
    for (const c of comments) {
      if (c.from?.id === config().meta.igUserId || c.username === config().meta.igUsername) continue;
      if (c.timestamp && Date.now() - Date.parse(c.timestamp) > 7 * 86400_000) continue;
      const isNew = await ingestComment({
        commentId: c.id, mediaId: m.id, parentId: c.parent_id, fromId: c.from?.id, username: c.username ?? c.from?.username,
        text: c.text ?? "", time: c.timestamp ? Math.floor(Date.parse(c.timestamp) / 1000) : undefined,
      }, config().meta.mock ? "mock" : "poll");
      if (isNew) found++;
    }
  }
  return { media: media.length, newComments: found };
}

export async function syncInsights() {
  const media = await graph.recentMedia(25);
  let stored = 0;
  for (const m of media) {
    const ins = await graph.mediaInsights(m);
    if (!Object.keys(ins).length) continue;
    await q(
      `INSERT INTO media_insights (media_id, reach, views, saved, shares, comments, likes, total_interactions, raw)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
       ON CONFLICT (media_id, captured_on) DO UPDATE SET reach = EXCLUDED.reach, views = EXCLUDED.views, saved = EXCLUDED.saved,
         shares = EXCLUDED.shares, comments = EXCLUDED.comments, likes = EXCLUDED.likes, total_interactions = EXCLUDED.total_interactions, raw = EXCLUDED.raw`,
      [m.id, ins.reach ?? null, ins.views ?? null, ins.saved ?? null, ins.shares ?? null, ins.comments ?? null, ins.likes ?? null, ins.total_interactions ?? null, JSON.stringify(ins)],
    );
    stored++;
  }
  return { media: media.length, withInsights: stored };
}

export async function refreshToken() {
  try {
    return await graph.refreshToken();
  } catch (e) {
    const m = errorAlert("Instagram token refresh failed", `${(e as Error).message}\nIf this keeps failing, generate a new long-lived token (docs/03-meta-setup.md, step 6).`);
    await sendMail({ kind: "error_alert", dedupeKey: `token-refresh:${new Date().toISOString().slice(0, 10)}`, to: config().email.owner, ...m });
    throw e;
  }
}

function localDate(d = new Date()) {
  return new Intl.DateTimeFormat("en-GB", { timeZone: config().timezone, year: "numeric", month: "short", day: "2-digit" }).format(d);
}

// Everything that did NOT get its own email in the last 24h, plus anything still waiting.
export async function dailyDigest() {
  const items = await q<{ comment_id: string; username: string | null; text: string; intent: string | null; priority: number | null; status: string; draft_reply: string | null }>(
    `SELECT comment_id, username, text, intent, priority, status, draft_reply FROM comments
      WHERE status <> 'skipped' AND (
        (email_kind = 'digest' AND received_at > now() - interval '24 hours')
        OR status IN ('needs_approval','escalated'))
      ORDER BY priority DESC NULLS LAST, received_at DESC LIMIT 60`);
  const o = await overview(1);
  const stats = { received: o.comments.received, answered: o.comments.answered, waiting: o.comments.waiting, "keyword DMs": o.funnel.dmsSent, "new subscribers": o.subscribers.newConfirmed };
  const label = localDate();
  const m = digestTpl(label, items.map((i) => ({ commentId: i.comment_id, username: i.username, text: i.text, intent: i.intent, priority: i.priority, status: i.status, draft: i.draft_reply })), stats);
  return sendMail({ kind: "daily_digest", dedupeKey: `digest:${new Date().toISOString().slice(0, 10)}`, to: config().email.owner, ...m });
}

export async function weeklyReport() {
  const o = await overview(7);
  const t = await themes(7);
  const recs = await recommendations(28);
  const pct = (x: number | null) => (x == null ? "n/a" : `${(x * 100).toFixed(1)}%`);
  const money = (c: number) => `£${(c / 100).toFixed(2)}`;
  const sections: { title: string; rows: [string, string][] }[] = [
    { title: "Comments", rows: [
      ["Received", String(o.comments.received)], ["Answered", `${o.comments.answered} (${o.comments.autoAnswered} automatically)`],
      ["Still waiting", String(o.comments.waiting)], ["Median response delay", o.comments.medianDelayMin == null ? "n/a" : `${o.comments.medianDelayMin} min`],
      ["Conversations (commenter came back)", String(o.comments.conversations)], ["Flagged crisis", String(o.comments.crisis)],
    ] },
    { title: "Conversion", rows: [
      ["Keyword comments", String(o.funnel.keywordComments)], ["DMs sent", String(o.funnel.dmsSent)], ["Link clicks", String(o.funnel.linkClicks)],
      ["Newsletter signups confirmed", String(o.funnel.signupsConfirmed)], ["Unsubscribes", String(o.funnel.unsubscribes)],
    ] },
    { title: "Sponsorship & revenue", rows: [
      ["Prospects by stage", Object.entries(o.sponsors.byStage).map(([k, v]) => `${k} ${v}`).join(", ") || "none"],
      ["Outreach reply rate", pct(o.sponsors.replyRate)], ["Revenue (7 days)", money(o.money.revenueCents)], ["Expenses (7 days)", money(o.money.expensesCents)],
    ] },
    { title: "Themes", rows: t.slice(0, 8).map((r) => [r.category, `${r.substantive} substantive / ${r.comments} comments, ${r.questions} questions, ${r.keyword} keyword requests`] as [string, string]) },
  ];
  const label = `week to ${localDate()}`;
  const m = weeklyTpl(label, sections, recs);
  return sendMail({ kind: "weekly_report", dedupeKey: `weekly:${new Date().toISOString().slice(0, 10)}`, to: config().email.owner, ...m });
}

export async function sponsorFollowUps() {
  const due = await dueFollowUps();
  return { dueTasks: due.length };
}

// Retention from the privacy notice: comments 12 months, unconfirmed sign-ups 30 days, logs 90 days.
export async function retention() {
  const comments = await q<{ comment_id: string }>("DELETE FROM comments WHERE received_at < now() - interval '12 months' RETURNING comment_id");
  const subs = await purgeUnconfirmed();
  await q("DELETE FROM webhook_events WHERE received_at < now() - interval '30 days'");
  await q("DELETE FROM jobs WHERE status = 'done' AND updated_at < now() - interval '30 days'");
  await q("UPDATE email_log SET html = NULL WHERE created_at < now() - interval '90 days'");
  return { commentsDeleted: comments.length, unconfirmedDeleted: subs };
}

export const scheduled = {
  retention,
  "process-queue": processQueue,
  "poll-comments": pollComments,
  "sync-insights": syncInsights,
  "refresh-token": refreshToken,
  "daily-digest": dailyDigest,
  "weekly-report": weeklyReport,
  "sponsor-followups": sponsorFollowUps,
  // One-off, after the Meta app is set up: subscribes the account to comment webhooks.
  "subscribe-webhooks": () => graph.subscribeWebhooks(),
} as const;
export type ScheduledJob = keyof typeof scheduled;

export async function runScheduled(name: string) {
  const fn = (scheduled as Record<string, () => Promise<unknown>>)[name];
  if (!fn) throw new Error(`unknown job ${name}`);
  const started = Date.now();
  const result = await fn();
  log.info("scheduled job done", { job: name, ms: Date.now() - started, result: result as Record<string, unknown> });
  return result;
}

export async function health() {
  const r = await one<{ queued: string; failed: string }>(
    "SELECT count(*) FILTER (WHERE status='queued') AS queued, count(*) FILTER (WHERE status='failed') AS failed FROM jobs");
  const c = config();
  return {
    ok: true, mode: { meta: c.meta.mock ? "mock" : "live", claude: c.claude.mock ? "heuristic" : c.claude.model, email: c.email.mock ? "log-only" : "resend" },
    queue: { queued: Number(r?.queued ?? 0), failed: Number(r?.failed ?? 0) },
  };
}
