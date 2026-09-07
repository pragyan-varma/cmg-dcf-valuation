"""
WACC / CAPM inputs and calculation for Chipotle Mexican Grill (CMG).

The headline point about Chipotle's capital structure: it has no traditional
borrowings. The FY2025 10-K (Note 12, Debt) discloses a $500.0 million revolving
credit facility with JPMorgan Chase as administrative agent that was UNDRAWN at
12/31/2025, and us-gaap:LongTermDebt is reported as zero in every year FY2021-25.
Chipotle also holds ~$1.25 billion of cash and investments.

Consequence: D / (D + E) is ~0, so WACC collapses to the cost of equity. The
model says that explicitly rather than inventing a debt tranche to make the
formula look fuller.

LEASE TREATMENT (stated again on the WACC tab of the workbook):
Operating leases are treated as an OPERATING EXPENSE. Occupancy cost stays inside
EBIT, and the $5.08 billion of operating lease liabilities is therefore EXCLUDED
from net debt. This is the internally consistent pairing. The alternative - treat
capitalised leases as debt, add rent back to EBIT, and deduct lease liabilities in
the bridge - is a legitimate and common treatment; see docs/methodology.md.
"""

# --------------------------------------------------------------------------
# Cost of equity inputs (retrieved 2026-09-06)
# --------------------------------------------------------------------------
RISK_FREE_RATE = 0.0478
RISK_FREE_RATE_SOURCE = (
    "U.S. Department of the Treasury, Daily Treasury Par Yield Curve Rates, 10-year "
    "constant maturity = 4.78% on 2026-09-04 (most recent published session). "
    "Retrieved 2026-09-06 from home.treasury.gov."
)

LEVERED_BETA = 0.94
LEVERED_BETA_SOURCE = (
    "stockanalysis.com/stocks/cmg/statistics/, 5-year monthly beta = 0.94; retrieved "
    "2026-09-06. Because Chipotle carries no financial debt, its levered beta is "
    "effectively its unlevered beta - no re-levering is required."
)

EQUITY_RISK_PREMIUM = 0.050
EQUITY_RISK_PREMIUM_SOURCE = (
    "5.0%, the low end of the 5.0-5.5% mature-market range commonly applied in "
    "practice. For reference, Damodaran's implied ERP for the S&P 500 on 2026-09-01 "
    "was 4.14% (trailing 12-month, adjusted payout; pages.stern.nyu.edu/~adamodar, "
    "retrieved 2026-09-06). Using 4.14% would lower the cost of equity by ~81bps and "
    "raise the implied value materially - flagged in README 'Open Items'."
)

# --------------------------------------------------------------------------
# Cost of debt / capital structure
# --------------------------------------------------------------------------
TOTAL_DEBT = 0.0
TOTAL_DEBT_SOURCE = (
    "FY2025 10-K Note 12, Debt: $500.0m revolving credit facility, undrawn at "
    "2025-12-31. us-gaap:LongTermDebt = 0 in FY2021-FY2025."
)

PRETAX_COST_OF_DEBT = 0.0538
PRETAX_COST_OF_DEBT_SOURCE = (
    "Illustrative only, and it carries zero weight in the WACC because debt is zero. "
    "Set at the drawn rate on the undrawn revolver: SOFR + 1.125% per FY2025 10-K "
    "Note 12, proxied here with the 10-year Treasury of 4.78% + 60bps."
)

EXCLUDE_OPERATING_LEASES_FROM_NET_DEBT = True


def cost_of_equity(rf=RISK_FREE_RATE, beta=LEVERED_BETA, erp=EQUITY_RISK_PREMIUM):
    """CAPM: Re = Rf + beta x ERP."""
    return rf + beta * erp


def wacc(equity_value, debt=TOTAL_DEBT, tax_rate=0.240,
         rf=RISK_FREE_RATE, beta=LEVERED_BETA, erp=EQUITY_RISK_PREMIUM,
         rd=PRETAX_COST_OF_DEBT):
    """WACC = E/(D+E) x Re + D/(D+E) x Rd x (1 - t)."""
    re = cost_of_equity(rf, beta, erp)
    total = equity_value + debt
    we = equity_value / total
    wd = debt / total
    return we * re + wd * rd * (1 - tax_rate)


if __name__ == "__main__":
    import assumptions as a
    mcap = a.CURRENT_SHARE_PRICE * a.SHARES_OUTSTANDING_AT_VALUATION
    print(f"Market cap (current price x shares o/s): ${mcap:,.1f}m")
    print(f"Cost of equity (CAPM):                   {cost_of_equity():.2%}")
    print(f"Debt weight:                             {TOTAL_DEBT / (TOTAL_DEBT + mcap):.2%}")
    print(f"WACC:                                    {wacc(mcap):.2%}")
