"""
Compares two builds of the workbook cell by cell: every formula, and every cached
value written by cache_values.py.

A byte comparison doesn't work, because the .xlsx zip stores timestamps, so two
identical builds never have identical bytes. CI uses this to fail when the committed
output/CMG_DCF_Model.xlsx is out of date with the code that generates it.

    python src/compare_workbooks.py <committed.xlsx> <fresh.xlsx>

Exits 0 if the workbooks match, 1 if any cell differs.
"""
from __future__ import annotations

import sys
import warnings

warnings.filterwarnings("ignore")

from openpyxl import load_workbook

REL_TOL = 1e-9


def same(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) \
            and not isinstance(a, bool) and not isinstance(b, bool):
        return abs(a - b) <= REL_TOL * max(1.0, abs(a), abs(b))
    return a == b


def compare(path_a, path_b):
    diffs, cells = [], 0
    for data_only, kind in ((False, "formula"), (True, "cached value")):
        wa = load_workbook(path_a, data_only=data_only)
        wb = load_workbook(path_b, data_only=data_only)
        if wa.sheetnames != wb.sheetnames:
            return [f"sheet names differ: {wa.sheetnames} vs {wb.sheetnames}"], 0
        for name in wa.sheetnames:
            a, b = wa[name], wb[name]
            for r in range(1, max(a.max_row, b.max_row) + 1):
                for c in range(1, max(a.max_column, b.max_column) + 1):
                    cells += 1
                    va, vb = a.cell(r, c).value, b.cell(r, c).value
                    if not same(va, vb):
                        diffs.append(f"{kind:12} {name}!{a.cell(r, c).coordinate}: "
                                     f"{va!r:.60} != {vb!r:.60}")
    return diffs, cells


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    diffs, cells = compare(sys.argv[1], sys.argv[2])
    if diffs:
        print(f"{len(diffs)} cell(s) differ out of {cells} compared:")
        for d in diffs[:25]:
            print("  " + d)
        print("The committed workbook is out of date. Rebuild it with build_model.py "
              "and cache_values.py, then commit output/CMG_DCF_Model.xlsx.")
        sys.exit(1)
    print(f"Workbooks match: {cells} cells compared (formulas and cached values).")


if __name__ == "__main__":
    main()
