// Builds public/**/index.html from pages/*.html: wraps each page body in the shared
// layout and fills {{tokens}} from site.config.json.
//   node scripts/build-pages.mjs            build, warn about empty settings
//   node scripts/build-pages.mjs --strict   fail if any setting is still empty (use before going live)
import { readFileSync, writeFileSync, mkdirSync, readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const cfg = JSON.parse(readFileSync(join(root, "site.config.json"), "utf8"));
const strict = process.argv.includes("--strict");
const layout = readFileSync(join(root, "pages", "_layout.html"), "utf8");
const missing = new Set();

// Optional settings: an empty one hides its <!--if:key-->...<!--/if--> block, or falls back.
const OPTIONAL = { pinterest_url: null, substack_url: "/guide/" };
const fill = (s) =>
  s.replace(/<!--if:(\w+)-->([\s\S]*?)<!--\/if-->/g, (_, k, inner) => (cfg[k] ? inner : "")).replace(/\{\{(\w+)\}\}/g, (_, k) => {
    if (cfg[k]) return cfg[k];
    if (k in OPTIONAL && OPTIONAL[k] !== null) return OPTIONAL[k];
    missing.add(k);
    return k.endsWith("_url") ? "#" : "[to be added]";
  });

let n = 0;
const indexable = [];
for (const file of readdirSync(join(root, "pages")).filter((f) => f.endsWith(".html") && !f.startsWith("_"))) {
  const src = readFileSync(join(root, "pages", file), "utf8");
  const meta = Object.fromEntries([...src.matchAll(/^<!--\s*(\w+):\s*(.*?)\s*-->$/gm)].map((m) => [m[1], m[2]]));
  const body = src.replace(/^<!--\s*\w+:.*-->\n/gm, "");
  const nav = ["/shop/", "/guide/", "/about/"]
    .map((href) => `<a href="${href}"${meta.path?.startsWith(href) ? ' aria-current="page"' : ""}>${{ "/shop/": "Shop", "/guide/": "Free guide", "/about/": "About" }[href]}</a>`)
    .join("");
  const html = fill(
    layout
      .replaceAll("{{title}}", () => meta.title || "Moodius Aurelius")
      .replaceAll("{{description}}", () => meta.description || "")
      .replaceAll("{{page}}", () => meta.page || "")
      .replaceAll("{{robots}}", () => meta.robots || "index, follow")
      .replaceAll("{{canonical}}", () => meta.path || "/")
      .replaceAll("{{nav}}", () => nav)
      .replaceAll("{{body}}", () => body),
  );
  const out = meta.path === "/404" ? join(root, "public", "404.html") : join(root, "public", meta.path, "index.html");
  mkdirSync(dirname(out), { recursive: true });
  writeFileSync(out, html);
  if (meta.path !== "/404" && !(meta.robots || "").includes("noindex")) indexable.push(meta.path);
  n++;
}
// Search engines: robots.txt and a sitemap on the canonical domain.
const site = (cfg.site_url || "").replace(/\/$/, "");
if (site) {
  const urls = indexable.sort().map((p) => `  <url><loc>${site}${p}</loc></url>`).join("\n");
  writeFileSync(join(root, "public", "sitemap.xml"), `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}\n</urlset>\n`);
  writeFileSync(join(root, "public", "robots.txt"), `User-agent: *\nDisallow: /api/\nDisallow: /download/\nDisallow: /backoffice/\nDisallow: /mock-checkout/\nDisallow: /thank-you/\n\nSitemap: ${site}/sitemap.xml\n`);
}
console.log(`built ${n} pages`);
if (missing.size) {
  console.warn(`settings still empty in site.config.json: ${[...missing].join(", ")}`);
  if (strict) process.exit(1);
}
