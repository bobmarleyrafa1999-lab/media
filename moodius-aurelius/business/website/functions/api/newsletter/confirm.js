// GET /api/newsletter/confirm?token=...  — double opt-in click.
import { config } from "../../../src/config.js";
import { confirm } from "../../../src/newsletter.js";
import { page } from "../../../src/html.js";
import { escapeHtml } from "../../../src/util.js";

export async function onRequestGet({ request, env }) {
  const c = config(env);
  const r = await confirm(c, env.DB, new URL(request.url).searchParams.get("token"));
  if (!r) return page("Link not valid", "<h1>That confirmation link isn't valid</h1><p>It may already have been used. If you're not getting emails, sign up again on the <a href=\"/guide/\">guide page</a>.</p>", { status: 404 });
  return page(
    "You're in",
    `<p class="kicker">Subscribed</p><h1>You're in.</h1>` +
      (r.magnet
        ? `<p>Your guide is ready. We've emailed it too.</p><p><a class="btn" href="${escapeHtml(r.magnet.path)}">Download ${escapeHtml(r.magnet.title)}</a></p>`
        : "<p>Expect about one essay a week.</p>") +
      `<p class="muted">Want to go further? <a href="/shop/the-unexamined-self/">The Unexamined Self</a> is the full 30-day journal.</p>`,
  );
}
