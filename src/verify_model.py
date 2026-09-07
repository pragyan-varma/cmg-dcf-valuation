"""
Recalculates every formula in output/CMG_DCF_Model.xlsx without Excel and
asserts that the model ties.

This exists because openpyxl writes formulas but does not evaluate them - the
workbook on disk has no cached values until Excel opens it once. This script
closes that gap so the build can be checked in CI or from the terminal.

    pip install formulas
    python src/verify_model.py

Checks performed
----------------
1. No #REF!, #DIV/0!, #VALUE!, #NAME? or #N/A in any calculated cell.
2. Historicals: the built EBIT ties to EBIT as reported in the 10-K (all years).
3. Historicals: the built restaurant count ties to the count reported in the 10-K.
4. Bridge: EV = sum of PV of UFCF + PV of terminal value.
5. Bridge: equity value = EV - debt + cash, and price = equity value / shares.
6. Sensitivity: the base-case cell of each table equals the bridge's implied price.
7. Terminal growth is below WACC.
"""
from __future__ import annotations

import os
import sys
import warnings

warnings.filterwarnings("ignore")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX = os.path.join(ROOT, "output", "CMG_DCF_Model.xlsx")

try:
    import formulas
except ImportError:
    sys.exit("This script needs the optional 'formulas' package:  pip install formulas")

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

ERR_TOKENS = ("#REF!", "#DIV/0!", "#VALUE!", "#NAME?", "#N/A", "#NULL!", "#NUM!")


def main():
    print(f"Recalculating {XLSX} ...")
    sol = formulas.ExcelModel().loads(XLSX).finish().calculate()
    vals = {}
    for k, v in sol.items():
        try:
            vals[k] = v.value[0, 0]
        except Exception:
            pass

    wb = load_workbook(XLSX)
    base = os.path.basename(XLSX)

    def val(sheet, cell):
        return vals.get(f"'[{base}]{sheet.upper()}'!{cell}")

    def row_of(sheet, label_startswith):
        """First row whose column-A label matches AND which actually holds a value
        in column C. The column-C test skips section-header bars, which can share
        wording with the line item beneath them."""
        ws = wb[sheet]
        for r in range(1, ws.max_row + 1):
            a = ws.cell(r, 1).value
            if a and str(a).strip().lower().startswith(label_startswith.lower()) \
                    and ws.cell(r, 3).value is not None:
                return r
        raise KeyError(f"{sheet}: no row starting '{label_startswith}'")

    failures, checks = [], 0

    def check(name, ok, detail=""):
        nonlocal checks
        checks += 1
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}{'  ' + detail if detail else ''}")
        if not ok:
            failures.append(name)

    # 1 - error scan (column B holds literal '#' unit labels, so skip column B)
    bad = []
    for key, v in vals.items():
        if isinstance(v, str) and any(t in v for t in ERR_TOKENS):
            if "'!B" in key:
                continue
            bad.append((key, v))
    print("\nFormula error scan")
    check("no Excel error values in any calculated cell", not bad,
          f"({len(bad)} found)" if bad else f"({len(vals)} cells evaluated)")
    for k, v in bad[:10]:
        print(f"        {k} -> {v}")

    # 2/3 - historical tie-outs
    print("\nHistorical tie-outs")
    r = row_of("Historicals", "Check: build vs. reported (must be 0.0)")
    diffs = [val("Historicals", f"{c}{r}") or 0 for c in "CDEFG"]
    check("built EBIT ties to EBIT as reported, FY2021A-FY2025A",
          all(abs(d) < 0.01 for d in diffs), f"max diff {max(abs(d) for d in diffs):.2e}")
    r = row_of("Historicals", "Check: build vs. reported (must be 0)")
    diffs = [val("Historicals", f"{c}{r}") or 0 for c in "CDEFG"]
    check("built restaurant count ties to the count reported",
          all(abs(d) < 0.5 for d in diffs))

    # 4/5 - bridge
    print("\nValuation bridge")
    b = {k: val("Valuation Bridge", f"C{row_of('Valuation Bridge', k)}") for k in
         ("Sum of PV of forecast UFCF", "Plus: PV of terminal value", "ENTERPRISE VALUE",
          "Less: total debt", "Plus: cash and investments", "EQUITY VALUE",
          "Diluted shares outstanding", "IMPLIED SHARE PRICE")}
    ev = b["Sum of PV of forecast UFCF"] + b["Plus: PV of terminal value"]
    check("EV = PV(UFCF) + PV(TV)", abs(ev - b["ENTERPRISE VALUE"]) < 0.01,
          f"${b['ENTERPRISE VALUE']:,.1f}mm")
    eq = b["ENTERPRISE VALUE"] + b["Less: total debt"] + b["Plus: cash and investments"]
    check("equity value = EV - debt + cash", abs(eq - b["EQUITY VALUE"]) < 0.01,
          f"${b['EQUITY VALUE']:,.1f}mm")
    px = b["EQUITY VALUE"] / b["Diluted shares outstanding"]
    check("implied price = equity value / diluted shares",
          abs(px - b["IMPLIED SHARE PRICE"]) < 0.005, f"${b['IMPLIED SHARE PRICE']:,.2f}")

    # 6 - sensitivity base cells
    print("\nSensitivity base-case cells")
    ws = wb["Sensitivity"]
    found = 0
    for r in range(1, ws.max_row + 1):
        for c in range(3, 12):
            cell = ws.cell(r, c)
            if cell.fill is not None and cell.fill.fgColor is not None \
                    and cell.fill.fgColor.rgb == "FFFFF2CC":
                v = val("Sensitivity", f"{get_column_letter(c)}{r}")
                found += 1
                check(f"base-case cell {get_column_letter(c)}{r} equals the bridge price",
                      isinstance(v, (int, float)) and abs(v - b["IMPLIED SHARE PRICE"]) < 0.01,
                      f"${v:,.2f}" if isinstance(v, (int, float)) else str(v))
    check("both sensitivity tables have a highlighted base case", found == 2,
          f"({found} found)")

    # 7 - g < WACC
    print("\nTerminal assumptions")
    g = val("Assumptions", f"C{row_of('Assumptions', 'Terminal growth rate')}")
    w = val("WACC", f"C{row_of('WACC', 'WACC =')}")
    check("terminal growth is below WACC", g < w, f"g={g:.2%} vs WACC={w:.2%}")

    print(f"\n{checks - len(failures)}/{checks} checks passed.")
    if failures:
        print("FAILED: " + "; ".join(failures))
        sys.exit(1)
    print("Model ties. Implied share price: "
          f"${b['IMPLIED SHARE PRICE']:,.2f}")


if __name__ == "__main__":
    main()
