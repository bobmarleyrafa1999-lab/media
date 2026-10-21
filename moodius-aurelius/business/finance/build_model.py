"""Builds moodius-finance-model.xlsx: costs, unit economics, scenarios, 90-day P&L and cash,
unlock gates and other income streams for Moodius Aurelius.

Run:  python3 build_model.py  then recalculate (LibreOffice) so cached values exist.

Every number lives on the Inputs sheet (or in a clearly marked blue cell) with its type and source.
Journal pricing mirrors business/pricing/margins.py (owned by the digital-products thread); the
Journals sheet recomputes it with formulas and shows margins.csv beside it as a check.
"""
import csv
import os

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "moodius-finance-model.xlsx")
MARGINS_CSV = os.path.join(HERE, "..", "pricing", "margins.csv")

FONT = "Arial"
BLUE = Font(name=FONT, color="0000FF")
BLACK = Font(name=FONT)
GREEN = Font(name=FONT, color="008000")
BOLD = Font(name=FONT, bold=True)
H1 = Font(name=FONT, bold=True, size=14)
H2 = Font(name=FONT, bold=True, size=11, color="FFFFFF")
NOTE = Font(name=FONT, italic=True, color="555555", size=9)
YELLOW = PatternFill("solid", fgColor="FFFF00")
HEAD = PatternFill("solid", fgColor="2A2F36")
BAND = PatternFill("solid", fgColor="F3EFE7")
THIN = Border(bottom=Side(style="thin", color="B8B3A9"))
WRAP = Alignment(wrap_text=True, vertical="top")

GBP = '£#,##0.00;(£#,##0.00);"-"'
GBP0 = '£#,##0;(£#,##0);"-"'
EUR = '€#,##0.00;(€#,##0.00);"-"'
EUR0 = '€#,##0;(€#,##0);"-"'
USD = '$#,##0.00;($#,##0.00);"-"'
PCT = '0.0%;(0.0%);"-"'
NUM = '#,##0;(#,##0);"-"'
NUM1 = '#,##0.0;(#,##0.0);"-"'

wb = Workbook()
wb.remove(wb.active)


def sheet(title, widths):
    ws = wb.create_sheet(title)
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.sheet_view.showGridLines = False
    return ws


def header(ws, row, labels):
    for i, label in enumerate(labels, 1):
        c = ws.cell(row=row, column=i, value=label)
        c.font, c.fill, c.alignment = H2, HEAD, WRAP
    ws.row_dimensions[row].height = 30


def put(ws, ref, value, font=BLACK, fmt=None, fill=None, wrap=False):
    c = ws[ref]
    c.value = value
    c.font = font
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    if wrap:
        c.alignment = WRAP
    return c


def q(name):
    return "'" + name + "'"


# ---------------------------------------------------------------- Inputs
INPUTS = [
    ("Currency", None),
    ("fx_gbp_eur", "Euros per £1", 1.15, "€ per £", "Assumption", "Approximate rate on 21 Oct 2026. Update from your bank or xe.com; every EUR column follows it."),
    ("fx_usd_gbp", "Pounds per $1", 0.75, "£ per $", "Assumption", "Approximate rate on 21 Oct 2026. Used to convert US-dollar supplier and ad benchmarks."),
    ("Measured today (Metricool, @moodiusaurelius, pulled 21 Oct 2026, window 22 Sep-21 Oct)", None),
    ("m_followers", "Instagram followers now", 14, "followers", "Measured", "Metricool IGEV01 on 21 Oct 2026 (was 3 on 4 Oct, account-snapshot-2026-10-04.md)."),
    ("m_reel_views_30d", "Reel views, last 30 days", 1347, "views", "Measured", "Metricool IGEV23, sum of daily values 22 Sep-21 Oct 2026."),
    ("m_account_views_30d", "All account views, last 30 days", 2252, "views", "Measured", "Metricool IGEV05, organic + paid, same window."),
    ("m_reel_median", "Median views per reel (baseline)", 130, "views", "Measured", "strategy/09-scaling-roadmap.md baseline (~130). Feed posts ~53 per 20 Oct insights."),
    ("m_best_reel_day", "Best single day of reel views (proxy for best reel)", 278, "views", "Measured", "Metricool IGEV23, 12 Oct 2026. Daily total, so a proxy, not a per-reel figure."),
    ("m_nonfollower", "Share of views from non-followers", 0.93, "%", "Measured", "Instagram insights screenshots, 20 Oct 2026."),
    ("m_shares_30d", "Reel shares (sends), last 30 days", 6, "shares", "Measured", "Metricool IGEV39, same window. Sends ≈ 0 per post."),
    ("m_signups", "Free guide / newsletter sign-ups so far", 0, "people", "Measured", "No list is live yet. Update weekly once the guide page is live."),
    ("m_journal_orders", "Journal orders so far", 0, "orders", "Measured", "Shop is in test mode. Update from the back office once live."),
    ("m_substack_subs", "Substack free subscribers", 0, "people", "Measured", "Publication not created yet (first essay planned 5 Nov 2026)."),
    ("m_comments_week", "Comments + story replies per week", 0, "per week", "Surafel input", "Not measured yet. Fill in from Instagram; drives the VPS/Claude API gate."),
    ("m_shop_live", "Shop live? (1 = yes, 0 = no)", 0, "flag", "Surafel input", "Set to 1 the day you say 'go live' on the storefront."),
    ("Journals and digital products (from the digital-products thread, business/pricing/margins.py)", None),
    ("vat", "VAT assumed inside every digital price", 0.20, "%", "From shop thread", "Conservative: UK e-publications are zero-rated, but fill-in journals may not qualify."),
    ("mp_fee", "Stripe Managed Payments fee", 0.035, "% of sale", "From shop thread", "support.stripe.com/questions/managed-payments-pricing"),
    ("card_uk_pct", "Stripe UK card %", 0.015, "% of sale", "From shop thread", "stripe.com/gb/pricing, checked 21 Oct 2026"),
    ("card_eea_pct", "Stripe EEA card % (incl. 2% FX)", 0.045, "% of sale", "From shop thread", "2.5% + 2% currency conversion, stripe.com/gb/pricing"),
    ("card_intl_pct", "Stripe international card % (incl. 2% FX)", 0.0515, "% of sale", "From shop thread", "3.15% + 2% currency conversion, stripe.com/gb/pricing"),
    ("card_fixed", "Stripe fixed fee per payment", 0.20, "£", "From shop thread", "stripe.com/gb/pricing"),
    ("hour_rate", "Value of your time for personalised items", 15, "£/hour", "From shop thread", "margins.py HOUR"),
    ("refund_rate", "Refund rate", 0.03, "% of sales", "Assumption", "Suggested by the shop thread; not sourced. Replace with real refunds after 25 orders."),
    ("mix_uk", "Buyer mix: UK cards", 0.60, "%", "Assumption", "No sales yet and audience location unknown. Replace with Stripe data."),
    ("mix_eea", "Buyer mix: EEA cards", 0.20, "%", "Assumption", "As above."),
    ("mix_intl", "Buyer mix: international cards", 0.20, "%", "Assumption", "As above. The three mix cells should add to 100%."),
    ("bundle_gate", "Journal orders before the £29 bundle is built", 25, "orders", "From shop thread", "business/funnel/bundle-plan.md (or 6 weeks on sale)."),
    ("Paid Instagram ads (benchmarks, replace with your own results)", None),
    ("ad_test_eur", "Suggested first test", 35, "€", "Plan", "growth-and-monetisation-plan.md: €5/day x 7 days on one winning reel. Needs your OK."),
    ("ad_cpc_low", "Cost per link click, low", 0.40, "$", "Benchmark", "topgrowthmarketing.com/instagram-ads-cost (2026, aggregated; no UK split)."),
    ("ad_cpc_high", "Cost per link click, high", 1.80, "$", "Benchmark", "Same source, destination clicks $0.50-1.80."),
    ("ad_cpm_low", "Reels CPM, low", 4, "$ per 1,000", "Benchmark", "Ryze.AI via topgrowthmarketing.com (2026), consumer verticals."),
    ("ad_cpm_high", "Reels CPM, high", 8, "$ per 1,000", "Benchmark", "Same source."),
    ("ad_cpf_low", "Cost per follower (boost), low", 0.30, "£", "Assumption", "No reliable published benchmark found. Replace with your ad screenshot."),
    ("ad_cpf_high", "Cost per follower (boost), high", 1.50, "£", "Assumption", "As above."),
    ("Merch (print-on-demand, no inventory)", None),
    ("etsy_listing", "Etsy listing fee per sale", 0.20, "$", "Benchmark", "Etsy fees policy (etsy.com/legal/fees). Check before launch."),
    ("etsy_txn", "Etsy transaction fee", 0.065, "% of item + shipping", "Benchmark", "Etsy fees policy."),
    ("etsy_proc_pct", "Etsy Payments processing (UK)", 0.04, "% of order", "Benchmark", "Etsy Payments UK: 4% + £0.20."),
    ("etsy_proc_fixed", "Etsy Payments fixed fee (UK)", 0.20, "£", "Benchmark", "As above."),
    ("vat_on_fees", "VAT charged on Etsy fees (UK seller, not VAT-registered)", 0.20, "%", "Benchmark", "Etsy charges UK VAT on its fees to UK sellers."),
    ("merch_returns", "Returns / reprint allowance", 0.05, "% of retail", "Assumption", "POD suppliers reprint their own misprints; this covers change-of-mind returns you absorb."),
    ("merch_samples", "One-off sample orders before launch", 45, "£", "Assumption", "3 items x ~£15 incl. shipping. A spend: needs your OK."),
    ("Other income streams", None),
    ("aff_comm", "Bookshop.org affiliate commission", 0.10, "% of order", "Benchmark", "supadu.com/blogs/news-and-views/bookshop-org (10% to affiliates)."),
    ("aff_order", "Average affiliate book order", 12, "£", "Assumption", "One paperback. Not sourced."),
    ("aff_conv", "Affiliate click to order", 0.05, "%", "Assumption", "Not sourced; replace after the Week 3 affiliate experiment."),
    ("ss_price", "Paid Substack price", 5, "£/month", "Assumption", "Substack minimum is $5/month (bestwriting.com/substack-statistics)."),
    ("ss_fee", "Substack platform fee", 0.10, "% of payment", "Benchmark", "substack/10-costs-and-apis.md and bestwriting.com."),
    ("ss_stripe_pct", "Stripe fee on Substack payments", 0.029, "% of payment", "Benchmark", "substack/10-costs-and-apis.md (2.9% + €0.30)."),
    ("ss_stripe_fixed", "Stripe fixed fee on Substack payments", 0.25, "£", "Benchmark", "€0.30 converted, rounded."),
    ("ss_conv", "Free to paid Substack conversion", 0.03, "%", "Benchmark", "Average 3%, niche 4-10% (bestwriting.com, citing reallygoodbusinessideas.com)."),
    ("rc_cpm_low", "Creator rate CPM, low", 5, "$ per 1,000 views", "Benchmark", "influee.co Instagram influencer pricing 2026, nano/micro $5-15 CPM."),
    ("rc_cpm_high", "Creator rate CPM, high", 15, "$ per 1,000 views", "Benchmark", "Same source."),
    ("rc_nano_low", "Nano creator (1k-10k followers) reel, low", 50, "$", "Benchmark", "Same source: nano reel $50-300."),
    ("rc_nano_high", "Nano creator (1k-10k followers) reel, high", 300, "$", "Benchmark", "Same source."),
    ("mentor_1to1", "Reflective mentoring, 1:1 session (50 min)", 45, "£", "Assumption", "Not sourced. Positioned as reflective mentoring, never therapy."),
    ("mentor_group", "Small-group cohort, per person (4 sessions)", 60, "£", "Assumption", "Not sourced. 6 people per cohort."),
    ("workshop_ticket", "Live online workshop ticket (90 min)", 15, "£", "Assumption", "Not sourced."),
    ("course_price", "Self-paced course", 49, "£", "Assumption", "Not sourced."),
    ("member_price", "Paid community / membership", 6, "£/month", "Assumption", "Not sourced."),
    ("licence_fee", "Content-system licence per brand", 250, "£/month", "Assumption", "Not sourced. Long-term plan in strategy/09-scaling-roadmap.md."),
    ("licence_cost", "Extra running cost per licensed brand", 30, "£/month", "Assumption", "Scheduler seat + API usage share. Not sourced."),
    ("kdp_price", "Print edition list price (Amazon KDP paperback)", 12.99, "£", "Assumption", "Not sourced."),
    ("kdp_royalty", "KDP paperback royalty rate", 0.60, "% of list", "Benchmark", "KDP 60% royalty minus printing cost. Check the KDP calculator."),
    ("kdp_print", "KDP printing cost, ~120 pp black and white", 2.29, "£", "Assumption", "Estimated, check the KDP printing-cost calculator."),
    ("Cash", None),
    ("opening_cash", "Cash set aside for the business on 1 Nov", 0, "£", "Surafel input", "Put your starting budget here; the cash view shows if it ever goes below zero."),
    ("po_deposit", "PO box postage deposit (one-off, refundable)", 20, "£", "From shop thread", "i-support Post Forwarding deposit; paid in month 1 of the cash view."),
    ("payout_lag", "Share of a month's sales paid out the next month", 0.25, "%", "Assumption", "Roughly a 7-day payout delay. Replace with your Stripe payout schedule."),
    ("shop_live_month", "Month the shop starts selling (1 = Nov, 2 = Dec, 3 = Jan)", 1, "month", "Surafel input", "Set to 2 if the shop isn't live by the end of November."),
]

ws = sheet("Inputs", [5, 50, 12, 18, 16, 90])
put(ws, "B1", "Inputs: every number the model uses", H1)
put(ws, "B2", "Blue = a value you can change. Yellow = waiting on you. Type says where it came from: Measured, Benchmark (with source), Assumption (not sourced, replace with real data), From shop thread, Plan, Surafel input.", NOTE)
header(ws, 4, ["", "Input", "Value", "Unit", "Type", "Source / note"])
REF = {}
r = 5
for item in INPUTS:
    if item[1] is None:
        put(ws, f"B{r}", item[0], BOLD)
        for col in "BCDEF":
            ws[f"{col}{r}"].fill = BAND
        r += 1
        continue
    key, label, value, unit, kind, src = item
    put(ws, f"B{r}", label)
    fmt = PCT if unit.startswith("%") else (GBP if unit.startswith("£") else (USD if unit.startswith("$") else (EUR if unit == "€" else None)))
    if key.startswith("fx"):
        fmt = "0.00"
    c = put(ws, f"C{r}", value, BLUE, fmt or NUM)
    if kind == "Surafel input":
        c.fill = YELLOW
    put(ws, f"D{r}", unit)
    put(ws, f"E{r}", kind)
    put(ws, f"F{r}", src, NOTE, wrap=True)
    REF[key] = f"Inputs!$C${r}"
    r += 1
ws.freeze_panes = "A5"


def I(key):
    return REF[key]


FX = I("fx_gbp_eur")
USD2GBP = I("fx_usd_gbp")

# ---------------------------------------------------------------- Fixed costs
ws = sheet("Fixed costs", [44, 10, 14, 14, 14, 10, 22, 70])
put(ws, "A1", "Fixed monthly costs (GBP with EUR alongside)", H1)
put(ws, "A2", "Include = 1 counts the cost in the P&L. Costs marked 'Needs your OK' are set as they would be once approved; set Include to 0 to see the model without them.", NOTE)
header(ws, 4, ["Item", "Currency", "Amount (native)", "Monthly £", "Monthly €", "Include", "Status", "Note"])
COSTS = [
    ("Metricool Starter (scheduling + analytics)", "EUR", 20, 1, 1, "Active (paid 21 Oct)", "Monthly plan; Instagram + Facebook now, Threads/Pinterest when connected."),
    ("Domain for the shop", "GBP", 8, 12, 1, "Needs your OK", "About £8 a year at Cloudflare cost price (shop thread, 22 Oct), shown per month. Paid upfront in the cash view."),
    ("PO box / virtual address", "GBP", 13, 1, 1, "Needs your OK", "i-support Post Forwarding £13/mo (or £130/yr), picked by the shop thread 22 Oct; plus a £20 one-off postage deposit in the cash view. Legally needed on the legal pages and in marketing emails."),
    ("VPS for comment agent + n8n", "EUR", 5, 1, 0, "Needs your OK", "€4-6 a month (community-agent/docs/04). Off until the comments gate is met."),
    ("Claude API for comment replies", "EUR", 5, 1, 0, "Needs your OK", "€1-10 a month depending on model and volume. Runs on the VPS, so same gate."),
    ("Cloudflare Pages + D1 + R2 (shop)", "GBP", 0, 1, 1, "Free tier", "Commercial use allowed on the free tier."),
    ("Resend email", "GBP", 0, 1, 1, "Free tier", "Free up to 3,000 emails a month."),
    ("Substack", "GBP", 0, 1, 1, "Free", "Free to publish; 10% + Stripe only if paid subscriptions are switched on."),
    ("Stripe (Managed Payments)", "GBP", 0, 1, 1, "No monthly fee", "Per-sale fees sit in the unit economics, not here."),
    ("GitHub, Kit free tier, Canva free", "GBP", 0, 1, 1, "Free", ""),
    ("Etsy shop for merch (later)", "GBP", 0, 1, 0, "Not started", "No monthly fee on Etsy Standard; fees are per sale (Merch sheet)."),
]
r0 = 5
for i, (name, cur, amt, per, inc, status, note) in enumerate(COSTS):
    r = r0 + i
    put(ws, f"A{r}", name)
    put(ws, f"B{r}", cur, BLUE)
    put(ws, f"C{r}", amt, BLUE, GBP if cur == "GBP" else EUR)
    if per == 12:
        ws[f"C{r}"].comment = Comment("Annual amount; divided by 12 in the monthly columns.", "Claude")
        put(ws, f"D{r}", f'=IF(B{r}="GBP",C{r},C{r}/{FX})/12', fmt=GBP)
    else:
        put(ws, f"D{r}", f'=IF(B{r}="GBP",C{r},C{r}/{FX})', fmt=GBP)
    put(ws, f"E{r}", f"=D{r}*{FX}", fmt=EUR)
    put(ws, f"F{r}", inc, BLUE)
    put(ws, f"G{r}", status)
    put(ws, f"H{r}", note, NOTE, wrap=True)
rl = r0 + len(COSTS) - 1
rt = rl + 2
put(ws, f"A{rt}", "Total included in the model", BOLD)
put(ws, f"D{rt}", f"=SUMPRODUCT(D{r0}:D{rl},F{r0}:F{rl})", BOLD, GBP)
put(ws, f"E{rt}", f"=D{rt}*{FX}", BOLD, EUR)
put(ws, f"A{rt+1}", "Total if every cost listed is switched on")
put(ws, f"D{rt+1}", f"=SUM(D{r0}:D{rl})", fmt=GBP)
put(ws, f"E{rt+1}", f"=D{rt+1}*{FX}", fmt=EUR)
put(ws, f"A{rt+2}", "Lean budget target (upper end)")
put(ws, f"E{rt+2}", 25, BLUE, EUR)
put(ws, f"D{rt+2}", f"=E{rt+2}/{FX}", fmt=GBP)
put(ws, f"A{rt+3}", "Headroom (included vs target)")
put(ws, f"D{rt+3}", f"=D{rt+2}-D{rt}", fmt=GBP)
put(ws, f"E{rt+3}", f"=E{rt+2}-E{rt}", fmt=EUR)
FIXED_TOTAL = f"{q('Fixed costs')}!$D${rt}"
FIXED_ALL = f"{q('Fixed costs')}!$D${rt+1}"
FC_ROWS = {name: r0 + i for i, (name, *_rest) in enumerate(COSTS)}
DOMAIN_ROW = FC_ROWS["Domain for the shop"]

# ---------------------------------------------------------------- Journals
ws = sheet("Journals", [52, 10, 9, 10, 10, 10, 10, 11, 11, 11, 12, 12, 40])
put(ws, "A1", "Journals and digital products: per-sale economics", H1)
put(ws, "A2", "Prices and fees are the digital-products thread's (business/pricing/margins.py). Recomputed here with formulas; column L shows margins.csv so you can see both agree. Digital cost of goods is £0 (delivery runs on free tiers).", NOTE)
header(ws, 4, ["Product", "Price £ (VAT incl.)", "Minutes of your time", "VAT £", "Fees UK £", "Profit UK £", "Profit EEA £", "Profit intl £", "Blended profit £", "After refunds £", "Margin (after refunds)", "margins.csv UK profit £", "Status"])
csv_rows = []
if os.path.exists(MARGINS_CSV):
    with open(MARGINS_CSV) as f:
        csv_rows = list(csv.DictReader(f))
MINUTES = {"Personalised journal (journal + personalisation)": 3, "Gift edition (personalised + gift page + chosen send date)": 4, "Personalised bundle": 3}
JROW = {}
r = 5
for row in csv_rows:
    name, price = row["product"], float(row["price_gbp"])
    put(ws, f"A{r}", name)
    put(ws, f"B{r}", price, BLUE, GBP)
    put(ws, f"C{r}", MINUTES.get(name, 0), BLUE, NUM)
    put(ws, f"D{r}", f"=B{r}-B{r}/(1+{I('vat')})", fmt=GBP)
    lab = f"C{r}/60*{I('hour_rate')}"
    put(ws, f"E{r}", f"=IF(B{r}=0,0,B{r}*({I('card_uk_pct')}+{I('mp_fee')})+{I('card_fixed')})", fmt=GBP)
    put(ws, f"F{r}", f"=IF(B{r}=0,0,B{r}-D{r}-E{r}-{lab})", fmt=GBP)
    put(ws, f"G{r}", f"=IF(B{r}=0,0,B{r}-D{r}-(B{r}*({I('card_eea_pct')}+{I('mp_fee')})+{I('card_fixed')})-{lab})", fmt=GBP)
    put(ws, f"H{r}", f"=IF(B{r}=0,0,B{r}-D{r}-(B{r}*({I('card_intl_pct')}+{I('mp_fee')})+{I('card_fixed')})-{lab})", fmt=GBP)
    put(ws, f"I{r}", f"=F{r}*{I('mix_uk')}+G{r}*{I('mix_eea')}+H{r}*{I('mix_intl')}", fmt=GBP)
    put(ws, f"J{r}", f"=I{r}-B{r}*{I('refund_rate')}", fmt=GBP)
    put(ws, f"K{r}", f"=IF(B{r}=0,0,J{r}/B{r})", fmt=PCT)
    put(ws, f"L{r}", float(row["profit_uk"]), GREEN, GBP)
    ws[f"L{r}"].comment = Comment("Copied from business/pricing/margins.csv (shop thread). Should equal column F.", "Claude")
    put(ws, f"M{r}", row["status"], NOTE)
    JROW[name] = r
    r += 1
jlast = r - 1
r += 1
put(ws, f"A{r}", "Future print edition (Amazon KDP paperback, no inventory)", BOLD)
r += 1
put(ws, f"A{r}", "List price £")
put(ws, f"B{r}", f"={I('kdp_price')}", GREEN, GBP)
put(ws, f"A{r+1}", "Royalty (60% of list) minus printing cost = profit per copy £")
put(ws, f"B{r+1}", f"={I('kdp_price')}*{I('kdp_royalty')}-{I('kdp_print')}", fmt=GBP)
put(ws, f"A{r+2}", "Cost of goods per copy £ (printing, deducted by Amazon)")
put(ws, f"B{r+2}", f"={I('kdp_print')}", GREEN, GBP)
put(ws, f"A{r+3}", "Postage: Amazon ships; buyer pays or Prime covers it. You hold no stock. A printed personalised paperback (shop thread idea) would cost ~£3-4 to print + £3-4 UK post at ~£24-27, and can't use Managed Payments (digital only).", NOTE)
KDP_PROFIT = f"Journals!$B${r+1}"
J_MAIN = JROW.get("The Unexamined Self (journal)", 6)
J_BUNDLE = JROW.get("The Examined Life bundle", 9)
J_PROFIT = f"Journals!$J${J_MAIN}"
J_PRICE = f"Journals!$B${J_MAIN}"
B_PROFIT = f"Journals!$J${J_BUNDLE}"
B_PRICE = f"Journals!$B${J_BUNDLE}"
r += 5
put(ws, f"A{r}", "Check: rows where the recomputed UK profit differs from margins.csv by more than 1p")
put(ws, f"B{r}", f"=SUMPRODUCT(--(ABS(F5:F{jlast}-L5:L{jlast})>0.011))", BOLD, NUM)

# ---------------------------------------------------------------- Merch
ws = sheet("Merch", [50, 13, 13, 13, 4, 60])
put(ws, "A1", "Merch plan: print-on-demand, cost of goods and postage by region", H1)
put(ws, "A2", "A plan only: no store or listings exist. Default channel is Etsy + a POD supplier (Printful shown; Printify or Gelato are alternatives) because Etsy collects UK/EU VAT on your behalf as the marketplace. Supplier choice is yours.", NOTE)
MERCH = [
    ("Minimal typographic tee (Bella+Canvas 3001, one front print, Ember accent)", 28, (12.95, 12.95, 12.95), ("usd", 3.99, 4.99, 3.99), "Printful base on Free plan, $12.95 (podvector.ai, May 2026). Shipping UK/US $3.99, EU $4.99 first item."),
    ("Art print 12x16 in, enhanced matte (quote + Ember rule)", 22, (10.95, 10.95, 10.95), ("mixed", 4.99, 5.49, 4.99), "Printful base $10.95; shipping UK £4.99, EU €5.49, US $4.99 (podvector.ai, May 2026)."),
    ("Hardcover lined notebook (Slate cover, small Ember mark)", 22, (15.00, 15.00, 15.00), ("usd", 5.99, 5.99, 5.99), "ESTIMATE: Printful's page shows no price without login. Check base and shipping in the supplier dashboard."),
]
SHIP_CHARGED = (3.95, 5.95, 6.95)
r = 4
MERCH_UK = []
for name, retail, base, ship, src in MERCH:
    put(ws, f"A{r}", name, BOLD)
    for col in "ABCDF":
        ws[f"{col}{r}"].fill = BAND
    r += 1
    header(ws, r, ["Line (per order of one item)", "UK", "EU", "US", "", "Source / note"])
    r += 1
    top = r
    rows = [
        ("Retail price £ (what the buyer pays for the item)", [retail] * 3, "in", "Assumption: priced for a premium minimal brand. Not sourced."),
        ("Shipping charged to buyer £", list(SHIP_CHARGED), "in", "Assumption: set to roughly cover postage."),
        ("Revenue £", None, "rev", ""),
        ("Supplier base cost (cost of goods) $", list(base), "in_usd", src),
        ("Cost of goods £", None, "cogs", "Converted at the Inputs rate."),
        ("Postage (supplier shipping) £", None, "ship", "Supplier shipping rates; packaging is included by POD suppliers."),
        ("Branded packaging / insert card £", [0, 0, 0], "in", "Assumption: £0, plain supplier packaging. Add ~£0.50-1 if you want inserts."),
        ("Etsy listing fee £", None, "list", ""),
        ("Etsy transaction fee £", None, "txn", "6.5% of item + shipping."),
        ("Etsy Payments processing £", None, "proc", "4% + £0.20."),
        ("VAT on Etsy fees £", None, "vatfee", "20% on Etsy's fees."),
        ("Returns / reprint allowance £", None, "ret", "Allowance on retail price."),
        ("Total cost £", None, "tot", ""),
        ("Contribution per order £", None, "con", ""),
        ("Margin on revenue", None, "mar", ""),
        ("Same order on your own site with Stripe (no Etsy fees) £", None, "own", "Higher margin, but you then handle VAT on goods sold to EU buyers yourself. Etsy first."),
    ]
    idx = {}
    for j, (label, vals, kind, note) in enumerate(rows):
        rr = top + j
        idx[kind] = rr
        put(ws, f"A{rr}", label, BOLD if kind in ("con", "tot", "rev") else BLACK)
        put(ws, f"F{rr}", note, NOTE, wrap=True)
        for k, col in enumerate("BCD"):
            if kind == "in":
                put(ws, f"{col}{rr}", vals[k], BLUE, GBP)
            elif kind == "in_usd":
                put(ws, f"{col}{rr}", vals[k], BLUE, USD)
    for k, col in enumerate("BCD"):
        R = lambda kind: f"{col}{idx[kind]}"
        put(ws, R("rev"), f"={col}{top}+{col}{top+1}", BOLD, GBP)
        put(ws, R("cogs"), f"={R('in_usd')}*{USD2GBP}", fmt=GBP)
        kindship, uk, eu, us = ship
        if kindship == "usd":
            put(ws, R("ship"), f"={[uk, eu, us][k]}*{USD2GBP}", BLUE, GBP)
        else:
            put(ws, R("ship"), ["=4.99", f"=5.49/{FX}", f"=4.99*{USD2GBP}"][k], BLUE, GBP)
        put(ws, R("list"), f"={I('etsy_listing')}*{USD2GBP}", fmt=GBP)
        put(ws, R("txn"), f"={R('rev')}*{I('etsy_txn')}", fmt=GBP)
        put(ws, R("proc"), f"={R('rev')}*{I('etsy_proc_pct')}+{I('etsy_proc_fixed')}", fmt=GBP)
        put(ws, R("vatfee"), f"=({R('list')}+{R('txn')}+{R('proc')})*{I('vat_on_fees')}", fmt=GBP)
        put(ws, R("ret"), f"={col}{top}*{I('merch_returns')}", fmt=GBP)
        put(ws, R("tot"), f"={R('cogs')}+{R('ship')}+{col}{top+6}+{R('list')}+{R('txn')}+{R('proc')}+{R('vatfee')}+{R('ret')}", BOLD, GBP)
        put(ws, R("con"), f"={R('rev')}-{R('tot')}", BOLD, GBP)
        put(ws, R("mar"), f"=IF({R('rev')}=0,0,{R('con')}/{R('rev')})", fmt=PCT)
        cardpct = [I("card_uk_pct"), I("card_eea_pct"), I("card_intl_pct")][k]
        put(ws, R("own"), f"={R('rev')}-{R('cogs')}-{R('ship')}-{col}{top+6}-({R('rev')}*{cardpct}+{I('card_fixed')})-{R('ret')}", fmt=GBP)
    MERCH_UK.append(f"Merch!$B${idx['con']}")
    r = top + len(rows) + 1
put(ws, f"A{r}", "One-off before launch (needs your OK)", BOLD)
put(ws, f"B{r}", f"={I('merch_samples')}", GREEN, GBP)
put(ws, f"F{r}", "Order one sample of each item to check print quality and colour (Ember on Slate).", NOTE, wrap=True)
r += 2
put(ws, f"A{r}", "Merch vs journals: contribution per sale (UK)", BOLD)
put(ws, f"A{r+1}", "Journal, after refunds")
put(ws, f"B{r+1}", f"={J_PROFIT}", GREEN, GBP)
put(ws, f"A{r+2}", "Tee, via Etsy")
put(ws, f"B{r+2}", f"={MERCH_UK[0]}", GREEN, GBP)
put(ws, f"A{r+3}", "Art print, via Etsy")
put(ws, f"B{r+3}", f"={MERCH_UK[1]}", GREEN, GBP)
put(ws, f"A{r+4}", "Notebook, via Etsy (estimate)")
put(ws, f"B{r+4}", f"={MERCH_UK[2]}", GREEN, GBP)
put(ws, f"A{r+6}", "When merch is worth launching: per sale it earns about what a journal earns, but it needs samples, design and a second shop, people buy apparel from brands they already know, and returns and support are physical. Launch only after the gate on the Gates sheet (50 journal sales and visible demand). Until then journals win: the same reel sells a product with zero cost of goods that already exists.", NOTE, wrap=True)
ws.merge_cells(f"A{r+6}:F{r+8}")
ws.row_dimensions[r + 6].height = 30
MERCH_TEE = MERCH_UK[0]

# ---------------------------------------------------------------- Scenarios (built before Ads so Ads can link to value per sign-up)
ws = sheet("Scenarios", [56, 15, 15, 15, 70])
put(ws, "A1", "Scenarios: what a month looks like at the end of the 90 days", H1)
put(ws, "A2", "Only today's numbers are measured. The funnel rates below are assumptions (blue), labelled; replace them with what the shop and guide page record after 30 days.", NOTE)
header(ws, 4, ["Driver (per month)", "Conservative", "Base", "Optimistic", "Type and source"])
SC = [
    ("reels", "Reels published per month", (30, 30, 30), NUM, "Plan: 1 reel a day (strategy/06-30-day-calendar.md)."),
    ("vpr", "Views per reel by month 3", (f"={I('m_reel_median')}", 400, 1000), NUM, "Conservative = today's median (measured). Base = Phase 0 gate target (strategy/09). Optimistic = assumption."),
    ("cpk", "Profile/link clicks per 1,000 views", (2, 4, 8), NUM1, "Assumption, not sourced. Week 1 of the monetisation plan measures it."),
    ("lsr", "Guide page visit to sign-up", (0.20, 0.30, 0.40), PCT, "Assumption, not sourced."),
    ("spr", "Sign-up to journal purchase (within the 90 days)", (0.01, 0.02, 0.04), PCT, "Assumption, not sourced (the shop thread used no conversion benchmarks either)."),
    ("dpr", "Share of clicks that go straight to the shop and buy", (0.005, 0.01, 0.02), PCT, "Assumption, not sourced."),
    ("apk", "Affiliate clicks per 1,000 views", (0.5, 1, 2), NUM1, "Assumption; starts in week 3 of the monetisation plan."),
]
SCR = {}
r = 5
for key, label, vals, fmt, src in SC:
    put(ws, f"A{r}", label)
    for k, col in enumerate("BCD"):
        put(ws, f"{col}{r}", vals[k], BLUE if not str(vals[k]).startswith("=") else GREEN, fmt)
    put(ws, f"E{r}", src, NOTE, wrap=True)
    SCR[key] = r
    r += 1
r += 1
put(ws, f"A{r}", "Results at month-3 run rate", BOLD)
for col in "ABCDE":
    ws[f"{col}{r}"].fill = BAND
r += 1
OUTS = [
    ("views", "Reel views", "={c}{reels}*{c}{vpr}", NUM),
    ("clicks", "Link clicks", "={c}{views}/1000*{c}{cpk}", NUM1),
    ("signups", "Guide sign-ups", "={c}{clicks}*{c}{lsr}", NUM1),
    ("jsales", "Journal sales", "={c}{signups}*{c}{spr}+{c}{clicks}*{c}{dpr}", NUM1),
    ("jgross", "Journal sales £ (gross, VAT incl.)", "={c}{jsales}*" + J_PRICE, GBP),
    ("jcon", "Journal contribution £ (after VAT, fees, refunds)", "={c}{jsales}*" + J_PROFIT, GBP),
    ("acon", "Affiliate commission £", "={c}{views}/1000*{c}{apk}*" + I("aff_conv") + "*" + I("aff_order") + "*" + I("aff_comm"), GBP),
    ("tcon", "Total contribution £", "={c}{jcon}+{c}{acon}", GBP),
    ("fixed", "Fixed costs £ (included set)", "=" + FIXED_TOTAL, GBP),
    ("net", "Net result £ per month", "={c}{tcon}-{c}{fixed}", GBP),
    ("neteur", "Net result € per month", "={c}{net}*" + FX, EUR),
    ("rpk", "Revenue per 1,000 views £ (gross)", "=IF({c}{views}=0,0,({c}{jgross}+{c}{acon})/{c}{views}*1000)", GBP),
    ("cpk1", "Contribution per 1,000 views £", "=IF({c}{views}=0,0,{c}{tcon}/{c}{views}*1000)", GBP),
    ("vsu", "Value of one guide sign-up £ (journal only)", "={c}{spr}*" + J_PROFIT, GBP),
    ("bev", "Views per month to cover fixed costs", "=IF({c}{cpk1}=0,0,{c}{fixed}/{c}{cpk1}*1000)", NUM),
    ("bes", "Journal sales per month to cover fixed costs", "=IF(" + J_PROFIT + "=0,0,{c}{fixed}/" + J_PROFIT + ")", NUM1),
]
for key, label, f, fmt in OUTS:
    SCR[key] = r
    r += 1
for key, label, f, fmt in OUTS:
    rr = SCR[key]
    put(ws, f"A{rr}", label, BOLD if key in ("net", "rpk", "bev") else BLACK)
    for col in "BCD":
        put(ws, f"{col}{rr}", f.format(c=col, **SCR), BOLD if key in ("net", "rpk", "bev") else BLACK, fmt)
r += 1
put(ws, f"A{r}", "Today, measured: revenue per 1,000 views £", BOLD)
put(ws, f"B{r}", 0, BLUE, GBP)
put(ws, f"E{r}", "Measured: £0 revenue on 1,347 reel views in the last 30 days (nothing is for sale yet).", NOTE, wrap=True)
SC_TODAY_RPK = r
r += 2
put(ws, f"A{r}", "90-day totals by scenario (from the P&L logic, shop live from the month set on Inputs)", BOLD)
SC_TOT_ROW = r + 1

# ---------------------------------------------------------------- 90-day P&L
ws = sheet("90-day P&L", [52, 14, 14, 14, 15, 60])
put(ws, "A1", "90-day P&L and cash (2 Nov 2026 to 31 Jan 2027)", H1)
put(ws, "A2", "Day 1 is 2 Nov (bio link to Substack), first essay 5 Nov, day 90 is 31 Jan, aligned with substack/08-calendar-90-day.csv and the 30-day monetisation plan (community-agent/docs/06).", NOTE)
put(ws, "A3", "Scenario (1 = conservative, 2 = base, 3 = optimistic)", BOLD)
put(ws, "B3", 2, BLUE, fill=YELLOW)
dv = DataValidation(type="whole", operator="between", formula1="1", formula2="3")
ws.add_data_validation(dv)
dv.add("B3")
SEL = q("90-day P&L") + "!$B$3"
header(ws, 5, ["Line", "Nov 2026 (M1)", "Dec 2026 (M2)", "Jan 2027 (M3)", "90-day total", "Note"])
MILESTONES = [
    "Wk1 measure only; Wk2 DM keyword → guide; essays 1-4 from 5 Nov; Wk3 affiliate test; Wk4 first product push",
    "Day-30 review picks one experiment; essays weekly; €35 ad test only if the gate is met and you OK it",
    "Bundle only if 25 orders; day-90 review 31 Jan; decide next spends from Gates",
]
put(ws, "A6", "What happens this month")
for k, col in enumerate("BCD"):
    put(ws, f"{col}6", MILESTONES[k], NOTE, wrap=True)
ws.row_dimensions[6].height = 75


def sc(key):
    return f"INDEX(Scenarios!$B${SCR[key]}:$D${SCR[key]},{SEL})"


LINES = [
    ("m", "Month number", ["1", "2", "3"], NUM, ""),
    ("live", "Shop selling this month? (1/0)", "=IF({c}{m}>=" + I("shop_live_month") + ",1,0)", NUM, "From Inputs."),
    ("views", "Reel views", "=" + I("m_reel_views_30d") + "+(" + sc("views") + "-" + I("m_reel_views_30d") + ")*{c}{m}/3", NUM, "Ramps in a straight line from today's measured 30-day views to the scenario's month-3 level."),
    ("clicks", "Link clicks", "={c}{views}/1000*" + sc("cpk"), NUM1, ""),
    ("signups", "Guide sign-ups", "={c}{clicks}*" + sc("lsr"), NUM1, ""),
    ("jsales", "Journal sales", "=({c}{signups}*" + sc("spr") + "+{c}{clicks}*" + sc("dpr") + ")*{c}{live}", NUM1, ""),
    ("cumj", "Cumulative journal orders", "={c}{jsales}+{p}", NUM1, ""),
    ("bsales", "Bundle sales (only after the order gate)", "=IF({prevcum}>=" + I("bundle_gate") + ",{c}{jsales}*0.3,0)", NUM1, "Assumption: 30% of buyers take the bundle once it exists. Not sourced."),
    ("sp1", "REVENUE (gross, VAT included)", None, None, ""),
    ("rj", "Journals £", "={c}{jsales}*" + J_PRICE, GBP, ""),
    ("rb", "Bundle £", "={c}{bsales}*" + B_PRICE, GBP, ""),
    ("ra", "Affiliate commission £", "={c}{views}/1000*" + sc("apk") + "*" + I("aff_conv") + "*" + I("aff_order") + "*" + I("aff_comm"), GBP, ""),
    ("rm", "Merch £", "0", GBP, "Not launched in the 90 days (gate not met)."),
    ("rs", "Brand deals, mentoring, paid Substack £", "0", GBP, "Not realistic at today's audience; see Other income for gates."),
    ("rev", "Total revenue £", "=SUM({c}{rj}:{c}{rs})", GBP, ""),
    ("sp2", "COST OF SALES", None, None, ""),
    ("vat", "VAT inside digital prices £", "=({c}{rj}+{c}{rb})*(1-1/(1+" + I("vat") + "))", GBP, "Collected and paid by Stripe as merchant of record."),
    ("fees", "Payment fees £", "=({c}{rj}+{c}{rb})/(1+" + I("vat") + ")-({c}{jsales}*(" + J_PROFIT + "+" + J_PRICE + "*" + I("refund_rate") + ")+{c}{bsales}*(" + B_PROFIT + "+" + B_PRICE + "*" + I("refund_rate") + "))", GBP, "Blended Stripe + Managed Payments fees (Journals sheet)."),
    ("ref", "Refunds £", "=({c}{rj}+{c}{rb})*" + I("refund_rate"), GBP, ""),
    ("cogs", "Cost of goods and postage £", "0", GBP, "Digital: £0. Becomes real only with merch or a print edition."),
    ("gp", "Gross profit £", "={c}{rev}-{c}{vat}-{c}{fees}-{c}{ref}-{c}{cogs}", GBP, ""),
    ("sp3", "OPERATING COSTS", None, None, ""),
    ("fx1", "Metricool £", "=" + q("Fixed costs") + "!$D${mr}*" + q("Fixed costs") + "!$F${mr}", GBP, ""),
    ("fx2", "Other fixed costs £ (domain, PO box, VPS, API if included)", "=" + FIXED_TOTAL + "-{c}{fx1}", GBP, "Domain amortised monthly here; paid upfront in the cash view."),
    ("ads", "Paid ads £ (needs your OK per spend)", ["0", "0", "0"], GBP, "Blue cells: type a spend only after you approve it. €35 test ≈ £30."),
    ("opex", "Total operating costs £", "={c}{fx1}+{c}{fx2}+{c}{ads}", GBP, ""),
    ("net", "NET RESULT £", "={c}{gp}-{c}{opex}", GBP, ""),
    ("neteur", "Net result €", "={c}{net}*" + FX, EUR, ""),
    ("sp4", "CASH", None, None, ""),
    ("open", "Opening cash £", "={prevclose}", GBP, "M1 starts from Inputs 'Cash set aside'."),
    ("cin", "Cash in £ (net of VAT/fees/refunds, after payout delay)", "=({c}{gp}+{c}{cogs})*(1-" + I("payout_lag") + ")+{prevgp}*" + I("payout_lag"), GBP, ""),
    ("cout", "Cash out £", "={c}{opex}-{c}{fx2}+{c}{cashfixed}", GBP, ""),
    ("cashfixed", "  of which fixed costs paid this month £", "={c}{fx2}-" + q("Fixed costs") + "!$D${dr}*" + q("Fixed costs") + "!$F${dr}+IF({c}{m}=1," + q("Fixed costs") + "!$C${dr}*" + q("Fixed costs") + "!$F${dr}+" + I("po_deposit") + ",0)", GBP, "Domain's year and the PO box deposit paid in M1."),
    ("close", "Closing cash £", "={c}{open}+{c}{cin}-{c}{cout}", GBP, ""),
]
PR = {}
r = 7
for key, *_ in LINES:
    PR[key] = r
    r += 1
COLS = "BCD"
for key, label, f, fmt, note in LINES:
    rr = PR[key]
    if f is None:
        put(ws, f"A{rr}", label, BOLD)
        for col in "ABCDEF":
            ws[f"{col}{rr}"].fill = BAND
        continue
    put(ws, f"A{rr}", label, BOLD if key in ("rev", "gp", "net", "close") else BLACK)
    put(ws, f"F{rr}", note, NOTE, wrap=True)
    for k, col in enumerate(COLS):
        prev = COLS[k - 1] if k else None
        if isinstance(f, list):
            put(ws, f"{col}{rr}", int(f[k]), BLUE, fmt)
            continue
        if key == "m":
            continue
        ctx = dict(PR)
        ctx.update(c=col, mr=FC_ROWS["Metricool Starter (scheduling + analytics)"], dr=DOMAIN_ROW)
        ctx["p"] = f"{prev}{PR['cumj']}" if prev else "0"
        ctx["prevcum"] = f"{prev}{PR['cumj']}" if prev else "0"
        ctx["prevclose"] = f"{prev}{PR['close']}" if prev else I("opening_cash")
        ctx["prevgp"] = f"({prev}{PR['gp']}+{prev}{PR['cogs']})" if prev else "0"
        formula = f.format(**ctx)
        if not formula.startswith("="):
            formula = "=" + formula
        put(ws, f"{col}{rr}", formula, BOLD if key in ("rev", "gp", "net", "close") else BLACK, fmt)
for k, col in enumerate(COLS):
    ws[f"{col}{PR['m']}"].font = BLACK
SUMKEYS = ["views", "clicks", "signups", "jsales", "bsales", "rj", "rb", "ra", "rm", "rs", "rev", "vat", "fees", "ref", "cogs", "gp", "fx1", "fx2", "ads", "opex", "net", "neteur", "cin", "cout", "cashfixed"]
for key in SUMKEYS:
    rr = PR[key]
    fmt = ws[f"B{rr}"].number_format
    put(ws, f"E{rr}", f"=SUM(B{rr}:D{rr})", BOLD, fmt)
put(ws, f"E{PR['close']}", f"=D{PR['close']}", BOLD, GBP)
put(ws, f"E{PR['cumj']}", f"=D{PR['cumj']}", BOLD, NUM1)
r = PR["close"] + 2
put(ws, f"A{r}", "Lowest closing cash in the 90 days £", BOLD)
put(ws, f"B{r}", f"=MIN(B{PR['close']}:D{PR['close']})", BOLD, GBP)
put(ws, f"F{r}", "If this is below zero, the business needs that much from your own pocket over the period.", NOTE, wrap=True)
LOW_CASH = f"{q('90-day P&L')}!$B${r}"
PL = lambda key, col="E": f"{q('90-day P&L')}!${col}${PR[key]}"

# 90-day totals per scenario on the Scenarios sheet: recompute compactly with each scenario's column
ws = wb["Scenarios"]
r = SC_TOT_ROW
header(ws, r, ["90-day totals", "Conservative", "Base", "Optimistic", "Note"])
r += 1
TOT = [
    ("Journal sales (units)", "jsales_t", NUM1),
    ("Gross revenue £", "rev_t", GBP),
    ("Contribution £", "con_t", GBP),
    ("Fixed costs £", "fix_t", GBP),
    ("Net result £", "net_t", GBP),
    ("Net result €", "neteur_t", EUR),
]
TR = {}
for label, key, fmt in TOT:
    TR[key] = r
    put(ws, f"A{r}", label, BOLD if key == "net_t" else BLACK)
    r += 1
for col in "BCD":
    # month k views = now + (target-now)*k/3 → sum over k=1..3 = 3*now + (target-now)*2
    v = f"(3*{I('m_reel_views_30d')}+({col}{SCR['views']}-{I('m_reel_views_30d')})*2)"
    # months live: M(k) live if k>=shop_live_month; weight views of live months
    vlive = (f"(IF(1>={I('shop_live_month')},{I('m_reel_views_30d')}+({col}{SCR['views']}-{I('m_reel_views_30d')})/3,0)"
             f"+IF(2>={I('shop_live_month')},{I('m_reel_views_30d')}+({col}{SCR['views']}-{I('m_reel_views_30d')})*2/3,0)"
             f"+IF(3>={I('shop_live_month')},{col}{SCR['views']},0))")
    per_view_sales = f"({col}{SCR['cpk']}/1000*({col}{SCR['lsr']}*{col}{SCR['spr']}+{col}{SCR['dpr']}))"
    put(ws, f"{col}{TR['jsales_t']}", f"={vlive}*{per_view_sales}", fmt=NUM1)
    aff = f"{v}/1000*{col}{SCR['apk']}*{I('aff_conv')}*{I('aff_order')}*{I('aff_comm')}"
    put(ws, f"{col}{TR['rev_t']}", f"={col}{TR['jsales_t']}*{J_PRICE}+{aff}", fmt=GBP)
    put(ws, f"{col}{TR['con_t']}", f"={col}{TR['jsales_t']}*{J_PROFIT}+{aff}", fmt=GBP)
    put(ws, f"{col}{TR['fix_t']}", f"=3*{FIXED_TOTAL}", fmt=GBP)
    put(ws, f"{col}{TR['net_t']}", f"={col}{TR['con_t']}-{col}{TR['fix_t']}", BOLD, GBP)
    put(ws, f"{col}{TR['neteur_t']}", f"={col}{TR['net_t']}*{FX}", fmt=EUR)
put(ws, f"E{TR['jsales_t']}", "Excludes the bundle and ads; the P&L sheet adds those for the selected scenario.", NOTE, wrap=True)
SC_NET = {c: f"Scenarios!${c}${TR['net_t']}" for c in "BCD"}
SC_RPK = {c: f"Scenarios!${c}${SCR['rpk']}" for c in "BCD"}
SC_BEV = {c: f"Scenarios!${c}${SCR['bev']}" for c in "BCD"}
SC_VSU = {c: f"Scenarios!${c}${SCR['vsu']}" for c in "BCD"}
SC_JS = {c: f"Scenarios!${c}${TR['jsales_t']}" for c in "BCD"}

# ---------------------------------------------------------------- Ads
ws = sheet("Ads", [56, 15, 15, 15, 70])
put(ws, "A1", "Paid Instagram ads: what a result costs and what it is worth", H1)
put(ws, "A2", "Rule: no spend happens without your OK for that specific spend. Benchmarks are aggregated 2026 figures with no UK split; your own ad screenshot replaces them.", NOTE)
header(ws, 4, ["The €35 test (€5/day x 7 days, one winning reel)", "Expensive clicks", "Middle", "Cheap clicks", "Note"])
r = 5
A = {}
ADL = [
    ("spend_gbp", "Spend £", f"={I('ad_test_eur')}/{FX}", GBP, "€35 converted."),
    ("cpc", "Cost per link click £", None, GBP, "Benchmark $0.40-1.80 converted; middle = average of the two."),
    ("clicks", "Link clicks", "={c}{spend_gbp}/{c}{cpc}", NUM, ""),
    ("impr", "Impressions at Reels CPM (for reference)", None, NUM, "Benchmark Reels CPM $4-8."),
    ("lsr", "Guide page sign-up rate (base scenario)", "=Scenarios!$C$" + str(SCR["lsr"]), PCT, "Same assumption as organic."),
    ("su", "Guide sign-ups", "={c}{clicks}*{c}{lsr}", NUM1, ""),
    ("cpsu", "Cost per guide sign-up £", "=IF({c}{su}=0,0,{c}{spend_gbp}/{c}{su})", GBP, ""),
    ("sales", "Journal sales (sign-ups x purchase rate + direct buyers)", "={c}{su}*Scenarios!$C$" + str(SCR["spr"]) + "+{c}{clicks}*Scenarios!$C$" + str(SCR["dpr"]), NUM1, "Base-scenario assumptions."),
    ("cps", "Cost per journal sale £", "=IF({c}{sales}=0,0,{c}{spend_gbp}/{c}{sales})", GBP, ""),
    ("fol", "Followers if run as a profile-visit boost", None, NUM, "Assumed £0.30-1.50 per follower; not sourced."),
    ("cpf", "Cost per follower £", "=IF({c}{fol}=0,0,{c}{spend_gbp}/{c}{fol})", GBP, ""),
    ("ret", "Contribution earned back from journal sales £", "={c}{sales}*" + J_PROFIT, GBP, ""),
    ("roi", "Return on spend", "=IF({c}{spend_gbp}=0,0,{c}{ret}/{c}{spend_gbp})", PCT, "Below 100% = the test costs money; it buys data, not profit."),
]
for key, *_ in ADL:
    A[key] = r
    r += 1
for key, label, f, fmt, note in ADL:
    rr = A[key]
    put(ws, f"A{rr}", label, BOLD if key in ("cpsu", "cps", "roi") else BLACK)
    put(ws, f"E{rr}", note, NOTE, wrap=True)
    for k, col in enumerate("BCD"):
        if key == "cpc":
            put(ws, f"{col}{rr}", [f"={I('ad_cpc_high')}*{USD2GBP}", f"=({I('ad_cpc_low')}+{I('ad_cpc_high')})/2*{USD2GBP}", f"={I('ad_cpc_low')}*{USD2GBP}"][k], fmt=fmt)
        elif key == "impr":
            put(ws, f"{col}{rr}", [f"={col}{A['spend_gbp']}/({I('ad_cpm_high')}*{USD2GBP})*1000", f"={col}{A['spend_gbp']}/(({I('ad_cpm_low')}+{I('ad_cpm_high')})/2*{USD2GBP})*1000", f"={col}{A['spend_gbp']}/({I('ad_cpm_low')}*{USD2GBP})*1000"][k], fmt=fmt)
        elif key == "fol":
            put(ws, f"{col}{rr}", [f"={col}{A['spend_gbp']}/{I('ad_cpf_high')}", f"={col}{A['spend_gbp']}/(({I('ad_cpf_low')}+{I('ad_cpf_high')})/2)", f"={col}{A['spend_gbp']}/{I('ad_cpf_low')}"][k], fmt=fmt)
        else:
            ctx = dict(A)
            ctx["c"] = col
            put(ws, f"{col}{rr}", f.format(**ctx), BOLD if key in ("cpsu", "cps", "roi") else BLACK, fmt)
r += 1
put(ws, f"A{r}", "Break-even: the most a result can cost before ads lose money", BOLD)
for col in "ABCDE":
    ws[f"{col}{r}"].fill = BAND
r += 1
put(ws, f"A{r}", "Max cost per journal sale £ (= contribution per sale)")
put(ws, f"B{r}", f"={J_PROFIT}", GREEN, GBP)
BE_SALE = f"Ads!$B${r}"
put(ws, f"A{r+1}", "Max cost per guide sign-up £ (= value of a sign-up, base scenario)")
put(ws, f"B{r+1}", f"={SC_VSU['C']}", GREEN, GBP)
BE_SU = f"Ads!$B${r+1}"
put(ws, f"E{r+1}", "At a 2% purchase rate a sign-up is worth ~20p in journal profit within 90 days. Paid sign-ups only pay back once the list buys more than one product (bundle, Substack, later streams).", NOTE, wrap=True)
ws.row_dimensions[r + 1].height = 40
r += 3
put(ws, f"A{r}", "Your ad results (from the screenshot you still owe)", BOLD)
for col in "ABCDE":
    ws[f"{col}{r}"].fill = BAND
r += 1
ACT = [("Spend £", GBP), ("Impressions", NUM), ("Reach", NUM), ("Link clicks or results", NUM), ("Followers gained", NUM), ("Guide sign-ups attributed (src=ig_ad)", NUM), ("Journal sales attributed", NUM)]
act0 = r
for label, fmt in ACT:
    put(ws, f"A{r}", label)
    c = put(ws, f"B{r}", None, BLUE, fmt, YELLOW)
    r += 1
put(ws, f"E{act0}", "Fill these from Instagram > Professional dashboard > Ad tools, or send the screenshot and Claude fills them.", NOTE, wrap=True)
put(ws, f"A{r}", "Your cost per click £", BOLD)
put(ws, f"B{r}", f'=IF(N(B{act0+3})=0,"",B{act0}/B{act0+3})', BOLD, GBP)
put(ws, f"A{r+1}", "Your cost per follower £", BOLD)
put(ws, f"B{r+1}", f'=IF(N(B{act0+4})=0,"",B{act0}/B{act0+4})', BOLD, GBP)
put(ws, f"A{r+2}", "Your cost per guide sign-up £", BOLD)
put(ws, f"B{r+2}", f'=IF(N(B{act0+5})=0,"",B{act0}/B{act0+5})', BOLD, GBP)
put(ws, f"A{r+3}", "Your cost per journal sale £", BOLD)
put(ws, f"B{r+3}", f'=IF(N(B{act0+6})=0,"",B{act0}/B{act0+6})', BOLD, GBP)
put(ws, f"A{r+4}", "Your CPM £", BOLD)
put(ws, f"B{r+4}", f'=IF(N(B{act0+1})=0,"",B{act0}/B{act0+1}*1000)', BOLD, GBP)
AD_MID_CPSU = f"Ads!$C${A['cpsu']}"
AD_MID_CPS = f"Ads!$C${A['cps']}"
AD_CPSU_RANGE = (f"Ads!$B${A['cpsu']}", f"Ads!$D${A['cpsu']}")
AD_CPS_RANGE = (f"Ads!$B${A['cps']}", f"Ads!$D${A['cps']}")
AD_CPF_RANGE = (f"Ads!$B${A['cpf']}", f"Ads!$D${A['cpf']}")

# ---------------------------------------------------------------- Rate card
ws = sheet("Rate card", [52, 15, 15, 15, 70])
put(ws, "A1", "Brand partnership rate card (tied to measured numbers only)", H1)
put(ws, "A2", "Price = average views per reel ÷ 1,000 x creator CPM. Nano-tier floors apply only once you pass 1,000 followers. Every deal needs your OK, #ad disclosure (ASA/CAP), and the outreach rules in community-agent (PO box, consent).", NOTE)
header(ws, 4, ["Inputs", "Today", "At the outreach gate", "", "Note"])
put(ws, "A5", "Average views per reel")
put(ws, "B5", f"={I('m_reel_median')}", GREEN, NUM)
put(ws, "C5", 1000, BLUE, NUM)
put(ws, "E5", "Gate: median reel views ≥ 1,000 for 4 weeks (Gates sheet).", NOTE)
put(ws, "A6", "Followers")
put(ws, "B6", f"={I('m_followers')}", GREEN, NUM)
put(ws, "C6", 1000, BLUE, NUM)
put(ws, "A7", "Creator CPM low / high $")
put(ws, "B7", f"={I('rc_cpm_low')}", GREEN, USD)
put(ws, "C7", f"={I('rc_cpm_high')}", GREEN, USD)
put(ws, "E7", "influee.co 2026: $5-15 per 1,000 views for nano/micro.", NOTE)
header(ws, 9, ["Package", "Today low £", "Today high £", "At gate (low-high midpoint) £", "How it's priced"])
PK = [
    ("One reel (in-feed + reels tab)", 1.0, "Base rate."),
    ("Carousel (7 slides)", 0.8, "0.8x reel: lower reach on feed posts today (53 vs 1.1k views)."),
    ("Story set (3 frames, link sticker)", 0.5, "0.5x reel."),
    ("Link in bio / links page for 7 days", 0.3, "0.3x reel."),
    ("Substack sponsor line (per issue)", 0, "Separate: subscribers x 45% opens ÷ 1,000 x £25 CPM (assumption). £0 until the publication exists."),
    ("Usage rights for brand ads (per month)", 0.3, "+30% of the package per month (common practice, assumption)."),
    ("Category exclusivity (per month)", 0.25, "+25% (assumption)."),
]
r = 10
for name, mult, how in PK:
    put(ws, f"A{r}", name)
    put(ws, f"F{r}", None)
    if mult:
        put(ws, f"B{r}", f"=$B$5/1000*$B$7*{USD2GBP}*{mult}", fmt=GBP)
        put(ws, f"C{r}", f"=$B$5/1000*$C$7*{USD2GBP}*{mult}", fmt=GBP)
        put(ws, f"D{r}", f"=MAX($C$5/1000*($B$7+$C$7)/2*{USD2GBP},IF($C$6>=1000,{I('rc_nano_low')}*{USD2GBP},0))*{mult}", fmt=GBP)
    else:
        put(ws, f"B{r}", f"={I('m_substack_subs')}*0.45/1000*25", fmt=GBP)
        put(ws, f"C{r}", f"=B{r}", fmt=GBP)
        put(ws, f"D{r}", "=1000*0.45/1000*25", fmt=GBP)
    put(ws, f"E{r}", how, NOTE, wrap=True)
    r += 1
RC_REEL_GATE = "'Rate card'!$D$10"
RC_REEL_NOW = "'Rate card'!$C$10"
r += 1
put(ws, f"A{r}", "Sellable today?", BOLD)
put(ws, f"B{r}", f'=IF(AND({I("m_followers")}>=1000,{I("m_reel_median")}>=1000),"Yes","Not yet")', BOLD)
put(ws, f"E{r}", "At today's numbers a reel is worth about £0.50-1.50 to a sponsor, so outreach would cost more in time than it earns.", NOTE, wrap=True)
r += 2
header(ws, r, ["Category (from the sponsorship CRM)", "Fit", "", "", "Notes and red lines"])
CATS = [
    ("Stationery (notebooks, pens, planners)", "Strong", "Natural fit with journaling; also merch overlap."),
    ("Books and publishers (philosophy, psychology)", "Strong", "Affiliate first, sponsored reading lists later."),
    ("Education (courses, learning platforms)", "Good", "Only reputable providers; no 'get rich' courses."),
    ("Mindfulness and meditation apps", "Good", "No clinical or therapy claims; you are not a therapist."),
    ("Productivity software", "Medium", "Fits the Tools highlight; avoid hustle framing."),
    ("Men's grooming", "Weak", "Off-positioning: the brand is not men-only or young-men framed."),
    ("Accessories (watches, bags)", "Medium", "Only minimal, slow-design brands; no luxury flexing."),
    ("Professional development", "Good", "Coaching platforms, writing tools."),
    ("Never", "No", "Gambling, crypto, supplements, alcohol, payday loans, red-pill content, anything making health claims."),
]
r += 1
for cat, fit, note in CATS:
    put(ws, f"A{r}", cat)
    put(ws, f"B{r}", fit, BLUE)
    put(ws, f"E{r}", note, NOTE, wrap=True)
    r += 1

# ---------------------------------------------------------------- Other income
ws = sheet("Other income", [34, 11, 12, 12, 10, 8, 40, 11, 13, 11, 7, 14, 60])
put(ws, "A1", "Other income streams: margin, effort, threshold and order", H1)
put(ws, "A2", "Contribution excludes your time (effort captures that). 'Volume at gate' is a deliberately small assumption for the first month after the gate is met. Score = monthly contribution at gate ÷ effort; rank 1 = do first.", NOTE)
header(ws, 4, ["Stream", "Price £", "Fees + COGS per unit £", "Contribution per unit £", "Margin", "Effort (1-5)", "Gate before it's realistic", "Units/month at gate", "Monthly contribution at gate £", "Score", "Rank", "Horizon", "Notes and risks"])
STREAMS = [
    ("Journal + digital products", f"={J_PRICE}", f"={J_PRICE}-{J_PROFIT}", 1, "Shop live (already built, test mode)", 3, "90 days", "Built and priced by the shop thread. Zero cost of goods."),
    ("Affiliate links (books, stationery)", f"={I('aff_order')}", f"={I('aff_order')}*(1-{I('aff_comm')})", 1, "Any reach; Week 3 of the monetisation plan", 2, "90 days", "Tiny money; useful mainly to measure buying intent. #ad disclosure."),
    ("Print edition of the journal (KDP)", f"={I('kdp_price')}", f"={I('kdp_price')}-{KDP_PROFIT}", 2, "50 digital sales or repeated requests for print", 3, "3-6 months", "No stock; Amazon prints and posts. Cost of goods = printing."),
    ("Merch (POD tee via Etsy)", f"=Merch!$B$6+Merch!$B$7", f"=(Merch!$B$6+Merch!$B$7)-{MERCH_TEE}", 2, "50 journal sales + people asking for merch", 3, "4-6 months", "Physical returns and support; needs samples (~£45)."),
    ("Brand partnerships / sponsored posts", f"={RC_REEL_GATE}", f"={RC_REEL_GATE}*0.05", 3, "≥1,000 followers, median reel views ≥1,000 for 4 weeks, PO box, media kit", 1, "4-8 months", "Rate card ties price to measured views. Each deal needs your OK."),
    ("Live online workshop (90 min)", f"={I('workshop_ticket')}", f"={I('workshop_ticket')}*{I('card_uk_pct')}+{I('card_fixed')}", 3, "≥500 on the email list", 15, "4-6 months", "Free tools (Google Meet). Record it to become course material."),
    ("Paid Substack tier", f"={I('ss_price')}", f"={I('ss_price')}*({I('ss_fee')}+{I('ss_stripe_pct')})+{I('ss_stripe_fixed')}", 3, "1,000 free subscribers, ≥45% opens (Substack plan)", f"=1000*{I('ss_conv')}", "6-12 months", "Recurring, but needs a weekly paid-only piece you'd keep up."),
    ("Small-group reflective mentoring (cohort of 6)", f"={I('mentor_group')}", f"={I('mentor_group')}*{I('card_uk_pct')}+{I('card_fixed')}", 4, "≥1,000 list + 10 people asking", 3, "6-9 months", "Not therapy: reflective mentoring with a clear scope, signposting to professionals, no crisis work. Breaks anonymity unless run under the brand voice only."),
    ("1:1 reflective mentoring (50 min)", f"={I('mentor_1to1')}", f"={I('mentor_1to1')}*{I('card_uk_pct')}+{I('card_fixed')}", 5, "≥1,000 list + 10 people asking", 4, "6-9 months", "Same scope limits. Consider professional indemnity insurance (~£10-15/mo, assumption) before the first paid session."),
    ("Paid community / membership", f"={I('member_price')}", f"={I('member_price')}*({I('ss_fee')}+{I('ss_stripe_pct')})+{I('ss_stripe_fixed')}", 4, "300+ engaged newsletter readers (monetisation plan)", 15, "9-12 months", "Ongoing moderation load; overlaps paid Substack, so pick one."),
    ("Self-paced course", f"={I('course_price')}", f"={I('course_price')}-{I('course_price')}/(1+{I('vat')})+{I('course_price')}*({I('card_uk_pct')}+{I('mp_fee')})+{I('card_fixed')}", 5, "≥1,000 list + 50 journal buyers", 3, "9-12 months", "Sold through the same shop (VAT handled). Big build."),
    ("Licensing the content system to other brands", f"={I('licence_fee')}", f"={I('licence_cost')}", 5, "Moodius meets Phase 0 gates and the engine is productised (strategy/09 Phase 1)", 1, "12+ months", "Contracts, support, IP. Only after the engine runs 2-3 of your own brands."),
]
r = 5
for name, price, cost, effort, gate, vol, horizon, note in STREAMS:
    put(ws, f"A{r}", name, BOLD)
    put(ws, f"B{r}", price, GREEN, GBP)
    put(ws, f"C{r}", cost, BLACK, GBP)
    put(ws, f"D{r}", f"=B{r}-C{r}", fmt=GBP)
    put(ws, f"E{r}", f"=IF(B{r}=0,0,D{r}/B{r})", fmt=PCT)
    put(ws, f"F{r}", effort, BLUE, NUM)
    put(ws, f"G{r}", gate, wrap=True)
    put(ws, f"H{r}", vol, BLUE if not str(vol).startswith("=") else GREEN, NUM)
    put(ws, f"I{r}", f"=D{r}*H{r}", fmt=GBP)
    put(ws, f"J{r}", f"=I{r}/F{r}", fmt=NUM1)
    put(ws, f"L{r}", horizon)
    put(ws, f"M{r}", note, NOTE, wrap=True)
    ws.row_dimensions[r].height = 42
    r += 1
olast = r - 1
for rr in range(5, olast + 1):
    put(ws, f"K{rr}", f"=RANK(J{rr},$J$5:$J${olast})", BOLD, NUM)

# ---------------------------------------------------------------- Gates
ws = sheet("Gates", [44, 46, 13, 13, 11, 60])
put(ws, "A1", "Unlock thresholds: what has to be true before the next spend or stream", H1)
put(ws, "A2", "Current values link to Inputs; update Inputs weekly and the status updates itself. A met gate still needs your OK for any spend.", NOTE)
header(ws, 4, ["Gate", "What it unlocks", "Current", "Target", "Status", "Why this number"])
GATES = [
    ("Shop live", "Product reels P001-P006, journal revenue", f"={I('m_shop_live')}", 1, "Nothing can be sold before this."),
    ("Organic guide sign-ups (cumulative)", "€35 ad test (with your OK)", f"={I('m_signups')}", 25, "Proves the guide page converts organically, so an ad isn't buying the first-ever test."),
    ("A reel at ≥2x the median views", "Pick the ad creative", f"={I('m_best_reel_day')}", f"=2*{I('m_reel_median')}", "Proxy uses the best day's reel views. Boost a proven reel, never an untested one."),
    ("Ad test cost per sign-up ≤ 3x a sign-up's value", "Second ad round (€70-100, with your OK)", "", f"=3*{BE_SU}", "Enter your result from the Ads sheet. 3x allows for the bundle and later streams."),
    ("Journal orders", "Build the £29 bundle", f"={I('m_journal_orders')}", f"={I('bundle_gate')}", "Shop thread's rule (or 6 weeks on sale)."),
    ("Journal orders", "Merch samples (~£45) and the print edition", f"={I('m_journal_orders')}", 50, "Proof people pay for the brand before adding physical products."),
    ("Comments + story replies per week", "VPS + Claude API for comment replies (€6-15/mo)", f"={I('m_comments_week')}", 20, "Below this you answer by hand in a few minutes a day."),
    ("Followers", "Brand outreach (plus PO box and 4 weeks of data)", f"={I('m_followers')}", 1000, "Nano tier starts at 1,000; brands check this first."),
    ("Median reel views", "Brand outreach; base-scenario revenue", f"={I('m_reel_median')}", 1000, "At this level the rate card prices a reel at ~£37 (nano floor); below it outreach isn't worth the time."),
    ("Median reel views", "Phase 0 → Phase 1 of the scaling roadmap", f"={I('m_reel_median')}", 400, "strategy/09 gate (3 weeks in a row)."),
    ("Email list (guide + Substack)", "Live workshop pilot", f"={I('m_signups')}+{I('m_substack_subs')}", 500, "~3% of a list buying a £15 ticket ≈ 15 seats."),
    ("Substack free subscribers", "Paid Substack tier", f"={I('m_substack_subs')}", 1000, "Substack plan gate; at 3% conversion that's ~30 paying."),
    ("Email list (guide + Substack)", "Mentoring pilot (small group first)", f"={I('m_signups')}+{I('m_substack_subs')}", 1000, "Plus 10 people asking unprompted."),
    ("Engaged newsletter readers", "Paid community / membership", f"={I('m_substack_subs')}*0.3", 300, "Monetisation plan gate; engaged ≈ 30% of subscribers (assumption)."),
    ("Months with contribution ≥ fixed costs", "Any new recurring cost", "", 2, "Enter the count from your monthly review; keeps the business self-funding."),
]
r = 5
for gate, unlocks, cur, target, why in GATES:
    put(ws, f"A{r}", gate, BOLD)
    put(ws, f"B{r}", unlocks, wrap=True)
    if cur == "":
        put(ws, f"C{r}", None, BLUE, NUM, YELLOW)
    else:
        put(ws, f"C{r}", cur, GREEN, NUM)
    put(ws, f"D{r}", target, BLUE if not str(target).startswith("=") else GREEN, GBP if "sign-up's value" in gate else NUM)
    if "≤" in gate:
        ws[f"C{r}"].number_format = GBP
        put(ws, f"E{r}", f'=IF(C{r}="","No data",IF(C{r}<=D{r},"Met","Not yet"))', BOLD)
    else:
        put(ws, f"E{r}", f'=IF(C{r}="","No data",IF(C{r}>=D{r},"Met","Not yet"))', BOLD)
    put(ws, f"F{r}", why, NOTE, wrap=True)
    ws.row_dimensions[r].height = 30
    r += 1
glast = r - 1
put(ws, f"A{r+1}", "Gates met", BOLD)
put(ws, f"C{r+1}", f'=COUNTIF(E5:E{glast},"Met")', BOLD, NUM)
put(ws, f"D{r+1}", f"=ROWS(E5:E{glast})", BOLD, NUM)
GATES_MET = f"Gates!$C${r+1}"
GATES_ALL = f"Gates!$D${r+1}"

# ---------------------------------------------------------------- 12-month plan
ws = sheet("12-month plan", [16, 46, 46, 46])
put(ws, "A1", "12-month sequence (gated: a step moves when its gate is met, not on the date)", H1)
header(ws, 3, ["Months", "Focus", "Income active or tested", "Spend that may unlock (each needs your OK)"])
PLAN = [
    ("Nov 2026", "Shop live, guide page, DM keyword funnel, essays weekly from 5 Nov", "Journal, affiliate test", "Domain £10/yr, PO box ~£10/mo"),
    ("Dec 2026", "Day-30 review; holiday gift edition push", "Journal, gift edition, affiliate", "€35 ad test if 25 organic sign-ups"),
    ("Jan 2027", "Day-90 review (31 Jan); Substack vs Ghost revisit 30 Jan", "Journal; bundle if 25 orders", "Second ad round only if the test passed"),
    ("Feb-Mar 2027", "Bundle + workbooks; Phase 1 engine productisation if Phase 0 met", "Journal, bundle, upgrade", "VPS + Claude API if comments ≥ 20/week"),
    ("Apr-Jun 2027", "Print edition and merch pilot if 50 orders; first brand deals if 1k followers / 1k views", "+ print edition, merch, sponsored posts, workshop pilot", "Merch samples ~£45; Etsy listings"),
    ("Jul-Sep 2027", "Paid Substack if 1,000 free; small-group mentoring pilot", "+ paid Substack, mentoring", "Insurance before paid mentoring"),
    ("Oct 2027", "12-month review; decide membership vs course; brands 2-3", "+ membership or course", "Metricool upgrade for more brands (strategy/09)"),
    ("12+ months", "Licensing the content system once it runs 2-3 of your own brands", "+ licensing", "Legal review of a licence contract"),
]
for i, row in enumerate(PLAN):
    for k, val in enumerate(row):
        put(ws, f"{'ABCD'[k]}{4+i}", val, BOLD if k == 0 else BLACK, wrap=True)
    ws.row_dimensions[4 + i].height = 45

# ---------------------------------------------------------------- Your inputs
ws = sheet("Your inputs", [44, 34, 70, 14])
put(ws, "A1", "What only Surafel can provide", H1)
header(ws, 3, ["Input", "Where it goes", "Why", "Status"])
YOU = [
    ("Ad results screenshot", "Ads sheet, yellow cells", "Replaces the benchmark cost per click/follower with your real numbers.", "Owed"),
    ("Approve domain (£10/yr) and PO box (£5-15/mo)", "Fixed costs: Include column", "Both are switched on in the model already; set to 0 if you decline.", "Pending"),
    ("OK for VPS + Claude API (€6-15/mo)", "Fixed costs: Include column", "Off until the comments gate is met.", "Pending"),
    ("Shop live date", "Inputs: Shop live month, Shop live flag", "Revenue starts that month.", "Pending"),
    ("Starting cash / budget for the business", "Inputs: Cash set aside", "Shows whether cash ever goes negative.", "Pending"),
    ("Real Stripe fees and payout schedule once live", "Inputs: Stripe rows, payout delay", "Benchmarks today; your statements later.", "After launch"),
    ("Buyer country mix", "Inputs: Buyer mix", "From Stripe after ~25 sales.", "After launch"),
    ("Merch supplier choice and real base costs", "Merch sheet, blue cells", "Printful prices shown; Printify/Gelato differ. Notebook price is an estimate.", "Later"),
    ("Where you're tax-resident and whether you're VAT-registered", "Tell Claude (affects Merch and own-site sales)", "Stripe Managed Payments and Etsy cover VAT on sales; your income tax isn't modelled. Check with an accountant.", "Open"),
    ("Weekly numbers: sign-ups, orders, comments, Substack subs", "Inputs: Measured section", "Drives the Gates sheet.", "Weekly"),
    ("Mentoring yes/no (it may break anonymity)", "Other income", "Positioned as reflective mentoring, not therapy.", "Later"),
    ("Exchange rates", "Inputs: Currency", "Set to approximate 21 Oct 2026 values.", "Optional"),
]
for i, row in enumerate(YOU):
    for k, val in enumerate(row):
        c = put(ws, f"{'ABCD'[k]}{4+i}", val, BOLD if k == 0 else BLACK, wrap=True)
    ws[f"D{4+i}"].fill = YELLOW
    ws.row_dimensions[4 + i].height = 32

# ---------------------------------------------------------------- Sources
ws = sheet("Sources", [40, 100])
put(ws, "A1", "Sources", H1)
SRC = [
    ("Metricool analytics (measured)", "brand 7224060, IGEV01/05/23/39, pulled 21 Oct 2026"),
    ("Journal pricing and fees", "business/pricing/margins.py and margins.csv (digital-products thread); stripe.com/gb/pricing; support.stripe.com/questions/managed-payments-pricing"),
    ("Instagram ad CPC/CPM 2026", "https://topgrowthmarketing.com/instagram-ads-cost/ (updated 25 Sep 2026; aggregates AdBacklog, WordStream, Ryze.AI, WebFX)"),
    ("Printful tee base + shipping", "https://podvector.ai/articles/printful/costs-and-charges/printful-bella-canvas-3001-price-shipping-time-full-breakdown-for-pod-sellers (May 2026)"),
    ("Printful poster base + shipping", "https://podvector.ai/articles/printful/costs-and-charges/printful-poster-pricing-full-breakdown-for-pod-sellers (May 2026)"),
    ("Gelato pricing", "https://ecommerce-platforms.com/articles/gelato-print-on-demand-pricing (Gelato+ $19.99-29.99/mo; base costs only in dashboard)"),
    ("Creator rates", "https://influee.co/gb/blog/instagram-influencer-pricing (Mar 2026; directional ranges)"),
    ("Substack conversion and fees", "https://bestwriting.com/substack-statistics; substack/10-costs-and-apis.md"),
    ("Bookshop.org affiliate", "https://www.supadu.com/blogs/news-and-views/bookshop-org"),
    ("Etsy fees", "etsy.com/legal/fees (listing $0.20, 6.5% transaction, Etsy Payments UK 4% + £0.20); check before launch"),
    ("Gates and plans", "strategy/09-scaling-roadmap.md; community-agent/docs/06-monetisation-30-day.md; business/funnel/bundle-plan.md; substack/08-calendar-90-day.csv"),
]
for i, (a, b) in enumerate(SRC):
    put(ws, f"A{3+i}", a, BOLD)
    put(ws, f"B{3+i}", b, wrap=True)

# ---------------------------------------------------------------- Start here (first tab)
ws = sheet("Start here", [58, 16, 16, 16, 50])
wb.move_sheet("Start here", offset=-(len(wb.sheetnames) - 1))
put(ws, "A1", "Moodius Aurelius: financial model", H1)
put(ws, "A2", "Costs, cost of goods and postage, per-unit economics, scenarios, 90-day P&L and cash, unlock gates and other income streams. Built 21 Oct 2026 by Claude.", NOTE)
put(ws, "A4", "Colour key", BOLD)
put(ws, "A5", "Blue text = an input you can change", BLUE)
put(ws, "A6", "Black text = a formula", BLACK)
put(ws, "A7", "Green text = linked from another sheet", GREEN)
put(ws, "A8", "Yellow fill = waiting on you", fill=YELLOW)
header(ws, 10, ["Headline numbers (live)", "Conservative", "Base", "Optimistic", "Note"])
HL = [
    ("Fixed costs per month £ (included set)", [f"={FIXED_TOTAL}"] * 3, GBP, "Metricool + domain + PO box by default."),
    ("Fixed costs per month €", [f"={FIXED_TOTAL}*{FX}"] * 3, EUR, "Lean target ≈ €20-25."),
    ("Journal profit per sale £ (blended, after refunds)", [f"={J_PROFIT}"] * 3, GBP, "From the shop thread's prices and fees."),
    ("Journal sales a month to cover fixed costs", [f"=Scenarios!${c}${SCR['bes']}" for c in "BCD"], NUM1, ""),
    ("Revenue per 1,000 views £ (month-3 run rate)", [f"={SC_RPK[c]}" for c in "BCD"], GBP, "Today, measured: £0 (nothing on sale)."),
    ("Views a month needed to cover fixed costs", [f"={SC_BEV[c]}" for c in "BCD"], NUM, "Today: ~1,350 reel views a month."),
    ("Journal sales over the 90 days", [f"={SC_JS[c]}" for c in "BCD"], NUM1, ""),
    ("90-day net result £", [f"={SC_NET[c]}" for c in "BCD"], GBP, "Excludes ads."),
    ("€35 ad test: cost per guide sign-up £ (expensive to cheap clicks)", [f"={AD_CPSU_RANGE[0]}", f"={AD_MID_CPSU}", f"={AD_CPSU_RANGE[1]}"], GBP, "Worth about £0.10-0.41 each in journal profit (Scenarios)."),
    ("€35 ad test: cost per journal sale £", [f"={AD_CPS_RANGE[0]}", f"={AD_MID_CPS}", f"={AD_CPS_RANGE[1]}"], GBP, "Break-even is the journal profit per sale."),
    ("Gates met", [f"={GATES_MET}", f"={GATES_ALL}", ""], NUM, "Met / total, Gates sheet."),
]
r = 11
for label, vals, fmt, note in HL:
    put(ws, f"A{r}", label, BOLD)
    for k, col in enumerate("BCD"):
        if vals[k] != "":
            put(ws, f"{col}{r}", vals[k], GREEN, fmt)
    put(ws, f"E{r}", note, NOTE, wrap=True)
    r += 1
put(ws, f"A{r+1}", "Sheets", BOLD)
GUIDE = [
    ("Inputs", "Every number, with type and source"),
    ("Fixed costs", "Monthly costs in £ and €, with approval status"),
    ("Journals", "Per-sale economics from the shop thread, plus a print edition"),
    ("Merch", "POD tee, print and notebook: cost of goods, postage UK/EU/US, Etsy fees, margin"),
    ("Ads", "€35 test maths, break-even cost per result, slot for your ad results"),
    ("Scenarios", "Conservative / base / optimistic, revenue per 1,000 views, break-even"),
    ("90-day P&L", "Monthly P&L and cash, 2 Nov-31 Jan; pick the scenario in B3"),
    ("Rate card", "Brand-deal pricing tied to measured views; partner categories"),
    ("Other income", "Mentoring, membership, workshops, paid Substack, affiliates, brand deals, licensing: ranked"),
    ("Gates", "Thresholds that unlock each spend or stream, with live status"),
    ("12-month plan", "Sequence of streams and spends"),
    ("Your inputs", "What only you can provide"),
]
for i, (a, b) in enumerate(GUIDE):
    put(ws, f"A{r+2+i}", a)
    put(ws, f"B{r+2+i}", b, NOTE)

for name in wb.sheetnames:
    wb[name].sheet_properties.tabColor = "C9742E" if name in ("Start here", "Inputs", "Your inputs") else "3A4049"
wb.save(OUT)
print("wrote", OUT)
