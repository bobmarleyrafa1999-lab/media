import Anthropic from "@anthropic-ai/sdk";
import { config } from "./config";
import { log } from "./log";
import { CLASSIFICATION_SCHEMA, COMMENT_SYSTEM_PROMPT, commentUserMessage } from "./prompts";
import { checkDraft, preRules } from "./safety";
import { maxSimilarity } from "./similarity";
import { HUMAN_ONLY, type Classification, type Intent } from "./taxonomy";

export interface ClassifyInput {
  comment: string;
  username: string | null;
  caption: string | null;
  mediaType: string | null;
  parentText: string | null;
  history: { comment: string; reply: string | null }[];
  recentReplies: string[];
}

let client: Anthropic | null = null;
function anthropic(): Anthropic {
  if (!client) client = new Anthropic({ maxRetries: 3, timeout: 60_000 });
  return client;
}

async function callClaude(input: ClassifyInput, extraInstruction?: string): Promise<Classification> {
  const c = config().claude;
  const user = commentUserMessage(input) + (extraInstruction ? `\n\n${extraInstruction}` : "");
  const res = await anthropic().beta.messages.create({
    model: c.model,
    max_tokens: 2000,
    betas: ["server-side-fallback-2026-07-01"],
    fallbacks: "default",
    system: [{ type: "text", text: COMMENT_SYSTEM_PROMPT, cache_control: { type: "ephemeral" } }],
    output_config: { effort: c.effort, format: { type: "json_schema", schema: CLASSIFICATION_SCHEMA as unknown as Record<string, unknown> } },
    messages: [{ role: "user", content: user }],
  } as any);
  if (res.stop_reason === "refusal") throw new Error("model declined to classify this comment");
  const text = res.content.filter((b: any) => b.type === "text").map((b: any) => b.text).join("");
  const parsed = JSON.parse(text) as Omit<Classification, "flags">;
  return { ...parsed, flags: [] };
}

// Offline classifier used when no API key is configured (and as a fallback when the API fails).
// Rules + small template bank; good enough to exercise the whole pipeline on mock data.
const BANK: Record<string, string[]> = {
  appreciation: [
    "Glad it landed today. Which line stayed with you?",
    "Thank you for saying so. Keep it somewhere you'll see it at 2am.",
    "Appreciate you reading it closely.",
    "That means a lot. What made it hit today rather than last week?",
  ],
  answer_to_prompt: [
    "That's an honest answer. Write it down tonight, it reads differently in a month.",
    "That's more self-aware than most of us manage. What made you notice it?",
    "Keeping that one. Thank you for answering properly.",
  ],
  genuine_question: [
    "Good question. Start small: Epictetus' Enchiridion in Long's translation is short and blunt. Then Marcus, book 2.",
    "Honest answer: start with whichever one you'll actually finish. The Enchiridion is the shortest door in.",
  ],
  philosophical_disagreement: [
    "Fair push. The Stoics I read never asked anyone to stop feeling, only to choose what to do next. Where does it break for you?",
    "Good challenge. I think we agree that bottling it up fails. What would you keep from the idea?",
  ],
  light_struggle: [
    "Thank you for saying it out loud. Naming it is already a move. Go gently this week.",
    "Rough weeks pass faster when you stop arguing with them. Hope tomorrow is lighter.",
  ],
  personal_story: [
    "Thank you for trusting a comment section with that. It took something to write.",
  ],
  criticism: ["Fair point, I'll think about that."],
  other: ["Thanks for being here."],
};

export function heuristicClassify(input: ClassifyInput): Classification {
  const t = input.comment.trim();
  const rule = preRules(t);
  let intent: Intent = rule?.intent ?? "other";
  if (!rule) {
    if (/\?\s*$/.test(t) || /^(how|what|which|why|where|who|is|are|do|does|can|should)\b/i.test(t)) intent = "genuine_question";
    else if (/\b(isn'?t|but|disagree|not true|wrong|opposite|i don'?t think)\b/i.test(t)) intent = "philosophical_disagreement";
    else if (/\b(rough|hard|tough|struggl|needed this|tired|exhausted)\b/i.test(t)) intent = "light_struggle";
    else if (/\b(me|my|i)\b/i.test(t) && t.length > 120) intent = "personal_story";
    else if (/\b(love|saving|saved|true|needed|beautiful|thank|exactly|so good|brilliant)\b/i.test(t) || /^[\p{Extended_Pictographic}\s]+$/u.test(t)) intent = "appreciation";
    else if (t.length > 25) intent = "answer_to_prompt";
  }
  const substantive = !["spam", "troll", "keyword_request"].includes(intent) && t.length > 25;
  const risky = HUMAN_ONLY.has(intent);
  const action = intent === "spam" || intent === "troll" ? "skip" : risky ? "escalate" : "reply";
  const options = BANK[intent] ?? [];
  const pick = options
    .map((o) => ({ o, s: maxSimilarity(o, input.recentReplies).score }))
    .sort((a, b) => a.s - b.s)[0]?.o ?? "";
  return {
    intent,
    sentiment: intent === "troll" || intent === "crisis" || intent === "sensitive" ? "negative" : intent === "philosophical_disagreement" ? "mixed" : intent === "spam" ? "neutral" : "positive",
    topic: /stoic|seneca|marcus|epictetus/i.test(t + (input.caption ?? "")) ? "stoicism" : /journal/i.test(t) ? "journaling" : "other",
    risk: intent === "crisis" || intent === "sensitive" || intent === "sponsorship" ? "high" : intent === "philosophical_disagreement" || intent === "personal_story" ? "medium" : "low",
    action,
    substantive,
    confidence: rule ? 0.95 : 0.6,
    draft_reply: action === "reply" || (action === "escalate" && intent !== "crisis" && intent !== "sponsorship") ? pick : "",
    follow_up_question: "",
    reason: rule ? `rule: ${rule.flag}` : "offline heuristic (no API key)",
    flags: rule ? [rule.flag, "heuristic"] : ["heuristic"],
  };
}

// Final classification = model output, then deterministic rules on top. Rules can only make a
// comment safer (escalate / skip), never less safe.
export async function classifyComment(input: ClassifyInput): Promise<Classification> {
  const rule = preRules(input.comment);
  let out: Classification;
  // Spam and bare keyword comments ("JOURNAL") don't need a model call.
  if (config().claude.mock || rule?.intent === "spam" || rule?.intent === "keyword_request") {
    out = heuristicClassify(input);
  } else {
    try {
      out = await callClaude(input);
      const sim = maxSimilarity(out.draft_reply, input.recentReplies);
      if (out.draft_reply && sim.score > config().agent.maxSimilarity) {
        out = await callClaude(input, `Your previous draft was too close to an earlier reply ("${sim.match}"). Write a different reply.`);
      }
    } catch (e) {
      log.error("claude classify failed, using heuristic", { error: (e as Error).message });
      out = heuristicClassify(input);
      out.flags.push("claude_error");
      out.confidence = Math.min(out.confidence, 0.5);
    }
  }

  if (rule) {
    out.flags.push(rule.flag);
    const order: Intent[] = ["crisis", "sensitive", "sponsorship", "spam"];
    if (order.includes(rule.intent) && out.intent !== rule.intent) {
      out.flags.push(`rule_override_from_${out.intent}`);
      out.intent = rule.intent;
    }
    if (rule.intent === "keyword_request" && out.intent !== "keyword_request") out.flags.push("keyword_present");
  }
  if (out.intent === "crisis") { out.action = "escalate"; out.risk = "high"; out.draft_reply = ""; }
  if (HUMAN_ONLY.has(out.intent)) { out.action = "escalate"; if (out.risk === "low") out.risk = "medium"; }
  if (out.intent === "spam" || out.intent === "troll") { out.action = "skip"; out.draft_reply = ""; }

  if (out.draft_reply) {
    const check = checkDraft(out.draft_reply);
    if (!check.ok) {
      out.flags.push(...check.problems.map((p) => `draft_veto: ${p}`));
      if (check.problems.some((p) => p.startsWith("possible_fabrication"))) out.flags.push("possible_fabrication");
      if (out.action === "reply") out.action = "escalate";
      out.confidence = Math.min(out.confidence, 0.4);
    }
    const sim = maxSimilarity(out.draft_reply, input.recentReplies);
    if (sim.score > config().agent.maxSimilarity) {
      out.flags.push(`repetitive (${sim.score.toFixed(2)})`);
      out.confidence = Math.min(out.confidence, 0.5);
    }
  }
  out.confidence = Math.max(0, Math.min(1, Number(out.confidence) || 0));
  out.flags = [...new Set(out.flags)];
  return out;
}
