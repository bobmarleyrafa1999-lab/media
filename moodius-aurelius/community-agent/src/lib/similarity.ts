// Character-trigram Jaccard similarity: cheap, dependency-free and good enough to stop
// the agent repeating the same sentence across comments.
function grams(s: string): Set<string> {
  const t = ` ${s.toLowerCase().replace(/[^\p{L}\p{N}\s]/gu, "").replace(/\s+/g, " ").trim()} `;
  const out = new Set<string>();
  for (let i = 0; i < t.length - 2; i++) out.add(t.slice(i, i + 3));
  return out;
}

export function similarity(a: string, b: string): number {
  const A = grams(a);
  const B = grams(b);
  if (!A.size || !B.size) return 0;
  let inter = 0;
  for (const g of A) if (B.has(g)) inter++;
  return inter / (A.size + B.size - inter);
}

export function maxSimilarity(candidate: string, history: string[]): { score: number; match?: string } {
  let best = { score: 0, match: undefined as string | undefined };
  for (const h of history) {
    const s = similarity(candidate, h);
    if (s > best.score) best = { score: s, match: h };
  }
  return best;
}
