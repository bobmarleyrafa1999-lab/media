import { beforeEach, describe, expect, it } from "vitest";
import { testEnv, resetDb } from "./helpers";
testEnv();
import { one, q } from "../src/lib/db";
import { canMove, moveStage, optOut } from "../src/lib/sponsors/crm";
import { totalScore, qualifies } from "../src/lib/sponsors/scoring";
import { researchBrand, robotsAllows, pickContact, type Fetcher } from "../src/lib/sponsors/discovery";
import { research, setScores, draft, approveOutreach, sendApproved } from "../src/lib/sponsors/outreach";
import { OPT_OUT_LINE } from "../src/lib/sponsors/compliance";

beforeEach(async () => {
  await resetDb();
  process.env.OUTREACH_FROM = "Moodius Aurelius <partners@moodius.example>";
  process.env.OUTREACH_POSTAL_ADDRESS = "PO Box 123, London, EC1A 1BB";
});

// A fake brand site: an affiliate page with a role address, and robots.txt blocking /press.
const site: Record<string, string> = {
  "https://brand.example/robots.txt": "User-agent: *\nDisallow: /press",
  "https://brand.example/": "<title>Brand Journals</title><meta name=\"description\" content=\"Linen journals.\">",
  "https://brand.example/affiliates": "<p>Join our affiliate programme. Email partnerships@brand.example or jane.doe@brand.example</p>",
  "https://brand.example/creators": "<p>Our creator programme works with writers.</p>",
};
const fetcher: Fetcher = async (url) => ({ url, status: site[url] ? 200 : 404, html: site[url] ?? "" });
const scores = {
  audience_fit: { score: 5, reason: "journals for reflective readers" }, sponsorship_likelihood: { score: 4, reason: "affiliate page" },
  product_quality: { score: 4, reason: "reviews" }, geography: { score: 4, reason: "ships UK" }, reputation: { score: 3, reason: "ok" },
  format_fit: { score: 4, reason: "carousel" }, commercial_value: { score: 3, reason: "mid" },
};

describe("scoring", () => {
  it("counts unevidenced dimensions as zero and needs evidence to qualify", () => {
    expect(totalScore({ audience_fit: { score: 5, reason: "" } }).total).toBe(0);
    expect(totalScore(scores).total).toBeGreaterThan(60);
    expect(qualifies(scores, 1).ok).toBe(false);
    expect(qualifies(scores, 2).ok).toBe(true);
  });
});

describe("discovery", () => {
  it("respects robots.txt, collects evidence, and picks a role address on the brand's domain only", async () => {
    expect(robotsAllows("User-agent: *\nDisallow: /press", "/press")).toBe(false);
    const r = await researchBrand("brand.example", fetcher, 0);
    expect(r.blockedByRobots).toContain("/press");
    expect(r.title).toBe("Brand Journals");
    expect(r.evidence.map((e) => e.claim)).toEqual(expect.arrayContaining(["affiliate programme", "creator / ambassador programme"]));
    expect(pickContact(r)).toEqual({ email: "partnerships@brand.example", source_url: "https://brand.example/affiliates" });
  });
});

describe("CRM + outreach", () => {
  it("only allows defined stage moves", async () => {
    expect(canMove("Prospect", "Qualified")).toBe(true);
    expect(canMove("Prospect", "Paid")).toBe(false);
    const s = await one<{ id: number }>("INSERT INTO sponsors (name, website, category) VALUES ('B','https://b.example','journals') RETURNING id");
    await expect(moveStage(s!.id, "Contracted", "test")).rejects.toThrow();
  });

  it("goes research → qualified → drafted → approved, and blocks sending until compliance passes", async () => {
    const s = await one<{ id: number }>("INSERT INTO sponsors (name, website, category) VALUES ('Brand','https://brand.example','journals') RETURNING id");
    const id = s!.id;
    const r = await research(id, fetcher);
    expect(r.contact?.email).toBe("partnerships@brand.example");
    const sc = await setScores(id, scores);
    expect(sc.qualified.ok).toBe(true);
    await draft(id);
    expect((await one<any>("SELECT stage FROM sponsors WHERE id = $1", [id]))!.stage).toBe("Drafted");
    const outs = await q<{ id: number; sequence: number; status: string }>("SELECT id, sequence, status FROM outreach WHERE sponsor_id = $1 ORDER BY sequence", [id]);
    expect(outs.map((o) => o.sequence)).toEqual([0, 1, 2]);

    // Not approved yet: cannot send.
    await expect(sendApproved(outs[0].id)).rejects.toThrow(/approved/);
    await approveOutreach(outs[0].id, {});
    const body = (await one<{ body: string }>("SELECT body FROM outreach WHERE id = $1", [outs[0].id]))!.body;
    expect(body).toContain(OPT_OUT_LINE);

    // Entity type unknown → blocked under PECR.
    let res = await sendApproved(outs[0].id);
    expect(res.sent).toBe(false);
    expect(res.errors.join(" ")).toMatch(/entity type/);

    await q("UPDATE sponsors SET entity_type = 'corporate' WHERE id = $1", [id]);
    res = await sendApproved(outs[0].id);
    expect(res).toMatchObject({ sent: true, logged: true });
    expect((await one<any>("SELECT stage FROM sponsors WHERE id = $1", [id]))!.stage).toBe("Contacted");

    // Follow-up isn't due yet, and opt-out blocks everything afterwards.
    await approveOutreach(outs[1].id, { body: `Short follow-up.\n\nPO Box 123, London, EC1A 1BB\n\n${OPT_OUT_LINE}` });
    await expect(sendApproved(outs[1].id)).rejects.toThrow(/not due/);
    await optOut(id);
    await q("UPDATE outreach SET sent_at = now() - interval '30 days' WHERE id = $1", [outs[0].id]);
    // Opting out cancels pending follow-ups, so nothing further can be sent.
    await expect(sendApproved(outs[1].id)).rejects.toThrow(/approved/);
    expect((await one<any>("SELECT status FROM outreach WHERE id = $1", [outs[1].id]))!.status).toBe("cancelled");
    expect(await q("SELECT 1 FROM suppression WHERE entry = 'partnerships@brand.example'")).toHaveLength(1);
  });
});
