"""Shared constants and small helper functions used by every part of the app."""
import os
from datetime import datetime
from decimal import Decimal

ZERO = Decimal("0")
import sys
if getattr(sys, "frozen", False):   # running as a packaged .exe
    APP_DIR = os.path.join(os.path.expanduser("~"), "AccountingApp")
    os.makedirs(APP_DIR, exist_ok=True)
else:                               # running as a .py script
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(APP_DIR, "accounting_data.json")

# Account type decides which statement columns an account lands in.
ASSET, LIAB, CAP, DRAW, REV, EXP = "Asset", "Liability", "Owner's Capital", "Owner's Drawings", "Revenue", "Expense"
TYPES = [ASSET, LIAB, CAP, DRAW, REV, EXP]
SECTION = {ASSET: "BS", LIAB: "BS", CAP: "OE", DRAW: "OE", REV: "IS", EXP: "IS"}
SECTION_COL = {"IS": 6, "OE": 8, "BS": 10}  # index of the Dr column of each statement

CHART = [  # the dropdown list (from the account-name sheet)
    ("Cash", ASSET), ("Accounts Receivable", ASSET), ("Supplies", ASSET),
    ("Prepaid Insurance", ASSET), ("Prepaid Rent", ASSET), ("Equipment", ASSET),
    ("Accumulated Depreciation Equipment", ASSET), ("Furniture", ASSET), ("Vehicles", ASSET),
    ("Accounts Payable", LIAB), ("Unearned Revenue", LIAB), ("Notes Payable", LIAB),
    ("Salaries Payable", LIAB), ("Owner's Capital", CAP), ("Owner's Drawings", DRAW),
    ("Service Revenue", REV), ("Advertising Expense", EXP), ("Utilities Expense", EXP),
    ("Salaries Expense", EXP), ("Maintenance Expense", EXP), ("Professional Fees Expense", EXP),
    ("Repairs Expense", EXP), ("Rent Expense", EXP), ("Interest Expense", EXP),
    ("Insurance Expense", EXP), ("Supplies Expense", EXP), ("Depreciation Expense", EXP),
]
HEADS = [f"{p} {s}" for p in ("TB", "ADJ", "ATB", "IS", "OE", "BS") for s in ("Dr", "Cr")]


def fmt(v):
    """Whole numbers without decimals; blank for zero/None."""
    if v is None or v == 0:
        return ""
    return f"{v:,.0f}" if v == v.to_integral_value() else f"{v:,.2f}"


def balfmt(b):
    return "0" if b == 0 else f"{fmt(abs(b))} {'Dr' if b > 0 else 'Cr'}"


def date_to_display(iso_date):
    """Convert ISO date (2026-11-04) to display format (Nov 04, 2026)."""
    try:
        dt = datetime.strptime(iso_date, "%Y-%m-%d")
        return dt.strftime("%b %d, %Y")
    except (ValueError, TypeError):
        return iso_date  # Return as-is if invalid