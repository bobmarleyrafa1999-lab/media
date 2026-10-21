// Sponsor fit score, 0-100. Each dimension is 0-5 and MUST carry a reason; a dimension with no
// evidence stays null and counts as 0, so an unresearched brand can never look like a good fit.

export const DIMENSIONS = {
  audience_fit: { weight: 25, label: "Audience and brand relevance" },
  sponsorship_likelihood: { weight: 20, label: "Sponsorship likelihood (creator, affiliate or partner programme seen)" },
  product_quality: { weight: 15, label: "Product quality" },
  geography: { weight: 10, label: "Geographic suitability (sells/ships to UK and EU)" },
  reputation: { weight: 10, label: "Reputation" },
  format_fit: { weight: 10, label: "Campaign format fit (reel, carousel, newsletter)" },
  commercial_value: { weight: 10, label: "Estimated commercial value" },
} as const;
export type Dimension = keyof typeof DIMENSIONS;

export type Scores = Partial<Record<Dimension, { score: number; reason: string; evidence_url?: string } | null>>;

export function totalScore(s: Scores): { total: number; missing: Dimension[] } {
  let total = 0;
  const missing: Dimension[] = [];
  for (const [k, d] of Object.entries(DIMENSIONS) as [Dimension, (typeof DIMENSIONS)[Dimension]][]) {
    const v = s[k];
    if (!v || typeof v.score !== "number" || !v.reason) { missing.push(k); continue; }
    total += (Math.max(0, Math.min(5, v.score)) / 5) * d.weight;
  }
  return { total: Math.round(total * 10) / 10, missing };
}

// Qualified = good enough AND researched enough to spend an outreach email on.
export function qualifies(s: Scores, evidenceCount: number): { ok: boolean; why: string } {
  const { total, missing } = totalScore(s);
  if (missing.includes("audience_fit") || missing.includes("sponsorship_likelihood")) return { ok: false, why: "audience fit and sponsorship likelihood need evidence first" };
  if (evidenceCount < 2) return { ok: false, why: "needs at least two evidence links" };
  if (total < 60) return { ok: false, why: `score ${total} < 60` };
  return { ok: true, why: `score ${total}` };
}

// Pricing framework, not a price list. Inputs are our own measured numbers; the CPM band is an
// assumption Surafel sets (PRICING_CPM_LOW/HIGH) and tests, never presented as market data.
export function pricingFramework(m: { medianReach: number | null; subscribers: number }, cpmLow = Number(process.env.PRICING_CPM_LOW ?? 20), cpmHigh = Number(process.env.PRICING_CPM_HIGH ?? 40)) {
  const lines: string[] = [];
  if (m.medianReach) {
    const lo = Math.round((m.medianReach / 1000) * cpmLow);
    const hi = Math.round((m.medianReach / 1000) * cpmHigh);
    lines.push(`One reel or carousel: median measured reach ${m.medianReach.toLocaleString("en-GB")} × £${cpmLow}–£${cpmHigh} per 1,000 = £${lo}–£${hi} (CPM band is our own test assumption).`);
  } else {
    lines.push("Reach not yet measured through the API: quote per deliverable only after 30 days of insights, or offer a performance-based (affiliate) trial first.");
  }
  if (m.subscribers >= 500) lines.push(`Newsletter mention: ${m.subscribers} confirmed subscribers; price it separately, and only once open rates are known.`);
  lines.push("Bundle discount 15–20% for 3+ deliverables; usage rights (brand reposting, paid ads) priced on top, 30-day default.");
  lines.push("Never accept products the brand can't let us review honestly; every paid post is labelled #ad / Paid partnership.");
  return lines;
}
