import { config, type AgentMode } from "./config";
import { getSetting, one } from "./db";
import { HUMAN_ONLY, type Classification } from "./taxonomy";

// Mode A draft_only: nothing is ever published without a human click.
// Mode B assisted:   low-risk categories in ASSISTED_CATEGORIES (default: appreciation) auto-publish.
// Mode C controlled: CONTROLLED_CATEGORIES auto-publish, all under hourly/daily caps and a kill switch.
export async function currentMode(): Promise<AgentMode> {
  const m = await getSetting<AgentMode>("agent_mode", config().agent.defaultMode);
  return ["draft_only", "assisted", "controlled"].includes(m) ? m : "draft_only";
}

export async function killSwitchOn(): Promise<boolean> {
  return getSetting<boolean>("kill_switch", false);
}

export interface Decision { publish: boolean; reason: string }

export async function decide(c: Classification, mode?: AgentMode): Promise<Decision> {
  const cfg = config().agent;
  const m = mode ?? (await currentMode());
  if (c.action !== "reply") return { publish: false, reason: `action=${c.action}` };
  if (!c.draft_reply) return { publish: false, reason: "no draft" };
  if (m === "draft_only") return { publish: false, reason: "draft-only mode" };
  if (await killSwitchOn()) return { publish: false, reason: "kill switch on" };
  if (HUMAN_ONLY.has(c.intent)) return { publish: false, reason: `${c.intent} always needs a human` };
  if (c.risk !== "low") return { publish: false, reason: `risk ${c.risk}` };
  if (c.flags.some((f) => f.startsWith("draft_veto") || f.startsWith("repetitive") || f === "claude_error" || f === "heuristic"))
    return { publish: false, reason: "draft flagged or produced offline" };
  if (c.confidence < cfg.minConfidence) return { publish: false, reason: `confidence ${c.confidence.toFixed(2)} < ${cfg.minConfidence}` };
  const allowed = m === "assisted" ? cfg.assistedCategories : cfg.controlledCategories;
  if (!allowed.includes(c.intent)) return { publish: false, reason: `${c.intent} not auto-approved in ${m}` };

  const counts = await one<{ hour: string; day: string }>(
    `SELECT count(*) FILTER (WHERE created_at > now() - interval '1 hour') AS hour,
            count(*) FILTER (WHERE created_at > now() - interval '1 day') AS day
       FROM outbound_actions WHERE kind = 'public_reply' AND actor = 'auto' AND status <> 'failed'`,
  );
  if (Number(counts?.hour ?? 0) >= cfg.maxAutoPerHour) return { publish: false, reason: "hourly auto-reply cap reached" };
  if (Number(counts?.day ?? 0) >= cfg.maxAutoPerDay) return { publish: false, reason: "daily auto-reply cap reached" };
  return { publish: true, reason: `auto-approved (${m}, ${c.intent})` };
}
