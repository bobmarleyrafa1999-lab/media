// Short links for bios, captions, pins and DMs: /r/<slug>?src=<source>.
// Fallback only: once COMMUNITY_AGENT_URL is set, /r/* is proxied to the agent, which owns
// the canonical list. Keep slugs in sync with the agent's (lowercase kebab-case).

export function linkTable(c) {
  return {
    shop: "/shop/the-unexamined-self/",
    journal: "/shop/the-unexamined-self/",
    "the-unexamined-self": "/shop/the-unexamined-self/",
    guide: "/guide/",
    "free-guide": "/guide/",
    newsletter: c.substackUrl || "/guide/",
    substack: c.substackUrl || "/guide/",
    instagram: "https://www.instagram.com/moodiusaurelius/",
    pinterest: c.raw.PINTEREST_URL || "https://www.pinterest.com/",
    home: "/",
  };
}

export function resolveLink(c, slug, src) {
  const dest = linkTable(c)[slug];
  if (!dest) return null;
  const url = new URL(dest, c.siteUrl);
  // Only our own pages get ?src= appended; external sites don't need our attribution.
  if (src && url.origin === new URL(c.siteUrl).origin) url.searchParams.set("src", src);
  return url.toString();
}
