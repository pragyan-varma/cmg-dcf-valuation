# Methodology — why each assumption is what it is

This is the document that has to survive *"why did you assume that?"* Every assumption
below is tied to a filed historical figure, to management guidance, or to a stated
benchmark. Where I made a judgement call, I say so and I say what would change it.

Companion documents: [`../README.md`](../README.md) for sources and open items,
[`walkthrough.md`](walkthrough.md) for how to present this verbally.

---

## 1. Structural choices

### 1.1 Why revenue is built units × AUV, not a growth rate

Chipotle is a unit-growth story. Revenue is driven by two independent levers that behave
differently and can be forecast separately:

- **Restaurant count** — a physical, capital-constrained variable that management guides to
  explicitly, and that has grown every single year
- **AUV** — a price-and-traffic variable that is cyclical and, in FY2025, actually declined

Collapsing both into one "revenue grows 9%" input hides the fact that FY2025 revenue growth
of 5.4% was entirely unit growth (+8.5%) offset by an AUV decline of (3.4%). A blunt top-line
growth rate would have let me carry FY2024's momentum forward and miss the deterioration that
is the single most important thing happening at this company right now.

The build is:

```
Revenue = Average units during the year  ×  AUV  ×  Revenue realisation factor
```

### 1.2 The revenue realisation factor (0.9867x)

Average units × AUV over-states revenue, because AUV is a *trailing-twelve-month* figure for
restaurants open at least 12 full months, while units opened during the year contribute only
a partial year of sales. The Historicals tab computes the reconciling factor from filed data:

| | FY2021A | FY2022A | FY2023A | FY2024A | FY2025A |
|---|---|---|---|---|---|
| Revenue / (avg units × AUV) | 1.0125x | 1.0024x | 0.9876x | 0.9832x | 0.9892x |

**The forecast uses the FY2023–FY2025 average of 0.9867x.** FY2021–22 are excluded because
Chipotle disclosed AUV to only one decimal in those years ($2.6m, $2.8m), which is why those
two factors implausibly exceed 1.0x. This is a calibration input, not a plug — it is computed
on the Historicals tab and you can watch it tie.

**Validation:** the build produces FY2026E revenue of $12,883m. H1 2026 actual revenue was
$6,436.8m; H1 has represented 49.8% of the full year, implying an FY2026 run-rate near
$12,925m. The build lands within 0.3% of that without being fitted to it.

### 1.3 No franchise revenue

Chipotle owns and operates every restaurant it consolidates. The 14 partner-operated
restaurants in the Middle East disclosed in the FY2025 10-K are licensed and are excluded
from the unit build entirely — they generate no consolidated restaurant revenue and the
licensing fee is not separately disclosed because it is immaterial. There is no franchise
revenue line to model, and adding one would be wrong.

---

## 2. Revenue drivers

### 2.1 New restaurant openings — 347 rising to 370

| | FY2026E | FY2027E | FY2028E | FY2029E | FY2030E |
|---|---|---|---|---|---|
| Openings | 347 | 355 | 360 | 365 | 370 |
| Implied unit growth | 8.1% | 7.7% | 7.3% | 6.9% | 6.5% |

**FY2026 is guided.** The FY2025 10-K states: *"We expect to open approximately 350 to 370
restaurants in 2026, which includes 10 to 15 international partner-operated restaurants."*
Midpoint 360, less ~13 partner-operated, gives **347 company-owned**.

**FY2027–30 is a judgement call.** History: 215 → 236 → 271 → 304 → 334, i.e. openings have
increased every year for five years. I hold them *roughly flat* rather than extrapolating the
increase. Rationale: absolute openings do not need to keep climbing for the story to work —
against a growing base, a flat 360-ish pace still means unit growth decelerates naturally from
8.1% to 6.5%, which is the right shape for a company maturing toward its stated long-term goal
of **7,000 restaurants in the U.S. and Canada** (FY2025 10-K, Item 1A). At this pace Chipotle
reaches 5,749 units by FY2030 — a little over 80% of the way to that goal.

**This is deliberately not aggressive.** Extrapolating the historical acceleration (say 400+ by
FY2030) would raise the valuation. If a company can genuinely keep raising its build rate,
that is upside to this model, not a base case.

Closures are held at **18/year**, against a FY2021–25 average of 17 (permanent closures plus
relocations, per the Restaurant Activity tables).

### 2.2 AUV growth — flat, then 1.5% rising to 2.5%

| | FY2026E | FY2027E | FY2028E | FY2029E | FY2030E |
|---|---|---|---|---|---|
| AUV growth | 0.0% | 1.5% | 2.0% | 2.5% | 2.5% |

**FY2026 flat** is grounded in two independent pieces of evidence:
- Management guides FY2026 comparable restaurant sales to *"be about flat"* (FY2025 10-K MD&A)
- H1 2026 revenue of $6,436.8m is +8.4% year-over-year against roughly 8.5% average-unit
  growth, which implies AUV was approximately flat in the first half

**FY2027–30 at 1.5% → 2.5%** is essentially menu pricing. FY2025 menu price increase was 2.1%
with transactions down 2.9% and check mix down 0.9%. I am assuming pricing power of roughly
2–3% persists, traffic stabilises rather than recovers strongly, and new-unit AUV dilution
continues to drag the average down slightly. That nets to AUV growth a touch below the pricing
rate.

**Why AUV growth and comps are not the same number.** Comps measure only restaurants open 13+
months; AUV is the average across all restaurants open 12+ months, so a heavy new-unit cohort
opening below system average drags AUV below the comp. Historically: FY2024 comps +7.4% vs AUV
+6.5%; FY2025 comps (1.7%) vs AUV (3.4%). Comps are carried on the Assumptions tab as a memo
row so the relationship is visible, but AUV is the driver.

---

## 3. EBIT margin — the assumption that matters most after WACC

| | FY2021A | FY2022A | FY2023A | FY2024A | FY2025A | **H1 2026A** | FY2026E | FY2027E | FY2028E | FY2029E | FY2030E |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EBIT margin | 10.7% | 13.4% | 15.8% | **16.9%** | 16.2% | **14.3%** | 14.5% | 15.0% | 15.5% | 16.0% | 16.3% |

**Stated position: near-term COMPRESSION, then partial recovery. Not expansion.**

This is the assumption most student models get wrong, by drawing a straight line up from the
last actual year. Chipotle's margin already peaked in FY2024 at 16.9% and fell in FY2025 to
16.2%. More importantly, **H1 2026 operating margin was 14.3%** ($922.7m on $6,436.8m per the
Q2 2026 10-Q) versus 17.5% in H1 2025 — operating income fell 11% year-over-year on revenue
that grew 8.4%.

- **FY2026E at 14.5%** is set roughly at the observed H1 2026 rate. This is close to
  arithmetic, not forecasting: half the year is already reported.
- **FY2027E–FY2030E recovering to 16.3%** assumes (a) the tariff impact on food, beverage and
  packaging costs flagged in the FY2025 10-K risk factors normalises, and (b) sales leverage
  returns as comps turn positive, since occupancy and a large part of labour are fixed against
  volume.
- **The terminal margin of 16.3% deliberately does not exceed FY2025A.** It recovers to where
  the company was, not to a new peak. Assuming a return to the FY2024 high of 16.9% — let alone
  above it — would require believing the current pressure is purely transitory. Every 150bps of
  terminal margin is worth roughly $1.56 per share, so this restraint costs about $0.60 versus
  a 16.9% terminal assumption.

**What would change it:** evidence that the food-cost pressure is structural rather than
tariff-driven would argue for a terminal margin closer to 15%; a genuine traffic recovery with
pricing intact would support 17%+. Table B on the Sensitivity tab spans 13.3%–19.3% for exactly
this reason.

---

## 4. Tax rate — 24.0%

| FY2021A | FY2022A | FY2023A | FY2024A | FY2025A |
|---|---|---|---|---|
| 19.7% | 23.9% | 24.2% | 23.7% | 23.6% |

The FY2022–FY2025 average is **23.9%**, rounded to **24.0%**.

**FY2021 is excluded** from the average. Its 19.7% was depressed by unusually large excess tax
benefits on equity compensation — the FY2025 10-K rate reconciliation shows equity compensation
adjustments still worth (1.0)–(1.3) points, and those swing with the share price. Averaging in
a year distorted by a one-off understates the sustainable rate.

The rate is applied to **EBIT, not to pre-tax income** — this is an unlevered free cash flow,
so the interest tax shield is deliberately excluded from the cash flows and captured instead in
the WACC. Chipotle has no debt, so the distinction is nearly moot here, but the model does it
correctly regardless.

---

## 5. Capital intensity

### 5.1 D&A — 3.1% of revenue

Actuals: 3.4% (2021), 3.3% (2022), 3.2% (2023), 3.0% (2024), 3.0% (2025); H1 2026 also 3.0%.

The trend is gently declining as the revenue base outgrows the asset base. I hold it at
**3.1%**, slightly *above* the most recent year, because the assets being added now
(Chipotlanes, kitchen automation, back-of-house technology) are more capital-intensive per
unit than the historical average and will depreciate into the forecast period. This is a
modestly conservative choice — a higher D&A add-back raises FCF, but it also raises normalised
terminal capex, and the two largely offset.

### 5.2 CapEx — 6.5% falling to 5.6% of revenue

| | FY2026E | FY2027E | FY2028E | FY2029E | FY2030E |
|---|---|---|---|---|---|
| CapEx % of revenue | 6.5% | 6.2% | 6.0% | 5.8% | 5.6% |

**FY2026 is guided.** The FY2025 10-K states: *"In 2026, we expect to incur about $834.1
million in total capital expenditures,"* split $531.8m for new restaurant construction and
$266.9m for existing restaurants, equipment and technology. At 6.5% of forecast FY2026 revenue
the model produces **$837.4m** — within 0.4% of guidance. The Assumptions tab carries this as an
explicit check row.

**FY2027–30 stepping down to 5.6%** reflects a flattening absolute build programme against a
growing revenue base. It returns capital intensity to roughly the FY2021–25 actual range
(5.9%, 5.5%, 5.7%, 5.2%, 5.6%), which the FY2026 step-up temporarily exceeds.

The disclosed unit economics support this: FY2025 development and construction cost was
**~$1.5m gross / ~$1.3m net of landlord reimbursements** per restaurant. 370 units × $1.3m
≈ $481m of new-unit capex in FY2030, plus maintenance and technology, against forecast revenue
of $18.6bn — consistent with 5.6%.

### 5.3 Change in net working capital — +0.5% of the change in revenue, as a SOURCE of cash

**The sign here is the point, and it is modelled as it actually behaves.**

Chipotle runs **negative working capital**. The FY2025 10-K states it plainly: the company
*"has not required significant working capital because guests generally pay using cash or credit
and debit cards"* and it pays for food, beverages and supplies *"generally within ten days."*
Cash comes in at the point of sale; it goes out on supplier terms. Growth therefore *releases*
cash rather than consuming it.

The model's input is expressed as **% of the change in revenue, where positive = cash source**.
Computed from the filed cash flow statements (AR, inventory, prepaid, other assets, AP, accrued
payroll, accrued liabilities, unearned revenue, other long-term liabilities):

| FY2021A | FY2022A | FY2023A | FY2024A | FY2025A | **5-yr avg** |
|---|---|---|---|---|---|
| (0.8%) | +0.5% | +4.9% | +5.0% | **(7.2%)** | **+0.5%** |

**The series is volatile**, and FY2025 is sharply negative because revenue growth decelerated
to 5.4% while the unearned-revenue tailwind (gift cards and Chipotle Rewards deferrals, +$40.7m)
could no longer offset the other outflows. I use the **five-year average of +0.5%** rather than
the recent trend, because a single deceleration year is a poor guide to the steady state.

**Two deliberate exclusions from the NWC definition:**
1. **Income taxes payable** — taxes are modelled separately inside NOPAT; including the balance
   sheet movement would double-count
2. **Operating lease assets and liabilities** — these are lease accounting, not working capital,
   and under the leases-as-operating-expense treatment the cash rent is already inside EBIT via
   occupancy cost

**Materiality check:** at +0.5% of roughly $1.2bn of annual incremental revenue, this line
contributes only $5–8m a year — under 0.5% of UFCF. Setting it to zero would change the implied
price by about $0.07. Getting the *sign* conceptually right matters far more than the precision
of the number, and this is a good thing to say out loud in an interview.

---

## 6. Cost of capital — WACC of 9.48%

### 6.1 Cost of equity via CAPM

**Re = Rf + β × ERP = 4.78% + 0.94 × 5.0% = 9.48%**

| Input | Value | Source |
|---|---|---|
| Risk-free rate | 4.78% | 10-year U.S. Treasury constant maturity, 2026-09-04, U.S. Treasury daily par yield curve |
| Levered beta | 0.94 | stockanalysis.com 5-year monthly, retrieved 2026-09-06 |
| Equity risk premium | 5.0% | Low end of the 5.0–5.5% mature-market range |

**On the risk-free rate:** the 10-year is the right tenor because it roughly matches the
duration of the cash flows being discounted, and it is the market convention. Using the 30-year
would be defensible; using the 3-month would not.

**On beta:** at 0.94, Chipotle is very slightly less volatile than the market — plausible for a
business with no financial leverage and reasonably defensive consumer demand. Because **Chipotle
carries no debt, its levered beta is effectively its unlevered beta**; there is no re-levering
step, which removes a common source of error. This is a genuinely nice feature of valuing CMG.

**On the ERP — this is the most contestable input in the model.** I use 5.0% per the standard
practitioner range. Damodaran's *implied* ERP for the S&P 500 at 2026-09-01 was **4.14%**
(trailing twelve month, adjusted payout). Using 4.14% would give a cost of equity of 8.67% and
lift the implied price to **$22.72, +12.9%**. The 5.0% figure is the more conservative
choice and I have flagged the alternative in the README's Open Items rather than burying it.
An interviewer who pushes on this is testing whether you know your own model's soft spot.

### 6.2 Cost of debt and capital structure — the honest answer

**Chipotle has no traditional borrowings.** FY2025 10-K Note 12 (Debt) discloses a **$500.0
million revolving credit facility** with JPMorgan Chase as administrative agent, bearing SOFR
+ 1.125%, which was **undrawn** at 12/31/2025. `us-gaap:LongTermDebt` is zero in every year
FY2021–FY2025. The company simultaneously holds roughly $1.25bn of cash and investments.

Therefore:
- **D / (D + E) ≈ 0%**
- **WACC ≈ cost of equity = 9.48%**

The WACC tab states this explicitly and includes an automated check that reports *"Yes — debt
weight is zero, so WACC = cost of equity."* A pre-tax cost of debt of 5.38% is carried as an
illustrative input (10-year Treasury + 60bps, proxying the revolver's SOFR + 1.125%) so the
formula is complete and the mechanics are visible — but it carries **zero weight**. No debt
tranche has been fabricated to make the formula look fuller, and no target capital structure
has been assumed. If the interviewer asks *"why is your WACC just the cost of equity?"* the
answer is one sentence: because the company has no debt, and here is the note that says so.

---

## 7. Lease treatment — stated, consistent, and defensible either way

**The treatment used: operating leases are an OPERATING EXPENSE.**

1. Occupancy cost stays inside EBIT — it is one of the four restaurant operating cost lines,
   $624.9m in FY2025A
2. The **$5,075.8m** of operating lease liabilities at 12/31/2025 is therefore **EXCLUDED from
   net debt** in the valuation bridge
3. Because rent is never added back, the lease obligation is already fully captured in the cash
   flows being discounted. Deducting the liability again in the bridge would be double-counting

**The alternative treatment (capitalise leases as debt), which you must be able to explain:**

- Add rent expense back to EBIT, so EBIT and EBITDA rise materially
- Add a depreciation charge on the right-of-use asset; treat the implied interest component as
  financing rather than operating
- Add the ~$5.1bn of lease liabilities to debt, which raises net debt *and* introduces a real
  debt weight into the WACC calculation, lowering WACC
- Enterprise value rises — but so does the deduction in the bridge

**Done consistently, both routes should land in a similar place on equity value.** The two
treatments differ mainly in where the obligation shows up, not in whether it is counted.

**The error to avoid is the hybrid**: leaving rent inside EBIT *and* deducting lease liabilities
as debt. That double-counts the lease obligation and would understate equity value here by
roughly **$3.88 per share** ($5,075.8m ÷ 1,307.6m shares). It is a common mistake in student
models and screeners disagree on it too — stockanalysis.com reports CMG's "total debt" as
$5.42bn, which is essentially the capitalised lease liability, not borrowings.

---

## 8. Terminal value

### 8.1 Terminal growth — 2.25%

The midpoint of the 2.0–2.5% long-run U.S. nominal GDP / inflation anchor, and comfortably
below the 9.48% WACC (spread of 7.23%).

The constraint is conceptual, not arithmetic: a perpetual growth rate above nominal GDP implies
the company eventually becomes the entire economy. 2.25% is a statement that in the very long
run Chipotle grows with the economy — which, for a restaurant chain approaching a 7,000-unit
domestic ceiling, is the right shape.

### 8.2 Terminal-year normalisation — 3.8% capex, and why it is necessary

**This is the single most important technical judgement in the terminal value.**

FY2030E capex runs at **5.6% of revenue** because Chipotle is still opening ~370 restaurants a
year and growing units 6.5%. You cannot apply a 2.25% perpetuity to a cash flow that is being
depressed by growth-stage capital spending — a business growing at 2.25% forever does not need
to spend like one growing at 6.5%.

The Terminal Value tab therefore normalises terminal capex to **3.8% of revenue**:
- ~3.1% = maintenance capex, set equal to D&A as a percentage of revenue
- ~0.7% = the growth capital needed to sustain 2.25% growth

This raises the normalised terminal UFCF from $1,843.7m to **$2,177.9m** and the terminal value
from $26.1bn to **$30.8bn** — worth **$2.30 per share**, or 11% of the implied price ($20.12
with the adjustment versus $17.82 without). **Both versions are shown on the tab** so the
adjustment is visible rather than buried.

The historical `CapEx / D&A` ratio is displayed on the Historicals tab (consistently well above
1.0x) precisely to make this point self-evident.

### 8.3 Gordon Growth as primary, exit multiple as cross-check

**Gordon Growth: TV = $2,177.9m × 1.0225 / (9.48% − 2.25%) = $30,801m**

**Exit multiple: TV = FY2030E EBITDA of $3,601.7m × 18.0x = $64,831m**

The 18.0x is grounded in CMG's current trading multiple of **20.5x** LTM EV/EBITDA (computed on
the WACC tab from market cap less cash and investments, over FY2025A EBITDA, on the same
leases-as-opex basis as the rest of the model), with a modest discount applied for multiple
compression as unit growth decelerates.

**Gordon Growth is the primary method** because it is anchored to fundamentals — the cash flows,
the cost of capital, and a growth rate constrained by GDP. The exit multiple is anchored to
today's market sentiment, which is precisely the thing this analysis is trying to test. Using a
market multiple to value a company and then concluding the market is right would be circular.

### 8.4 The two cross-checks — and what to do when they disagree

| Check | Result | Flag |
|---|---|---|
| Implied exit EV/EBITDA from the Gordon Growth TV | **8.6x** | Below 10x — flagged |
| Implied perpetuity growth from the exit-multiple TV | **5.92%** | Above nominal GDP — flagged |

Both flags fire automatically on the Terminal Value tab.

**8.6x** is below where any mature restaurant operator trades. **5.92%** is roughly double
sustainable nominal GDP growth. They cannot both be right, and neither is comfortable.

**I have not split the difference, and that is deliberate.** Averaging two methods that disagree
this violently produces a number with no defensible logic behind it. Instead the model reports
Gordon Growth as the base case, discloses both flags, and treats the disagreement as the actual
analytical output:

> A GDP-anchored DCF at a CAPM cost of capital says CMG is worth around $20. The market pays
> $36.96. The difference is not arithmetic — it is the premium the market assigns to Chipotle's
> brand durability, its runway to 7,000 units, and its historical ability to take price. To
> justify today's price on this model you need either a materially lower discount rate (roughly
> 7%, implying the market sees CMG as far less risky than CAPM does) or perpetual growth near
> 6% (which is not sustainable).

That is a more honest and more interesting conclusion than a number engineered to land near the
share price.

### 8.5 Discounting the terminal value — n = 5.0

The explicit forecast uses **mid-year convention** (n = 0.5, 1.5, 2.5, 3.5, 4.5), on the basis
that cash flows arrive evenly through the year rather than in a lump on 31 December. The
convention is set in a labelled input cell on the DCF tab so it can be switched off in one
keystroke.

The **terminal value is discounted a full 5.0 periods**, because it is a year-5 *year-end*
value. Some practitioners use 4.5 for internal consistency with the mid-year convention on the
explicit cash flows. The choice is stated in an input cell on the Terminal Value tab with the
alternative noted, rather than left as a silent default.

**The magnitudes here are worth knowing precisely, because the textbook answer is misleading
for this particular company.** Mid-year convention on the explicit cash flows alone is worth
only **+0.9%** ($20.12 versus $19.93 at year-end) — far less than the 4–5% usually quoted —
because 78% of the value sits in the terminal value, which is discounted a full five periods
under either convention. Switching the terminal value to n = 4.5 as well is worth a further
**+3.4%** ($20.81). Applying mid-year consistently to everything is worth **+4.4%** in total.
If an interviewer quotes the 4–5% rule of thumb, the useful reply is that the rule assumes the
terminal value moves with the convention, and in a terminal-value-heavy model almost all of the
effect comes from that one choice — not from the explicit period.

### 8.6 Terminal value is 78.2% of enterprise value

Above the 75% threshold, and flagged automatically. This is normal for a company still growing
units at 6–8% — five years is simply not long enough for the business to reach steady state.

It is disclosed as a model limitation in the README because it has a real consequence: **the
answer is a statement about WACC and terminal assumptions far more than about the five forecast
years.** That is exactly why the Sensitivity tab exists, and why the honest framing of the
output is a range, not a point estimate.

---

## 9. Share count and net debt

**Diluted shares: 1,307.6m** = 1,302.4m shares outstanding × 1.00395 dilution factor.

- **1,302,423k** is the FY2025 10-K cover-page count as of 2026-01-30 — the count closest to
  the 12/31/2025 valuation date. Using period-end shares rather than the FY2025 weighted average
  of 1,342.6m is correct for a point-in-time valuation, and it matters: Chipotle is buying back
  stock aggressively, so the weighted average lags reality by roughly 3%.
- **1.00395** is FY2025 diluted ÷ basic weighted-average shares (1,342,616k / 1,337,336k) from
  the FY2025 income statement. Chipotle's option and RSU overhang is small — only ~0.4%.
- **All figures are post the 50-for-1 split effective 26 June 2024.** No pre-split figure appears
  anywhere in the model. The one derived number is FY2021's 1,425,550k (28,511k as reported ×
  50), flagged in the README because Chipotle never restated FY2021 in a later filing.

**Net debt: net CASH of $1,246.3m.** Total debt is zero; cash and investments of $1,246.3m at
12/31/2025 is cash and equivalents ($350.5m) + short-term investments ($698.6m) + long-term
investments ($197.1m). Restricted cash of $35.4m is excluded. Operating lease liabilities are
excluded per the lease treatment above.

---

## 10. Sensitivity design

Two live 2-variable tables. Every cell is a **real formula** that re-discounts all five forecast
UFCFs and rebuilds the terminal value at that parameter pair — not a pasted value, and not
Excel's native Data Table function (which openpyxl cannot write reliably).

**Table A — WACC × terminal growth.** WACC ±1.5% around the 9.48% base in 0.25% steps; terminal
growth 1.5%–3.0% in 0.25% steps. Cells where g approaches WACC return `NA()` rather than a
nonsense number.

**Table B — WACC × terminal EBIT margin.** The terminal margin flexes FY2030E EBIT, which changes
both the year-5 cash flow *and* the normalised terminal cash flow. Terminal growth is held at the
base case.

Both tables carry a red-yellow-green colour scale and a highlighted, bordered base-case cell that
ties exactly to the Valuation Bridge — a check `src/verify_model.py` asserts on every build.

**What the tables show:** the full range is **$14.13 – $29.71**. The vertical spread (WACC) is
wider than the horizontal spread in Table A, which tells you the answer is more sensitive to the
discount rate than to terminal growth. **Even at the most favourable corner of either table, the
model does not reach the $36.96 market price** — which is itself the most useful thing the
sensitivity analysis tells you.

---

## 11. Ranked sensitivity — what actually drives the answer

| Rank | Assumption | Range tested | Implied price range | Swing |
|---|---|---|---|---|
| **1** | **WACC** (driven by the ERP and beta) | 7.98% – 10.98% | $25.54 – $16.58 | **+27% / (18%)** |
| **2** | **Terminal EBIT margin** | 13.3% – 19.3% | $16.99 – $23.24 | **(16%) / +16%** |
| **3** | **Terminal growth rate** | 1.50% – 3.00% | $18.61 – $21.97 | **(7%) / +9%** |

A fourth driver not in the tables: the **terminal capex normalisation**. Moving it from 3.8% of
revenue to the unadjusted 5.6% would cut the implied price by **$2.30 (11%)**, to $17.82 — about
two-thirds of the entire terminal growth range ($3.36) compressed into a single assumption. That
is a lot of weight on one judgement call, which is why both versions are displayed side by side
on the Terminal Value tab rather than netted into one number.

The practical read: **this is a cost-of-capital story, not a forecasting story.** The five-year
operating forecast is well grounded in guidance and reported H1 actuals; the valuation gap versus
the market is almost entirely a disagreement about the discount rate and the terminal assumptions.
