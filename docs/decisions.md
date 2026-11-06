# Decision log

The design choices behind the model and its build, what each one bought, and what it
cost. Constants referenced here live in `src/assumptions.py`, `src/wacc.py`,
`src/build_model.py`, `src/cache_values.py` and `src/verify_model.py`. Where
[`methodology.md`](methodology.md) already argues the reasoning in full, this log
summarises it and points to the section.

### 1. Generate the workbook from code, with every calculated cell a live formula

**Decision.** `build_model.py` writes the workbook with openpyxl. The only numbers typed
into cells are historical actuals and forecast assumptions. Everything else is an Excel
formula (549 formula cells in the current build).
**Why.** A reviewer can click any output and trace it back to an input inside Excel, and
the Python source is a reviewable, diffable record of how the model is built.
**Tradeoff.** openpyxl writes formulas but can't evaluate them, which is why decisions 3
and 4 exist. The Python files, not the workbook, are the source of truth: a change made
by editing the workbook is lost on the next rebuild. Some build-time logic also doesn't
follow in-workbook edits, notably the sensitivity axes ([#4](https://github.com/pragyan-varma/cmg-dcf-valuation/issues/4)).

### 2. Put a source note next to every input

**Decision.** Every assumption in `assumptions.py` and `wacc.py` carries a `*_SOURCE`
string, and every row in `data/historicals.csv` has a `source` column. `build_model.py`
writes these into column I beside the input cell.
**Why.** No number in the workbook is unsourced. The filing, the figure and any
judgement are visible where the number is used.
**Tradeoff.** The notes are free text and nothing checks them against the model. One
has already drifted: the exit-multiple note says ~19.8x where the model computes 20.5x
([#2](https://github.com/pragyan-varma/cmg-dcf-valuation/issues/2)). The print areas also leave out the source-note column so the
pages fit one page wide, so the notes don't appear on a printout.

### 3. Write cached values into the file after building it

**Decision.** `cache_values.py` recalculates the workbook with the `formulas` package,
writes each result into the cell's `<v>` element next to the untouched formula, and sets
`fullCalcOnLoad` so Excel still recalculates on open.
**Why.** Viewers with no calculation engine (macOS Quick Look, browser previews, most
phone and webmail viewers) otherwise show every formula cell as blank. The README's "Why
the `cache_values.py` step exists" section explains this in full.
**Tradeoff.** It rewrites the sheet XML with regular expressions, and it assumes
`xl/worksheets/sheetN.xml` follows the workbook's tab order. That holds for openpyxl's
output but isn't a general guarantee. It adds a second dependency, and the step exits
with an error if any Excel error value is found.

### 4. Verify the build by recalculating it, not by eye

**Decision.** `verify_model.py` recalculates every formula and asserts eight groups of
checks, 11 assertions in total: no Excel error values; built EBIT ties to reported EBIT
in all five years; built restaurant count ties to the reported count; EV = PV(UFCF) +
PV(TV); equity value = EV − debt + cash and price = equity / diluted shares; each
sensitivity table's base-case cell equals the bridge price; terminal growth is below
WACC; and every blue input on the forecast tabs feeds at least one formula.
**Why.** Tie-outs and bridge arithmetic are the errors a reviewer would check first, and
they can be checked mechanically on every build.
**Tradeoff.** It checks internal consistency, not whether the assumptions are
reasonable. The error scan skips column B on every sheet, because that column holds `#`
unit labels. CI runs it on every push and pull request
([#1](https://github.com/pragyan-varma/cmg-dcf-valuation/issues/1)), which takes about 30
seconds per run and makes `requirements.txt` and the Python version part of the contract.

### 5. Build revenue as units × AUV × a calibrated realisation factor

**Decision.** Revenue = average restaurants × AUV × 0.9867, where 0.9867 is the
FY2023–FY2025 average of reported revenue ÷ (average units × AUV), computed on the
Historicals tab.
**Why.** Unit growth and AUV moved in opposite directions in FY2025, and a single
top-line growth rate would hide that. See [`methodology.md`](methodology.md) §1.1–1.2.
**Tradeoff.** It adds a calibration input. FY2021–22 are left out of the average
because AUV was disclosed to only one decimal in those years, so the factor rests on
three data points.

### 6. Forecast costs at the EBIT-margin level, not line by line

**Decision.** The forecast applies one EBIT-margin path (14.5% in FY2026E, recovering to
16.3% in FY2030E). The Historicals tab common-sizes every cost line, so the margin sits
next to its history.
**Why.** It keeps the number of assumptions small and puts judgement on the series that
matters most after WACC. See [`methodology.md`](methodology.md) §3.
**Tradeoff.** The model can't isolate a single cost driver, such as the tariff impact on
food costs that the FY2025 10-K flags (README Model limitation 4).

### 7. Let WACC equal the cost of equity, because there is no debt

**Decision.** WACC = 4.78% + 0.94 × 5.0% = 9.48%, with a debt weight of zero. A pre-tax
cost of debt (5.38%) is carried so the formula is complete, but it carries no weight. A
check cell on the WACC tab confirms that WACC equals the cost of equity.
**Why.** Chipotle's only facility is an undrawn $500m revolver, and long-term debt is
zero in FY2021–FY2025. A debt tranche would have to be invented. See
[`methodology.md`](methodology.md) §6.
**Tradeoff.** The whole discount rate rests on CAPM inputs from single sources. Using
Damodaran's 4.14% implied ERP instead of 5.0% raises the implied price from $20.12 to
$22.72. Beta isn't cross-checked against peers ([#8](https://github.com/pragyan-varma/cmg-dcf-valuation/issues/8)).

### 8. Treat operating leases as an operating expense

**Decision.** Occupancy cost stays inside EBIT, and the $5,075.8m of operating lease
liabilities is excluded from net debt in the bridge.
**Why.** It's the internally consistent pairing. Deducting the liability while rent is
still in EBIT would count the obligation twice. See [`methodology.md`](methodology.md) §7.
**Tradeoff.** The model's EV/EBITDA (20.5x) isn't comparable with screeners that
capitalise leases. The methodology's claim that the two treatments converge is argued
but not demonstrated in the repo. The `EXCLUDE_OPERATING_LEASES_FROM_NET_DEBT` flag in
`wacc.py` isn't read by the build, so the treatment can't be switched
([#6](https://github.com/pragyan-varma/cmg-dcf-valuation/issues/6)).

### 9. Gordon Growth as the primary terminal method, exit multiple as a flagged cross-check

**Decision.** The terminal value is Gordon Growth at 2.25%. An 18.0x exit multiple is
computed alongside it, and neither is averaged with the other. Formula flags fire when
the implied exit multiple falls outside 10x–25x, when the implied perpetual growth is
above 3% or below 0, and when terminal value exceeds 75% of EV.
**Why.** Gordon Growth is anchored to cash flows and GDP-level growth. Valuing with a
market multiple and then concluding that the market is right would be circular. See
[`methodology.md`](methodology.md) §8.3–8.4.
**Tradeoff.** The two methods disagree sharply (8.6x implied multiple against 5.92%
implied growth), and the model reports the disagreement rather than resolving it. All
three flags fire on the base case: 8.6x is below 10x, 5.92% is above 3%, and terminal
value is 78.2% of EV.

### 10. Normalise terminal-year capex

**Decision.** Terminal capex is set to 3.8% of revenue (3.1% maintenance, equal to D&A,
plus ~0.7% growth capital) instead of carrying forward FY2030E's 5.6%. The unadjusted
terminal value is shown beside it.
**Why.** A business growing 2.25% forever doesn't spend like one growing units 6.5% a
year. See [`methodology.md`](methodology.md) §8.2.
**Tradeoff.** It's a single judgement call worth $2.30 a share: rebuilding with 5.6%
terminal capex gives $17.82 instead of $20.12.

### 11. Mid-year discounting for the forecast years, a full five periods for the terminal value

**Decision.** The forecast years use discount periods of 0.5–4.5, set by a labelled
offset cell on the DCF tab (0.5). The terminal value is discounted at n = 5.0 from its
own input cell.
**Why.** Cash arrives through the year, but the terminal value is a year-5 year-end
value. Putting both conventions in input cells makes the choice visible and reversible.
See [`methodology.md`](methodology.md) §8.5.
**Tradeoff.** The two conventions differ, and the choice moves the answer. Year-end
discounting throughout gives $19.93, and discounting the terminal value at n = 4.5 gives
$20.81. The model uses neither.

### 12. Sensitivity tables as explicit formulas, not Excel data tables

**Decision.** Each of the 156 cells (13 × 7 in Table A, 13 × 5 in Table B) is its own
formula, which re-discounts the forecast cash flows and rebuilds the terminal value for
that pair of inputs. Cells return `NA()` when WACC is within 0.5% of terminal growth.
**Why.** The values recalculate live and tie to the bridge (asserted by
`verify_model.py`), without relying on Excel's data-table feature. See
[`methodology.md`](methodology.md) §10.
**Tradeoff.** The formulas are long and hard to read. The axes are fixed at build time,
and the base case is highlighted only if it falls exactly on a grid point, so an
off-grid terminal growth such as 2.4% fails verification
([#4](https://github.com/pragyan-varma/cmg-dcf-valuation/issues/4)). Table B flexes only the FY2030E margin, so FY2026E–FY2029E
cash flows stay at the base case.
