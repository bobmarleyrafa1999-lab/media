import type { IgComment, IgMedia } from "./graph";

// Fake Instagram data used until IG_ACCESS_TOKEN is set. Captions are written in the brand's
// voice so the classifier and drafter have realistic context; none of it is real account data.
const MEDIA: IgMedia[] = [
  { id: "mock_media_1", media_type: "CAROUSEL_ALBUM", media_product_type: "FEED", permalink: "https://www.instagram.com/p/MOCK1/",
    timestamp: "2026-10-20T10:00:00+0000",
    caption: "The 2am argument you keep winning in your head. Epictetus: it is not things that disturb us, but our judgements about things (Enchiridion 5, Long). What would you say if you only had one sentence? #stoicism #journaling" },
  { id: "mock_media_2", media_type: "VIDEO", media_product_type: "REELS", permalink: "https://www.instagram.com/reel/MOCK2/",
    timestamp: "2026-10-21T16:00:00+0000",
    caption: "Regulating is not suppressing. You can feel all of it and still choose what you do next. #emotionalintelligence #masculinity" },
];

const COMMENTS: Record<string, IgComment[]> = {
  mock_media_1: [
    { id: "mock_c_1", text: "This is exactly me at 2am. Saving this.", username: "quiet.reader", from: { id: "u1", username: "quiet.reader" }, timestamp: "2026-10-21T08:00:00+0000" },
    { id: "mock_c_2", text: "Isn't stoicism just telling men to bottle everything up? Feels like the opposite of therapy.", username: "philo_kate", from: { id: "u2", username: "philo_kate" }, timestamp: "2026-10-21T08:05:00+0000" },
    { id: "mock_c_3", text: "Hi! I run a notebook brand, we'd love to talk about a paid collaboration. Who do I email?", username: "inkandfolio", from: { id: "u3", username: "inkandfolio" }, timestamp: "2026-10-21T09:10:00+0000" },
  ],
  mock_media_2: [
    { id: "mock_c_4", text: "JOURNAL", username: "m.reflects", from: { id: "u4", username: "m.reflects" }, timestamp: "2026-10-21T17:00:00+0000" },
    { id: "mock_c_5", text: "Lost my dad in August and some days I don't see the point of anything anymore.", username: "anon_2814", from: { id: "u5", username: "anon_2814" }, timestamp: "2026-10-21T17:10:00+0000" },
    { id: "mock_c_6", text: "🔥🔥 check my page for crypto signals 💰 link in bio", username: "fx_profit_daily", from: { id: "u6", username: "fx_profit_daily" }, timestamp: "2026-10-21T17:12:00+0000" },
    { id: "mock_c_7", text: "Which book should I start with if I've never read any philosophy?", username: "new.to.this", from: { id: "u7", username: "new.to.this" }, timestamp: "2026-10-21T17:30:00+0000" },
  ],
};

let seq = 0;
export const mockWrites: { kind: string; commentId: string; text: string }[] = [];

export const mockGraph = {
  async getComment(id: string): Promise<IgComment> {
    for (const [mediaId, list] of Object.entries(COMMENTS)) {
      const c = list.find((x) => x.id === id);
      if (c) return { ...c, media: { id: mediaId } };
    }
    return { id, text: "", media: { id: "mock_media_1" } };
  },
  async getMedia(id: string): Promise<IgMedia> {
    return MEDIA.find((m) => m.id === id) ?? { id, caption: "", permalink: undefined };
  },
  async recentMedia(limit: number) { return MEDIA.slice(0, limit); },
  async listComments(mediaId: string) { return COMMENTS[mediaId] ?? []; },
  async replyToComment(commentId: string, message: string) {
    mockWrites.push({ kind: "public_reply", commentId, text: message });
    return { id: `mock_reply_${++seq}` };
  },
  async privateReply(commentId: string, text: string) {
    mockWrites.push({ kind: "private_reply", commentId, text });
    return { recipient_id: "mock_recipient", message_id: `mock_msg_${++seq}` };
  },
  async mediaInsights(id: string): Promise<Record<string, number>> {
    // Deliberately empty: the dashboard must never show invented numbers.
    void id;
    return {};
  },
  allComments(): { mediaId: string; comment: IgComment }[] {
    return Object.entries(COMMENTS).flatMap(([mediaId, list]) => list.map((comment) => ({ mediaId, comment })));
  },
};
