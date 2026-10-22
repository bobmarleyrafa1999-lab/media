import { migrate, pool, q } from "../src/lib/db";

// Real companies with their public websites only: no contacts, no scores, no claims. Each one starts
// as a Prospect and must be researched and scored before anything else happens. Seeded from
// strategy/crm/contacts.csv (CR001-CR005) plus the brief's categories.
const SPONSORS: [string, string, string, string][] = [
  ["Penguin Classics", "https://www.penguin.co.uk", "Books and reading", "UK"],
  ["Vintage Books", "https://www.vintage-books.co.uk", "Books and reading", "UK"],
  ["Bookshop.org UK", "https://uk.bookshop.org", "Books and reading", "UK"],
  ["Leuchtturm1917", "https://www.leuchtturm1917.com", "Stationery and journals", "DE"],
  ["Moleskine", "https://www.moleskine.com", "Stationery and journals", "IT"],
  ["Baron Fig", "https://www.baronfig.com", "Stationery and journals", "US"],
  ["Field Notes", "https://fieldnotesbrand.com", "Stationery and journals", "US"],
  ["Day One", "https://dayoneapp.com", "Productivity software", "US"],
  ["Readwise", "https://readwise.io", "Productivity software", "US"],
  ["Headspace", "https://www.headspace.com", "Mindfulness and meditation", "US"],
  ["Waking Up", "https://www.wakingup.com", "Mindfulness and meditation", "US"],
  ["Blinkist", "https://www.blinkist.com", "Educational products", "DE"],
  ["Bellroy", "https://bellroy.com", "Everyday accessories", "AU"],
  ["Aesop", "https://www.aesop.com", "Men's grooming and lifestyle", "AU"],
];

// Link-in-bio defaults. Destinations starting with / live on the public site (storefront).
const LINKS: [string, string, string, string, string | null, number][] = [
  ["newsletter", "The newsletter: one essay a week", "/newsletter", "newsletter", null, 10],
  ["substack", "Read the essays on Substack", process.env.SUBSTACK_URL ?? "https://moodiusaurelius.substack.com", "newsletter", null, 20],
  ["stoic-tools-guide", "Free guide: 7 Stoic tools for when emotions are loud", process.env.TOOLS_GUIDE_URL ?? "/free/reflection-exercise", "resource", null, 30],
  ["journal-worksheet", "Free: guided journaling worksheet", "/free/journal-worksheet", "resource", null, 40],
  ["reading-list", "A reading list for the inner life", "/free/reading-list", "resource", null, 50],
  ["reflection-exercise", "Tonight's reflection: the evening review", "/free/reflection-exercise", "resource", null, 60],
  // Same slugs and destinations as the storefront's fallback table (business/website/src/links.js).
  // Position 1000+ = alias: redirects work, but it isn't listed on /links.
  ["guide", "Free guide", "/guide/", "resource", null, 35],
  ["free-guide", "Free guide", "/guide/", "resource", null, 1036],
  ["shop", "The Unexamined Self: a 30-day journal", "/shop/the-unexamined-self/", "product", null, 70],
  ["journal", "The Unexamined Self: a 30-day journal", "/shop/the-unexamined-self/", "product", null, 1071],
  ["the-unexamined-self", "The Unexamined Self: a 30-day journal", "/shop/the-unexamined-self/", "product", null, 1072],
  ["home", "Website", "/", "resource", null, 1095],
  ["instagram", "Instagram @moodiusaurelius", "https://www.instagram.com/moodiusaurelius/", "resource", null, 90],
];

async function main() {
  await migrate();
  for (const [name, website, category, country] of SPONSORS) {
    await q("INSERT INTO sponsors (name, website, category, country, notes) VALUES ($1,$2,$3,$4,'Seeded prospect: not researched, not contacted') ON CONFLICT (website) DO NOTHING", [name, website, category, country]);
  }
  for (const [slug, label, destination, kind, disclosure, position] of LINKS) {
    await q("INSERT INTO links (slug, label, destination, kind, disclosure, position) VALUES ($1,$2,$3,$4,$5,$6) ON CONFLICT (slug) DO NOTHING", [slug, label, destination, kind, disclosure, position]);
  }
  console.log(`seeded ${SPONSORS.length} prospects and ${LINKS.length} links`);
}
main().catch((e) => { console.error(e); process.exitCode = 1; }).finally(() => pool().end());
