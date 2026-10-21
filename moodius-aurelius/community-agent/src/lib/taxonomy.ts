// Shared vocabulary for classification, routing, emails and analytics.

export const INTENTS = [
  "appreciation",            // praise, "saving this", emoji-only support
  "answer_to_prompt",        // answers the question the post asked
  "genuine_question",        // asks something answerable
  "philosophical_disagreement",
  "personal_story",          // meaningful personal disclosure, not in crisis
  "light_struggle",          // "rough week", "needed this today"
  "crisis",                  // self-harm, suicide, wanting to disappear, abuse happening now
  "sensitive",               // grief, illness, abuse in the past, anything a human should answer
  "commercial_interest",     // asks about buying, products, guide, newsletter
  "sponsorship",             // brand / collaboration / PR / business enquiry
  "keyword_request",         // JOURNAL, READ, REFLECT, NEWSLETTER, TOOLS
  "criticism",               // good-faith criticism of the account
  "troll",
  "spam",
  "other",
] as const;
export type Intent = (typeof INTENTS)[number];

export const SENTIMENTS = ["positive", "neutral", "negative", "mixed"] as const;
export type Sentiment = (typeof SENTIMENTS)[number];

export const TOPICS = [
  "stoicism", "jung_shadow", "masculinity_eq", "relationships_attachment", "loneliness",
  "journaling", "discipline_identity", "grief_meaning", "psychology", "literature_culture", "other",
] as const;
export type Topic = (typeof TOPICS)[number];

export type Action = "reply" | "escalate" | "skip";
export type Risk = "low" | "medium" | "high";

export interface Classification {
  intent: Intent;
  sentiment: Sentiment;
  topic: Topic;
  risk: Risk;
  action: Action;
  substantive: boolean;
  confidence: number;
  draft_reply: string;
  follow_up_question: string;
  reason: string;
  flags: string[];
}

// Intents that must always reach Surafel personally, whatever the mode.
export const HUMAN_ONLY: ReadonlySet<Intent> = new Set(["crisis", "sensitive", "sponsorship", "commercial_interest", "criticism"]);
// Intents that trigger an immediate email instead of waiting for the digest.
export const URGENT: ReadonlySet<Intent> = new Set(["crisis", "sponsorship", "commercial_interest"]);

export function priorityOf(c: Pick<Classification, "intent" | "substantive" | "sentiment" | "flags">, textLength: number): number {
  const base: Record<Intent, number> = {
    crisis: 100, sponsorship: 95, commercial_interest: 80, sensitive: 85, personal_story: 70,
    philosophical_disagreement: 65, genuine_question: 60, criticism: 55, answer_to_prompt: 50,
    light_struggle: 50, keyword_request: 35, appreciation: 25, other: 20, troll: 5, spam: 0,
  };
  let p = base[c.intent];
  if (c.substantive && p < 90) p += 8;
  if (textLength > 140 && p < 90) p += 5;
  if (c.flags.includes("possible_fabrication")) p += 5;
  return Math.max(0, Math.min(100, p));
}
