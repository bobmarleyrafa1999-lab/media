import { classifyComment } from "./classifier";
import { config } from "./config";
import { audit, one, q } from "./db";
import { commentAlert, type CommentMailData } from "./email/templates";
import { sendMail, underHourlyCap } from "./email/send";
import { log } from "./log";
import { commentPermalink, graph } from "./meta/graph";
import type { CommentEvent } from "./meta/webhook";
import { decide } from "./policy";
import { enqueue } from "./queue";
import { detectKeyword, type Keyword } from "./safety";
import { priorityOf, URGENT, type Classification } from "./taxonomy";
import { trackEvent } from "./tracking";

export interface CommentRow {
  comment_id: string; media_id: string; parent_id: string | null; from_id: string | null; username: string | null; text: string;
  status: string; sentiment: string | null; intent: string | null; topic: string | null; flags: string[]; risk: string | null;
  priority: number | null; substantive: boolean | null; draft_reply: string | null; follow_up_question: string | null;
  final_reply: string | null; dm_keyword: string | null; dm_status: string | null; received_at: Date; commented_at: Date | null;
  published_at: Date | null; email_kind: string | null;
}

// Step 1 (webhook or poll): store once, enqueue once. Safe to call any number of times.
export async function ingestComment(e: CommentEvent, source: "webhook" | "poll" | "mock"): Promise<boolean> {
  const row = await one<{ comment_id: string }>(
    `INSERT INTO comments (comment_id, media_id, parent_id, from_id, username, text, commented_at, source)
     VALUES ($1,$2,$3,$4,$5,$6,$7,$8) ON CONFLICT (comment_id) DO NOTHING RETURNING comment_id`,
    [e.commentId, e.mediaId, e.parentId ?? null, e.fromId ?? null, e.username ?? null, e.text,
     e.time ? new Date(e.time * 1000) : null, source],
  );
  if (!row) return false;
  await enqueue("process_comment", { commentId: e.commentId }, { dedupeKey: `comment:${e.commentId}` });
  return true;
}

async function ensureMedia(mediaId: string) {
  const existing = await one<{ caption: string | null; media_product_type: string | null; permalink: string | null }>(
    "SELECT caption, media_product_type, permalink FROM media WHERE media_id = $1", [mediaId]);
  if (existing) return existing;
  const m = await graph.getMedia(mediaId);
  await q(
    `INSERT INTO media (media_id, caption, media_type, media_product_type, permalink, posted_at, category)
     VALUES ($1,$2,$3,$4,$5,$6,$7) ON CONFLICT (media_id) DO NOTHING`,
    [m.id, m.caption ?? null, m.media_type ?? null, m.media_product_type ?? null, m.permalink ?? null, m.timestamp ?? null, categoryFromCaption(m.caption)],
  );
  return { caption: m.caption ?? null, media_product_type: m.media_product_type ?? null, permalink: m.permalink ?? null };
}

// Content category for "engagement by theme". Explicit tag [cat:xyz] in the caption wins, then keywords.
export function categoryFromCaption(caption?: string | null): string {
  const c = (caption ?? "").toLowerCase();
  const tag = c.match(/\[cat:([a-z_]+)\]/);
  if (tag) return tag[1];
  const rules: [string, RegExp][] = [
    ["jung_shadow", /\b(jung|shadow|projection|persona)\b/], ["masculinity_eq", /\b(masculin|men |man who|emotional intelligence|vulnerab)/],
    ["relationships", /\b(love|attachment|relationship|lonel|dating|partner)/], ["journaling", /\b(journal|write it down|evening review)/],
    ["discipline_identity", /\b(discipline|identity|habit|purpose|burnout)/], ["grief_meaning", /\b(grief|death|mortality|meaning|suffering)/],
    ["stoicism", /\b(stoic|seneca|marcus|epictetus)/],
  ];
  return rules.find(([, r]) => r.test(c))?.[0] ?? "other";
}

function composeReply(c: Classification): string {
  const d = c.draft_reply.trim();
  if (!d) return "";
  if (c.follow_up_question && !/\?\s*$/.test(d)) return `${d} ${c.follow_up_question.trim()}`;
  return d;
}

// Step 2: classify, draft, decide, maybe publish, maybe DM, notify. Idempotent: only runs for status 'new'.
export async function processComment(commentId: string): Promise<void> {
  const row = await one<CommentRow>("SELECT * FROM comments WHERE comment_id = $1", [commentId]);
  if (!row || row.status !== "new") return;

  const media = await ensureMedia(row.media_id);
  let parentText: string | null = null;
  if (row.parent_id) {
    const p = await one<{ text: string }>("SELECT text FROM comments WHERE comment_id = $1", [row.parent_id]);
    parentText = p?.text ?? (await graph.getComment(row.parent_id).then((x) => x.text).catch(() => null));
  }
  const history = row.from_id
    ? await q<{ comment: string; reply: string | null }>(
      `SELECT text AS comment, coalesce(final_reply, draft_reply) AS reply FROM comments
        WHERE from_id = $1 AND comment_id <> $2 ORDER BY received_at DESC LIMIT 5`, [row.from_id, commentId])
    : [];
  const recent = await q<{ r: string }>(
    `SELECT coalesce(final_reply, draft_reply) AS r FROM comments
      WHERE coalesce(final_reply, draft_reply) IS NOT NULL AND comment_id <> $1 ORDER BY received_at DESC LIMIT 40`, [commentId]);

  const c = await classifyComment({
    comment: row.text, username: row.username, caption: media.caption, mediaType: media.media_product_type,
    parentText, history, recentReplies: recent.map((x) => x.r),
  });
  const priority = priorityOf(c, row.text.length);
  const keyword = detectKeyword(row.text);
  const decision = await decide(c);
  const status = c.action === "skip" ? "skipped" : c.action === "escalate" ? "escalated" : decision.publish ? "approved" : "needs_approval";
  const reply = composeReply(c);

  await q(
    `UPDATE comments SET status = $2, sentiment = $3, intent = $4, topic = $5, flags = $6, risk = $7, priority = $8,
       substantive = $9, classifier = $10, draft_reply = $11, follow_up_question = $12, decision_reason = $13,
       dm_keyword = $14, updated_at = now() WHERE comment_id = $1`,
    [commentId, status, c.sentiment, c.intent, c.topic, c.flags, c.risk, priority, c.substantive, JSON.stringify(c),
     reply || null, c.follow_up_question || null, decision.reason, keyword],
  );

  let published = false;
  if (decision.publish && reply) {
    try {
      await publishReply(commentId, reply, "auto");
      published = true;
    } catch (e) {
      log.error("auto publish failed", { commentId, error: (e as Error).message });
    }
  }

  if (keyword) {
    await trackEvent("comment_keyword", { src: `kw_${keyword.toLowerCase()}`, ref: commentId });
    if (config().dm.enabled) await sendKeywordDm(commentId, keyword, "auto").catch((e) => log.error("keyword dm failed", { commentId, error: (e as Error).message }));
  }

  await notify(commentId, URGENT.has(c.intent) || c.intent === "crisis", published);
}

export async function publishReply(commentId: string, text: string, actor: string): Promise<string> {
  const claim = await one<{ id: number }>(
    `INSERT INTO outbound_actions (kind, comment_id, actor) VALUES ('public_reply', $1, $2)
     ON CONFLICT (kind, comment_id) DO UPDATE SET status = 'pending', actor = EXCLUDED.actor, error = NULL
       WHERE outbound_actions.status = 'failed'
     RETURNING id`, [commentId, actor]);
  if (!claim) throw Object.assign(new Error("already replied to this comment"), { retryable: false });
  try {
    const r = await graph.replyToComment(commentId, text);
    await q("UPDATE outbound_actions SET status = 'sent', remote_id = $2 WHERE id = $1", [claim.id, r.id]);
    await q(
      `UPDATE comments SET status = 'published', final_reply = $2, reply_comment_id = $3, published_at = now(),
         published_by = $4, updated_at = now() WHERE comment_id = $1`, [commentId, text, r.id, actor]);
    await audit(actor, "publish_reply", commentId, { text });
    return r.id;
  } catch (e) {
    await q("UPDATE outbound_actions SET status = 'failed', error = $2 WHERE id = $1", [claim.id, (e as Error).message]);
    await q("UPDATE comments SET error = $2, updated_at = now() WHERE comment_id = $1", [commentId, (e as Error).message]);
    throw e;
  }
}

// Private replies: Meta allows exactly one per comment, within 7 days. Links point at our own
// tracked redirect, and the text says plainly that nothing was signed up for.
export const KEYWORD_DMS: Record<Keyword, { slug: string; text: (url: string) => string }> = {
  JOURNAL: { slug: "journal-worksheet", text: (u) => `Here's the guided journaling worksheet you asked for: ${u}\nNo sign-up, it's yours.` },
  READ: { slug: "reading-list", text: (u) => `Here's the reading list, with the translations I'd start with: ${u}` },
  REFLECT: { slug: "reflection-exercise", text: (u) => `Here's tonight's reflection exercise. Ten minutes, pen and paper: ${u}` },
  NEWSLETTER: { slug: "newsletter", text: (u) => `Here's the newsletter page: ${u}\nYou're only added if you choose to subscribe there.` },
  TOOLS: { slug: "stoic-tools-guide", text: (u) => `Here's the free guide, 7 Stoic tools for when emotions are loud: ${u}` },
};

export async function sendKeywordDm(commentId: string, keyword: Keyword, actor: string) {
  const row = await one<{ commented_at: Date | null; received_at: Date }>("SELECT commented_at, received_at FROM comments WHERE comment_id = $1", [commentId]);
  if (!row) throw new Error("unknown comment");
  const at = row.commented_at ?? row.received_at;
  if (Date.now() - new Date(at).getTime() > 7 * 86400_000) {
    await q("UPDATE comments SET dm_status = 'skipped', error = 'private reply window (7 days) has passed' WHERE comment_id = $1", [commentId]);
    return;
  }
  const claim = await one<{ id: number }>(
    `INSERT INTO outbound_actions (kind, comment_id, actor) VALUES ('private_reply', $1, $2)
     ON CONFLICT (kind, comment_id) DO NOTHING RETURNING id`, [commentId, actor]);
  if (!claim) return; // already sent (or attempted): Meta allows one.
  const dm = KEYWORD_DMS[keyword];
  const url = `${config().baseUrl}/r/${dm.slug}?src=dm_${keyword.toLowerCase()}`;
  try {
    const r = await graph.privateReply(commentId, dm.text(url));
    await q("UPDATE outbound_actions SET status = 'sent', remote_id = $2 WHERE id = $1", [claim.id, r.message_id ?? null]);
    await q("UPDATE comments SET dm_status = 'sent', dm_sent_at = now() WHERE comment_id = $1", [commentId]);
    await trackEvent("dm_sent", { src: `dm_${keyword.toLowerCase()}`, ref: commentId });
    await audit(actor, "private_reply", commentId, { keyword });
  } catch (e) {
    await q("UPDATE outbound_actions SET status = 'failed', error = $2 WHERE id = $1", [claim.id, (e as Error).message]);
    await q("UPDATE comments SET dm_status = 'failed', error = $2 WHERE comment_id = $1", [commentId, (e as Error).message]);
    throw e;
  }
}

async function notify(commentId: string, urgent: boolean, published: boolean) {
  const r = await one<CommentRow & { caption: string | null; permalink: string | null }>(
    `SELECT c.*, m.caption, m.permalink FROM comments c LEFT JOIN media m ON m.media_id = c.media_id WHERE c.comment_id = $1`, [commentId]);
  if (!r) return;
  const cfg = config().email;
  let kind: "urgent" | "immediate" | "digest" | "none" = "none";
  if (r.status === "skipped") kind = "none";
  else if (urgent) kind = "urgent";
  else if (cfg.policy === "substantive" && r.substantive && (r.priority ?? 0) >= cfg.minPriority && (await underHourlyCap())) kind = "immediate";
  else kind = "digest";
  await q("UPDATE comments SET email_kind = $2 WHERE comment_id = $1", [commentId, kind]);
  if (kind === "none" || kind === "digest") return;

  const data: CommentMailData = {
    commentId, username: r.username, text: r.text, mediaCaption: r.caption, mediaPermalink: r.permalink,
    commentPermalink: commentPermalink(r.permalink, commentId), sentiment: r.sentiment, topic: r.topic, intent: r.intent,
    priority: r.priority, suggested: r.draft_reply, followUp: r.follow_up_question, published, publishedText: published ? r.draft_reply : null,
    status: published ? "published" : r.status, flags: r.flags ?? [],
  };
  const mail = commentAlert(data, kind === "urgent");
  const res = await sendMail({ kind: kind === "urgent" ? "urgent_alert" : "comment_alert", dedupeKey: `comment:${commentId}`, to: cfg.owner, ...mail });
  if (res.status === "sent" || res.status === "logged") await q("UPDATE comments SET email_notified_at = now() WHERE comment_id = $1", [commentId]);
}

// Human actions from the dashboard.
export async function approveAndPublish(commentId: string, text: string, actor = "surafel") {
  const sent = await one("SELECT 1 FROM outbound_actions WHERE kind = 'public_reply' AND comment_id = $1 AND status <> 'failed'", [commentId]);
  if (sent) throw Object.assign(new Error("already replied to this comment"), { retryable: false });
  if (!text.trim()) throw new Error("empty reply");
  await q("UPDATE comments SET status = 'approved', final_reply = $2, updated_at = now() WHERE comment_id = $1", [commentId, text]);
  return publishReply(commentId, text, actor);
}

export async function rejectComment(commentId: string, actor = "surafel", reason = "rejected in dashboard") {
  await q("UPDATE comments SET status = 'rejected', decision_reason = $2, updated_at = now() WHERE comment_id = $1", [commentId, reason]);
  await audit(actor, "reject", commentId);
}

export async function markRepliedManually(commentId: string, text: string | null, actor = "surafel") {
  await q(`UPDATE comments SET status = 'published', final_reply = coalesce($2, final_reply), published_at = now(),
           published_by = 'manual', updated_at = now() WHERE comment_id = $1`, [commentId, text]);
  await audit(actor, "mark_replied_manually", commentId);
}
