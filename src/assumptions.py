"""
CMG DCF - all forecast drivers in one place.

Every value below is either (a) taken directly from a filing / market source, or
(b) a judgement call anchored to a disclosed historical figure or to management
guidance. Each entry carries a SOURCE string that is written into the Excel
workbook next to the input cell, so no number in the model is unsourced.

Conventions
-----------
* All dollar amounts are in USD millions.
* Percentages are decimals (0.145 = 14.5%).
* NWC sign convention: `NWC_PCT_OF_DELTA_REVENUE` is expressed as a percentage
  of the *change* in revenue, POSITIVE = cash SOURCE. Chipotle runs negative
  working capital (guests pay at the point of sale, suppliers are paid on ~10-day
  terms), so growth generally releases cash rather than consuming it.
"""

# --------------------------------------------------------------------------
# Period setup
# --------------------------------------------------------------------------
LAST_ACTUAL_FY = 2025
FORECAST_YEARS = [2026, 2027, 2028, 2029, 2030]      # 5-year explicit forecast
HISTORICAL_YEARS = [2021, 2022, 2023, 2024, 2025]

VALUATION_DATE = "2025-12-31"
VALUATION_DATE_NOTE = (
    "Model is struck as of fiscal year-end 12/31/2025, the balance-sheet date of "
    "the most recent 10-K. Cash flows are discounted from that date; net debt and "
    "share count are taken as of that date. See README 'Open Items' for the "
    "timing gap versus the current market price."
)

# --------------------------------------------------------------------------
# Revenue build: units x AUV  (Chipotle is 100% company-operated; the 14
# partner-operated restaurants are licensed and generate no consolidated
# restaurant revenue, so they are deliberately excluded.)
# --------------------------------------------------------------------------
NEW_UNIT_OPENINGS = {2026: 347, 2027: 355, 2028: 360, 2029: 365, 2030: 370}
NEW_UNIT_OPENINGS_SOURCE = (
    "FY2025 10-K MD&A: 'We expect to open approximately 350 to 370 restaurants in "
    "2026, which includes 10 to 15 international partner-operated restaurants.' "
    "Midpoint 360 less ~13 partner-operated = 347 company-owned in FY2026. "
    "FY2027-30 held roughly flat to modestly up, consistent with the FY2021-25 "
    "trend (215 / 236 / 271 / 304 / 334) and the stated long-term goal of 7,000 "
    "restaurants in the U.S. and Canada."
)

UNIT_CLOSURES = {2026: -18, 2027: -18, 2028: -18, 2029: -18, 2030: -18}
UNIT_CLOSURES_SOURCE = (
    "FY2021-25 permanent closures plus relocations averaged 17/yr (17, 15, 21, 15, "
    "18 per the 10-K Restaurant Activity tables). Held at 18/yr."
)

AUV_GROWTH = {2026: 0.000, 2027: 0.015, 2028: 0.020, 2029: 0.025, 2030: 0.025}
AUV_GROWTH_SOURCE = (
    "FY2026: flat. Management guides FY2026 comparable restaurant sales to 'be "
    "about flat' (FY2025 10-K MD&A); H1 2026 revenue of $6,436.8m (Q2 2026 10-Q) "
    "is +8.4% YoY against ~8.5% average-unit growth, implying AUV roughly flat. "
    "FY2027-30: 1.5% rising to 2.5%, i.e. menu pricing of ~2-3% (FY2025 menu price "
    "increase was 2.1%) partly offset by continued new-unit AUV dilution. Note AUV "
    "growth runs below comps in expansion years because the denominator includes "
    "lower-volume new units."
)

COMP_SALES_GROWTH = {2026: 0.000, 2027: 0.015, 2028: 0.020, 2029: 0.025, 2030: 0.025}
COMP_SALES_GROWTH_SOURCE = (
    "Disclosed as context, not as the revenue driver. FY2026 'about flat' per "
    "FY2025 10-K MD&A. History: +19.3% (2021), +8.0% (2022), +7.9% (2023), +7.4% "
    "(2024), -1.7% (2025)."
)

# Reconciles (average units x AUV) to reported revenue. Captures the partial-year
# contribution of units opened during the period and the fact that AUV is a
# trailing-12-month figure for units open >= 12 months.
REVENUE_REALIZATION_FACTOR = 0.9867
REVENUE_REALIZATION_FACTOR_SOURCE = (
    "Computed as the FY2023-FY2025 average of [reported revenue / (average units x "
    "AUV)]: 0.988 (2023), 0.983 (2024), 0.989 (2025). Calibration input; see the "
    "Historicals tab where it is computed from filed figures."
)

# --------------------------------------------------------------------------
# Margin, tax and capital intensity
# --------------------------------------------------------------------------
EBIT_MARGIN = {2026: 0.145, 2027: 0.150, 2028: 0.155, 2029: 0.160, 2030: 0.163}
EBIT_MARGIN_SOURCE = (
    "PATH: compression then partial recovery - NOT a straight-line expansion. "
    "Actuals: 10.7% (2021), 13.4% (2022), 15.8% (2023), 16.9% (2024), 16.2% (2025). "
    "H1 2026 operating margin was 14.3% ($922.7m on $6,436.8m, Q2 2026 10-Q) versus "
    "17.5% in H1 2025, so FY2026 is set at 14.5%. FY2027-30 recover to 16.3% - back "
    "to the FY2025 level but still below the FY2024 peak of 16.9% - as the tariff "
    "impact on food, beverage and packaging costs flagged in the FY2025 10-K "
    "normalises and comps return to positive territory. Terminal margin = 16.3%."
)

EFFECTIVE_TAX_RATE = 0.240
EFFECTIVE_TAX_RATE_SOURCE = (
    "FY2022-FY2025 reported effective rates averaged 23.9% (23.9% / 24.2% / 23.7% / "
    "23.6%; FY2025 10-K Note 8). FY2021's 19.7% is excluded as it was inflated by "
    "unusually large excess tax benefits on equity compensation. Rounded to 24.0%."
)

DA_PCT_OF_REVENUE = {2026: 0.031, 2027: 0.031, 2028: 0.031, 2029: 0.031, 2030: 0.031}
DA_PCT_OF_REVENUE_SOURCE = (
    "D&A / revenue: 3.4% (2021), 3.3% (2022), 3.2% (2023), 3.0% (2024), 3.0% (2025); "
    "H1 2026 = 3.0%. Held at 3.1% - slightly above the most recent year, reflecting "
    "the heavier fixed-asset base being built (Chipotlanes, kitchen automation)."
)

CAPEX_PCT_OF_REVENUE = {2026: 0.065, 2027: 0.062, 2028: 0.060, 2029: 0.058, 2030: 0.056}
CAPEX_PCT_OF_REVENUE_SOURCE = (
    "FY2026 is guided: 'In 2026, we expect to incur about $834.1 million in total "
    "capital expenditures' (FY2025 10-K MD&A), which is ~6.5% of forecast FY2026 "
    "revenue. Build cost is disclosed at ~$1.5m gross / ~$1.3m net of landlord "
    "reimbursements per new restaurant. FY2027-30 step down to 5.6% as absolute "
    "openings flatten against a larger revenue base. Actual capex/revenue: 5.9% "
    "(2021), 5.5% (2022), 5.7% (2023), 5.2% (2024), 5.6% (2025)."
)

NWC_PCT_OF_DELTA_REVENUE = 0.005
NWC_PCT_OF_DELTA_REVENUE_SOURCE = (
    "POSITIVE = cash SOURCE. Computed from the 10-K cash flow statements as the sum "
    "of the AR, inventory, prepaid, other assets, AP, accrued payroll, accrued "
    "liabilities, unearned revenue and other long-term liability lines, divided by "
    "the change in revenue: -0.8% (2021), +0.5% (2022), +4.9% (2023), +5.0% (2024), "
    "-7.2% (2025); 5-year average +0.5%. Income taxes payable and the operating "
    "lease asset/liability lines are excluded - taxes are handled inside NOPAT and "
    "leases are treated as an operating expense (see the WACC tab). Chipotle states "
    "in the FY2025 10-K that it 'has not required significant working capital "
    "because guests generally pay using cash or credit and debit cards' and it pays "
    "suppliers 'generally within ten days'."
)

# --------------------------------------------------------------------------
# Terminal value
# --------------------------------------------------------------------------
TERMINAL_GROWTH = 0.0225
TERMINAL_GROWTH_SOURCE = (
    "2.25%, the midpoint of the 2.0-2.5% long-run U.S. nominal GDP / inflation "
    "anchor. Must be below WACC. A perpetual growth rate above nominal GDP would "
    "imply Chipotle eventually becomes the whole economy."
)

TERMINAL_CAPEX_PCT_OF_REVENUE = 0.038
TERMINAL_CAPEX_PCT_OF_REVENUE_SOURCE = (
    "Terminal-year normalisation. Year-5 capex of 5.6% of revenue supports ~7% unit "
    "growth and is inconsistent with a 2.25% perpetuity. Normalised to 3.8% = D&A of "
    "3.1% of revenue (maintenance) plus ~0.7% of growth capital to sustain 2.25% "
    "growth. Without this adjustment the terminal value is understated. The "
    "unadjusted figure is shown alongside it on the Terminal Value tab."
)

EXIT_EBITDA_MULTIPLE = 18.0
EXIT_EBITDA_MULTIPLE_SOURCE = (
    "Cross-check only. CMG currently trades at ~19.8x LTM EV/EBITDA on a "
    "leases-as-opex basis (EV of $45.5bn / FY2025 EBITDA of $2,297m; see the WACC "
    "and Terminal Value tabs where this is computed from market inputs). 18.0x "
    "applies a modest discount for multiple compression as unit growth decelerates."
)

TV_DISCOUNT_PERIOD = 5.0
TV_DISCOUNT_PERIOD_SOURCE = (
    "Terminal value is a year-5 year-END value, so it is discounted a full 5.0 "
    "periods even though the explicit cash flows use mid-year convention. Some "
    "practitioners use 4.5 for internal consistency with mid-year; that convention "
    "would raise the implied share price by 3.4% ($20.81 versus $20.12)."
)

# --------------------------------------------------------------------------
# Market data (retrieved 2026-09-06)
# --------------------------------------------------------------------------
MARKET_DATA_RETRIEVAL_DATE = "2026-09-06"

CURRENT_SHARE_PRICE = 36.96
CURRENT_SHARE_PRICE_SOURCE = (
    "stockanalysis.com/stocks/cmg/, closing price 2026-09-04 (last completed "
    "session); retrieved 2026-09-06."
)

SHARES_OUTSTANDING_AT_VALUATION = 1302.423
SHARES_OUTSTANDING_SOURCE = (
    "FY2025 10-K cover page, dei:EntityCommonStockSharesOutstanding = 1,302,423,000 "
    "as of 2026-01-30 (the count closest to the 12/31/2025 valuation date). "
    "Post 50-for-1 split. The Q2 2026 10-Q cover reports 1,265,418,000 as of "
    "2026-07-24 after further buybacks - see README 'Open Items'."
)

DILUTION_FACTOR = 1.00395
DILUTION_FACTOR_SOURCE = (
    "FY2025 diluted weighted-average shares (1,342,616k) / basic weighted-average "
    "shares (1,337,336k) = 1.00395, per the FY2025 10-K income statement. Applied "
    "to shares outstanding to approximate a fully diluted count."
)
