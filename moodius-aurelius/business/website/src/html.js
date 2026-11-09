// Minimal server-rendered pages (download page, newsletter confirm/unsubscribe) in the site's look.
import { escapeHtml } from "./util.js";

export function page(title, inner, { status = 200, noindex = true } = {}) {
  const html = `<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${escapeHtml(title)} · Moodius Aurelius</title>
${noindex ? '<meta name="robots" content="noindex, nofollow">' : ""}
<link rel="stylesheet" href="/assets/site.css">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
</head>
<body>
<header class="masthead"><a class="wordmark" href="/"><span class="sq" aria-hidden="true"></span>MOODIUS</a></header>
<main class="narrow stack">${inner}</main>
<footer class="foot"><p>Moodius Aurelius · <a href="/legal/privacy/">Privacy</a> · <a href="/legal/terms/">Terms</a> · <a href="/orders/">Find my order</a></p></footer>
</body>
</html>`;
  return new Response(html, {
    status,
    headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store", "x-robots-tag": "noindex", "referrer-policy": "no-referrer" },
  });
}
