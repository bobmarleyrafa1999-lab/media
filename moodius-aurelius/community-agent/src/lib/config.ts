// All configuration comes from environment variables. Anything missing puts that
// integration into mock mode instead of failing, so the system runs end to end on
// fake data until Surafel adds real credentials.

export type AgentMode = "draft_only" | "assisted" | "controlled";

function str(name: string, fallback = ""): string {
  const v = process.env[name];
  return v === undefined || v === "" ? fallback : v;
}
function int(name: string, fallback: number): number {
  const v = Number(process.env[name]);
  return Number.isFinite(v) && process.env[name] !== "" && process.env[name] !== undefined ? v : fallback;
}
function list(name: string, fallback: string[]): string[] {
  const v = process.env[name];
  return v ? v.split(",").map((s) => s.trim()).filter(Boolean) : fallback;
}

export function config() {
  const igToken = str("IG_ACCESS_TOKEN");
  return {
    env: str("NODE_ENV", "development"),
    baseUrl: str("APP_BASE_URL", "http://localhost:3000").replace(/\/$/, ""),
    databaseUrl: str("DATABASE_URL", "postgres://moodius:moodius@localhost:5432/moodius"),
    timezone: str("APP_TIMEZONE", "Europe/Madrid"),
    sessionSecret: str("SESSION_SECRET"),
    adminPassword: str("ADMIN_PASSWORD"),
    encryptionKey: str("ENCRYPTION_KEY"),
    cronSecret: str("CRON_SECRET"),

    meta: {
      mock: !igToken,
      appSecret: str("META_APP_SECRET"),
      verifyToken: str("META_VERIFY_TOKEN"),
      igUserId: str("IG_USER_ID", "17841400000000000"),
      igUsername: str("IG_USERNAME", "moodiusaurelius"),
      accessToken: igToken,
      // Instagram API with Instagram Login uses graph.instagram.com; with Facebook Login use graph.facebook.com.
      host: str("IG_API_HOST", "graph.instagram.com"),
      version: str("IG_API_VERSION", "v25.0"),
      pollLookbackMedia: int("IG_POLL_MEDIA", 12),
    },

    claude: {
      mock: !str("ANTHROPIC_API_KEY") && !str("ANTHROPIC_AUTH_TOKEN"),
      model: str("CLAUDE_MODEL", "claude-opus-5-5"),
      effort: str("CLAUDE_EFFORT", "low") as "low" | "medium" | "high",
    },

    email: {
      mock: !str("RESEND_API_KEY"),
      resendKey: str("RESEND_API_KEY"),
      from: str("EMAIL_FROM", "Moodius Agent <agent@example.com>"),
      owner: str("OWNER_EMAIL", "owner@example.com"),
      // "substantive" = email every substantive comment; "important" = only urgent ones, rest in the digest.
      policy: str("NOTIFY_POLICY", "substantive") as "substantive" | "important",
      maxPerHour: int("NOTIFY_MAX_PER_HOUR", 12),
      minPriority: int("NOTIFY_MIN_PRIORITY", 40),
    },

    agent: {
      defaultMode: str("AGENT_MODE", "draft_only") as AgentMode,
      maxAutoPerHour: int("AUTO_REPLY_MAX_PER_HOUR", 4),
      maxAutoPerDay: int("AUTO_REPLY_MAX_PER_DAY", 25),
      assistedCategories: list("ASSISTED_CATEGORIES", ["appreciation"]),
      controlledCategories: list("CONTROLLED_CATEGORIES", ["appreciation", "answer_to_prompt", "light_struggle"]),
      minConfidence: Number(str("AUTO_MIN_CONFIDENCE", "0.85")),
      maxSimilarity: Number(str("REPLY_MAX_SIMILARITY", "0.55")),
    },

    dm: {
      enabled: str("DM_KEYWORDS_ENABLED", "false") === "true",
    },

    publicSiteUrl: str("PUBLIC_SITE_URL", str("APP_BASE_URL", "http://localhost:3000")).replace(/\/$/, ""),

    newsletter: {
      substackUrl: str("SUBSTACK_URL", "https://moodiusaurelius.substack.com"),
      consentVersion: str("CONSENT_VERSION", "2026-10-21"),
    },

    outreach: {
      from: str("OUTREACH_FROM", ""),
      replyTo: str("OUTREACH_REPLY_TO", ""),
      postalAddress: str("OUTREACH_POSTAL_ADDRESS", ""),
      dailyCap: int("OUTREACH_DAILY_CAP", 10),
      senderName: str("OUTREACH_SENDER_NAME", "Moodius Aurelius"),
    },
  };
}

export type Config = ReturnType<typeof config>;
