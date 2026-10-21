import { beforeEach, describe, expect, it } from "vitest";
import { testEnv, resetDb } from "./helpers";
testEnv();
import { one, q } from "../src/lib/db";
import { subscribe, confirm, unsubscribe, erase, CONSENT_TEXT } from "../src/lib/newsletter";

beforeEach(async () => { await resetDb(); });

const tokenFrom = (html: string, path: string) => html.match(new RegExp(`${path}\\?t=([A-Za-z0-9_-]+)`))![1];

describe("newsletter double opt-in", () => {
  it("refuses sign-ups without the consent box ticked", async () => {
    const r = await subscribe({ email: "a@example.org", consent: false });
    expect(r.ok).toBe(false);
    expect(await q("SELECT 1 FROM subscribers")).toHaveLength(0);
  });

  it("stores consent evidence, stays pending until the link is clicked, and only keeps token hashes", async () => {
    const r = await subscribe({ email: "Reader@Example.org", consent: true, source: "dm_journal", ip: "203.0.113.9", leadMagnet: "seven-day-reflection-guide" });
    expect(r).toEqual({ ok: true, status: "pending" });
    const s = await one<any>("SELECT * FROM subscribers");
    expect(s).toMatchObject({ email: "reader@example.org", status: "pending", consent_text: CONSENT_TEXT, source: "dm_journal", lead_magnet: "seven-day-reflection-guide" });
    expect(s.ip_hash).not.toContain("203.0.113.9");
    const mail = await one<{ html: string }>("SELECT html FROM email_log WHERE kind = 'newsletter_confirm'");
    const t = tokenFrom(mail!.html, "/newsletter/confirm");
    expect(s.confirm_token_hash).not.toBe(t);

    const c = await confirm(t);
    expect(c.ok).toBe(true);
    expect(c.leadMagnet?.url).toContain("/downloads/free/seven-day-reflection-guide.pdf");
    expect((await one<any>("SELECT status FROM subscribers"))!.status).toBe("confirmed");
    expect((await confirm(t)).ok).toBe(false); // single use

    const lead = await one<{ html: string }>("SELECT html FROM email_log WHERE kind = 'lead_magnet'");
    const u = tokenFrom(lead!.html, "/newsletter/unsubscribe");
    expect(await unsubscribe(u)).toBe(true);
    expect((await one<any>("SELECT status FROM subscribers"))!.status).toBe("unsubscribed");
    const events = (await q<{ kind: string }>("SELECT kind FROM conversion_events ORDER BY id")).map((e) => e.kind);
    expect(events).toEqual(["signup_pending", "signup_confirmed", "unsubscribe"]);
  });

  it("erases a subscriber completely", async () => {
    await subscribe({ email: "gone@example.org", consent: true });
    await erase("GONE@example.org");
    expect(await q("SELECT 1 FROM subscribers")).toHaveLength(0);
  });
});
