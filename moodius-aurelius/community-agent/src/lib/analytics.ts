import { q, one } from "./db";

const n = (v: unknown) => Number(v ?? 0);

export async function overview(days = 30) {
  const c = await one<Record<string, string>>(
    `SELECT count(*) AS received,
            count(*) FILTER (WHERE status = 'published') AS answered,
            count(*) FILTER (WHERE status = 'published' AND published_by = 'auto') AS auto_answered,
            count(*) FILTER (WHERE status IN ('needs_approval','escalated')) AS waiting,
            count(*) FILTER (WHERE intent = 'crisis') AS crisis,
            count(*) FILTER (WHERE status = 'skipped') AS skipped,
            count(*) FILTER (WHERE substantive) AS substantive,
            percentile_cont(0.5) WITHIN GROUP (ORDER BY extract(epoch FROM published_at - coalesce(commented_at, received_at)))
              FILTER (WHERE published_at IS NOT NULL) AS median_delay_s,
            avg(extract(epoch FROM published_at - coalesce(commented_at, received_at))) FILTER (WHERE published_at IS NOT NULL) AS avg_delay_s
       FROM comments WHERE received_at > now() - make_interval(days => $1)`, [days]);
  // "Meaningful conversation" = a commenter who wrote again after we replied (a real back-and-forth).
  const conv = await one<{ n: string }>(
    `SELECT count(DISTINCT a.from_id) AS n FROM comments a JOIN comments b
       ON b.from_id = a.from_id AND b.received_at > a.published_at AND b.comment_id <> a.comment_id
      WHERE a.published_at IS NOT NULL AND a.received_at > now() - make_interval(days => $1)`, [days]);
  const funnel = await q<{ kind: string; n: string }>(
    `SELECT kind, count(*) AS n FROM conversion_events WHERE at > now() - make_interval(days => $1) GROUP BY kind`, [days]);
  const f = Object.fromEntries(funnel.map((r) => [r.kind, n(r.n)]));
  const subs = await one<Record<string, string>>(
    `SELECT count(*) FILTER (WHERE status = 'confirmed') AS confirmed,
            count(*) FILTER (WHERE status = 'confirmed' AND confirmed_at > now() - make_interval(days => $1)) AS new_confirmed,
            count(*) FILTER (WHERE status = 'unsubscribed') AS unsubscribed FROM subscribers`, [days]);
  const spon = await q<{ stage: string; n: string }>("SELECT stage, count(*) AS n FROM sponsors GROUP BY stage");
  const outreach = await one<Record<string, string>>(
    `SELECT count(*) FILTER (WHERE status = 'sent' AND sequence = 0) AS contacted,
            (SELECT count(*) FROM sponsors WHERE stage IN ('Replied','Negotiating','Contracted','Delivered','Paid')) AS replied
       FROM outreach`);
  const money = await one<Record<string, string>>(
    `SELECT (SELECT coalesce(sum(amount_cents),0) FROM revenue_entries WHERE occurred_on > current_date - $1::int) AS revenue,
            (SELECT coalesce(sum(amount_cents),0) FROM expenses WHERE occurred_on > current_date - $1::int) AS expenses,
            (SELECT count(*) FROM deals WHERE signed_at IS NOT NULL) AS deals_signed,
            (SELECT count(*) FROM sponsors WHERE stage = 'Negotiating') AS negotiating`, [days]);
  const views = await one<{ v: string }>(
    `SELECT sum(views) AS v FROM (SELECT DISTINCT ON (media_id) views FROM media_insights i JOIN media m USING (media_id)
       WHERE m.posted_at > now() - make_interval(days => $1) ORDER BY media_id, captured_on DESC) t`, [days]);
  const contacted = n(outreach?.contacted);
  return {
    comments: {
      received: n(c?.received), answered: n(c?.answered), autoAnswered: n(c?.auto_answered), waiting: n(c?.waiting),
      crisis: n(c?.crisis), skipped: n(c?.skipped), substantive: n(c?.substantive),
      medianDelayMin: c?.median_delay_s ? Math.round(n(c.median_delay_s) / 60) : null,
      avgDelayMin: c?.avg_delay_s ? Math.round(n(c.avg_delay_s) / 60) : null,
      conversations: n(conv?.n),
    },
    funnel: {
      keywordComments: f.comment_keyword ?? 0, dmsSent: f.dm_sent ?? 0, linkClicks: f.link_click ?? 0,
      signupsPending: f.signup_pending ?? 0, signupsConfirmed: f.signup_confirmed ?? 0, unsubscribes: f.unsubscribe ?? 0,
    },
    subscribers: { confirmed: n(subs?.confirmed), newConfirmed: n(subs?.new_confirmed), unsubscribed: n(subs?.unsubscribed) },
    sponsors: { byStage: Object.fromEntries(spon.map((r) => [r.stage, n(r.n)])), contacted, replyRate: contacted ? n(outreach?.replied) / contacted : null },
    money: {
      revenueCents: n(money?.revenue), expensesCents: n(money?.expenses), dealsSigned: n(money?.deals_signed), negotiating: n(money?.negotiating),
      views: views?.v ? n(views.v) : null,
      revenuePer1kViews: views?.v && n(views.v) > 0 ? (n(money?.revenue) / 100) / (n(views.v) / 1000) : null,
    },
  };
}

// Which themes start real conversations: substantive comments, replies that led to a second comment,
// keyword requests and signups attributed to a post (src=post_<media_id>), per content category.
export async function themes(days = 30) {
  return q<{ category: string; posts: string; comments: string; substantive: string; questions: string; disagreements: string; stories: string; keyword: string; saves: string | null; shares: string | null; reach: string | null }>(
    `WITH latest AS (SELECT DISTINCT ON (media_id) media_id, reach, saved, shares FROM media_insights ORDER BY media_id, captured_on DESC),
          ins AS (SELECT coalesce(m.category,'other') AS category, sum(l.saved) AS saves, sum(l.shares) AS shares, sum(l.reach) AS reach
                    FROM latest l JOIN media m USING (media_id) GROUP BY 1),
          com AS (SELECT coalesce(m.category,'other') AS category, count(DISTINCT m.media_id) AS posts, count(c.comment_id) AS comments,
                         count(c.comment_id) FILTER (WHERE c.substantive) AS substantive,
                         count(c.comment_id) FILTER (WHERE c.intent = 'genuine_question') AS questions,
                         count(c.comment_id) FILTER (WHERE c.intent = 'philosophical_disagreement') AS disagreements,
                         count(c.comment_id) FILTER (WHERE c.intent IN ('personal_story','light_struggle')) AS stories,
                         count(c.comment_id) FILTER (WHERE c.dm_keyword IS NOT NULL) AS keyword
                    FROM media m LEFT JOIN comments c ON c.media_id = m.media_id AND c.received_at > now() - make_interval(days => $1)
                   GROUP BY 1)
     SELECT com.*, ins.saves, ins.shares, ins.reach FROM com LEFT JOIN ins USING (category)
      ORDER BY com.substantive DESC, com.comments DESC`, [days]);
}

// Recommendations come from meaningful engagement (substantive comments, conversations, keyword
// requests, saves/shares per reach), never from likes. With too little data it says so.
export async function recommendations(days = 30): Promise<string[]> {
  const t = await themes(days);
  const withData = t.filter((r) => Number(r.comments) > 0);
  if (withData.reduce((s, r) => s + Number(r.substantive), 0) < 10) {
    return ["Not enough substantive comments yet (fewer than 10) to rank themes. Keep the current calendar and re-check next week."];
  }
  const score = (r: (typeof t)[number]) => Number(r.substantive) / Math.max(1, Number(r.posts)) + 2 * Number(r.keyword) / Math.max(1, Number(r.posts));
  const ranked = [...withData].sort((a, b) => score(b) - score(a));
  const out: string[] = [];
  const top = ranked[0];
  out.push(`Make more "${top.category}": ${Number(top.substantive)} substantive comments across ${top.posts} posts, the best ratio this period.`);
  const q1 = [...withData].sort((a, b) => Number(b.questions) - Number(a.questions))[0];
  if (Number(q1.questions) >= 3) out.push(`"${q1.category}" drew ${q1.questions} genuine questions: answer the best one as next week's carousel.`);
  const d1 = [...withData].sort((a, b) => Number(b.disagreements) - Number(a.disagreements))[0];
  if (Number(d1.disagreements) >= 2) out.push(`"${d1.category}" started ${d1.disagreements} good-faith disagreements: a "two readings" reel (format C) fits.`);
  const low = ranked[ranked.length - 1];
  if (ranked.length > 2) out.push(`"${low.category}" produced the least real discussion; keep it for reach only if its saves/shares per reach are strong.`);
  return out;
}

export async function revenueByStream(days = 90) {
  return q<{ stream: string; cents: string }>(
    "SELECT stream, sum(amount_cents) AS cents FROM revenue_entries WHERE occurred_on > current_date - $1::int GROUP BY stream ORDER BY 2 DESC", [days]);
}

export async function linkClicks(days = 30) {
  return q<{ slug: string; label: string; kind: string; clicks: string; signups: string }>(
    `SELECT l.slug, l.label, l.kind,
            (SELECT count(*) FROM conversion_events e WHERE e.kind = 'link_click' AND e.slug = l.slug AND e.at > now() - make_interval(days => $1)) AS clicks,
            (SELECT count(*) FROM conversion_events e WHERE e.kind = 'signup_confirmed' AND e.src = 'link_' || l.slug AND e.at > now() - make_interval(days => $1)) AS signups
       FROM links l ORDER BY l.position, l.slug`, [days]);
}

// Media-kit numbers: only what was actually measured. Missing data returns null, and the page
// prints "not yet measured" instead of a number.
export async function mediaKitMetrics() {
  const reach = await one<{ posts: string; median_reach: string | null; median_views: string | null; saves_rate: string | null; shares_rate: string | null; since: Date | null }>(
    `WITH latest AS (SELECT DISTINCT ON (i.media_id) i.* FROM media_insights i JOIN media m USING (media_id)
                     WHERE m.posted_at > now() - interval '90 days' ORDER BY i.media_id, i.captured_on DESC)
     SELECT count(*) AS posts, percentile_cont(0.5) WITHIN GROUP (ORDER BY reach) AS median_reach,
            percentile_cont(0.5) WITHIN GROUP (ORDER BY views) AS median_views,
            sum(saved)::float / nullif(sum(reach),0) AS saves_rate, sum(shares)::float / nullif(sum(reach),0) AS shares_rate,
            (SELECT min(posted_at) FROM media WHERE posted_at > now() - interval '90 days') AS since
       FROM latest WHERE reach IS NOT NULL`);
  const subs = await one<{ n: string }>("SELECT count(*) AS n FROM subscribers WHERE status = 'confirmed'");
  const conv = await overview(90);
  return {
    postsMeasured: Number(reach?.posts ?? 0),
    medianReach: reach?.median_reach != null ? Math.round(Number(reach.median_reach)) : null,
    medianViews: reach?.median_views != null ? Math.round(Number(reach.median_views)) : null,
    savesPerReach: reach?.saves_rate != null ? Number(reach.saves_rate) : null,
    sharesPerReach: reach?.shares_rate != null ? Number(reach.shares_rate) : null,
    newsletterSubscribers: Number(subs?.n ?? 0),
    substantiveComments90d: conv.comments.substantive,
    since: reach?.since ?? null,
  };
}
