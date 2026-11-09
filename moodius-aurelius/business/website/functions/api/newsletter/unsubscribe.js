// GET shows a one-button page; POST (including RFC 8058 one-click from mail clients) unsubscribes.
import { unsubscribe } from "../../../src/newsletter.js";
import { page } from "../../../src/html.js";
import { escapeHtml } from "../../../src/util.js";

export async function onRequestGet({ request }) {
  const token = new URL(request.url).searchParams.get("token") || "";
  return page("Unsubscribe", `<h1>Unsubscribe?</h1><form method="post" action="?token=${escapeHtml(encodeURIComponent(token))}"><button class="btn" type="submit">Yes, unsubscribe me</button></form>`);
}

export async function onRequestPost({ request, env }) {
  const token = new URL(request.url).searchParams.get("token");
  await unsubscribe(env.DB, token);
  return page("Unsubscribed", "<h1>You're unsubscribed.</h1><p>No more emails. If this was a mistake you can sign up again any time.</p>");
}
