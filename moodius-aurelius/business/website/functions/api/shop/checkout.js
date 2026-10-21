// POST /api/shop/checkout  (form post from the product page, or JSON)
// Creates our checkout record and sends the buyer to the payment provider.
import { config, paymentGuard } from "../../../src/config.js";
import { startCheckout } from "../../../src/orders.js";
import { json, cleanSlug, normalizeEmail } from "../../../src/util.js";

export async function onRequestPost({ request, env }) {
  const c = config(env);
  const isJson = (request.headers.get("content-type") || "").includes("application/json");
  const input = isJson ? await request.json().catch(() => ({})) : Object.fromEntries(await request.formData());
  const productSlug = cleanSlug(input.product) || "the-unexamined-self";
  const back = (msg) =>
    isJson ? json({ ok: false, error: msg }, 400) : Response.redirect(`${c.siteUrl}/shop/${productSlug}/?error=${encodeURIComponent(msg)}`, 303);

  const guard = paymentGuard(c);
  if (guard) {
    console.error("checkout blocked:", guard);
    return isJson ? json({ ok: false, error: "Checkout is not available right now." }, 503) : back("Checkout is not available right now.");
  }
  if (input.website) return back("Please try again."); // honeypot field, invisible to people
  const digitalConsent = input.consent === true || input.consent === "on" || input.consent === "true";
  try {
    const { url } = await startCheckout(c, env.DB, {
      productSlug,
      src: input.src,
      email: normalizeEmail(input.email),
      digitalConsent,
    });
    return isJson ? json({ ok: true, url }) : Response.redirect(url, 303);
  } catch (err) {
    if (err.status && err.status < 500) return back(err.message);
    throw err;
  }
}
