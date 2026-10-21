"""Per-sale margins for the Moodius product line. Run: python3 margins.py  (writes margins.csv)

Assumptions (edit here, everything else is computed):
- Prices are what the buyer pays, VAT included (Stripe Managed Payments, tax_behavior=inclusive).
- VAT: 20% assumed on every digital sale. Conservative: UK e-publications are zero-rated, but
  journals made mainly for writing in may not qualify, and EU rates vary (often lower for ebooks).
- Stripe card fees, UK account (stripe.com/gb/pricing, checked 21 Oct 2026): UK standard 1.5% + 20p,
  EEA 2.5% + 20p, international 3.15% + 20p, +2% when currency conversion is needed.
- Managed Payments: +3.5% of the transaction (support.stripe.com/questions/managed-payments-pricing).
- Lemon Squeezy fallback: 5% + 50¢ (≈38p) per sale, VAT handled by them; shown as its own column.
- Refunds: not deducted here; the finance model applies its own refund rate (suggest 3%, an assumption).
- Hosting, file delivery and email: £0 per sale on the free tiers.
- Personalised items cost a few minutes of Surafel's time, valued at £15/hour.
"""
import csv, os

VAT = 0.20
MP = 0.035
CARDS = {"UK card": (0.015, 0.20), "EEA card": (0.025 + 0.02, 0.20), "International card": (0.0315 + 0.02, 0.20)}
LS = (0.05, 0.38)  # Lemon Squeezy fallback, includes its own processing
HOUR = 15.0

# name, price, production cost per sale (£), minutes of manual work per sale, status
PRODUCTS = [
    ("Seven Days of Honest Reflection (free guide)", 0.00, 0.00, 0, "Live"),
    ("The Unexamined Self (journal)", 14.00, 0.00, 0, "Live"),
    ("Themed 14-day journal (one per highlight)", 6.00, 0.00, 0, "Planned"),
    ("Workbook (Feeling Clearly / How You Attach / What You Live By)", 9.00, 0.00, 0, "Planned"),
    ("The Examined Life bundle", 29.00, 0.00, 0, "Planned"),
    ("Bundle upgrade for journal buyers", 15.00, 0.00, 0, "Planned"),
    ("Personalised journal (journal + personalisation)", 19.00, 0.00, 3, "Built (test mode)"),
    ("Gift edition (personalised + gift page + chosen send date)", 22.00, 0.00, 4, "Built (test mode)"),
    ("Personalised bundle", 34.00, 0.00, 3, "Planned"),
]

def sale(price, cost, minutes, card):
    if price == 0:
        return dict(vat=0, fees=0, net=-cost - minutes / 60 * HOUR)
    pct, fixed = CARDS[card]
    vat = price - price / (1 + VAT)
    fees = price * (pct + MP) + fixed
    labour = minutes / 60 * HOUR
    return dict(vat=vat, fees=fees, net=price - vat - fees - cost - labour)

rows = []
for name, price, cost, minutes, status in PRODUCTS:
    r = {"product": name, "price_gbp": f"{price:.2f}", "status": status}
    for card in CARDS:
        s = sale(price, cost, minutes, card)
        key = card.split()[0].lower()
        r[f"vat_{key}"] = f"{s['vat']:.2f}"
        r[f"fees_{key}"] = f"{s['fees']:.2f}"
        r[f"profit_{key}"] = f"{s['net']:.2f}"
        r[f"margin_{key}"] = f"{(s['net'] / price * 100) if price else 0:.0f}%"
    if price:
        ls_fees = price * LS[0] + LS[1]; ls_net = price - (price - price / (1 + VAT)) - ls_fees - cost - minutes / 60 * HOUR
    else:
        ls_fees, ls_net = 0, 0
    r["fees_lemonsqueezy"] = f"{ls_fees:.2f}"; r["profit_lemonsqueezy"] = f"{ls_net:.2f}"
    rows.append(r)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "margins.csv")
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

for r in rows:
    print(f"{r['product'][:55]:55} £{r['price_gbp']:>6}  UK £{r['profit_uk']:>6} ({r['margin_uk']:>4})  EEA £{r['profit_eea']:>6}  Intl £{r['profit_international']:>6}  fees UK £{r['fees_uk']}  vat £{r['vat_uk']}  LS £{r['profit_lemonsqueezy']}")

# Break-even on fixed costs, using the journal's UK profit
FIXED = {"Domain (£10/yr)": 10 / 12, "PO box / virtual address (mid estimate)": 10.0}
monthly = sum(FIXED.values())
j = float(next(r for r in rows if r["product"].startswith("The Unexamined"))["profit_uk"])
print(f"\nFixed costs £{monthly:.2f}/month -> break-even {monthly / j:.1f} journal sales/month (UK cards)")
print(f"With a €6 (~£5.20) VPS as well: {(monthly + 5.2) / j:.1f} sales/month")
