import type { Intent } from "./taxonomy";

// Deterministic rules that run BEFORE the model (to force routing) and AFTER it (to veto drafts).
// The model can never downgrade a rule hit: a crisis match stays escalated even if Claude disagrees.

const CRISIS = [
  /\bsuicid/i, /\bkill(ing)? my ?self\b/i, /\bend (it all|my life)\b/i, /\bself[- ]?harm/i, /\bcutting myself\b/i,
  /\b(don'?t|do not) want to (be here|live|exist|wake up)\b/i, /\bwant to disappear\b/i,
  /\bno (point|reason) (in |of )?(living|anything|going on)\b/i, /\bdon'?t see the point of anything\b/i,
  /\boverdos/i, /\bnot (going to|gonna) be around\b/i, /\bbetter off without me\b/i,
];
const SENSITIVE = [
  /\b(lost|losing) my (dad|mum|mom|father|mother|wife|husband|partner|son|daughter|brother|sister|friend|baby)\b/i,
  /\b(passed away|funeral|died|death of)\b/i, /\b(abuse[ds]?|assault(ed)?|raped?)\b/i, /\b(cancer|diagnos(ed|is)|chemo|terminal)\b/i,
  /\b(eating disorder|anorexi|bulimi)\b/i, /\b(depress(ed|ion)|panic attacks?)\b/i, /\b(lawyer|legal action|sue you|journalist|press enquiry)\b/i,
];
const SPONSOR = [
  /\b(collab(oration)?|sponsor(ship|ed)?|partnership|paid (post|promo|collab)|brand deal|media ?kit|rate card|your rates)\b/i,
  /\b(business (enquiry|inquiry)|work together|pr (team|agency)|marketing (team|manager))\b/i,
  /\bwho do i email\b/i, /\bemail (you|for business)\b/i,
];
const COMMERCIAL = [/\b(buy|purchase|price|cost|how much|course|ebook|workbook|pdf|guide|newsletter|substack|merch)\b/i];
const SPAM = [
  /https?:\/\/|www\.|\.com\b|\.io\b/i, /\b(check (out )?my (page|profile|bio)|link in (my )?bio)\b/i,
  /\b(crypto|forex|bitcoin|signals|investment opportunity|dm me for|promote (it|your page)|send pic)\b/i,
  /\b(followers?|likes) (for|4) (free|cheap)\b/i,
];
const TROLL = [/\b(cringe|cope|seethe|simp|beta male|soy|grifter|idiot|stupid page)\b/i];

export const KEYWORDS = ["JOURNAL", "READ", "REFLECT", "NEWSLETTER", "TOOLS", "GUIDE"] as const;
export type Keyword = (typeof KEYWORDS)[number];

export function detectKeyword(text: string): Keyword | null {
  const t = text.trim();
  // Only short comments count, so "I read this twice" doesn't trigger READ.
  if (t.length > 40) return null;
  const words = t.replace(/[^\p{L}\s]/gu, " ").split(/\s+/).filter(Boolean);
  if (words.length > 4) return null;
  for (const k of KEYWORDS) if (words.some((w) => w.toUpperCase() === k)) return k;
  return null;
}

export interface RuleHit { intent: Intent; flag: string }

export function preRules(text: string): RuleHit | null {
  const t = text || "";
  if (CRISIS.some((r) => r.test(t))) return { intent: "crisis", flag: "rule_crisis" };
  if (SENSITIVE.some((r) => r.test(t))) return { intent: "sensitive", flag: "rule_sensitive" };
  if (SPONSOR.some((r) => r.test(t))) return { intent: "sponsorship", flag: "rule_sponsorship" };
  if (SPAM.some((r) => r.test(t))) return { intent: "spam", flag: "rule_spam" };
  if (/^(\s*@[\w.]+\s*)+$/.test(t)) return { intent: "spam", flag: "rule_tag_only" };
  if (detectKeyword(t)) return { intent: "keyword_request", flag: "rule_keyword" };
  if (TROLL.some((r) => r.test(t))) return { intent: "troll", flag: "rule_troll" };
  if (COMMERCIAL.some((r) => r.test(t))) return { intent: "commercial_interest", flag: "rule_commercial" };
  return null;
}

// Only these citations may appear in a reply, word for word. Anything else in quotation marks is vetoed.
export const ALLOWED_CITATIONS = [
  { text: "We suffer more often in imagination than in reality.", source: "Seneca, Letters 13.4 (Gummere)" },
  { text: "Men are disturbed not by the things which happen, but by the opinions about the things", source: "Epictetus, Enchiridion 5 (Long)" },
];

const FABRICATION = [
  /\b(stud(y|ies)|research|scientists?|psychologists?) (show|shows|found|prove|proves|suggests?)\b/i,
  /\baccording to (a |the )?(study|research|survey|data)\b/i, /\b\d{1,3}(\.\d+)? ?%/, /\bstatistically\b/i,
];

export interface DraftCheck { ok: boolean; problems: string[] }

export function checkDraft(reply: string): DraftCheck {
  const problems: string[] = [];
  const r = reply.trim();
  if (!r) problems.push("empty");
  if (r.length > 320) problems.push("too long");
  if (/https?:\/\/|www\./i.test(r)) problems.push("contains a link");
  if (/#\w/.test(r)) problems.push("contains a hashtag");
  if (/\b(dm me|link in bio|check my|subscribe|buy)\b/i.test(r)) problems.push("selling or DM bait");
  if (FABRICATION.some((x) => x.test(r))) problems.push("possible_fabrication: cites research or numbers");
  const quoted = [...r.matchAll(/[“"]([^”"]{12,})[”"]/g)].map((m) => m[1].trim());
  for (const qt of quoted) {
    if (!ALLOWED_CITATIONS.some((c) => c.text.replace(/[.]$/, "") === qt.replace(/[.]$/, ""))) problems.push(`unverified quotation: "${qt.slice(0, 40)}"`);
  }
  if (/\b(you should see a (therapist|professional)|diagnos|you have (adhd|depression|anxiety))\b/i.test(r)) problems.push("clinical advice");
  return { ok: problems.length === 0, problems };
}
