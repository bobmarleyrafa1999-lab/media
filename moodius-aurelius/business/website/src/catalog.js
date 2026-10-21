// What the shop sells. Prices are tax-inclusive: with Stripe Managed Payments the
// Stripe price uses tax_behavior=inclusive, so a UK buyer pays exactly £14.
// Files live in the private R2 bucket (binding FILES) and are only reachable through /download/<token>.

export const PRODUCTS = {
  "the-unexamined-self": {
    slug: "the-unexamined-self",
    name: "The Unexamined Self",
    subtitle: "A 30-day guided reflection journal",
    status: "available",
    amountCents: 1400,
    currency: "GBP",
    // Stripe product tax code: Digital Books, downloaded, permanent rights (eligible for Managed Payments).
    stripeTaxCode: "txcd_10302000",
    stripePriceEnv: "STRIPE_PRICE_THE_UNEXAMINED_SELF", // optional: use a Dashboard price instead of inline price_data
    lemonVariantEnv: "LEMONSQUEEZY_VARIANT_THE_UNEXAMINED_SELF",
    files: [
      { key: "products/the-unexamined-self/v1/The-Unexamined-Self-A5-digital.pdf", filename: "The-Unexamined-Self-A5-digital.pdf", label: "Digital edition (A5, type-in fields)" },
      { key: "products/the-unexamined-self/v1/The-Unexamined-Self-A4-print.pdf", filename: "The-Unexamined-Self-A4-print.pdf", label: "Print edition (A4)" },
    ],
  },
  "the-examined-life-bundle": {
    slug: "the-examined-life-bundle",
    name: "The Examined Life Workbook Bundle",
    subtitle: "Journal + three workbooks",
    status: "coming_soon",
    amountCents: 2900,
    currency: "GBP",
    stripeTaxCode: "txcd_10302000",
    stripePriceEnv: "STRIPE_PRICE_BUNDLE",
    lemonVariantEnv: "LEMONSQUEEZY_VARIANT_BUNDLE",
    files: [],
  },
};

export const getProduct = (slug) => PRODUCTS[slug] || null;

export function formatMoney(cents, currency) {
  return new Intl.NumberFormat("en-GB", { style: "currency", currency }).format(cents / 100);
}
