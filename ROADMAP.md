# Roadmap

Ordered by dependency rather than appeal: work that makes later changes safe or
measurable comes first. Each item links to its backlog issue. This is the single list of
planned work. The README's former "What I would build next" list and the forward-looking
parts of its Open Items now live here.

## Now

- **Run the build-and-verify pipeline in CI** ([#1](https://github.com/pragyan-varma/cmg-dcf-valuation/issues/1)) — `verify_model.py`
  says it exists so the build can be checked in CI, but nothing runs it automatically.
  Every item below changes the model, so automated verification comes first.
- **README figures and a workbook source note disagree with the model** ([#2](https://github.com/pragyan-varma/cmg-dcf-valuation/issues/2)) —
  a mislabelled sensitivity range, a stale 19.8x exit-multiple note against the computed
  20.5x, and three other statements that don't match the code. A correctness bug in what a
  reviewer reads, so it goes first.
- **"Explicit forecast period" input cell has no effect** ([#3](https://github.com/pragyan-varma/cmg-dcf-valuation/issues/3)) — a blue
  input that no formula reads. A bug, and a small one, so it goes in Now.

## Next

- **Centre the sensitivity tables on the live base case** ([#4](https://github.com/pragyan-varma/cmg-dcf-valuation/issues/4)) — the axes
  are hardcoded, so moving terminal growth off the grid fails verification. Needed before
  any change to the capital structure. Depends on #1.
- **Reverse DCF** ([#5](https://github.com/pragyan-varma/cmg-dcf-valuation/issues/5)) — solves for the growth, WACC and margin implied
  by $36.96, the framing the README already argues is most useful. Uses only data already
  in the repo. Depends on #1.

## Later

- **Lease-capitalised version** ([#6](https://github.com/pragyan-varma/cmg-dcf-valuation/issues/6)) — tests the methodology's claim that
  the two lease treatments converge. It introduces a debt weight into WACC, so it depends
  on #4, and it needs lease-cost data that isn't in the repo yet. Depends on #1, #4.
- **Mid-2026 valuation date with a stub period** ([#7](https://github.com/pragyan-varma/cmg-dcf-valuation/issues/7)) — removes the
  eight-month gap between the valuation date and the market price. The README calls it
  materially more complex, and it needs Q2 2026 balance-sheet data. Depends on #1.
- **Comparable-companies screen and peer beta cross-check** ([#8](https://github.com/pragyan-varma/cmg-dcf-valuation/issues/8)) —
  answers which multiple is the outlier and whether the 0.94 beta holds up. It needs a
  new, sourced peer dataset, which makes it the largest data dependency on the list.
  Depends on #1.

## Assumptions

These shape the ordering above and none have been validated.

- **The users are assumed, not researched.** The personas in the README and in backlog
  stories (an analyst or reviewer checking the model, and the maintainer) describe who
  the project was designed for. Nobody has been interviewed, and nobody outside the
  project has reviewed the model.
- **Reviewers care more about traceability than new features.** That is why the CI and
  accuracy fixes (#1–#3) sit ahead of new analysis. If reviewers mostly want broader
  analysis, #5 and #8 move up.
- **The gap to the market price is the question reviewers want answered.** That is why
  the reverse DCF (#5) leads the new analysis. If reviewers care more about a
  triangulated value, comps (#8) matter more.
- **New external data is the main cost driver.** Items that need data not already in
  `data/historicals.csv` (#6, #7, #8) are in Later for that reason.

The next step for testing these is putting the workbook in front of a handful of people
who review financial models, watching which numbers they try to trace or challenge, and
re-ranking this list based on that.
