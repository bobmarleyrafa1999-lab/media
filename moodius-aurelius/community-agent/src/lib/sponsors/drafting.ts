import Anthropic from "@anthropic-ai/sdk";
import { config } from "../config";
import { log } from "../log";
import { OPT_OUT_LINE } from "./compliance";
import { pricingFramework } from "./scoring";

// Prospect dossier + personalised outreach email. The model may only use facts in EVIDENCE
// (pages we fetched, with URLs) and OUR_METRICS (measured numbers or null). Prompt shape follows
// alongot/creator-crm lib/outreach-prompt.ts (MIT): JSON out, short, lead with something specific.

export interface DossierInput {
  name: string; website: string; category: string; evidence: { claim: string; url: string }[];
  siteTitle?: string | null; siteDescription?: string | null;
  metrics: { medianReach: number | null; subscribers: number; savesPerReach: number | null };
}

export interface Dossier {
  overview: string;
  relevance: { point: string; url: string }[];
  collab_idea: string;
  deliverables: string[];
  pricing: string[];
  negotiation: string[];
  followups: { day: number; note: string }[];
  email: { subject: string; body: string };
  unknowns: string[];
}

const SYSTEM = `You prepare sponsorship research and a first outreach email for Moodius Aurelius, an anonymous Instagram and newsletter brand about Stoicism, Jungian psychology, emotional intelligence, relationships, journaling and identity. The sender is "the writer behind Moodius Aurelius"; never invent a personal name.

Rules
- Use only facts in EVIDENCE and OUR_METRICS. If something is not there, say it is unknown and list it under unknowns. Never invent contacts, budgets, audience demographics, follower counts, past campaigns, testimonials or results.
- If a metric in OUR_METRICS is null, do not mention a number for it.
- Relevance points must each cite one EVIDENCE url.
- Email: under 150 words, plain text, no hype, no flattery clichés, one specific observation about the brand from EVIDENCE, one concrete idea, an easy question to end. Do not include the opt-out line or a signature; they are added after.
- Collaboration idea must suit the brand's restrained, editorial voice (e.g. a reflective carousel, a journaling prompt series, a reading-list newsletter feature), always labelled as a paid partnership.
Return JSON only.`;

const SCHEMA = {
  type: "object", additionalProperties: false,
  required: ["overview", "relevance", "collab_idea", "deliverables", "negotiation", "email", "unknowns"],
  properties: {
    overview: { type: "string" },
    relevance: { type: "array", items: { type: "object", additionalProperties: false, required: ["point", "url"], properties: { point: { type: "string" }, url: { type: "string" } } } },
    collab_idea: { type: "string" },
    deliverables: { type: "array", items: { type: "string" } },
    negotiation: { type: "array", items: { type: "string" } },
    email: { type: "object", additionalProperties: false, required: ["subject", "body"], properties: { subject: { type: "string" }, body: { type: "string" } } },
    unknowns: { type: "array", items: { type: "string" } },
  },
} as const;

export const FOLLOWUPS = [
  { day: 5, note: "Follow-up 1: two lines, add one new specific idea, same thread." },
  { day: 12, note: "Follow-up 2 (last): short, offer to close the loop; then stop and mark Lost if no reply." },
];

export function signature(): string {
  const o = config().outreach;
  return `\n\n— The writer behind Moodius Aurelius\n${config().publicSiteUrl}\n${o.postalAddress}\n\n${OPT_OUT_LINE}`;
}

function templateDossier(i: DossierInput): Omit<Dossier, "pricing" | "followups"> {
  const first = i.evidence[0];
  return {
    overview: `${i.name} (${i.website}) — ${i.siteDescription ?? i.siteTitle ?? "description not captured"}. Category: ${i.category}.`,
    relevance: i.evidence.slice(0, 4).map((e) => ({ point: e.claim, url: e.url })),
    collab_idea: `A paid "evening review" carousel built around a real use of ${i.name}'s product, written in the Moodius voice and labelled as a paid partnership.`,
    deliverables: ["1 carousel (7 slides) with #ad / Paid partnership label", "1 story set (3 frames) with link sticker", "Optional: a mention in one newsletter essay"],
    negotiation: ["Ask what success means for them before quoting.", "Keep editorial control of wording; they approve facts, not tone.", "Usage rights limited to 30 days unless paid extra."],
    email: {
      subject: `${i.name} × Moodius Aurelius: a quiet idea`,
      body: `Hello ${i.name} team,\n\nI write Moodius Aurelius, an anonymous journal on Instagram about Stoicism, psychology and the inner life.${first ? ` I noticed ${first.claim.toLowerCase()} on your site (${first.url}).` : ""}\n\nI think there's a natural fit: a reflective, clearly labelled paid carousel that uses your product the way our readers already work, at the end of the day with a pen.\n\nWould it be useful if I sent a one-page outline?`,
    },
    unknowns: ["Partnership budget", "Named contact", ...(i.metrics.medianReach ? [] : ["Our measured reach (insights not yet collected)"])],
  };
}

export async function buildDossier(i: DossierInput): Promise<Dossier> {
  let core: Omit<Dossier, "pricing" | "followups">;
  if (config().claude.mock) core = templateDossier(i);
  else {
    try {
      const client = new Anthropic({ maxRetries: 3 });
      const res = await client.beta.messages.create({
        model: config().claude.model, max_tokens: 4000,
        betas: ["server-side-fallback-2026-07-01"], fallbacks: "default",
        system: [{ type: "text", text: SYSTEM, cache_control: { type: "ephemeral" } }],
        output_config: { effort: "medium", format: { type: "json_schema", schema: SCHEMA as unknown as Record<string, unknown> } },
        messages: [{ role: "user", content: JSON.stringify({ BRAND: { name: i.name, website: i.website, category: i.category, title: i.siteTitle, description: i.siteDescription }, EVIDENCE: i.evidence, OUR_METRICS: i.metrics }) }],
      } as any);
      if (res.stop_reason === "refusal") throw new Error("model declined");
      core = JSON.parse(res.content.filter((b: any) => b.type === "text").map((b: any) => b.text).join(""));
      const urls = new Set(i.evidence.map((e) => e.url));
      core.relevance = core.relevance.filter((r) => urls.has(r.url)); // drop anything not backed by fetched evidence
    } catch (e) {
      log.error("dossier generation failed, using template", { error: (e as Error).message });
      core = templateDossier(i);
    }
  }
  return {
    ...core,
    pricing: pricingFramework({ medianReach: i.metrics.medianReach, subscribers: i.metrics.subscribers }),
    followups: FOLLOWUPS,
    email: { subject: core.email.subject, body: core.email.body.trim() + signature() },
  };
}
