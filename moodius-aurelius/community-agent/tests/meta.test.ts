import { describe, expect, it } from "vitest";
import fs from "node:fs";
import path from "node:path";
import { verifyMetaSignature, signForTest, verifyHandshake } from "../src/lib/meta/signature";
import { parseCommentWebhook } from "../src/lib/meta/webhook";
import { classifyGraphError, commentPermalink } from "../src/lib/meta/graph";

const fx = (n: string) => JSON.parse(fs.readFileSync(path.join(__dirname, "fixtures/devgine", n), "utf8"));
const OWN = "17841400000000001";

describe("webhook signature", () => {
  const body = JSON.stringify(fx("01-single-comment-price-keyword.json"));
  it("accepts a correct X-Hub-Signature-256", () => {
    expect(verifyMetaSignature(body, signForTest(body, "s3cret"), "s3cret")).toBe(true);
  });
  it("rejects wrong secret, tampered body, missing header", () => {
    expect(verifyMetaSignature(body, signForTest(body, "other"), "s3cret")).toBe(false);
    expect(verifyMetaSignature(body + " ", signForTest(body, "s3cret"), "s3cret")).toBe(false);
    expect(verifyMetaSignature(body, null, "s3cret")).toBe(false);
    expect(verifyMetaSignature(body, "sha1=abc", "s3cret")).toBe(false);
    expect(verifyMetaSignature(body, signForTest(body, "s3cret"), "")).toBe(false);
  });
  it("answers the GET handshake only with the right token", () => {
    expect(verifyHandshake(new URLSearchParams("hub.mode=subscribe&hub.verify_token=t&hub.challenge=42"), "t")).toBe("42");
    expect(verifyHandshake(new URLSearchParams("hub.mode=subscribe&hub.verify_token=x&hub.challenge=42"), "t")).toBeNull();
  });
});

describe("webhook parsing (devgine fixtures)", () => {
  it("parses a single comment", () => {
    const r = parseCommentWebhook(fx("01-single-comment-price-keyword.json"), OWN);
    expect(r.events).toHaveLength(1);
    expect(r.events[0]).toMatchObject({ commentId: "18000000000000001", mediaId: "17900000000000001", username: "test_user_alpha" });
  });
  it("parses batched entries", () => {
    expect(parseCommentWebhook(fx("02-batched-two-comments-reel.json"), OWN).events.map((e) => e.commentId)).toEqual(["18000000000000002", "18000000000000003"]);
  });
  it("ignores the account's own comments", () => {
    const r = parseCommentWebhook(fx("03-own-comment-should-be-ignored.json"), OWN);
    expect(r.events).toHaveLength(0);
    expect(r.ignored[0].reason).toBe("own comment");
  });
  it("ignores malformed and non-comment changes", () => {
    expect(parseCommentWebhook(fx("04-malformed-missing-media.json"), OWN).events).toHaveLength(0);
    expect(parseCommentWebhook(fx("05-non-comment-field-should-be-ignored.json"), OWN).events).toHaveLength(0);
    expect(parseCommentWebhook({ foo: 1 }, OWN).events).toHaveLength(0);
  });
});

describe("graph helpers", () => {
  it("classifies retryable vs permanent errors", () => {
    expect(classifyGraphError(429, {}).retryable).toBe(true);
    expect(classifyGraphError(500, {}).retryable).toBe(true);
    expect(classifyGraphError(400, { error: { code: 4, message: "App limit" } }).retryable).toBe(true);
    expect(classifyGraphError(400, { error: { code: 190, message: "token expired" } }).retryable).toBe(false);
    expect(classifyGraphError(429, {}, "7").retryAfterMs).toBe(7000);
  });
  it("builds a best-effort comment link", () => {
    expect(commentPermalink("https://www.instagram.com/p/ABC/", "123")).toBe("https://www.instagram.com/p/ABC/c/123/");
    expect(commentPermalink(null, "1")).toBeNull();
  });
});
