"""
Builds output/CMG_DCF_Model.xlsx - a fully formula-driven DCF of Chipotle
Mexican Grill (NYSE: CMG).

Design rule: the only values written as numbers are (a) historical actuals taken
from the 10-Ks and (b) forward-looking assumptions. EVERY calculated cell is a
live Excel formula, so an interviewer can click any output and trace it back to
an input.

Font convention (standard banking):
    BLUE   = hardcoded input / historical actual
    BLACK  = formula referencing cells on the same sheet
    GREEN  = formula referencing another sheet

Run:  python src/build_model.py
"""
from __future__ import annotations

import csv
import os
import sys

from openpyxl import Workbook
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.properties import PageSetupProperties

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assumptions as A          # noqa: E402
import wacc as W                 # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_CSV = os.path.join(ROOT, "data", "historicals.csv")
OUT_XLSX = os.path.join(ROOT, "output", "CMG_DCF_Model.xlsx")

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
BLUE, BLACK, GREEN = "FF0000FF", "FF000000", "FF008000"
GREY = "FF7F7F7F"

FMT_MM = '#,##0.0;(#,##0.0)'
FMT_PCT = '0.0%;(0.0%)'
FMT_PCT2 = '0.00%;(0.00%)'
FMT_PRICE = '$#,##0.00;($#,##0.00)'
FMT_X = '0.0"x"'
FMT_CNT = '#,##0;(#,##0)'
FMT_AUV = '$#,##0.000'
FMT_N = '0.0'
FMT_TXT = '@'

FILL_TITLE = PatternFill("solid", fgColor="FF1F3864")
FILL_SECTION = PatternFill("solid", fgColor="FFD9E1F2")
FILL_HDR = PatternFill("solid", fgColor="FFF2F2F2")
FILL_BASE = PatternFill("solid", fgColor="FFFFF2CC")
FILL_OUT = PatternFill("solid", fgColor="FFE2EFDA")

THIN = Side(style="thin", color="FFBFBFBF")
TOPBORDER = Border(top=Side(style="thin", color="FF000000"))
DBL = Border(top=Side(style="thin", color="FF000000"),
             bottom=Side(style="double", color="FF000000"))

TAB_INPUT = "4472C4"     # blue   - inputs
TAB_CALC = "ED7D31"      # orange - calculations
TAB_OUT = "70AD47"       # green  - outputs

PERIOD_COLS = ["C", "D", "E", "F", "G"]
SRC_COL = "I"


# ---------------------------------------------------------------------------
# Sheet writer
# ---------------------------------------------------------------------------
class Sheet:
    """Thin wrapper that writes rows top-to-bottom and remembers row numbers."""

    def __init__(self, wb, name, title, purpose, tab_color, years, col_width=46):
        self.ws = wb.create_sheet(name)
        self.ws.sheet_properties.tabColor = tab_color
        self.ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
        self.name = name
        self.r = 1
        self.rows = {}
        self.years = years

        self.ws.column_dimensions["A"].width = col_width
        self.ws.column_dimensions["B"].width = 13
        for c in PERIOD_COLS:
            self.ws.column_dimensions[c].width = 14
        self.ws.column_dimensions["H"].width = 3
        self.ws.column_dimensions[SRC_COL].width = 96

        c = self.ws.cell(1, 1, title)
        c.font = Font(bold=True, size=14, color="FFFFFFFF")
        c.fill = FILL_TITLE
        for col in range(2, 10):
            self.ws.cell(1, col).fill = FILL_TITLE
        c2 = self.ws.cell(2, 1, purpose)
        c2.font = Font(italic=True, size=9, color=GREY)
        self.r = 4

    # -- structural helpers -------------------------------------------------
    def blank(self, n=1):
        self.r += n

    def section(self, text):
        c = self.ws.cell(self.r, 1, text)
        c.font = Font(bold=True, size=10)
        c.fill = FILL_SECTION
        for col in range(2, 10):
            self.ws.cell(self.r, col).fill = FILL_SECTION
        self.r += 1

    def header(self, labels, unit_hdr="Units", src_hdr="Source / note"):
        self.ws.cell(self.r, 1, "").font = Font(bold=True)
        u = self.ws.cell(self.r, 2, unit_hdr)
        u.font = Font(bold=True, size=9)
        u.alignment = Alignment(horizontal="center")
        for col, lab in zip(PERIOD_COLS, labels):
            cc = self.ws.cell(self.r, self.ci(col), lab)
            cc.font = Font(bold=True, size=10)
            cc.alignment = Alignment(horizontal="center")
            cc.fill = FILL_HDR
            cc.border = Border(bottom=Side(style="medium", color="FF1F3864"))
        s = self.ws.cell(self.r, self.ci(SRC_COL), src_hdr)
        s.font = Font(bold=True, size=9)
        self.hdr_row = self.r
        self.r += 1

    @staticmethod
    def ci(letter):
        return {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8, "I": 9}[letter]

    # -- the main row writer ------------------------------------------------
    def row(self, key, label, unit="", values=None, fmt=FMT_MM, color=BLACK,
            source="", bold=False, indent=0, border=None, fill=None, italic=False):
        """values: list aligned to PERIOD_COLS. A leading '=' makes it a formula."""
        rr = self.r
        lc = self.ws.cell(rr, 1, ("    " * indent) + label)
        lc.font = Font(bold=bold, size=10, italic=italic)
        uc = self.ws.cell(rr, 2, unit)
        uc.font = Font(size=8, color=GREY)
        uc.alignment = Alignment(horizontal="center")

        if values is not None:
            for col, v in zip(PERIOD_COLS, values):
                if v is None:
                    continue
                cell = self.ws.cell(rr, self.ci(col), v)
                cell.number_format = fmt
                cell.font = Font(color=color, bold=bold, size=10, italic=italic)
                if border:
                    cell.border = border
                if fill:
                    cell.fill = fill
        if source:
            sc = self.ws.cell(rr, self.ci(SRC_COL), source)
            sc.font = Font(size=8, color=GREY)
            sc.alignment = Alignment(vertical="top", wrap_text=False)
        if key:
            self.rows[key] = rr
        self.r += 1
        return rr

    def single(self, key, label, unit, value, fmt=FMT_MM, color=BLUE, source="",
               bold=False, indent=0, fill=None, italic=False, border=None):
        """A one-off input/output that lives in column C only."""
        return self.row(key, label, unit, [value, None, None, None, None],
                        fmt=fmt, color=color, source=source, bold=bold,
                        indent=indent, fill=fill, italic=italic, border=border)

    def note(self, text, indent=0):
        c = self.ws.cell(self.r, 1, ("    " * indent) + text)
        c.font = Font(size=8, italic=True, color=GREY)
        self.r += 1

    def finish(self, freeze="C5", last_col="G"):
        self.ws.freeze_panes = freeze
        self.ws.print_area = f"A1:{last_col}{self.r}"
        self.ws.page_setup.orientation = "landscape"
        self.ws.page_setup.fitToWidth = 1
        self.ws.page_setup.fitToHeight = 0
        self.ws.print_options.horizontalCentered = True


# ---------------------------------------------------------------------------
# Load historicals
# ---------------------------------------------------------------------------
def load_historicals():
    out = {}
    with open(DATA_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            vals = []
            for y in ("fy2021", "fy2022", "fy2023", "fy2024", "fy2025"):
                raw = row[y].strip()
                vals.append(float(raw) if raw else None)
            out[row["metric"]] = {"unit": row["unit"], "v": vals,
                                  "src": row["source"]}
    return out


H = load_historicals()


def hv(metric):
    return H[metric]["v"]


def hs(metric):
    return H[metric]["src"]


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
wb = Workbook()
wb.remove(wb.active)

HIST_YEARS = ["FY2021A", "FY2022A", "FY2023A", "FY2024A", "FY2025A"]
FCST_YEARS = ["FY2026E", "FY2027E", "FY2028E", "FY2029E", "FY2030E"]

# Sheets are created in final tab order; Summary is populated last.
sSum = Sheet(wb, "Summary", "CHIPOTLE MEXICAN GRILL (NYSE: CMG) - DCF VALUATION SUMMARY",
             "OUTPUT | One-page valuation conclusion. Every figure links to the "
             "supporting tabs - nothing here is typed.", TAB_OUT, FCST_YEARS, col_width=52)
sHist = Sheet(wb, "Historicals", "HISTORICALS - FY2021A to FY2025A (as reported)",
              "INPUT | Actuals from Chipotle's 10-K filings. Blue = as filed. "
              "Black = computed margins and ratios that ground the forecast.",
              TAB_INPUT, HIST_YEARS, col_width=52)
sAsm = Sheet(wb, "Assumptions", "ASSUMPTIONS - FY2026E to FY2030E forecast drivers",
             "INPUT | Every forward-looking driver in the model. Blue cells are the "
             "only things you change. Revenue is built units x AUV, not a top-line "
             "growth rate.", TAB_INPUT, FCST_YEARS, col_width=52)
sW = Sheet(wb, "WACC", "WACC - cost of capital via CAPM",
           "CALC | Chipotle carries no financial debt, so WACC collapses to the "
           "cost of equity. Lease treatment is stated explicitly below.",
           TAB_CALC, ["", "", "", "", ""], col_width=52)
sDCF = Sheet(wb, "DCF", "DCF - unlevered free cash flow, FY2026E to FY2030E",
             "CALC | Revenue to UFCF to present value. Mid-year discounting "
             "convention is an explicit choice, set in a labelled input cell.",
             TAB_CALC, FCST_YEARS, col_width=52)
sTV = Sheet(wb, "Terminal Value", "TERMINAL VALUE - Gordon Growth, cross-checked against an exit multiple",
            "CALC | Primary method is Gordon Growth on a normalised terminal cash "
            "flow. The exit-multiple cross-check and the two implied-value checks "
            "are shown alongside.", TAB_CALC, ["", "", "", "", ""], col_width=52)
sBr = Sheet(wb, "Valuation Bridge", "VALUATION BRIDGE - enterprise value to implied share price",
            "OUTPUT | Sum of PV of forecast UFCF, plus PV of terminal value, less "
            "net debt, divided by diluted shares.", TAB_OUT, ["", "", "", "", ""],
            col_width=52)
sSen = Sheet(wb, "Sensitivity", "SENSITIVITY - implied share price",
             "OUTPUT | Live formulas, not pasted values. Each cell re-runs the "
             "whole discounting and terminal-value calculation at that "
             "WACC / growth / margin pair.", TAB_OUT, ["", "", "", "", ""], col_width=30)


# ===========================================================================
# TAB: HISTORICALS
# ===========================================================================
def build_historicals(s):
    s.header(HIST_YEARS)
    C = PERIOD_COLS

    s.section("INCOME STATEMENT ($ in millions, as reported)")
    s.row("rev", "Total revenue", "$mm", hv("Total revenue"), color=BLUE,
          source=hs("Total revenue"), bold=True)
    s.note("Restaurant operating costs (exclusive of D&A shown separately):")
    for key, metric in [("food", "Food, beverage and packaging"),
                        ("labor", "Labor"),
                        ("occ", "Occupancy"),
                        ("othop", "Other operating costs")]:
        s.row(key, metric, "$mm", hv(metric), color=BLUE, source=hs(metric), indent=1)
    s.row("totroc", "Total restaurant operating costs", "$mm",
          [f"={c}{s.rows['food']}+{c}{s.rows['labor']}+{c}{s.rows['occ']}+{c}{s.rows['othop']}"
           for c in C], source="Sum of the four restaurant operating cost lines above.",
          border=TOPBORDER)
    for key, metric in [("ga", "General and administrative expenses"),
                        ("da", "Depreciation and amortization"),
                        ("preop", "Pre-opening costs"),
                        ("imp", "Impairment, closure costs, and asset disposals")]:
        s.row(key, metric, "$mm", hv(metric), color=BLUE, source=hs(metric))
    s.row("totopex", "Total operating expenses", "$mm",
          [f"={c}{s.rows['totroc']}+{c}{s.rows['ga']}+{c}{s.rows['da']}+"
           f"{c}{s.rows['preop']}+{c}{s.rows['imp']}" for c in C],
          source="Total restaurant operating costs + G&A + D&A + pre-opening + impairment.",
          border=TOPBORDER)
    s.row("ebit", "Operating income (EBIT)", "$mm",
          [f"={c}{s.rows['rev']}-{c}{s.rows['totopex']}" for c in C], bold=True,
          source="Total revenue less total operating expenses.", border=TOPBORDER)
    s.row("ebit_rep", "Memo: EBIT as reported in the 10-K", "$mm",
          hv("Operating income (EBIT) - as reported"), color=BLUE,
          source=hs("Operating income (EBIT) - as reported"), italic=True)
    s.row("ebit_chk", "Check: build vs. reported (must be 0.0)", "$mm",
          [f"={c}{s.rows['ebit']}-{c}{s.rows['ebit_rep']}" for c in C],
          source="Tie-out. Any non-zero value means a cost line was mistyped.",
          italic=True)
    s.row("ebitda", "EBITDA (EBIT + D&A)", "$mm",
          [f"={c}{s.rows['ebit']}+{c}{s.rows['da']}" for c in C], bold=True,
          source="Chipotle reports D&A as a separate line, so EBITDA = EBIT + D&A.")
    s.row("pretax", "Income before income taxes", "$mm", hv("Income before income taxes"),
          color=BLUE, source=hs("Income before income taxes"))
    s.row("taxprov", "Provision for income taxes", "$mm", hv("Provision for income taxes"),
          color=BLUE, source=hs("Provision for income taxes"))
    s.row("etr_rep", "Effective income tax rate (as reported)", "%",
          hv("Effective income tax rate"), fmt=FMT_PCT, color=BLUE,
          source=hs("Effective income tax rate"))
    s.row("etr_calc", "Effective tax rate (check: provision / pre-tax income)", "%",
          [f"={c}{s.rows['taxprov']}/{c}{s.rows['pretax']}" for c in C], fmt=FMT_PCT,
          source="Recomputed from the two lines above.", italic=True)
    s.blank()

    s.section("COMMON-SIZE: EVERY COST LINE AS A % OF REVENUE (this is what anchors the forecast)")
    for key, label in [("food", "Food, beverage and packaging"), ("labor", "Labor"),
                       ("occ", "Occupancy"), ("othop", "Other operating costs"),
                       ("totroc", "Total restaurant operating costs"),
                       ("ga", "General and administrative"), ("da", "Depreciation and amortization"),
                       ("preop", "Pre-opening costs"), ("imp", "Impairment and closures")]:
        s.row(f"pct_{key}", label, "% rev",
              [f"={c}{s.rows[key]}/{c}{s.rows['rev']}" for c in C], fmt=FMT_PCT,
              indent=1, bold=(key == "totroc"))
    s.row("pct_ebit", "EBIT margin", "% rev",
          [f"={c}{s.rows['ebit']}/{c}{s.rows['rev']}" for c in C], fmt=FMT_PCT,
          bold=True, border=TOPBORDER,
          source="The single most important historical series in the model - the "
                 "Assumptions tab EBIT margin path is set against it.")
    s.row("pct_ebitda", "EBITDA margin", "% rev",
          [f"={c}{s.rows['ebitda']}/{c}{s.rows['rev']}" for c in C], fmt=FMT_PCT, bold=True)
    s.row("rev_growth", "Revenue growth (YoY)", "%",
          [None] + [f"={c}{s.rows['rev']}/{p}{s.rows['rev']}-1"
                    for c, p in zip(C[1:], C[:-1])], fmt=FMT_PCT)
    s.blank()

    s.section("CASH FLOW ITEMS ($ in millions, from the consolidated statements of cash flows)")
    s.row("cfo", "Net cash provided by operating activities", "$mm",
          hv("Net cash provided by operating activities"), color=BLUE,
          source=hs("Net cash provided by operating activities"))
    s.row("capex", "Capital expenditures (leasehold improvements, PP&E)", "$mm",
          hv("Capital expenditures (purchases of leasehold improvements, property and equipment)"),
          color=BLUE,
          source=hs("Capital expenditures (purchases of leasehold improvements, property and equipment)"))
    s.row("pct_capex", "CapEx as % of revenue", "% rev",
          [f"={c}{s.rows['capex']}/{c}{s.rows['rev']}" for c in C], fmt=FMT_PCT, indent=1)
    s.row("capex_da", "CapEx / D&A", "x",
          [f"={c}{s.rows['capex']}/{c}{s.rows['da']}" for c in C], fmt=FMT_X, indent=1,
          source="Comfortably above 1.0x - Chipotle is still in build-out mode. This ratio "
                 "is why the terminal year needs a normalised capex figure.")
    s.blank()
    s.note("Working capital: cash-flow-statement presentation (positive = source of cash).")
    nwc_items = [("nwc_ar", "CF: Accounts receivable"),
                 ("nwc_inv", "CF: Inventory"),
                 ("nwc_ppd", "CF: Prepaid expenses and other current assets"),
                 ("nwc_oa", "CF: Other assets"),
                 ("nwc_ap", "CF: Accounts payable"),
                 ("nwc_pay", "CF: Accrued payroll and benefits"),
                 ("nwc_acc", "CF: Accrued liabilities"),
                 ("nwc_un", "CF: Unearned revenue"),
                 ("nwc_oltl", "CF: Other long-term liabilities")]
    for key, metric in nwc_items:
        s.row(key, metric.replace("CF: ", ""), "$mm", hv(metric), color=BLUE,
              source=hs(metric), indent=1)
    s.row("dnwc", "Change in net working capital (+ = cash source)", "$mm",
          ["=" + "+".join(f"{c}{s.rows[k]}" for k, _ in nwc_items) for c in C],
          bold=True, border=TOPBORDER,
          source="Sum of the nine lines above. Income taxes payable and the operating "
                 "lease asset/liability lines are deliberately EXCLUDED - taxes are "
                 "modelled inside NOPAT, and leases are treated as an operating expense.")
    for key, metric in [("nwc_tax", "CF: Income tax payable/receivable (excluded from NWC)"),
                        ("nwc_lease_a", "CF: Operating lease assets (excluded from NWC)"),
                        ("nwc_lease_l", "CF: Operating lease liabilities (excluded from NWC)")]:
        s.row(key, metric.replace("CF: ", ""), "$mm", hv(metric), color=BLUE,
              source=hs(metric), indent=1, italic=True)
    s.row("rev_fy20", "Memo: FY2020 total revenue", "$mm", [5984.634, None, None, None, None],
          color=BLUE, italic=True,
          source="FY2021 10-K Results of Operations. Needed only to compute the FY2021 "
                 "change in revenue.")
    s.row("drev", "Change in revenue", "$mm",
          [f"=C{s.rows['rev']}-C{s.rows['rev_fy20']}"] +
          [f"={c}{s.rows['rev']}-{p}{s.rows['rev']}" for c, p in zip(C[1:], C[:-1])])
    s.row("nwc_pct", "Change in NWC as % of change in revenue", "%",
          [f"={c}{s.rows['dnwc']}/{c}{s.rows['drev']}" for c in C], fmt=FMT_PCT, bold=True,
          source="Positive = working capital RELEASES cash as revenue grows. Chipotle runs "
                 "negative working capital: guests pay at the point of sale while suppliers "
                 "are paid on ~10-day terms (FY2025 10-K, Liquidity and Capital Resources).")
    s.blank()

    s.section("BALANCE SHEET ($ in millions, fiscal year-end)")
    s.row("cash", "Cash and cash equivalents", "$mm", hv("Cash and cash equivalents (year-end)"),
          color=BLUE, source=hs("Cash and cash equivalents (year-end)"))
    s.row("sti", "Short-term investments", "$mm", hv("Short-term investments (year-end)"),
          color=BLUE, source=hs("Short-term investments (year-end)"))
    s.row("lti", "Long-term investments", "$mm", hv("Long-term investments (year-end)"),
          color=BLUE, source=hs("Long-term investments (year-end)"))
    s.row("cashinv", "Total cash and investments", "$mm",
          [f"={c}{s.rows['cash']}+{c}{s.rows['sti']}+{c}{s.rows['lti']}" for c in C],
          bold=True, border=TOPBORDER,
          source="Feeds the Valuation Bridge. Excludes restricted cash ($35.4m at 12/31/2025).")
    s.row("debt", "Total debt", "$mm", hv("Total debt (year-end)"), color=BLUE, bold=True,
          source=hs("Total debt (year-end)"))
    s.row("netcash", "Net cash / (net debt)", "$mm",
          [f"={c}{s.rows['cashinv']}-{c}{s.rows['debt']}" for c in C], bold=True)
    s.row("oll_c", "Operating lease liabilities - current", "$mm",
          hv("Operating lease liabilities - current (year-end)"), color=BLUE,
          source=hs("Operating lease liabilities - current (year-end)"), italic=True)
    s.row("oll_nc", "Operating lease liabilities - non-current", "$mm",
          hv("Operating lease liabilities - non-current (year-end)"), color=BLUE,
          source=hs("Operating lease liabilities - non-current (year-end)"), italic=True)
    s.row("oll", "Total operating lease liabilities (NOT in net debt)", "$mm",
          [f"={c}{s.rows['oll_c']}+{c}{s.rows['oll_nc']}" for c in C], bold=True, italic=True,
          border=TOPBORDER,
          source="EXCLUDED from net debt because occupancy cost is left inside EBIT. See "
                 "the lease treatment block on the WACC tab.")
    s.row("roua", "Operating lease right-of-use assets", "$mm",
          hv("Operating lease right-of-use assets (year-end)"), color=BLUE,
          source=hs("Operating lease right-of-use assets (year-end)"), italic=True)
    s.blank()

    s.section("SHARE COUNT (post 50-for-1 stock split, effective 26 June 2024)")
    s.row("dil_sh", "Diluted weighted-average shares outstanding", "mm",
          hv("Diluted weighted-average shares (post 50-for-1 split)"), fmt=FMT_CNT,
          color=BLUE, source=hs("Diluted weighted-average shares (post 50-for-1 split)"))
    s.row("bas_sh", "Basic weighted-average shares outstanding", "mm",
          hv("Basic weighted-average shares (post 50-for-1 split)"), fmt=FMT_CNT,
          color=BLUE, source=hs("Basic weighted-average shares (post 50-for-1 split)"))
    s.row("dil_fac", "Dilution factor (diluted / basic)", "x",
          [None, None] + [f"={c}{s.rows['dil_sh']}/{c}{s.rows['bas_sh']}" for c in C[2:]],
          fmt='0.000"x"', source="Only ~0.4% - Chipotle's option and RSU overhang is small.")
    s.blank()

    s.section("OPERATING METRICS - company-owned restaurants only")
    s.note("Chipotle owns and operates all of its restaurants. The 14 partner-operated "
           "(licensed) units in the Middle East are excluded - they generate no "
           "consolidated restaurant revenue. There is no franchise revenue to model.")
    s.row("u_beg", "Restaurants - beginning of period", "#",
          hv("Company-owned restaurants - beginning of period"), fmt=FMT_CNT, color=BLUE,
          source=hs("Company-owned restaurants - beginning of period"))
    s.row("u_open", "Openings", "#", hv("Company-owned restaurant openings"), fmt=FMT_CNT,
          color=BLUE, indent=1, source=hs("Company-owned restaurant openings"))
    s.row("u_close", "Closures and relocations", "#",
          hv("Company-owned closures and relocations"), fmt=FMT_CNT, color=BLUE, indent=1,
          source=hs("Company-owned closures and relocations"))
    s.row("u_end", "Restaurants - end of period", "#",
          [f"={c}{s.rows['u_beg']}+{c}{s.rows['u_open']}+{c}{s.rows['u_close']}" for c in C],
          fmt=FMT_CNT, bold=True, border=TOPBORDER)
    s.row("u_end_rep", "Memo: end of period as reported", "#",
          hv("Company-owned restaurants - end of period"), fmt=FMT_CNT, color=BLUE,
          italic=True, source=hs("Company-owned restaurants - end of period"))
    s.row("u_chk", "Check: build vs. reported (must be 0)", "#",
          [f"={c}{s.rows['u_end']}-{c}{s.rows['u_end_rep']}" for c in C], fmt=FMT_CNT,
          italic=True)
    s.row("u_avg", "Average restaurants during the period", "#",
          [f"=({c}{s.rows['u_beg']}+{c}{s.rows['u_end']})/2" for c in C], fmt=FMT_CNT)
    s.row("u_growth", "Unit growth (YoY, end of period)", "%",
          [None] + [f"={c}{s.rows['u_end']}/{p}{s.rows['u_end']}-1"
                    for c, p in zip(C[1:], C[:-1])], fmt=FMT_PCT)
    s.row("auv", "Average restaurant sales (AUV)", "$mm",
          hv("Average restaurant sales (AUV)"), fmt=FMT_AUV, color=BLUE,
          source=hs("Average restaurant sales (AUV)"))
    s.row("auv_g", "AUV growth (YoY)", "%",
          [None] + [f"={c}{s.rows['auv']}/{p}{s.rows['auv']}-1"
                    for c, p in zip(C[1:], C[:-1])], fmt=FMT_PCT, indent=1)
    s.row("comps", "Comparable restaurant sales growth", "%",
          hv("Comparable restaurant sales growth"), fmt=FMT_PCT, color=BLUE,
          source=hs("Comparable restaurant sales growth"))
    s.row("realiz", "Revenue realisation factor: revenue / (avg units x AUV)", "x",
          [f"={c}{s.rows['rev']}/({c}{s.rows['u_avg']}*{c}{s.rows['auv']})" for c in C],
          fmt='0.0000"x"', bold=True,
          source="Below 1.0x because units opened during the year contribute only a partial "
                 "year of sales while AUV is a trailing-12-month figure for mature units. The "
                 "FY2023-25 average of this row is the calibration input on the Assumptions tab.")
    s.row("realiz_avg", "  FY2023A-FY2025A average (used in the forecast)", "x",
          [None, None, None, None,
           f"=AVERAGE(E{s.rows['realiz']}:G{s.rows['realiz']})"],
          fmt='0.0000"x"', italic=True)
    s.finish(freeze="C5")


build_historicals(sHist)


# ===========================================================================
# TAB: ASSUMPTIONS
# ===========================================================================
def build_assumptions(s, hist):
    s.header(FCST_YEARS)
    C = PERIOD_COLS
    hr = hist.rows
    HN = "Historicals"

    s.note("BLUE = hardcoded assumption (the only cells you should change). "
           "BLACK = formula on this sheet. GREEN = link to another sheet.")
    s.blank()

    s.section("REVENUE BUILD - restaurant count x AUV (never a blunt top-line growth rate)")
    s.row("u_beg", "Restaurants - beginning of period", "#",
          [f"={HN}!G{hr['u_end']}"] +
          [f"={p}{s.r + 3}" for p in C[:-1]], fmt=FMT_CNT, color=GREEN,
          source="FY2026E opens from the FY2025A closing count of 4,042 on the Historicals tab.")
    s.row("u_open", "New restaurant openings", "#",
          [A.NEW_UNIT_OPENINGS[y] for y in A.FORECAST_YEARS], fmt=FMT_CNT, color=BLUE,
          indent=1, source=A.NEW_UNIT_OPENINGS_SOURCE)
    s.row("u_close", "Closures and relocations", "#",
          [A.UNIT_CLOSURES[y] for y in A.FORECAST_YEARS], fmt=FMT_CNT, color=BLUE, indent=1,
          source=A.UNIT_CLOSURES_SOURCE)
    s.row("u_end", "Restaurants - end of period", "#",
          [f"={c}{s.rows['u_beg']}+{c}{s.rows['u_open']}+{c}{s.rows['u_close']}" for c in C],
          fmt=FMT_CNT, bold=True, border=TOPBORDER)
    s.row("u_growth", "Unit growth (YoY)", "%",
          [f"=C{s.rows['u_end']}/{HN}!G{hr['u_end']}-1"] +
          [f"={c}{s.rows['u_end']}/{p}{s.rows['u_end']}-1" for c, p in zip(C[1:], C[:-1])],
          fmt=FMT_PCT, indent=1)
    s.row("u_avg", "Average restaurants during the period", "#",
          [f"=({c}{s.rows['u_beg']}+{c}{s.rows['u_end']})/2" for c in C], fmt=FMT_CNT)
    s.blank()
    s.row("auv_g", "AUV growth (YoY)", "%", [A.AUV_GROWTH[y] for y in A.FORECAST_YEARS],
          fmt=FMT_PCT, color=BLUE, source=A.AUV_GROWTH_SOURCE)
    s.row("auv", "Average restaurant sales (AUV)", "$mm",
          [f"={HN}!G{hr['auv']}*(1+C{s.rows['auv_g']})"] +
          [f"={p}{s.r}*(1+{c}{s.rows['auv_g']})" for c, p in zip(C[1:], C[:-1])],
          fmt=FMT_AUV, color=GREEN,
          source="Grown off the FY2025A AUV of $3.104m on the Historicals tab.")
    s.single("realiz", "Revenue realisation factor", "x", A.REVENUE_REALIZATION_FACTOR,
             fmt='0.0000"x"', color=BLUE, source=A.REVENUE_REALIZATION_FACTOR_SOURCE)
    s.row("rev", "TOTAL REVENUE", "$mm",
          [f"={c}{s.rows['u_avg']}*{c}{s.rows['auv']}*$C${s.rows['realiz']}" for c in C],
          bold=True, border=TOPBORDER, fill=FILL_OUT,
          source="Average units x AUV x realisation factor. This is the only revenue line "
                 "in the model; the DCF tab links to it.")
    s.row("rev_g", "Revenue growth (YoY)", "%",
          [f"=C{s.rows['rev']}/{HN}!G{hr['rev']}-1"] +
          [f"={c}{s.rows['rev']}/{p}{s.rows['rev']}-1" for c, p in zip(C[1:], C[:-1])],
          fmt=FMT_PCT, indent=1)
    s.row("rev_cagr", "Memo: FY2025A-FY2030E revenue CAGR", "%",
          [None, None, None, None, f"=(G{s.rows['rev']}/{HN}!G{hr['rev']})^(1/5)-1"],
          fmt=FMT_PCT, italic=True)
    s.row("comps", "Memo: comparable restaurant sales growth (context only)", "%",
          [A.COMP_SALES_GROWTH[y] for y in A.FORECAST_YEARS], fmt=FMT_PCT, color=BLUE,
          italic=True, source=A.COMP_SALES_GROWTH_SOURCE)
    s.blank()

    s.section("MARGIN PATH")
    s.note("STATED POSITION: near-term COMPRESSION, then partial recovery - not expansion. "
           "FY2025A was 16.2% and H1 2026 ran at 14.3%. The forecast troughs at 14.5% in "
           "FY2026E and recovers to 16.3% by FY2030E, back to the FY2025A level but still "
           "below the FY2024A peak of 16.9%.")
    s.row("ebit_m", "EBIT margin", "% rev", [A.EBIT_MARGIN[y] for y in A.FORECAST_YEARS],
          fmt=FMT_PCT, color=BLUE, bold=True, source=A.EBIT_MARGIN_SOURCE)
    s.row("ebit_m_hist", "Memo: FY2021A-FY2025A actual EBIT margin", "% rev",
          [f"={HN}!{c}{hr['pct_ebit']}" for c in C], fmt=FMT_PCT, color=GREEN, italic=True,
          source="Direct link to the Historicals tab so the assumption sits next to the trend.")
    s.blank()

    s.section("TAX, CAPITAL INTENSITY AND WORKING CAPITAL")
    s.single("tax", "Effective tax rate", "%", A.EFFECTIVE_TAX_RATE, fmt=FMT_PCT,
             color=BLUE, bold=True, source=A.EFFECTIVE_TAX_RATE_SOURCE)
    s.row("da_pct", "D&A as % of revenue", "% rev",
          [A.DA_PCT_OF_REVENUE[y] for y in A.FORECAST_YEARS], fmt=FMT_PCT, color=BLUE,
          source=A.DA_PCT_OF_REVENUE_SOURCE)
    s.row("capex_pct", "CapEx as % of revenue", "% rev",
          [A.CAPEX_PCT_OF_REVENUE[y] for y in A.FORECAST_YEARS], fmt=FMT_PCT, color=BLUE,
          source=A.CAPEX_PCT_OF_REVENUE_SOURCE)
    s.row("capex_chk", "Memo: implied FY2026E capex vs. the $834.1m guided", "$mm",
          [f"=C{s.rows['capex_pct']}*C{s.rows['rev']}", None, None, None, None],
          italic=True,
          source="FY2025 10-K MD&A: 'In 2026, we expect to incur about $834.1 million in "
                 "total capital expenditures.' This row should land close to that number.")
    s.single("nwc_pct", "Change in NWC as % of change in revenue (+ = cash SOURCE)", "%",
             A.NWC_PCT_OF_DELTA_REVENUE, fmt=FMT_PCT, color=BLUE, bold=True,
             source=A.NWC_PCT_OF_DELTA_REVENUE_SOURCE)
    s.row("nwc_hist", "Memo: FY2021A-FY2025A actual (same definition)", "%",
          [f"={HN}!{c}{hr['nwc_pct']}" for c in C], fmt=FMT_PCT, color=GREEN, italic=True)
    s.blank()

    s.section("FORECAST PERIOD AND TERMINAL ASSUMPTIONS")
    s.single("nyears", "Explicit forecast period", "years", 5, fmt='0',
             color=BLUE, source="FY2026E-FY2030E. Five years is long enough for the margin "
                                "recovery to play out and short enough to stay credible.")
    s.single("g", "Terminal growth rate (g)", "%", A.TERMINAL_GROWTH, fmt=FMT_PCT2,
             color=BLUE, bold=True, source=A.TERMINAL_GROWTH_SOURCE)
    s.single("g_chk", "Check: is g below WACC? (required, or the model breaks)", "",
             f"=IF($C${s.rows['g']}<WACC!$C${'{WACC_ROW}'},\"OK - g < WACC\","
             f"\"ERROR - g must be below WACC\")",
             fmt=FMT_TXT, color=GREEN, italic=True)
    s.finish(freeze="C5")


build_assumptions(sAsm, sHist)


# ===========================================================================
# TAB: WACC
# ===========================================================================
def build_wacc(s, hist, asm):
    C = PERIOD_COLS
    hr, ar = hist.rows, asm.rows
    HN, AN = "Historicals", "Assumptions"
    s.ws.column_dimensions["C"].width = 16

    s.section("COST OF EQUITY - CAPM:  Re = Rf + beta x ERP")
    s.single("rf", "Risk-free rate (Rf) - 10-year U.S. Treasury", "%", W.RISK_FREE_RATE,
             fmt=FMT_PCT2, color=BLUE, source=W.RISK_FREE_RATE_SOURCE)
    s.single("beta", "Levered beta (CMG)", "x", W.LEVERED_BETA, fmt='0.00"x"', color=BLUE,
             source=W.LEVERED_BETA_SOURCE)
    s.single("erp", "Equity risk premium (ERP)", "%", W.EQUITY_RISK_PREMIUM, fmt=FMT_PCT2,
             color=BLUE, source=W.EQUITY_RISK_PREMIUM_SOURCE)
    s.single("ke", "Cost of equity (Re)", "%",
             f"=C{s.rows['rf']}+C{s.rows['beta']}*C{s.rows['erp']}", fmt=FMT_PCT2,
             color=BLACK, bold=True, fill=FILL_OUT,
             source="Rf + beta x ERP.")
    s.blank()

    s.section("COST OF DEBT AND CAPITAL STRUCTURE")
    s.note("CHIPOTLE HAS NO TRADITIONAL BORROWINGS. The FY2025 10-K (Note 12, Debt) discloses "
           "a $500.0m revolving credit facility with JPMorgan Chase that was UNDRAWN at "
           "12/31/2025, and us-gaap:LongTermDebt is zero in every year FY2021-FY2025.")
    s.note("Because the debt weight is ~0%, WACC in this model APPROXIMATES THE COST OF EQUITY. "
           "No debt tranche has been fabricated to make the formula look fuller.")
    s.single("debt", "Total debt (D)", "$mm", f"={HN}!G{hr['debt']}", color=GREEN, bold=True,
             source="Link to FY2025A total debt on the Historicals tab.")
    s.single("rd", "Pre-tax cost of debt (Rd) - illustrative", "%", W.PRETAX_COST_OF_DEBT,
             fmt=FMT_PCT2, color=BLUE, source=W.PRETAX_COST_OF_DEBT_SOURCE)
    s.single("tax", "Effective tax rate (t)", "%", f"={AN}!C{ar['tax']}", fmt=FMT_PCT,
             color=GREEN, source="Link to the Assumptions tab.")
    s.single("rd_at", "After-tax cost of debt = Rd x (1 - t)", "%",
             f"=C{s.rows['rd']}*(1-C{s.rows['tax']})", fmt=FMT_PCT2, color=BLACK)
    s.blank()

    s.section("MARKET CAPITALISATION AND WEIGHTS")
    s.single("px", "Current share price", "$", A.CURRENT_SHARE_PRICE, fmt=FMT_PRICE,
             color=BLUE, source=A.CURRENT_SHARE_PRICE_SOURCE)
    s.single("sh_out", "Shares outstanding at the valuation date", "mm",
             A.SHARES_OUTSTANDING_AT_VALUATION, fmt=FMT_CNT, color=BLUE,
             source=A.SHARES_OUTSTANDING_SOURCE)
    s.single("dilf", "Dilution factor (diluted / basic)", "x", A.DILUTION_FACTOR,
             fmt='0.00000"x"', color=BLUE, source=A.DILUTION_FACTOR_SOURCE)
    s.single("sh_dil", "Diluted shares outstanding", "mm",
             f"=C{s.rows['sh_out']}*C{s.rows['dilf']}", fmt=FMT_CNT, color=BLACK, bold=True,
             source="Feeds the Valuation Bridge.")
    s.single("mcap", "Equity market capitalisation (E)", "$mm",
             f"=C{s.rows['px']}*C{s.rows['sh_dil']}", color=BLACK, bold=True)
    s.single("we", "Weight of equity  E / (D + E)", "%",
             f"=C{s.rows['mcap']}/(C{s.rows['mcap']}+C{s.rows['debt']})", fmt=FMT_PCT,
             color=BLACK)
    s.single("wd", "Weight of debt  D / (D + E)", "%",
             f"=C{s.rows['debt']}/(C{s.rows['mcap']}+C{s.rows['debt']})", fmt=FMT_PCT,
             color=BLACK)
    s.blank()

    s.section("WACC")
    s.single("wacc", "WACC = E/(D+E) x Re + D/(D+E) x Rd x (1 - t)", "%",
             f"=C{s.rows['we']}*C{s.rows['ke']}+C{s.rows['wd']}*C{s.rows['rd']}*(1-C{s.rows['tax']})",
             fmt=FMT_PCT2, color=BLACK, bold=True, fill=FILL_OUT)
    s.single("wacc_note", "Does WACC equal the cost of equity?", "",
             f"=IF(ABS(C{s.rows['wacc']}-C{s.rows['ke']})<0.0001,"
             f"\"Yes - debt weight is zero, so WACC = cost of equity\","
             f"\"No - the company now carries debt\")", fmt=FMT_TXT, color=BLACK, italic=True)
    s.blank()

    s.section("LEASE TREATMENT - STATED EXPLICITLY (this is a choice, and it must be consistent)")
    s.note("TREATMENT USED IN THIS MODEL: operating leases are an OPERATING EXPENSE.")
    s.note("  1. Occupancy cost stays inside EBIT (it is one of the four restaurant operating "
           "cost lines on the Historicals tab).")
    s.note("  2. Operating lease liabilities are therefore EXCLUDED from net debt in the "
           "Valuation Bridge.")
    s.note("  3. Because rent is never added back, the lease obligation is already captured "
           "in the cash flows being discounted. Deducting it again in the bridge would be "
           "double-counting.")
    s.single("oll", "Operating lease liabilities at FY2025A (EXCLUDED from net debt)", "$mm",
             f"={HN}!G{hr['oll']}", color=GREEN, italic=True,
             source="Shown so the number is visible, not hidden. It is NOT deducted in the bridge.")
    s.note("")
    s.note("THE ALTERNATIVE TREATMENT (know this for interviews): capitalise leases as debt.")
    s.note("  - Add rent expense back to EBIT, so EBIT and EBITDA rise.")
    s.note("  - Add a depreciation charge on the right-of-use asset and treat the interest "
           "component as financing.")
    s.note("  - Add the ~$5.1bn of lease liabilities to debt, which raises net debt and the "
           "debt weight in WACC.")
    s.note("  - Enterprise value rises, but so does the deduction in the bridge. Done "
           "correctly the two treatments should give a similar equity value - the error to "
           "avoid is a hybrid: keeping rent in EBIT AND deducting lease liabilities as debt, "
           "which double-counts and understates equity value by roughly $4/share here.")
    s.blank()

    s.section("MEMO: WHERE CMG TRADES TODAY (used to ground the exit multiple cross-check)")
    s.single("ev_mkt", "Market enterprise value = market cap - cash and investments", "$mm",
             f"=C{s.rows['mcap']}-{HN}!G{hr['cashinv']}", color=GREEN, bold=True,
             source="Leases-as-opex basis, consistent with the rest of this model. Screeners "
                    "that capitalise leases will show a materially higher EV.")
    s.single("ebitda25", "FY2025A EBITDA", "$mm", f"={HN}!G{hr['ebitda']}", color=GREEN)
    s.single("evebitda", "Current EV / LTM EBITDA", "x",
             f"=C{s.rows['ev_mkt']}/C{s.rows['ebitda25']}", fmt=FMT_X, color=BLACK, bold=True,
             fill=FILL_OUT)
    s.finish(freeze="C5", last_col="C")


build_wacc(sW, sHist, sAsm)

# Patch the g < WACC check on the Assumptions tab now that the WACC row is known.
sAsm.ws.cell(sAsm.rows["g_chk"], 3).value = (
    f"=IF($C${sAsm.rows['g']}<WACC!$C${sW.rows['wacc']},\"OK - g is below WACC\","
    f"\"ERROR - g must be below WACC\")")


# ===========================================================================
# TAB: DCF
# ===========================================================================
def build_dcf(s, hist, asm, wsh):
    C = PERIOD_COLS
    hr, ar, wr = hist.rows, asm.rows, wsh.rows
    HN, AN, WN = "Historicals", "Assumptions", "WACC"
    s.header(FCST_YEARS)

    s.section("UNLEVERED FREE CASH FLOW BUILD ($ in millions)")
    s.row("rev", "Revenue", "$mm", [f"={AN}!{c}{ar['rev']}" for c in C], color=GREEN,
          bold=True, source="Link to the Assumptions revenue build (average units x AUV).")
    s.row("rev_g", "Revenue growth (YoY)", "%",
          [f"=C{s.r - 1}/{HN}!G{hr['rev']}-1"] +
          [f"={c}{s.r - 1}/{p}{s.r - 1}-1" for c, p in zip(C[1:], C[:-1])],
          fmt=FMT_PCT, indent=1)
    s.row("ebit_m", "EBIT margin", "% rev", [f"={AN}!{c}{ar['ebit_m']}" for c in C],
          fmt=FMT_PCT, color=GREEN, indent=1)
    s.row("opcost", "Less: operating costs (implied by the margin assumption)", "$mm",
          [f"=-{c}{s.rows['rev']}*(1-{c}{s.rows['ebit_m']})" for c in C],
          source="Chipotle's cost structure is modelled at the EBIT-margin level rather than "
                 "line by line; the Historicals tab shows every cost line as a % of revenue "
                 "so the margin assumption is visibly grounded.")
    s.row("ebit", "EBIT", "$mm",
          [f"={c}{s.rows['rev']}+{c}{s.rows['opcost']}" for c in C], bold=True,
          border=TOPBORDER)
    s.row("tax_r", "Effective tax rate", "%", [f"={AN}!$C${ar['tax']}" for c in C],
          fmt=FMT_PCT, color=GREEN, indent=1)
    s.row("tax", "Less: taxes on EBIT (unlevered)", "$mm",
          [f"=-{c}{s.rows['ebit']}*{c}{s.rows['tax_r']}" for c in C],
          source="Taxed on EBIT, not on pre-tax income - this is an UNLEVERED cash flow, so "
                 "the interest tax shield is excluded (it lives in the WACC).")
    s.row("nopat", "NOPAT", "$mm",
          [f"={c}{s.rows['ebit']}+{c}{s.rows['tax']}" for c in C], bold=True, border=TOPBORDER)
    s.row("da_pct", "D&A as % of revenue", "% rev", [f"={AN}!{c}{ar['da_pct']}" for c in C],
          fmt=FMT_PCT, color=GREEN, indent=1)
    s.row("da", "Plus: depreciation and amortisation", "$mm",
          [f"={c}{s.rows['rev']}*{c}{s.rows['da_pct']}" for c in C],
          source="Non-cash charge added back.")
    s.row("capex_pct", "CapEx as % of revenue", "% rev",
          [f"={AN}!{c}{ar['capex_pct']}" for c in C], fmt=FMT_PCT, color=GREEN, indent=1)
    s.row("capex", "Less: capital expenditures", "$mm",
          [f"=-{c}{s.rows['rev']}*{c}{s.rows['capex_pct']}" for c in C],
          source="New-unit construction plus maintenance and technology capex.")
    s.row("drev", "Memo: change in revenue", "$mm",
          [f"=C{s.rows['rev']}-{HN}!G{hr['rev']}"] +
          [f"={c}{s.rows['rev']}-{p}{s.rows['rev']}" for c, p in zip(C[1:], C[:-1])],
          italic=True, indent=1)
    s.row("nwc_pct", "Change in NWC as % of change in revenue (+ = source)", "%",
          [f"={AN}!$C${ar['nwc_pct']}" for c in C], fmt=FMT_PCT, color=GREEN, indent=1)
    s.row("dnwc", "Plus / (less): change in net working capital", "$mm",
          [f"={c}{s.rows['drev']}*{c}{s.rows['nwc_pct']}" for c in C],
          source="POSITIVE here means working capital RELEASES cash. Chipotle runs negative "
                 "working capital, so growth is a small source of cash, not a use. The sign "
                 "is modelled as it actually behaves rather than assumed to be an outflow.")
    s.row("ufcf", "UNLEVERED FREE CASH FLOW", "$mm",
          [f"={c}{s.rows['nopat']}+{c}{s.rows['da']}+{c}{s.rows['capex']}+{c}{s.rows['dnwc']}"
           for c in C], bold=True, border=DBL, fill=FILL_OUT)
    s.row("ufcf_m", "UFCF margin", "% rev",
          [f"={c}{s.rows['ufcf']}/{c}{s.rows['rev']}" for c in C], fmt=FMT_PCT, indent=1)
    s.row("ebitda", "Memo: EBITDA (EBIT + D&A)", "$mm",
          [f"={c}{s.rows['ebit']}+{c}{s.rows['da']}" for c in C], italic=True, indent=1,
          source="Used by the exit-multiple cross-check on the Terminal Value tab.")
    s.blank()

    s.section("DISCOUNTING - MID-YEAR CONVENTION (an explicit choice, not a default)")
    s.note("Cash flows are assumed to arrive evenly through the year rather than in a lump on "
           "31 December, so each year is discounted from its midpoint: n = 0.5, 1.5, 2.5, 3.5, "
           "4.5. State the convention out loud in an interview - assessors look for it.")
    s.note("Worth knowing the magnitude: mid-year on the explicit cash flows alone is worth only "
           "+0.9% here ($20.12 vs $19.93), NOT the 4-5% usually quoted, because 78% of the value "
           "sits in the terminal value - which is discounted a full five periods either way. "
           "Moving the terminal value to n = 4.5 as well is worth a further +3.4%.")
    s.single("midyr", "Mid-year convention offset", "years", 0.5, fmt=FMT_N, color=BLUE,
             source="Set to 0.0 to switch the whole model to year-end discounting.")
    s.row("n", "Discount period (n)", "years",
          [f"={i}-$C${s.rows['midyr']}" for i in range(1, 6)], fmt=FMT_N)
    s.single("wacc", "WACC", "%", f"=WACC!C{wr['wacc']}", fmt=FMT_PCT2, color=GREEN, bold=True)
    s.row("df", "Discount factor = 1 / (1 + WACC) ^ n", "x",
          [f"=1/(1+$C${s.rows['wacc']})^{c}{s.rows['n']}" for c in C], fmt='0.0000"x"')
    s.row("pv", "Present value of UFCF", "$mm",
          [f"={c}{s.rows['ufcf']}*{c}{s.rows['df']}" for c in C], bold=True,
          border=TOPBORDER)
    s.single("sumpv", "Sum of PV of forecast UFCF (FY2026E-FY2030E)", "$mm",
             f"=SUM(C{s.rows['pv']}:G{s.rows['pv']})", bold=True, color=BLACK, fill=FILL_OUT)
    s.finish(freeze="C5")


build_dcf(sDCF, sHist, sAsm, sW)


# ===========================================================================
# TAB: TERMINAL VALUE
# ===========================================================================
def build_tv(s, hist, asm, wsh, dcf):
    hr, ar, wr, dr = hist.rows, asm.rows, wsh.rows, dcf.rows
    AN, WN, DN = "Assumptions", "WACC", "DCF"
    s.ws.column_dimensions["C"].width = 16
    s.ws.column_dimensions["D"].width = 16

    s.section("INPUTS CARRIED IN")
    s.single("wacc", "WACC", "%", f"={WN}!C{wr['wacc']}", fmt=FMT_PCT2, color=GREEN, bold=True)
    s.single("g", "Terminal growth rate (g)", "%", f"={AN}!C{ar['g']}", fmt=FMT_PCT2,
             color=GREEN, bold=True)
    s.single("spread", "Spread (WACC - g)", "%",
             f"=C{s.rows['wacc']}-C{s.rows['g']}", fmt=FMT_PCT2, color=BLACK,
             source="If this is not comfortably positive the Gordon Growth formula is meaningless.")
    s.single("rev5", "FY2030E revenue", "$mm", f"={DN}!G{dr['rev']}", color=GREEN)
    s.single("nopat5", "FY2030E NOPAT", "$mm", f"={DN}!G{dr['nopat']}", color=GREEN)
    s.single("da5", "FY2030E D&A", "$mm", f"={DN}!G{dr['da']}", color=GREEN)
    s.single("capex5", "FY2030E capital expenditures", "$mm", f"={DN}!G{dr['capex']}",
             color=GREEN, source="Negative, as presented on the DCF tab.")
    s.single("nwc5", "FY2030E change in net working capital", "$mm", f"={DN}!G{dr['dnwc']}",
             color=GREEN)
    s.single("ufcf5", "FY2030E unlevered free cash flow (as forecast)", "$mm",
             f"={DN}!G{dr['ufcf']}", color=GREEN, bold=True)
    s.single("ebitda5", "FY2030E EBITDA", "$mm", f"={DN}!G{dr['ebitda']}", color=GREEN)
    s.blank()

    s.section("TERMINAL-YEAR NORMALISATION (why the raw year-5 cash flow cannot be used)")
    s.note("FY2030E capex is 5.6% of revenue because the company is still opening ~370 "
           "restaurants a year. A perpetuity growing at 2.25% cannot also be spending at a "
           "7%-unit-growth rate. Capex is therefore normalised to maintenance (= D&A) plus "
           "the growth capital needed to sustain 2.25% growth. Without this the terminal "
           "value is understated. Both versions are shown below.")
    s.single("ncap_pct", "Normalised terminal capex as % of revenue", "% rev",
             A.TERMINAL_CAPEX_PCT_OF_REVENUE, fmt=FMT_PCT, color=BLUE,
             source=A.TERMINAL_CAPEX_PCT_OF_REVENUE_SOURCE)
    s.single("ncap", "Normalised terminal capex", "$mm",
             f"=-C{s.rows['rev5']}*C{s.rows['ncap_pct']}", color=BLACK)
    s.single("nufcf", "NORMALISED TERMINAL UFCF", "$mm",
             f"=C{s.rows['nopat5']}+C{s.rows['da5']}+C{s.rows['ncap']}+C{s.rows['nwc5']}",
             bold=True, color=BLACK, fill=FILL_OUT, border=TOPBORDER,
             source="NOPAT + D&A - normalised capex +/- change in NWC. This is the cash flow "
                    "the Gordon Growth formula is applied to.")
    s.blank()

    s.section("METHOD 1 (PRIMARY): GORDON GROWTH  -  TV = FCF x (1 + g) / (WACC - g)")
    s.single("tv_gg", "Terminal value (Gordon Growth, normalised FCF)", "$mm",
             f"=C{s.rows['nufcf']}*(1+C{s.rows['g']})/(C{s.rows['wacc']}-C{s.rows['g']})",
             bold=True, color=BLACK, fill=FILL_OUT)
    s.single("tv_gg_raw", "Memo: same formula on the UNadjusted FY2030E UFCF", "$mm",
             f"=C{s.rows['ufcf5']}*(1+C{s.rows['g']})/(C{s.rows['wacc']}-C{s.rows['g']})",
             color=BLACK, italic=True,
             source="Shown for transparency. Lower, because it perpetuates growth-stage capex.")
    s.blank()

    s.section("METHOD 2 (CROSS-CHECK): EXIT MULTIPLE  -  TV = FY2030E EBITDA x exit EV/EBITDA")
    s.single("exitx", "Exit EV / EBITDA multiple", "x", A.EXIT_EBITDA_MULTIPLE, fmt=FMT_X,
             color=BLUE, source=A.EXIT_EBITDA_MULTIPLE_SOURCE)
    s.single("cur_x", "Memo: CMG's current EV / LTM EBITDA", "x", f"={WN}!C{wr['evebitda']}",
             fmt=FMT_X, color=GREEN, italic=True,
             source="Computed on the WACC tab from the current market cap and FY2025A EBITDA, "
                    "leases-as-opex basis.")
    s.single("tv_exit", "Terminal value (exit multiple)", "$mm",
             f"=C{s.rows['ebitda5']}*C{s.rows['exitx']}", bold=True, color=BLACK)
    s.blank()

    s.section("THE TWO CROSS-CHECKS THAT MATTER")
    s.single("impx", "Implied exit EV/EBITDA from the Gordon Growth TV", "x",
             f"=C{s.rows['tv_gg']}/C{s.rows['ebitda5']}", fmt=FMT_X, bold=True, color=BLACK,
             source="Gordon Growth terminal value divided by FY2030E EBITDA.")
    s.single("impx_flag", "  Flag", "",
             f"=IF(C{s.rows['impx']}<10,\"FLAG - below 10x. A GDP-anchored perpetuity implies a "
             f"far lower exit multiple than CMG's current \"&TEXT(C{s.rows['cur_x']},\"0.0\")&"
             f"\"x. Either the market is embedding growth well above GDP, or this WACC is too "
             f"high.\",IF(C{s.rows['impx']}>25,\"FLAG - above 25x, implausibly rich for a "
             f"terminal multiple.\",\"Reasonable - within the 10x-25x range for a mature "
             f"restaurant operator.\"))", fmt=FMT_TXT, color=BLACK, italic=True)
    s.single("impg", "Implied perpetuity growth from the exit-multiple TV", "%",
             f"=(C{s.rows['tv_exit']}*C{s.rows['wacc']}-C{s.rows['nufcf']})/"
             f"(C{s.rows['tv_exit']}+C{s.rows['nufcf']})", fmt=FMT_PCT2, bold=True,
             color=BLACK,
             source="Solves TV = FCF x (1+g) / (WACC - g) for g, holding the normalised "
                    "terminal FCF constant.")
    s.single("impg_flag", "  Flag", "",
             f"=IF(C{s.rows['impg']}>0.03,\"FLAG - implies perpetual growth above ~3% nominal "
             f"GDP, which is not sustainable. The exit multiple is doing the work, not the "
             f"fundamentals.\",IF(C{s.rows['impg']}<0,\"FLAG - implies perpetual decline.\","
             f"\"Reasonable - consistent with long-run nominal GDP.\"))", fmt=FMT_TXT,
             color=BLACK, italic=True)
    s.note("Interpretation: when these two checks disagree sharply, that IS the finding. The "
           "Gordon Growth answer says what the business is worth on GDP-anchored fundamentals; "
           "the exit multiple says what the market is currently willing to pay. The gap is the "
           "growth premium embedded in the share price.")
    s.blank()

    s.section("DISCOUNTING THE TERMINAL VALUE TO PRESENT VALUE")
    s.single("tvn", "Terminal value discount period (n)", "years", A.TV_DISCOUNT_PERIOD,
             fmt=FMT_N, color=BLUE, source=A.TV_DISCOUNT_PERIOD_SOURCE)
    s.single("tvdf", "Discount factor = 1 / (1 + WACC) ^ n", "x",
             f"=1/(1+C{s.rows['wacc']})^C{s.rows['tvn']}", fmt='0.0000"x"', color=BLACK)
    s.single("pv_tv", "PRESENT VALUE OF TERMINAL VALUE", "$mm",
             f"=C{s.rows['tv_gg']}*C{s.rows['tvdf']}", bold=True, color=BLACK, fill=FILL_OUT,
             border=TOPBORDER)
    s.single("pv_tv_exit", "Memo: PV of the exit-multiple terminal value", "$mm",
             f"=C{s.rows['tv_exit']}*C{s.rows['tvdf']}", color=BLACK, italic=True)
    s.blank()

    s.section("HOW MUCH OF THE VALUE IS TERMINAL?")
    s.single("sumpv", "Sum of PV of forecast UFCF", "$mm", f"={DN}!C{dr['sumpv']}", color=GREEN)
    s.single("ev", "Enterprise value", "$mm",
             f"=C{s.rows['sumpv']}+C{s.rows['pv_tv']}", bold=True, color=BLACK)
    s.single("tv_pct", "Terminal value as % of enterprise value", "%",
             f"=C{s.rows['pv_tv']}/C{s.rows['ev']}", fmt=FMT_PCT, bold=True, color=BLACK,
             fill=FILL_OUT)
    s.single("tv_pct_flag", "  Flag", "",
             f"=IF(C{s.rows['tv_pct']}>0.75,\"FLAG - above 75%. Most of the value sits beyond "
             f"the forecast window, so the answer is driven by WACC and g rather than by the "
             f"five years of cash flow. Normal for a growth company; disclosed as a model "
             f"limitation in the README.\",\"Below 75% - the explicit forecast carries most of "
             f"the value.\")", fmt=FMT_TXT, color=BLACK, italic=True)
    s.finish(freeze="C5", last_col="D")


build_tv(sTV, sHist, sAsm, sW, sDCF)


# ===========================================================================
# TAB: VALUATION BRIDGE
# ===========================================================================
def build_bridge(s, hist, wsh, dcf, tv):
    hr, wr, dr, tr = hist.rows, wsh.rows, dcf.rows, tv.rows
    HN, WN, DN, TN = "Historicals", "WACC", "DCF", "'Terminal Value'"
    s.ws.column_dimensions["C"].width = 18

    s.section("ENTERPRISE VALUE TO IMPLIED SHARE PRICE ($ in millions, except per-share)")
    s.single("sumpv", "Sum of PV of forecast UFCF (FY2026E-FY2030E)", "$mm",
             f"={DN}!C{dr['sumpv']}", color=GREEN)
    s.single("pvtv", "Plus: PV of terminal value", "$mm", f"={TN}!C{tr['pv_tv']}", color=GREEN)
    s.single("ev", "ENTERPRISE VALUE", "$mm",
             f"=C{s.rows['sumpv']}+C{s.rows['pvtv']}", bold=True, color=BLACK,
             border=TOPBORDER, fill=FILL_OUT)
    s.single("debt", "Less: total debt", "$mm", f"=-{HN}!G{hr['debt']}", color=GREEN,
             source="Zero. Chipotle's only facility is a $500m undrawn revolver (FY2025 10-K "
                    "Note 12).")
    s.single("cash", "Plus: cash and investments", "$mm", f"={HN}!G{hr['cashinv']}",
             color=GREEN,
             source="Cash and cash equivalents + short-term investments + long-term "
                    "investments at 12/31/2025. Excludes $35.4m of restricted cash.")
    s.single("lease_note", "Operating lease liabilities are NOT deducted", "",
             "Leases are treated as an operating expense, so occupancy cost is already "
             "inside EBIT. See the WACC tab.", fmt=FMT_TXT, color=BLACK, italic=True)
    s.single("eqv", "EQUITY VALUE", "$mm",
             f"=C{s.rows['ev']}+C{s.rows['debt']}+C{s.rows['cash']}", bold=True, color=BLACK,
             border=TOPBORDER, fill=FILL_OUT)
    s.single("sh", "Diluted shares outstanding", "mm", f"={WN}!C{wr['sh_dil']}", fmt=FMT_CNT,
             color=GREEN)
    s.single("px_imp", "IMPLIED SHARE PRICE", "$",
             f"=C{s.rows['eqv']}/C{s.rows['sh']}", fmt=FMT_PRICE, bold=True, color=BLACK,
             border=DBL, fill=FILL_OUT)
    s.blank()

    s.section("VERSUS THE MARKET")
    s.single("px_mkt", "Current market price", "$", f"={WN}!C{wr['px']}", fmt=FMT_PRICE,
             color=GREEN, source=A.CURRENT_SHARE_PRICE_SOURCE)
    s.single("updown", "Implied upside / (downside)", "%",
             f"=C{s.rows['px_imp']}/C{s.rows['px_mkt']}-1", fmt=FMT_PCT, bold=True,
             color=BLACK, fill=FILL_OUT)
    s.single("verdict", "Conclusion", "",
             f"=IF(C{s.rows['updown']}>0.15,\"UNDERVALUED on these assumptions\","
             f"IF(C{s.rows['updown']}<-0.15,\"OVERVALUED on these assumptions\","
             f"\"FAIRLY VALUED - within +/-15%\"))", fmt=FMT_TXT, color=BLACK, bold=True)
    s.blank()

    s.section("SANITY CHECKS - does the answer make sense?")
    s.single("ev_ebitda25", "Implied EV / FY2025A EBITDA", "x",
             f"=C{s.rows['ev']}/{HN}!G{hr['ebitda']}", fmt=FMT_X, color=GREEN)
    s.single("ev_ebitda30", "Implied EV / FY2030E EBITDA", "x",
             f"=C{s.rows['ev']}/{DN}!G{dr['ebitda']}", fmt=FMT_X, color=GREEN)
    s.single("ev_mkt", "Memo: EV the market is currently paying", "$mm",
             f"={WN}!C{wr['ev_mkt']}", color=GREEN)
    s.single("cur_x", "Memo: current EV / LTM EBITDA", "x", f"={WN}!C{wr['evebitda']}",
             fmt=FMT_X, color=GREEN)
    s.single("gap", "Gap: implied EV vs. market EV", "$mm",
             f"=C{s.rows['ev']}-C{s.rows['ev_mkt']}", color=BLACK,
             source="Negative means the market is paying more than this DCF supports. That gap "
                    "is the thing to be able to explain in an interview.")
    s.finish(freeze="C5", last_col="C")


build_bridge(sBr, sHist, sW, sDCF, sTV)


# ===========================================================================
# TAB: SENSITIVITY
# ===========================================================================
def build_sensitivity(s, hist, asm, wsh, dcf, tv, bridge):
    hr, ar, wr, dr, tr, br = (hist.rows, asm.rows, wsh.rows, dcf.rows, tv.rows, bridge.rows)
    HN, AN, WN, DN, TN, BN = ("Historicals", "Assumptions", "WACC", "DCF",
                              "'Terminal Value'", "'Valuation Bridge'")
    ws = s.ws
    ws.column_dimensions["A"].width = 34
    ws.column_dimensions["B"].width = 11
    for i in range(3, 12):
        ws.column_dimensions[get_column_letter(i)].width = 11

    base_wacc = W.cost_of_equity()
    waccs = [round(base_wacc + d / 10000.0, 6) for d in range(-150, 151, 25)]
    growths = [0.015, 0.0175, 0.020, 0.0225, 0.025, 0.0275, 0.030]
    margins = [0.133, 0.148, 0.163, 0.178, 0.193]

    debt_ref = f"{HN}!$G${hr['debt']}"
    cash_ref = f"{HN}!$G${hr['cashinv']}"
    sh_ref = f"{WN}!$C${wr['sh_dil']}"
    tvn_ref = f"{TN}!$C${tr['tvn']}"

    def pv_ufcf_terms(w, upto=5):
        return "+".join(
            f"{DN}!${c}${dr['ufcf']}/(1+{w})^{DN}!${c}${dr['n']}"
            for c in PERIOD_COLS[:upto])

    r = 4
    ws.cell(r, 1, "TABLE A  -  WACC (rows) x TERMINAL GROWTH (columns)").font = Font(bold=True, size=11)
    r += 1
    ws.cell(r, 1, "Implied share price, $. Each cell re-discounts the five forecast UFCFs and "
                  "rebuilds the terminal value at that WACC / g pair.").font = Font(size=8, italic=True, color=GREY)
    r += 2
    hdr_a = r
    hc = ws.cell(r, 2, "WACC \\ g")
    hc.font = Font(bold=True, size=9)
    hc.fill = FILL_HDR
    hc.alignment = Alignment(horizontal="center")
    for j, g in enumerate(growths):
        c = ws.cell(r, 3 + j, g)
        c.number_format = FMT_PCT2
        c.font = Font(bold=True, size=9, color=BLUE)
        c.fill = FILL_HDR
        c.alignment = Alignment(horizontal="center")
    r += 1
    first_a = r
    for w in waccs:
        rc = ws.cell(r, 2, w)
        rc.number_format = FMT_PCT2
        rc.font = Font(bold=True, size=9, color=BLUE)
        rc.fill = FILL_HDR
        for j, g in enumerate(growths):
            wref = f"$B{r}"
            gref = f"{get_column_letter(3 + j)}${hdr_a}"
            tv_term = (f"{TN}!$C${tr['nufcf']}*(1+{gref})/({wref}-{gref})"
                       f"/(1+{wref})^{tvn_ref}")
            f = (f"=IF({wref}<={gref}+0.005,NA(),(({pv_ufcf_terms(wref)})"
                 f"+{tv_term}-{debt_ref}+{cash_ref})/{sh_ref})")
            c = ws.cell(r, 3 + j, f)
            c.number_format = FMT_PRICE
            c.font = Font(size=9)
            c.border = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
            if abs(w - base_wacc) < 1e-9 and abs(g - A.TERMINAL_GROWTH) < 1e-9:
                c.fill = FILL_BASE
                c.font = Font(size=9, bold=True)
                c.border = Border(left=Side(style="medium"), right=Side(style="medium"),
                                  top=Side(style="medium"), bottom=Side(style="medium"))
        r += 1
    last_a = r - 1
    ws.conditional_formatting.add(
        f"C{first_a}:{get_column_letter(2 + len(growths))}{last_a}",
        ColorScaleRule(start_type="min", start_color="FFF8696B",
                       mid_type="percentile", mid_value=50, mid_color="FFFFEB84",
                       end_type="max", end_color="FF63BE7B"))
    ws.cell(r, 1, "Base case is the shaded cell. Rows step 0.25% around the base WACC; "
                  "columns step 0.25% of terminal growth.").font = Font(size=8, italic=True, color=GREY)
    r += 3

    ws.cell(r, 1, "TABLE B  -  WACC (rows) x TERMINAL EBIT MARGIN (columns)").font = Font(bold=True, size=11)
    r += 1
    ws.cell(r, 1, "The terminal EBIT margin changes FY2030E EBIT, hence the year-5 cash flow "
                  "AND the normalised terminal cash flow. Terminal growth is held at the base "
                  "case.").font = Font(size=8, italic=True, color=GREY)
    r += 2
    hdr_b = r
    hc = ws.cell(r, 2, "WACC \\ margin")
    hc.font = Font(bold=True, size=9)
    hc.fill = FILL_HDR
    hc.alignment = Alignment(horizontal="center")
    for j, m in enumerate(margins):
        c = ws.cell(r, 3 + j, m)
        c.number_format = FMT_PCT
        c.font = Font(bold=True, size=9, color=BLUE)
        c.fill = FILL_HDR
        c.alignment = Alignment(horizontal="center")
    r += 1
    first_b = r
    g_ref = f"{AN}!$C${ar['g']}"
    rev5 = f"{DN}!$G${dr['rev']}"
    tax_ref = f"{AN}!$C${ar['tax']}"
    da5 = f"{DN}!$G${dr['da']}"
    cap5 = f"{DN}!$G${dr['capex']}"
    nwc5 = f"{DN}!$G${dr['dnwc']}"
    ncap_pct = f"{TN}!$C${tr['ncap_pct']}"

    for w in waccs:
        rc = ws.cell(r, 2, w)
        rc.number_format = FMT_PCT2
        rc.font = Font(bold=True, size=9, color=BLUE)
        rc.fill = FILL_HDR
        for j, m in enumerate(margins):
            wref = f"$B{r}"
            mref = f"{get_column_letter(3 + j)}${hdr_b}"
            nopat5 = f"({rev5}*{mref}*(1-{tax_ref}))"
            ufcf5 = f"({nopat5}+{da5}+{cap5}+{nwc5})"
            tvfcf = f"({nopat5}+{da5}-{rev5}*{ncap_pct}+{nwc5})"
            pv14 = pv_ufcf_terms(wref, upto=4)
            pv5 = f"{ufcf5}/(1+{wref})^{DN}!$G${dr['n']}"
            tv_term = f"{tvfcf}*(1+{g_ref})/({wref}-{g_ref})/(1+{wref})^{tvn_ref}"
            f = (f"=IF({wref}<={g_ref}+0.005,NA(),(({pv14})+{pv5}+{tv_term}"
                 f"-{debt_ref}+{cash_ref})/{sh_ref})")
            c = ws.cell(r, 3 + j, f)
            c.number_format = FMT_PRICE
            c.font = Font(size=9)
            c.border = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
            if abs(w - base_wacc) < 1e-9 and abs(m - A.EBIT_MARGIN[2030]) < 1e-9:
                c.fill = FILL_BASE
                c.font = Font(size=9, bold=True)
                c.border = Border(left=Side(style="medium"), right=Side(style="medium"),
                                  top=Side(style="medium"), bottom=Side(style="medium"))
        r += 1
    last_b = r - 1
    ws.conditional_formatting.add(
        f"C{first_b}:{get_column_letter(2 + len(margins))}{last_b}",
        ColorScaleRule(start_type="min", start_color="FFF8696B",
                       mid_type="percentile", mid_value=50, mid_color="FFFFEB84",
                       end_type="max", end_color="FF63BE7B"))
    ws.cell(r, 1, "Base case (16.3% terminal margin) is the shaded cell. Margin columns step "
                  "150bps.").font = Font(size=8, italic=True, color=GREY)
    r += 2
    ws.cell(r, 1, "Reading these tables: the vertical spread (WACC) is wider than the "
                  "horizontal spread in Table A, which tells you the answer is more sensitive "
                  "to the discount rate than to terminal growth.").font = Font(size=8, italic=True, color=GREY)

    s.r = r + 2
    s.finish(freeze="C1", last_col="I")


build_sensitivity(sSen, sHist, sAsm, sW, sDCF, sTV, sBr)


# ===========================================================================
# TAB: SUMMARY  (populated last, sits first)
# ===========================================================================
def build_summary(s, hist, asm, wsh, dcf, tv, bridge):
    hr, ar, wr, dr, tr, br = (hist.rows, asm.rows, wsh.rows, dcf.rows, tv.rows, bridge.rows)
    HN, AN, WN, DN, TN, BN = ("Historicals", "Assumptions", "WACC", "DCF",
                              "'Terminal Value'", "'Valuation Bridge'")
    s.ws.column_dimensions["C"].width = 20
    s.ws.column_dimensions["I"].width = 60

    s.section("VALUATION CONCLUSION")
    s.single("px_imp", "Implied share price (DCF)", "$", f"={BN}!C{br['px_imp']}",
             fmt=FMT_PRICE, color=GREEN, bold=True, fill=FILL_OUT)
    s.single("px_mkt", "Current market price", "$", f"={BN}!C{br['px_mkt']}", fmt=FMT_PRICE,
             color=GREEN, bold=True, source=A.CURRENT_SHARE_PRICE_SOURCE)
    s.single("updown", "Implied upside / (downside)", "%", f"={BN}!C{br['updown']}",
             fmt=FMT_PCT, color=GREEN, bold=True, fill=FILL_OUT)
    s.single("ev", "Implied enterprise value", "$mm", f"={BN}!C{br['ev']}", color=GREEN, bold=True)
    s.single("eqv", "Implied equity value", "$mm", f"={BN}!C{br['eqv']}", color=GREEN, bold=True)
    s.single("verdict", "Verdict", "", f"={BN}!C{br['verdict']}", fmt=FMT_TXT, color=GREEN,
             bold=True)
    s.blank()

    s.section("KEY ASSUMPTIONS")
    s.single("cagr", "Revenue CAGR, FY2025A-FY2030E", "%", f"={AN}!G{ar['rev_cagr']}",
             fmt=FMT_PCT, color=GREEN,
             source="Driven by unit growth of ~7%/yr plus low-single-digit AUV growth.")
    s.single("units30", "Restaurants at FY2030E", "#", f"={AN}!G{ar['u_end']}", fmt=FMT_CNT,
             color=GREEN, source="From 4,042 at FY2025A. Long-term company goal is 7,000 in "
                                 "the U.S. and Canada.")
    s.single("m26", "EBIT margin, FY2026E (trough)", "%", f"={AN}!C{ar['ebit_m']}",
             fmt=FMT_PCT, color=GREEN)
    s.single("m30", "Terminal EBIT margin, FY2030E", "%", f"={AN}!G{ar['ebit_m']}",
             fmt=FMT_PCT, color=GREEN,
             source="Recovers to the FY2025A level; still below the FY2024A peak of 16.9%.")
    s.single("tax", "Effective tax rate", "%", f"={AN}!C{ar['tax']}", fmt=FMT_PCT, color=GREEN)
    s.single("wacc", "WACC", "%", f"={WN}!C{wr['wacc']}", fmt=FMT_PCT2, color=GREEN, bold=True,
             source="Equals the cost of equity - Chipotle has no debt.")
    s.single("g", "Terminal growth rate", "%", f"={AN}!C{ar['g']}", fmt=FMT_PCT2, color=GREEN,
             bold=True)
    s.single("tvpct", "Terminal value as % of enterprise value", "%", f"={TN}!C{tr['tv_pct']}",
             fmt=FMT_PCT, color=GREEN)
    s.single("impx", "Implied exit EV/EBITDA (from the Gordon Growth TV)", "x",
             f"={TN}!C{tr['impx']}", fmt=FMT_X, color=GREEN)
    s.single("curx", "CMG's current EV / LTM EBITDA", "x", f"={WN}!C{wr['evebitda']}",
             fmt=FMT_X, color=GREEN)
    s.blank()

    s.section("VALUATION CONCLUSION - THREE SENTENCES")
    s.single("s1", "1.", "",
             f"=\"On a units-times-AUV revenue build reaching \"&TEXT(C{s.rows['units30']},\"#,##0\")&"
             f"\" restaurants by FY2030E, an EBIT margin that troughs at \"&"
             f"TEXT(C{s.rows['m26']},\"0.0%\")&\" in FY2026E before recovering to \"&"
             f"TEXT(C{s.rows['m30']},\"0.0%\")&\", a \"&TEXT(C{s.rows['wacc']},\"0.00%\")&"
             f"\" WACC and \"&TEXT(C{s.rows['g']},\"0.00%\")&\" terminal growth, the model "
             f"produces an implied value of \"&TEXT(C{s.rows['px_imp']},\"$#,##0.00\")&"
             f"\" per share against a market price of \"&TEXT(C{s.rows['px_mkt']},\"$#,##0.00\")&"
             f"\", or \"&TEXT(C{s.rows['updown']},\"0.0%\")&\".\"",
             fmt=FMT_TXT, color=GREEN)
    s.single("s2", "2.", "",
             f"=\"The gap is not an arithmetic error: it is the growth premium in the share "
             f"price. The Gordon Growth terminal value implies an exit multiple of only \"&"
             f"TEXT(C{s.rows['impx']},\"0.0\")&\"x EBITDA against the \"&"
             f"TEXT(C{s.rows['curx']},\"0.0\")&\"x CMG trades at today, so the market is "
             f"embedding either a materially lower discount rate or long-run growth well "
             f"above nominal GDP.\"",
             fmt=FMT_TXT, color=GREEN)
    s.single("s3", "3.", "",
             f"=\"With \"&TEXT(C{s.rows['tvpct']},\"0%\")&\" of enterprise value sitting in "
             f"the terminal value, the conclusion is a statement about the discount rate and "
             f"terminal assumptions rather than about the five forecast years - which is why "
             f"the Sensitivity tab, not the base case, is the real output of this model.\"",
             fmt=FMT_TXT, color=GREEN)
    s.blank()

    s.section("HOW TO READ THIS WORKBOOK")
    s.note("Font convention:  BLUE = hardcoded input   BLACK = formula on this sheet   "
           "GREEN = link to another sheet.")
    s.note("Tab colours:  BLUE tabs are inputs (Historicals, Assumptions).  "
           "ORANGE tabs are calculations (WACC, DCF, Terminal Value).  "
           "GREEN tabs are outputs (Summary, Valuation Bridge, Sensitivity).")
    s.note("Every input cell carries a source note in column I. No number in this workbook is "
           "unsourced.")
    s.note("Trace any figure by clicking it and pressing Ctrl+[ (Windows) or Ctrl+Alt+[ (Mac) "
           "to jump to its precedents.")
    s.finish(freeze="C5", last_col="C")


build_summary(sSum, sHist, sAsm, sW, sDCF, sTV, sBr)

os.makedirs(os.path.dirname(OUT_XLSX), exist_ok=True)
wb.save(OUT_XLSX)
print(f"Wrote {OUT_XLSX}")
print(f"Sheets: {wb.sheetnames}")
