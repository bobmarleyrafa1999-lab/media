import { migrate, pool, q } from "../src/lib/db";
import { processQueue, pollComments, dailyDigest } from "../src/lib/jobs";
import { config } from "../src/lib/config";

// End-to-end demo on mock data: poll fake comments, classify, route, email (logged), digest.
async function main() {
  await migrate();
  const c = config();
  console.log(`Instagram: ${c.meta.mock ? "MOCK" : "LIVE"} · Claude: ${c.claude.mock ? "offline heuristic" : c.claude.model} · email: ${c.email.mock ? "log only" : "Resend"}\n`);
  console.log("poll:", await pollComments());
  console.log("queue:", await processQueue(50));
  await dailyDigest();
  const rows = await q<any>("SELECT username, text, intent, priority, status, email_kind, draft_reply, flags FROM comments ORDER BY priority DESC NULLS LAST");
  for (const r of rows) {
    console.log(`\n[${r.priority}] @${r.username} → ${r.intent} / ${r.status} / email: ${r.email_kind}`);
    console.log(`   "${r.text}"`);
    if (r.draft_reply) console.log(`   draft: ${r.draft_reply}`);
    if (r.flags?.length) console.log(`   flags: ${r.flags.join(", ")}`);
  }
  const mails = await q<any>("SELECT kind, subject, status FROM email_log ORDER BY id");
  console.log("\nemails:"); for (const m of mails) console.log(`   ${m.status.padEnd(7)} ${m.kind.padEnd(14)} ${m.subject}`);
}
main().catch((e) => { console.error(e); process.exitCode = 1; }).finally(() => pool().end());
