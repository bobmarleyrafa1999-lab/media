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

const fill = (s) =>
  s.replace(/\{\{(\w+)\}\}/g, (_, k) => {
    if (cfg[k]) return cfg[k];
    missing.add(k);
    return k.endsWith("_url") ? "#" : "[to be added]";
  });

let n = 0;
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
  n++;
}
console.log(`built ${n} pages`);
if (missing.size) {
  console.warn(`settings still empty in site.config.json: ${[...missing].join(", ")}`);
  if (strict) process.exit(1);
}
