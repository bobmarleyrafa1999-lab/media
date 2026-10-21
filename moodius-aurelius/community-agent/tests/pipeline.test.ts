import { beforeAll, beforeEach, describe, expect, it } from "vitest";
import { testEnv, resetDb } from "./helpers";
testEnv();
import { one, q, setSetting } from "../src/lib/db";
import { ingestComment, processComment, approveAndPublish, sendKeywordDm } from "../src/lib/pipeline";
import { processQueue, pollComments, dailyDigest, weeklyReport } from "../src/lib/jobs";
import { mockWrites } from "../src/lib/meta/mock";

beforeAll(async () => { await resetDb(); });
beforeEach(async () => { await resetDb(); mockWrites.length = 0; });

const ev = (id: string, text: string, extra: Record<string, unknown> = {}) => ({ commentId: id, mediaId: "mock_media_1", fromId: `u_${id}`, username: `user_${id}`, text, time: Math.floor(Date.now() / 1000), ...extra });

describe("ingest + idempotency", () => {
  it("stores a comment once and enqueues one job, however often the webhook repeats", async () => {
    expect(await ingestComment(ev("c1", "Saving this."), "webhook")).toBe(true);
    expect(await ingestComment(ev("c1", "Saving this."), "webhook")).toBe(false);
    expect(await ingestComment(ev("c1", "Saving this."), "poll")).toBe(false);
    const jobs = await q("SELECT * FROM jobs");
    expect(jobs).toHaveLength(1);
  });
});

describe("draft-only mode (default)", () => {
  it("never publishes, queues drafts, and routes risky comments to a human", async () => {
    await ingestComment(ev("a", "This is exactly me at 2am. Saving this."), "webhook");
    await ingestComment(ev("b", "Lost my dad in August and some days I don't see the point of anything anymore."), "webhook");
    await ingestComment(ev("c", "Hi! We'd love to talk about a paid collaboration. Who do I email?"), "webhook");
    await ingestComment(ev("d", "check my page for crypto signals"), "webhook");
    const r = await processQueue();
    expect(r.done).toBe(4);
    const rows = await q<{ comment_id: string; status: string; intent: string; priority: number; draft_reply: string | null; email_kind: string }>(
      "SELECT comment_id, status, intent, priority, draft_reply, email_kind FROM comments ORDER BY comment_id");
    const by = Object.fromEntries(rows.map((x) => [x.comment_id, x]));
    expect(by.a.status).toBe("needs_approval");
    expect(by.a.draft_reply).toBeTruthy();
    expect(by.b).toMatchObject({ status: "escalated", intent: "crisis", priority: 100, draft_reply: null, email_kind: "urgent" });
    expect(by.c).toMatchObject({ status: "escalated", intent: "sponsorship", email_kind: "urgent" });
    expect(by.d).toMatchObject({ status: "skipped", intent: "spam", email_kind: "none" });
    expect(mockWrites).toHaveLength(0);
    const mails = await q<{ kind: string; subject: string; html: string }>("SELECT kind, subject, html FROM email_log ORDER BY id");
    expect(mails.filter((m) => m.kind === "urgent_alert")).toHaveLength(2);
    const crisisMail = mails.find((m) => m.subject.includes("URGENT"))!;
    expect(crisisMail.html).toContain("Samaritans");
    // each alert has the required fields
    for (const label of ["From", "Comment", "On", "Sentiment / topic", "Priority", "Suggested reply", "Published?"]) expect(mails[0].html).toContain(label);
  });

  it("does not send a second email for the same comment", async () => {
    await ingestComment(ev("x", "We'd love a paid collaboration"), "webhook");
    await processQueue();
    await q("UPDATE comments SET status = 'new' WHERE comment_id = 'x'");
    await processComment("x");
    expect((await q("SELECT 1 FROM email_log WHERE dedupe_key = 'comment:x'"))).toHaveLength(1);
  });
});

describe("human approval and duplicate-reply protection", () => {
  it("publishes once, and refuses a second reply to the same comment", async () => {
    await ingestComment(ev("h", "Which book should I start with if I've never read any philosophy?"), "webhook");
    await processQueue();
    await approveAndPublish("h", "Start with the Enchiridion. It's short.");
    expect(mockWrites).toEqual([{ kind: "public_reply", commentId: "h", text: "Start with the Enchiridion. It's short." }]);
    await expect(approveAndPublish("h", "again")).rejects.toThrow(/already replied/);
    expect(mockWrites).toHaveLength(1);
    expect((await one<{ status: string }>("SELECT status FROM comments WHERE comment_id='h'"))!.status).toBe("published");
  });
});

describe("assisted / controlled modes", () => {
  it("assisted mode still holds offline (heuristic) drafts for a human", async () => {
    await setSetting("agent_mode", "assisted");
    await ingestComment(ev("p", "Love this, saving it"), "webhook");
    await processQueue();
    const row = await one<{ status: string; decision_reason: string }>("SELECT status, decision_reason FROM comments WHERE comment_id='p'");
    expect(row!.status).toBe("needs_approval");
    expect(row!.decision_reason).toMatch(/offline|flagged/);
    expect(mockWrites).toHaveLength(0);
  });
});

describe("keyword DMs", () => {
  it("sends exactly one private reply with a tracked link and logs the funnel", async () => {
    await ingestComment(ev("k", "JOURNAL"), "webhook");
    await processQueue();
    await sendKeywordDm("k", "JOURNAL", "surafel");
    await sendKeywordDm("k", "JOURNAL", "surafel");
    const dms = mockWrites.filter((w) => w.kind === "private_reply");
    expect(dms).toHaveLength(1);
    expect(dms[0].text).toContain("https://agent.example.org/r/journal-worksheet?src=dm_journal");
    const ev2 = await q<{ kind: string }>("SELECT kind FROM conversion_events ORDER BY id");
    expect(ev2.map((e) => e.kind)).toEqual(["comment_keyword", "dm_sent"]);
  });
  it("refuses after the 7-day window", async () => {
    await ingestComment(ev("old", "READ", { time: Math.floor(Date.now() / 1000) - 8 * 86400 }), "webhook");
    await processQueue();
    await sendKeywordDm("old", "READ", "surafel");
    expect(mockWrites.filter((w) => w.kind === "private_reply")).toHaveLength(0);
  });
});

describe("polling fallback, digest, weekly report", () => {
  it("polls mock media, ignores already-seen comments, and builds digest + report", async () => {
    const first = await pollComments();
    expect(first.newComments).toBe(7);
    expect((await pollComments()).newComments).toBe(0);
    await processQueue(50);
    const d = await dailyDigest();
    expect(d.status).toBe("logged");
    const w = await weeklyReport();
    expect(w.status).toBe("logged");
    const digest = await one<{ html: string }>("SELECT html FROM email_log WHERE kind='daily_digest'");
    expect(digest!.html).toContain("quiet.reader");
    const report = await one<{ html: string }>("SELECT html FROM email_log WHERE kind='weekly_report'");
    expect(report!.html).toMatch(/Not enough substantive comments|Make more/);
  });
});
