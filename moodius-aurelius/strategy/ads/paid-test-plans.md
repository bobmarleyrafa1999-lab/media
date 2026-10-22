# Paid test plans: Instagram reel test A and TikTok Promote test B

Status: **written, not launched.** Nothing here spends money until Surafel says yes to that specific test. I can't launch either: both ad accounts take his payment card, so he presses the button.

Background and benchmarks: `../15-reach-channels.md`. Finance gate: `business/finance/` (Gates tab).

---

## Test A: Instagram reel → free guide (€35)

**Gate (all three):**
1. 25 organic guide sign-ups (finance model gate).
2. The guide page is live on the domain and logs `src` (business/funnel/tracking.md).
3. One reel from the last 30 days reached ≥2x the median reel views (today the median is ~130, so ≥260).

**Why this test:** it's the only test that checks the whole path: cold viewer, then guide page, then email. It tells us what a sign-up really costs, which replaces the benchmark in the finance model.

**Creative**
- The reel: whichever recent reel has the most views at gate time and passes the 2x rule. Today's pattern favours a blunt one-line hook ("Marcus Aurelius said this"), text on screen, original audio. Its quote must cite book and section (Long or Gummere translation).
- First frame: the hook line in Bone (#F3EFE7) on Slate (#1B1F24), large Playfair, nothing else.
- Last 2 seconds: an end card, "Free: 7 days of honest reflection", in Ember (#C9742E).
- Primary text (ad copy):
  > Stoicism for people who feel things.
  > A free 7-day reflection guide: one honest question a day, with the Stoic source for each.
- Headline: `Free 7-day reflection guide`
- Button: `Learn more` (not "Sign up", so the ad matches what the page asks).
- Link: `https://<domain>/r/guide?src=ig_ad_a1`

**Setup (Ads Manager, on a desktop so the iOS 30% fee doesn't apply)**
| Setting | Value |
|---|---|
| Objective | Traffic, optimised for landing page views |
| Placements | Instagram Reels and Stories only (Advantage+ placements off) |
| Locations | United Kingdom, Ireland, United States, Canada, Australia |
| Age | 18-44 |
| Detailed targeting | Stoicism, Marcus Aurelius, Seneca, journaling, philosophy, mindfulness, self-help books; Advantage+ audience on (it may widen) |
| Exclude | People who already follow @moodiusaurelius |
| Budget | €5/day for 7 days = €35, one ad set, one ad |
| Schedule | Start on a Monday. If the gate is met in December, use the gift edition as the offer or wait for January (Q4 prices run 25-50% higher) |

Note: €5 a day will never leave Meta's "learning" phase (it needs ~50 results a week). That's fine. The test is for a direction, not a tuned campaign.

**Success metric (decided before it runs)**
| Result | What happens |
|---|---|
| Cost per guide sign-up ≤ £0.66 (3x a sign-up's value; finance model gate) | Pass. Propose a second round of €70-100 |
| £0.66-2.00 | Learning. Keep organic, try one new creative later |
| > £2.00, or < 15 landing page views | Stop. Fix the page or the creative before any more spend |

Also read: landing page views ÷ link clicks (below 60% means the page loads too slowly), and the guide page's sign-up rate against the organic rate.

**Afterwards (me):** pull the results from your screenshot into the Ads tab of the finance model, compare with the benchmark, and write a short verdict.

---

## Test B: TikTok Promote → followers (~€18)

**Gate (all three):**
1. The @moodiusaurelius TikTok account exists and is connected in Metricool.
2. It has posted reels for at least 14 days (at least 10 reels).
3. One reel reached ≥2x the TikTok account's median views, using only original audio (our `audio/` originals). Promote refuses unlicensed sound.

**Why this test:** it's the cheapest way to learn whether our text-led reels travel on TikTok and what a follower costs there compared with Instagram. It doesn't depend on the guide page, so it can run before test A.

**Creative**
- The TikTok reel that passed the 2x rule, unchanged. Promote boosts the existing post.
- Caption stays as posted. Bio: "Stoicism for people who feel things. Free guide ↓" with `https://<domain>/r/guide?src=tt_bio` once the domain is live (if TikTok shows no link field, it'll need a business account).

**Setup (TikTok app: the post, then ⋯, then Promote)**
| Setting | Value |
|---|---|
| Goal | More followers |
| Audience | Custom: United Kingdom, Ireland, United States, Canada, Australia; 18-44; interests Books & literature, Self-improvement or wellbeing (whatever TikTok lists closest) |
| Budget | $3/day for 7 days ≈ $21 (≈ €18) |
| Pay | Your card in the app (in-app payment may add a store fee, so check the total before confirming) |

**Success metric (decided before it runs)**
| Result | What happens |
|---|---|
| Cost per follower ≤ $0.50 and ≥ 25 new followers | Pass. TikTok earns a share of the next ad round |
| $0.50-1.50 per follower | Compare with test A's cost per follower; the cheaper channel gets the next round |
| > $1.50, or a completion rate below the organic post's | Stop. TikTok stays organic only |

These pass lines are **my decision rules, not benchmarks.** I couldn't find a published Promote cost-per-follower figure. They're set so 1,000 followers would cost no more than ~€430 at the pass line, which the finance model treats as the threshold for brand partnerships.

**Afterwards (me):** record views, followers, profile views and cost per follower in `ads/results.csv` from your screenshot, and compare with test A.

---

## Not planned (and why)
- TikTok Ads Manager: $500 per campaign minimum.
- Google Search: one sale would cost ≈£21-77 against £10.77 kept.
- Pinterest ads: wait for 6-8 weeks of organic pins, January at the earliest.
- Reddit ads: build the organic account first; I can't monitor Reddit from here.
