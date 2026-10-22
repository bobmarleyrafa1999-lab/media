import { config } from "../config";

const esc = (s: unknown) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]!);

const shell = (title: string, body: string) => `<!doctype html><html><body style="margin:0;background:#F3EFE7;font-family:Inter,Helvetica,Arial,sans-serif;color:#1B1F24">
<div style="max-width:600px;margin:0 auto;padding:24px">
<div style="font-family:'Playfair Display',Georgia,serif;font-size:20px;margin-bottom:16px">${esc(title)}</div>
${body}
<p style="color:#6b6760;font-size:12px;margin-top:32px">Moodius community agent${hasAdmin() ? ` · <a href="${config().baseUrl}/admin" style="color:#C9742E">dashboard</a>` : ""} · notification settings live in .env (NOTIFY_POLICY, NOTIFY_MAX_PER_HOUR)</p>
</div></body></html>`;

const row = (k: string, v: string) => `<tr><td style="padding:6px 10px 6px 0;color:#6b6760;vertical-align:top;white-space:nowrap">${esc(k)}</td><td style="padding:6px 0">${v}</td></tr>`;
// NO_ADMIN=true: the free GitHub Actions setup has no web dashboard, so emails carry no dashboard buttons.
const hasAdmin = () => process.env.NO_ADMIN !== "true";
const btn = (href: string, label: string) => `<a href="${esc(href)}" style="display:inline-block;background:#1B1F24;color:#F3EFE7;padding:10px 14px;border-radius:6px;text-decoration:none;margin:4px 8px 0 0">${esc(label)}</a>`;

export interface CommentMailData {
  commentId: string; username: string | null; text: string; mediaCaption: string | null; mediaPermalink: string | null;
  commentPermalink: string | null; sentiment: string | null; topic: string | null; intent: string | null; priority: number | null;
  suggested: string | null; followUp: string | null; published: boolean; publishedText: string | null; status: string; flags: string[];
}

export function commentAlert(d: CommentMailData, urgent: boolean) {
  const tag = urgent ? (d.intent === "crisis" ? "URGENT: needs you now" : d.intent === "sponsorship" ? "Sponsorship enquiry" : "Needs you") : "New comment";
  const subject = `[Moodius] ${tag}: @${d.username ?? "unknown"} · ${d.text.slice(0, 50)}${d.text.length > 50 ? "…" : ""}`;
  const crisisNote = d.intent === "crisis"
    ? `<p style="background:#fff3e8;border-left:3px solid #C9742E;padding:10px">This comment may be from someone at risk. Nothing was posted. Consider a short, human reply that points to local help (UK: Samaritans 116 123; elsewhere: findahelpline.com), and do not leave it in a public argument.</p>` : "";
  const html = shell(tag, `${crisisNote}
<table style="font-size:14px;border-collapse:collapse;width:100%">
${row("From", `@${esc(d.username)}`)}
${row("Comment", `<strong>${esc(d.text)}</strong>`)}
${row("On", `${esc((d.mediaCaption ?? "").slice(0, 120))}${d.mediaPermalink ? ` · <a href="${esc(d.mediaPermalink)}" style="color:#C9742E">open post</a>` : ""}`)}
${row("Intent", esc(d.intent))}
${row("Sentiment / topic", `${esc(d.sentiment)} · ${esc(d.topic)}`)}
${row("Priority", `${esc(d.priority)}/100`)}
${row("Suggested reply", d.suggested ? esc(d.suggested) : "<em>none: answer personally</em>")}
${d.followUp ? row("Follow-up question", esc(d.followUp)) : ""}
${row("Published?", d.published ? `Yes, automatically: “${esc(d.publishedText)}”` : `No (status: ${esc(d.status)})`)}
${d.flags.length ? row("Flags", esc(d.flags.join(", "))) : ""}
</table>
<p>${hasAdmin() ? btn(`${config().baseUrl}/admin/queue?focus=${encodeURIComponent(d.commentId)}`, "Review / edit / approve") : ""}${d.commentPermalink ? btn(d.commentPermalink, "Reply on Instagram") : ""}</p>`);
  const text = `${tag}\n@${d.username}: ${d.text}\nPriority ${d.priority}/100 · ${d.intent} · ${d.sentiment}\nSuggested: ${d.suggested ?? "(answer personally)"}\nPublished: ${d.published ? "yes" : "no"}\n${hasAdmin() ? `${config().baseUrl}/admin/queue?focus=${d.commentId}` : d.commentPermalink ?? ""}`;
  return { subject, html, text };
}

export interface DigestItem { username: string | null; text: string; intent: string | null; priority: number | null; status: string; draft: string | null; commentId: string }

export function dailyDigest(dateLabel: string, items: DigestItem[], stats: Record<string, number>) {
  const list = items.map((i) => `<li style="margin-bottom:10px"><strong>@${esc(i.username)}</strong> <span style="color:#6b6760">(${esc(i.intent)}, ${esc(i.priority)}, ${esc(i.status)})</span><br>${esc(i.text)}${i.draft ? `<br><span style="color:#3A4049">↳ draft: ${esc(i.draft)}</span>` : ""}</li>`).join("");
  const html = shell(`Daily comment digest · ${dateLabel}`, `
<p>${Object.entries(stats).map(([k, v]) => `${esc(k)}: <strong>${v}</strong>`).join(" · ")}</p>
${items.length ? `<ol style="padding-left:18px;font-size:14px">${list}</ol>` : "<p>No comments waiting.</p>"}
${hasAdmin() ? `<p>${btn(`${config().baseUrl}/admin/queue`, "Open the queue")}</p>` : ""}`);
  return { subject: `[Moodius] Daily digest ${dateLabel}: ${items.length} comments to look at`, html };
}

export function weeklyReport(weekLabel: string, sections: { title: string; rows: [string, string][] }[], recommendations: string[]) {
  const body = sections.map((s) => `<h3 style="font-family:Georgia,serif;margin:20px 0 6px">${esc(s.title)}</h3><table style="font-size:14px">${s.rows.map(([k, v]) => row(k, esc(v))).join("")}</table>`).join("")
    + `<h3 style="font-family:Georgia,serif;margin:20px 0 6px">What to make next</h3><ul>${recommendations.map((r) => `<li>${esc(r)}</li>`).join("")}</ul>`;
  return { subject: `[Moodius] Weekly engagement report · ${weekLabel}`, html: shell(`Weekly report · ${weekLabel}`, body) };
}

export function errorAlert(what: string, detail: string) {
  return { subject: `[Moodius] Error: ${what}`, html: shell("Something failed", `<p><strong>${esc(what)}</strong></p><pre style="white-space:pre-wrap;font-size:12px">${esc(detail)}</pre>`) };
}

export function newsletterConfirm(confirmUrl: string, unsubscribeUrl: string) {
  return {
    subject: "Confirm your Moodius Aurelius subscription",
    html: shell("One click to confirm", `<p>You (or someone using this address) asked to receive the Moodius Aurelius newsletter. Confirm and you'll get the next essay. Ignore this email and nothing happens: we won't email you again.</p>
<p>${btn(confirmUrl, "Yes, subscribe me")}</p>
<p style="font-size:12px;color:#6b6760">Changed your mind later? <a href="${esc(unsubscribeUrl)}" style="color:#C9742E">Unsubscribe</a> at any time.</p>`),
  };
}
