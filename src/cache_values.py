"""
Injects cached values into output/CMG_DCF_Model.xlsx without touching the formulas.

WHY THIS EXISTS
---------------
openpyxl writes the formula string for a cell but cannot write a cached result
alongside it. A workbook straight out of build_model.py therefore contains
<f>...</f> with no <v>...</v>.

Excel, Google Sheets and LibreOffice don't care - they recalculate the whole
workbook on load and display the right numbers. But every viewer that does NOT
have a calculation engine renders those cells as EMPTY:

    - macOS Quick Look (spacebar in Finder) and Preview
    - GitHub / GitLab in-browser spreadsheet previews
    - most phone and webmail attachment viewers

For a portfolio model that is a real problem: someone glancing at the file sees
labels and blue inputs with no share price, and concludes the model is broken.

This script recalculates the workbook with the `formulas` engine and writes each
result into the cell's <v> element, exactly the way Excel does when it saves.
The <f> element is left untouched, so:

    - every formula is still live and auditable (click any cell, see the formula)
    - the value renders in viewers with no calculation engine
    - calcPr fullCalcOnLoad is set, so Excel recalculates on open anyway and a
      cached value can never go stale against an edited input

Run after build_model.py:

    python src/build_model.py
    python src/cache_values.py
"""
from __future__ import annotations

import os
import re
import shutil
import sys
import warnings
import zipfile

warnings.filterwarnings("ignore")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX = os.path.join(ROOT, "output", "CMG_DCF_Model.xlsx")

try:
    import formulas
except ImportError:
    sys.exit("This script needs the `formulas` package:  pip install formulas")

from openpyxl import load_workbook

ERR_VALUES = {"#REF!", "#DIV/0!", "#VALUE!", "#NAME?", "#N/A", "#NULL!", "#NUM!"}


def xml_escape(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def main():
    print(f"Recalculating {os.path.relpath(XLSX, ROOT)} ...")
    sol = formulas.ExcelModel().loads(XLSX).finish().calculate()
    computed = {}
    for key, cell in sol.items():
        try:
            computed[key.upper()] = cell.value[0, 0]
        except Exception:
            pass

    wb = load_workbook(XLSX)
    base = os.path.basename(XLSX).upper()
    # xl/worksheets/sheetN.xml is ordered the same as wb.sheetnames
    sheet_order = list(wb.sheetnames)

    tmp = XLSX + ".tmp"
    zin = zipfile.ZipFile(XLSX, "r")
    zout = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)

    stats = {"filled": 0, "formulas": 0, "missing": 0, "errors": 0}

    for item in zin.infolist():
        data = zin.read(item.filename)
        m = re.fullmatch(r"xl/worksheets/sheet(\d+)\.xml", item.filename)

        if item.filename == "xl/workbook.xml":
            text = data.decode("utf-8")
            # Force Excel to recalculate on open so a cached value can never be stale
            if "<calcPr" in text:
                text = re.sub(r"<calcPr[^/>]*/?>",
                              '<calcPr calcId="191029" fullCalcOnLoad="1"/>', text, count=1)
            else:
                text = text.replace("</workbook>",
                                    '<calcPr calcId="191029" fullCalcOnLoad="1"/></workbook>')
            data = text.encode("utf-8")

        elif m:
            idx = int(m.group(1)) - 1
            if idx < len(sheet_order):
                sheet = sheet_order[idx].upper()
                text = data.decode("utf-8")

                def fill(match):
                    whole = match.group(0)
                    # Self-closing empty cells (<c r="B10" s="5"/>) carry no formula.
                    # They must be matched and returned untouched, otherwise a regex
                    # that only understands <c ...>...</c> swallows the NEXT cell and
                    # misattributes its reference.
                    if whole.endswith("/>"):
                        return whole
                    head, body = match.group(1), match.group(2)
                    if "<f>" not in body and "<f " not in body:
                        return whole
                    stats["formulas"] += 1
                    ref = re.search(r'r="([A-Z]+\d+)"', head)
                    if not ref:
                        return whole
                    val = computed.get(f"'[{base}]{sheet}'!{ref.group(1)}")
                    if val is None or isinstance(val, str) and val.strip() == "":
                        stats["missing"] += 1
                        print(f"    skipped {sheet_order[idx]}!{ref.group(1)} (no computed result)")
                        return whole
                    # Strip any existing value element so this is idempotent.
                    # openpyxl emits a SELF-CLOSING <v/> for formula cells, which a
                    # naive <v>.*?</v> pattern misses - leaving two <v> elements in
                    # the cell, where readers take the empty first one.
                    body = re.sub(r"<v\s*/>|<v>.*?</v>", "", body, flags=re.S)
                    head_clean = re.sub(r'\st="[^"]*"', "", head)

                    # The `formulas` engine returns numpy scalars. repr() on those
                    # yields "np.float64(0.98...)", which is not valid cell XML and
                    # silently corrupts the workbook - so coerce to plain Python
                    # types via .item() before writing anything.
                    if hasattr(val, "item") and getattr(val, "ndim", 0) == 0:
                        val = val.item()

                    if isinstance(val, bool):
                        stats["filled"] += 1
                        return f'{head_clean} t="b">{body}<v>{1 if val else 0}</v></c>'
                    if isinstance(val, (int, float)):
                        if isinstance(val, float) and (val != val or val in (
                                float("inf"), float("-inf"))):
                            stats["missing"] += 1
                            return whole
                        stats["filled"] += 1
                        return f"{head_clean}>{body}<v>{repr(float(val))}</v></c>"
                    sval = str(val)
                    if sval in ERR_VALUES:
                        stats["errors"] += 1
                        return f'{head_clean} t="e">{body}<v>{sval}</v></c>'
                    stats["filled"] += 1
                    return f'{head_clean} t="str">{body}<v>{xml_escape(sval)}</v></c>'

                text = re.sub(r"(<c\b[^>]*?)(?:/>|>(.*?)</c>)", fill, text,
                              flags=re.S)
                data = text.encode("utf-8")

        zout.writestr(item, data)

    zin.close()
    zout.close()
    shutil.move(tmp, XLSX)

    print(f"  formula cells found      : {stats['formulas']}")
    print(f"  cached values written    : {stats['filled']}")
    print(f"  error values preserved   : {stats['errors']}")
    print(f"  skipped (no result)      : {stats['missing']}")
    print("  calcPr fullCalcOnLoad=1 set - Excel still recalculates on open.")
    if stats["errors"]:
        print("  WARNING: the workbook contains Excel error values. Investigate.")
        sys.exit(1)
    print("\nDone. Formulas intact; values now render in viewers with no calc engine.")


if __name__ == "__main__":
    main()
