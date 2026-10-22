// Fills in the seller details everywhere they're needed, in one go.
//   node scripts/configure.mjs --domain moodius.co.uk --operator "Surafel Flynn" \
//        --address "Moodius Aurelius, PO Box 123, London, AB1 2CD" [--support hello@moodius.co.uk] \
//        [--substack https://moodius.substack.com] [--pinterest https://pinterest.com/moodiusaurelius]
// Writes site.config.json and the production vars in wrangler.toml. Nothing here is secret.
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const args = {};
for (let i = 2; i < process.argv.length; i += 2) args[process.argv[i].replace(/^--/, "")] = process.argv[i + 1];

const domain = (args.domain || "").toLowerCase().replace(/^https?:\/\//, "").replace(/\/.*$/, "");
if (!/^[a-z0-9-]+(\.[a-z0-9-]+)+$/.test(domain)) {
  console.error("Give --domain, e.g. --domain moodius.co.uk");
  process.exit(1);
}
const support = args.support || `hello@${domain}`;

const cfgPath = join(root, "site.config.json");
const cfg = JSON.parse(readFileSync(cfgPath, "utf8"));
if (args.operator) cfg.operator_name = args.operator;
if (args.address) cfg.postal_address = args.address;
cfg.support_email = support;
cfg.site_url = `https://${domain}`;
if (args.substack) cfg.substack_url = args.substack;
if (args.pinterest) cfg.pinterest_url = args.pinterest;
writeFileSync(cfgPath, JSON.stringify(cfg, null, 2) + "\n");

const tomlPath = join(root, "wrangler.toml");
let toml = readFileSync(tomlPath, "utf8");
const prodStart = toml.indexOf("[env.production.vars]");
if (prodStart < 0) throw new Error("wrangler.toml has no [env.production.vars] section");
let head = toml.slice(0, prodStart);
let prod = toml.slice(prodStart);
const setVar = (key, value) => {
  const line = `${key} = ${JSON.stringify(value)}`;
  const re = new RegExp(`^${key} = .*$`, "m");
  prod = re.test(prod) ? prod.replace(re, line) : prod.replace("[env.production.vars]", `[env.production.vars]\n${line}`);
};
setVar("SITE_URL", `https://${domain}`);
setVar("SUPPORT_EMAIL", support);
setVar("EMAIL_FROM", `Moodius Aurelius <${support}>`);
if (args.address) setVar("POSTAL_ADDRESS", args.address);
if (args.substack) setVar("SUBSTACK_URL", args.substack);
if (args.pinterest) setVar("PINTEREST_URL", args.pinterest);
writeFileSync(tomlPath, head + prod);

const empty = Object.entries(cfg).filter(([k, v]) => !k.startsWith("_") && !v).map(([k]) => k);
console.log(`Configured for https://${domain} (support ${support}).`);
console.log(empty.length ? `Still empty: ${empty.join(", ")}` : "All site settings filled.");
