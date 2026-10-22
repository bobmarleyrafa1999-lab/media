// Turns a Meta webhook body into comment events. Handles batched entries, skips
// non-comment fields, malformed changes, and the account's own comments.

export interface CommentEvent {
  commentId: string;
  mediaId: string;
  mediaProductType?: string;
  parentId?: string;
  fromId?: string;
  username?: string;
  text: string;
  time?: number;
}

export interface ParseResult {
  events: CommentEvent[];
  ignored: { reason: string; id?: string }[];
}

export function parseCommentWebhook(body: unknown, ownIgUserId: string): ParseResult {
  const out: ParseResult = { events: [], ignored: [] };
  const b = body as { object?: string; entry?: unknown[] };
  if (!b || (b.object !== "instagram" && b.object !== "page") || !Array.isArray(b.entry)) {
    out.ignored.push({ reason: "not an instagram webhook" });
    return out;
  }
  for (const entry of b.entry as { time?: number; changes?: unknown[] }[]) {
    for (const change of (entry?.changes ?? []) as { field?: string; value?: Record<string, any> }[]) {
      if (change?.field !== "comments") {
        out.ignored.push({ reason: `field ${change?.field ?? "?"} not handled` });
        continue;
      }
      const v = change.value ?? {};
      const commentId = typeof v.id === "string" ? v.id : undefined;
      const mediaId = typeof v.media?.id === "string" ? v.media.id : undefined;
      if (!commentId || !mediaId) {
        out.ignored.push({ reason: "missing comment or media id", id: commentId });
        continue;
      }
      const fromId = v.from?.id;
      if (fromId && fromId === ownIgUserId) {
        out.ignored.push({ reason: "own comment", id: commentId });
        continue;
      }
      out.events.push({
        commentId,
        mediaId,
        mediaProductType: v.media?.media_product_type,
        parentId: v.parent_id,
        fromId,
        username: v.from?.username,
        text: typeof v.text === "string" ? v.text : "",
        time: entry.time,
      });
    }
  }
  return out;
}
