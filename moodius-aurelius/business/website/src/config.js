// Reads the environment once per request and applies safe defaults.
// Every secret comes from Cloudflare environment variables (or .dev.vars locally); none live in code.

const bool = (v, d = false) => (v === undefined || v === "" ? d : ["1", "true", "yes", "on"].includes(String(v).toLowerCase()));
const int = (v, d) => (Number.isFinite(parseInt(v, 10)) ? parseInt(v, 10) : d);

export function config(env = {}) {
  const provider = (env.PAYMENT_PROVIDER || "mock").toLowerCase();
  const c = {
    siteUrl: (env.SITE_URL || "http://localhost:8788").replace(/\/$/, ""),
    provider,
    liveMode: bool(env.LIVE_MODE),
    allowMock: bool(env.ALLOW_MOCK_PAYMENTS),
    stripe: {
      secretKey: env.STRIPE_SECRET_KEY || "",
      webhookSecret: env.STRIPE_WEBHOOK_SECRET || "",
      apiVersion: env.STRIPE_API_VERSION || "2026-04-22.dahlia",
      managedPayments: bool(env.STRIPE_MANAGED_PAYMENTS, true),
      apiBase: env.STRIPE_API_BASE || "https://api.stripe.com",
    },
    lemonsqueezy: {
      apiKey: env.LEMONSQUEEZY_API_KEY || "",
      storeId: env.LEMONSQUEEZY_STORE_ID || "",
      webhookSecret: env.LEMONSQUEEZY_WEBHOOK_SECRET || "",
      apiBase: env.LEMONSQUEEZY_API_BASE || "https://api.lemonsqueezy.com",
    },
    mockWebhookSecret: env.MOCK_WEBHOOK_SECRET || "mock_whsec_local_only",
    email: {
      provider: (env.EMAIL_PROVIDER || "log").toLowerCase(),
      resendKey: env.RESEND_API_KEY || "",
      from: env.EMAIL_FROM || "Moodius Aurelius <hello@example.com>",
      replyTo: env.SUPPORT_EMAIL || "",
      postalAddress: env.POSTAL_ADDRESS || "",
    },
    adminToken: env.ADMIN_TOKEN || "",
    communityAgentUrl: (env.COMMUNITY_AGENT_URL || "").replace(/\/$/, ""),
    revenueSecret: env.REVENUE_WEBHOOK_SECRET || "",
    downloadTtlDays: int(env.DOWNLOAD_TTL_DAYS, 30),
    downloadMaxUses: int(env.DOWNLOAD_MAX_USES, 5),
    pageClaimLimit: int(env.PAGE_CLAIM_LIMIT, 3),
    ipHashSalt: env.IP_HASH_SALT || "",
    substackUrl: env.SUBSTACK_URL || "",
    raw: env,
  };
  return c;
}

// Refuse to take real money by accident: live Stripe keys need LIVE_MODE=true,
// and the mock provider can never run with LIVE_MODE on.
export function paymentGuard(c) {
  if (c.provider === "stripe") {
    if (!c.stripe.secretKey) return "Stripe is selected but STRIPE_SECRET_KEY is not set.";
    const live = c.stripe.secretKey.startsWith("sk_live_") || c.stripe.secretKey.startsWith("rk_live_");
    if (live && !c.liveMode) return "A live Stripe key is configured but LIVE_MODE is not true. Refusing to charge real cards.";
    if (!live && c.liveMode) return "LIVE_MODE is true but the Stripe key is a test key.";
  } else if (c.provider === "lemonsqueezy") {
    if (!c.lemonsqueezy.apiKey || !c.lemonsqueezy.storeId) return "Lemon Squeezy is selected but LEMONSQUEEZY_API_KEY / LEMONSQUEEZY_STORE_ID are not set.";
  } else if (c.provider === "mock") {
    if (!c.allowMock) return "The mock provider is disabled. Set ALLOW_MOCK_PAYMENTS=true for local testing only.";
    if (c.liveMode) return "The mock provider cannot run with LIVE_MODE=true.";
  } else {
    return `Unknown PAYMENT_PROVIDER "${c.provider}".`;
  }
  return null;
}
