import { describe, expect, it } from "vitest";
import { checkDraft, detectKeyword, preRules } from "../src/lib/safety";
import { similarity } from "../src/lib/similarity";
import { priorityOf } from "../src/lib/taxonomy";

describe("pre-rules", () => {
  it.each([
    ["Some days I don't see the point of anything anymore", "crisis"],
    ["honestly I want to disappear", "crisis"],
    ["I've thought about suicide", "crisis"],
    ["Lost my dad in August", "sensitive"],
    ["We'd love a paid collaboration, who do I email?", "sponsorship"],
    ["check my page for crypto signals", "spam"],
    ["@friend @other", "spam"],
    ["JOURNAL", "keyword_request"],
    ["cringe cope", "troll"],
    ["how much is the workbook?", "commercial_interest"],
  ])("%s -> %s", (text, intent) => {
    expect(preRules(text)?.intent).toBe(intent);
  });
  it("leaves ordinary comments to the model", () => {
    expect(preRules("This made me rethink my morning")).toBeNull();
  });
});

describe("keywords", () => {
  it("matches short keyword comments only", () => {
    expect(detectKeyword("journal")).toBe("JOURNAL");
    expect(detectKeyword("READ please 🙏")).toBe("READ");
    expect(detectKeyword("I read this twice last night and it stayed with me")).toBeNull();
  });
});

describe("draft veto", () => {
  it("passes a clean reply", () => expect(checkDraft("That's honest. Which part was hardest to admit?").ok).toBe(true));
  it("vetoes invented research, links, hashtags and unknown quotes", () => {
    expect(checkDraft("Studies show 80% of men suppress feelings.").problems.join()).toMatch(/fabrication/);
    expect(checkDraft("See https://x.com").ok).toBe(false);
    expect(checkDraft("So true #stoic").ok).toBe(false);
    expect(checkDraft('Marcus said "the obstacle is the way forward always".').problems.join()).toMatch(/unverified quotation/);
  });
  it("allows the verified Seneca citation word for word", () => {
    expect(checkDraft('Seneca: "We suffer more often in imagination than in reality." (Letters 13.4)').ok).toBe(true);
  });
});

describe("similarity and priority", () => {
  it("detects near-duplicates", () => {
    expect(similarity("Glad it landed today. Which line stayed with you?", "Glad it landed today! Which line stayed with you")).toBeGreaterThan(0.8);
    expect(similarity("Glad it landed today.", "Fair push. Where does it break for you?")).toBeLessThan(0.2);
  });
  it("ranks crisis and sponsorship highest, spam lowest", () => {
    const p = (intent: any) => priorityOf({ intent, substantive: false, sentiment: "neutral", flags: [] }, 10);
    expect(p("crisis")).toBe(100);
    expect(p("sponsorship")).toBeGreaterThan(p("genuine_question"));
    expect(p("spam")).toBe(0);
  });
});

describe("GUIDE keyword", () => {
  it("is detected like the other keywords", async () => {
    const { detectKeyword } = await import("../src/lib/safety");
    expect(detectKeyword("GUIDE")).toBe("GUIDE");
    expect(detectKeyword("guide please 🙏")).toBe("GUIDE");
    expect(detectKeyword("this is a great guide to living, thank you so much")).toBeNull();
  });
});
