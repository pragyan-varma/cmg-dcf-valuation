# Walkthrough — how to explain this model out loud

Two parts:

1. **[The verbal walkthrough](#part-1--the-verbal-walkthrough)** — the model in the order you
   should present it, with a 60-second version and a 5-minute version
2. **[Ten questions you will be asked](#part-2--ten-questions-you-will-be-asked)** — with
   answers specific to *this* model, not generic DCF theory

Numbers referenced throughout are the current base case. If you change an assumption, re-run
`src/build_model.py` and update your talking points.

---

## Part 1 — the verbal walkthrough

### The 60-second version (use this first, every time)

> I built a five-year DCF of Chipotle from their 10-K filings. I model revenue as restaurant
> count times average unit volume rather than a top-line growth rate, because Chipotle is a
> unit-growth story — and in FY2025 those two levers moved in opposite directions: units grew
> 8.5% while AUV actually fell 3.4%.
>
> I get an implied value of about **$20 a share against a market price of $37**. The gap isn't
> an error — it's the finding. Chipotle trades at **20.5 times EBITDA**, and my Gordon Growth
> terminal value implies an exit multiple of only **8.6 times**. To justify today's price you'd
> need either a discount rate near 7%, or perpetual growth near 6% — which is double nominal
> GDP. So the model's real output is: *here is what the market must believe, and here is why a
> GDP-anchored DCF can't get there.*
>
> The two things I'd push back on in my own model are the equity risk premium — I used 5.0%,
> and Damodaran's current implied number is 4.14%, which alone is worth about 13% of value —
> and the fact that 78% of my enterprise value sits in the terminal value.

**Why open this way:** you lead with the conclusion, you pre-empt the "your answer looks wrong"
objection by reframing it as the analysis, and you volunteer your own model's weaknesses before
the interviewer finds them. That last move is what separates a student project from a candidate
who thinks like an analyst.

### The 5-minute version — tab by tab

**1. Start with the data, not the model.** *"Everything historical comes from the 10-Ks — I
pulled FY2021 through FY2025 from four separate filings and cross-checked every line against
SEC's XBRL data. Every input cell in the workbook has a source note next to it. Blue font is
hardcoded, black is a same-sheet formula, green is a cross-sheet link, and there are no
hardcoded numbers inside formulas."*

Then show them the tie-out row on the Historicals tab: EBIT built from the cost lines versus
EBIT as reported, zero in all five years. And the restaurant count build tying to the reported
count. **Volunteer these.** It signals you know that a model nobody can check is worthless.

**2. The revenue build.** *"Revenue is average units times AUV times a realisation factor. The
realisation factor is 0.9867 — it's below one because AUV is a trailing-twelve-month figure for
mature restaurants, while units opened during the year only contribute part of a year. I computed
it from three years of filed data, and it's on the Historicals tab so you can see it tie."*

Then the validation: *"FY2026 comes out at $12.9 billion. H1 2026 actual revenue was $6.4
billion, and H1 has been about 49.8% of the full year, so the run-rate implies $12.9 billion. The
build lands within 0.3% without being fitted to it."*

**3. The margin — this is where you show judgement.** *"This is the assumption I spent the most
time on. Chipotle's EBIT margin peaked at 16.9% in FY2024 and fell to 16.2% in FY2025. But look
at H1 2026: **14.3%**, versus 17.5% a year earlier. Operating income fell 11% on revenue that grew
8.4%. So I forecast **compression, then partial recovery** — 14.5% in FY2026 rising back to 16.3%
by FY2030. My terminal margin deliberately doesn't exceed FY2025, and it stays below the FY2024
peak. A lot of student models draw a straight line up from the last actual year; this one goes
down first because the reported data says it should."*

**4. WACC — the short, confident version.** *"9.48%, and it equals my cost of equity, because
Chipotle has no debt. Note 12 of the 10-K discloses a $500 million revolver that was undrawn at
year-end, and long-term debt is zero in all five years. I didn't invent a debt tranche to make
the formula look fuller — I set the debt weight to zero and said so on the tab. CAPM is 4.78%
risk-free, which is the 10-year Treasury as of September 4th, times a beta of 0.94, plus a 5%
equity risk premium."*

**5. Leases — say this before they ask.** *"I treat operating leases as an operating expense.
Occupancy cost stays in EBIT, so I exclude the $5.1 billion of lease liabilities from net debt.
That's the internally consistent pairing. The alternative is to capitalise them — add rent back
to EBIT, add the liability to debt — and done properly the two converge on a similar equity value.
The mistake to avoid is the hybrid: keeping rent in EBIT and also deducting the lease liability,
which double-counts and would cost about $3.88 a share here. It's worth knowing that screeners
disagree on this — stockanalysis.com reports CMG's total debt as $5.4 billion, which is
essentially the capitalised lease, not borrowings."*

**6. The DCF.** Revenue → EBIT → tax on EBIT → NOPAT → add D&A → less capex → adjust working
capital → UFCF. One line worth flagging: *"Working capital is a small **source** of cash, not a
use. Chipotle runs negative working capital — guests pay at the till, suppliers get paid on
ten-day terms — and the 10-K says so directly. It's only worth about $0.07 a share, but I modelled
the sign as it actually behaves rather than assuming growth consumes cash."*

**7. Terminal value — the sophisticated part.** *"Two things here. First, I normalise terminal
capex. My FY2030 capex is 5.6% of revenue because they're still opening 370 restaurants a year —
you can't apply a 2.25% perpetuity to a cash flow depressed by growth-stage spending. So I
normalise to 3.8%, which is maintenance capex equal to D&A plus enough growth capital for 2.25%
growth. That's worth $2.30 a share, and I show both versions so the adjustment isn't hidden.*

*Second, the cross-checks. My Gordon Growth terminal value implies an **8.6x** exit multiple. If
I instead apply an 18x exit multiple, that implies **5.9%** perpetual growth. Both are flagged
automatically on the tab. They can't both be right — and I didn't average them, because averaging
two methods that disagree this violently gives you a number with no logic behind it."*

**8. Land on the sensitivity table, not the point estimate.** *"78% of my enterprise value is
terminal value, so honestly this is a statement about the discount rate more than about the five
forecast years. The full sensitivity range is **$14 to $30**. The most important thing that table
tells you is that **even at the most favourable corner, I don't reach $37**. So the disagreement
with the market isn't a rounding issue in my assumptions — it's structural."*

---

## Part 2 — ten questions you will be asked

### 1. "Why run a DCF on a company trading at a premium multiple? Isn't the answer just going to be 'overvalued'?"

**That's exactly why you run it.** A multiple tells you what the market is paying; it doesn't tell
you what has to be true to justify it. The DCF converts the market price into a set of testable
statements about growth, margin and risk.

Here the output isn't really "$20, sell." It's: *to pay $37 you need a discount rate near 7% or
perpetual growth near 6%.* Now you have something to argue about with actual content — is
Chipotle genuinely 250bps less risky than CAPM implies, given no debt, no franchise complexity
and durable pricing power? Maybe. Can it grow at 6% forever? No. That decomposition is only
available from a DCF.

The honest framing: **the DCF is a bad tool for pricing a premium growth business and a very good
tool for interrogating one.** If I were making a real recommendation I'd triangulate with comps
and a reverse DCF — which is the first thing on my "what I'd build next" list.

### 2. "Why is your terminal value 78% of enterprise value? Doesn't that make the model useless?"

It makes it *sensitive*, not useless — and it's normal. Chipotle is still growing units 6–8% a
year, so five years isn't long enough to reach steady state. Any growth company will show 70–85%.

But I take the point seriously, and I did three things about it:

1. **Normalised the terminal year.** Rather than perpetuating growth-stage capex at 5.6% of
   revenue, I normalise to 3.8% — maintenance capex plus the growth capital consistent with 2.25%
   growth. Both versions are shown.
2. **Cross-checked the terminal value two ways** and flagged both when they implied something
   unreasonable, rather than picking whichever was more convenient.
3. **Made the sensitivity table the headline output**, because with 78% in the terminal value the
   point estimate is less informative than the range.

The thing I'd flag as a genuine limitation: with this much weight in the terminal value, my answer
is really a view on the discount rate. If you disagree with my 5% ERP, you disagree with my
valuation — the five-year forecast barely moves it.

### 3. "How does your lease treatment affect the answer? Walk me through the alternative."

**My treatment:** leases are an operating expense. Occupancy of $624.9m stays in EBIT, so EBIT is
lower but the lease obligation is already in the cash flows. I therefore exclude the $5.08bn of
lease liabilities from net debt.

**The alternative:** capitalise them. Add rent back to EBIT — EBIT and EBITDA both rise materially.
Add depreciation on the right-of-use asset and treat the implied interest as financing. Add the
$5.1bn to debt, which raises net debt *and* introduces a real debt weight into WACC, lowering the
discount rate. Enterprise value goes up, but so does the deduction in the bridge.

**Done consistently, the two converge on a similar equity value.** They differ in *where* the
obligation appears, not in *whether* it's counted.

**The error to avoid is the hybrid** — leaving rent in EBIT *and* deducting the lease liability as
debt. That double-counts, and here it would cost $3.88 a share. It's a common mistake, and it's
worth knowing that data providers disagree: stockanalysis.com shows CMG with $5.42bn of "total
debt," which is the capitalised lease, not borrowings. That's why my EV/EBITDA of 20.5x differs
from what a screener will show you — mine is computed consistently with the rest of the model.

*(If they push further:* the reason I chose leases-as-opex is that for a restaurant operator,
occupancy is genuinely an operating input, not a financing decision — they lease because that's
how retail real estate works, not to lever the balance sheet. Both treatments are defensible;
inconsistency isn't.*)*

### 4. "What happens if unit growth disappoints?"

Less than you'd think in the explicit period, and more than you'd think in the terminal value.

I ran it. Suppose openings run **250 a year** instead of 347–370 — roughly the FY2022 pace. FY2030
units come in at **5,202** instead of 5,749, about 9.5% lower, and FY2030 revenue drops about 9% to
**$16.9bn**. Because margins are modelled as a percentage of revenue, UFCF and the terminal value
fall roughly proportionally, so the implied price goes to **$18.57 — down $1.55, or 7.7%**.

**That's less than people expect, and the reason is worth stating:** most of my value is terminal,
and slower unit growth scales the terminal cash flow down without changing the multiple applied to
it. Unit growth is a level effect here, not a rate effect.

**But it understates the real risk**, and this is the more interesting answer: a unit-growth
disappointment rarely arrives alone. If they're slowing openings it's usually because new-unit
returns have deteriorated or the domestic market is saturating — and that shows up in AUV and in
margin too, since occupancy and much of labour are fixed against volume. Slower units **and** a
terminal margin of 14.0% instead of 16.3% takes it to **$16.14, down 20%**. That combined scenario
is the one worth worrying about, not the unit count on its own.

**The offsetting point:** they're at 4,042 units against a stated long-term goal of 7,000 in the
U.S. and Canada. There's a lot of runway before saturation is the binding constraint — which is
part of why the market is willing to pay 20x.

### 5. "Your answer is 46% below the market. Convince me you didn't just build the model wrong."

Fair challenge, and the first thing I'd say is that I built explicit tie-outs so you can check it
rather than take my word for it:

- The EBIT I build from the cost lines ties exactly to EBIT as reported, all five years
- The restaurant count I build ties to the count in the 10-K, all five years
- My FY2026 capex assumption produces $837m against management's guidance of $834.1m — 0.4% off,
  and I didn't tune it to hit that
- My FY2026 revenue build lands within 0.3% of the H1 2026 run-rate
- There's a verification script that recalculates every formula and asserts the bridge ties

So the mechanics are sound. **The gap is in the assumptions, and specifically in the discount rate
and terminal value — which is where it should be.** Three things drive it:

1. **ERP of 5.0%.** Damodaran's current implied ERP is 4.14%. Using that alone is worth +13%.
2. **Terminal growth of 2.25%.** Anchored to nominal GDP by construction. The market is implicitly
   paying for something closer to 6%.
3. **CAPM itself.** A beta of 0.94 says Chipotle is roughly market-risky. You could argue a
   debt-free business with this brand and pricing power deserves a lower cost of capital than CAPM
   assigns it.

**The intellectually honest position is that the DCF isn't wrong, it's just answering a narrower
question than the market is.** The market is paying for optionality — international expansion,
7,000 units, digital margin — that a five-year explicit forecast with a GDP terminal growth rate
structurally cannot capture.

### 6. "Why did you use a 5% equity risk premium?"

Because it's the standard mature-market range practitioners use, and it's the *conservative* end
of my model's answer.

**But I'll flag the tension myself:** Damodaran's implied ERP for the S&P 500 on September 1st was
4.14%. Using that gives a cost of equity of 8.67% instead of 9.48%, and an implied price of $22.72
— about 13% higher. It's flagged in my Open Items.

The distinction worth drawing: the **implied** ERP is forward-looking, derived from current index
prices and expected cash flows, and it moves around a lot. The 5.0–5.5% range is closer to a
long-run **historical** average and is what most deal teams actually put in a model. Neither is
"correct." What matters is that you know which one you used, why, and what it's worth — which here
is more than the entire terminal growth sensitivity range.

### 7. "Walk me from EBITDA to unlevered free cash flow."

For Chipotle specifically, D&A is a separate line on the income statement — restaurant operating
costs are stated *exclusive* of D&A — so EBITDA is just EBIT plus D&A, no digging required.

Going the other way to UFCF:

> **EBIT** (I forecast this directly off a margin assumption)
> **less taxes on EBIT** at 24% — note that's tax on *EBIT*, not on pre-tax income, because this
> is an *unlevered* cash flow; the interest tax shield is excluded from the cash flows and
> captured in the WACC instead. Chipotle has no debt so it barely matters, but the model does it
> correctly regardless.
> **= NOPAT**
> **plus D&A**, 3.1% of revenue — non-cash, so it comes back
> **less capex**, 6.5% falling to 5.6% — the real cash cost of the growth
> **plus/less the change in working capital** — a small *source* here, +0.5% of the revenue change
> **= UFCF**

The one to watch is capex versus D&A: capex runs about 1.8x D&A because they're building. That gap
is real cash going out the door, and it's why UFCF margin is only 7.7% in FY2026 despite a 14.5%
EBIT margin.

### 8. "Why is working capital a source of cash? Isn't growth supposed to consume it?"

For most businesses, yes — you build inventory and extend receivables before you collect. Chipotle
is the opposite, and it's a genuinely nice feature of the business model.

Guests pay by cash or card at the point of sale, so receivables are almost nothing. Inventory turns
in days because the food is fresh. And the 10-K says they pay suppliers "generally within ten days"
of receipt. So cash comes in before it goes out: **negative working capital**, and growth *releases*
cash.

Historically it's swung between (7.2%) and +5.0% of the change in revenue, averaging +0.5%, which is
what I use. FY2025 was sharply negative because revenue growth decelerated and the unearned-revenue
tailwind from gift cards and Chipotle Rewards couldn't offset the other outflows.

**Materiality:** it's worth about $0.07 a share. Setting it to zero barely moves the answer. I'd
say that up front — knowing which of your assumptions *don't* matter is as useful as knowing which
do, and it stops you defending a number to three decimal places when it's worth seven cents.

### 9. "Why Gordon Growth over an exit multiple, and what do you do when they disagree this badly?"

**Gordon Growth is primary because it's anchored to fundamentals** — the cash flows, the cost of
capital, and a growth rate constrained by nominal GDP. The exit multiple is anchored to today's
market sentiment, which is the thing I'm trying to *test*. Using a market multiple to value the
company and then concluding the market is right would be circular.

**When they disagree, don't average them.** Splitting the difference gives you a number with no
logic behind it. Instead I report both, show what each implies about the other, and treat the
disagreement as the output:

- Gordon Growth implies an **8.6x** exit multiple — below where any mature restaurant operator
  trades, which says either my WACC is too high or my growth too low
- An 18x exit multiple implies **5.9%** perpetual growth — roughly double nominal GDP, which says
  the market multiple is carrying assumptions that can't be sustained forever

Both flags fire automatically on the tab, with the text written into the model rather than added by
hand afterwards.

**The synthesis:** the truth is probably that CMG's fair value sits above my DCF and below the
market — the DCF misses real optionality, and the market is extrapolating a growth phase that has
a finite runway. But I'd rather present two honest bounds than one fabricated midpoint.

### 10. "What's the biggest weakness in this model?"

Pick one and answer it properly rather than listing five. The strongest answer:

> **The model is a cost-of-capital story dressed up as a forecasting exercise.**
>
> My five-year operating forecast is well grounded — FY2026 revenue is within 0.3% of the H1
> run-rate, capex is within 0.4% of guidance, and the margin trough comes straight off reported
> H1 results. But 78% of my enterprise value sits in the terminal value, so almost none of that
> care actually drives the answer. Change the ERP by 86 basis points and the value moves 13%,
> which is more than any operating assumption in the model.
>
> So if I were defending this in a real setting, I'd be honest that the forecast is the credible
> part and the discount rate is the contestable part — and I'd want to bound it with a reverse DCF
> and a comps screen before making a recommendation.

**Runners-up, if they want more:**
- I model costs at the EBIT-margin level rather than line by line, so I can't isolate the tariff
  impact on food costs that the 10-K flags
- Beta is a single point estimate from a secondary source, not regressed from returns or
  cross-checked against unlevered peer betas
- The valuation date is 12/31/2025 but I compare to a September 2026 price — about eight months of
  value accretion isn't rolled forward, which overstates the downside somewhat

---

## Three things to have memorised

Interviewers test whether you actually built it by asking for a specific number without warning.

| | |
|---|---|
| **Implied price / market / gap** | $20.12 / $36.96 / (45.6%) |
| **WACC and how you got there** | 9.48% = 4.78% + 0.94 × 5.0%, and it equals cost of equity because there's no debt |
| **The one-line reframe** | "8.6x implied exit multiple versus 20.5x traded — the gap is the growth premium, not an error" |

And know these three cold, because they're the follow-ups:
- **FY2025 revenue and EBIT margin:** $11.9bn, 16.2% — falling from 16.9% in FY2024
- **H1 2026 margin:** 14.3%, versus 17.5% a year earlier. This is *why* the forecast compresses
- **Units:** 4,042 today, 5,749 by FY2030E, long-term company goal of 7,000 in the U.S. and Canada
