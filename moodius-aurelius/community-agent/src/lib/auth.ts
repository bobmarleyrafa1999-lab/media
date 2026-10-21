import { config } from "./config";
import { hmac, safeEqual } from "./crypto";

// Dashboard login. Replaces creator-crm's approach (raw password stored in the cookie, app open when
// the password is unset) with: no password configured = dashboard locked; cookie = HMAC-signed expiry.
export const SESSION_COOKIE = "moodius_admin";
const TTL_S = 7 * 24 * 3600;

export function passwordOk(pw: string): boolean {
  const expected = config().adminPassword;
  return !!expected && expected.length >= 12 && safeEqual(pw, expected);
}

export function makeSession(now = Date.now()): string {
  const secret = config().sessionSecret;
  if (!secret) throw new Error("SESSION_SECRET is not set");
  const exp = Math.floor(now / 1000) + TTL_S;
  return `${exp}.${hmac(secret, `admin.${exp}`)}`;
}

export function sessionValid(cookie: string | undefined | null, now = Date.now()): boolean {
  const secret = config().sessionSecret;
  if (!cookie || !secret) return false;
  const [exp, sig] = cookie.split(".");
  if (!exp || !sig || Number(exp) * 1000 < now) return false;
  return safeEqual(sig, hmac(secret, `admin.${exp}`));
}

export function cronAuthorized(header: string | null): boolean {
  const s = config().cronSecret;
  return !!s && !!header && safeEqual(header.replace(/^Bearer /, ""), s);
}

export const sessionMaxAge = TTL_S;
