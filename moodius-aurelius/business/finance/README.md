# Moodius finance model

`moodius-finance-model.xlsx` is the working model: fixed costs (GBP + EUR), cost of goods and postage, per-unit economics for journals, merch and ads, scenarios, a 90-day P&L and cash view (2 Nov 2026 - 31 Jan 2027), a brand rate card, other income streams ranked by effort vs margin, unlock gates and a 12-month sequence. Start on the "Start here" tab; change numbers only on "Inputs" (blue cells) and the yellow cells.

- Rebuild: `python3 build_model.py`, then recalculate (open in Excel/LibreOffice, or the xlsx skill's `recalc.py`).
- Journal prices/fees come from `../pricing/margins.py` (digital-products thread). The Journals tab recomputes them and flags any mismatch with `margins.csv`.
- Measured numbers: Metricool, pulled 21 Oct 2026. Benchmarks are cited on the Sources tab; anything unsourced is labelled Assumption.
- Summary page: `summary.html` (published as an artifact).
- Google Sheets: File > Import > Upload this xlsx (formulas survive).
