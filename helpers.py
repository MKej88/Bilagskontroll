# -*- coding: utf-8 -*-
import os
import re
import sys
import logging

logger = logging.getLogger("bilagskontroll")
if not logger.handlers:
    handler = logging.FileHandler("bilagskontroll.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

def _pd():
    import pandas as pd
    return pd

# Forhåndskompiler regex som brukes hyppig
_RE_DIGITS = re.compile(r"\D+")
_RE_FLOAT_SUFFIX = re.compile(r"\d+\.0")
_RE_NUMBER = re.compile(r"-?\d+(?:[.,]\d+)?")
_INVOICE_PATS = [
    re.compile(r"^faktura\.?nr\.?$"),
    re.compile(r"^fakturanr\.?$"),
    re.compile(r"^faktura[ \._-]*nummer$"),
    re.compile(r"^invoice.*(no|number)$"),
]


def resource_path(relpath: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relpath)


def to_str(v):
    pd = _pd()
    if pd.isna(v):
        return ""
    if isinstance(v, pd.Timestamp):
        return v.strftime("%Y-%m-%d")
    s = str(v).strip()
    if _RE_FLOAT_SUFFIX.fullmatch(s):
        return s[:-2]
    return s


def only_digits(s: str) -> str:
    return _RE_DIGITS.sub("", to_str(s))


def parse_amount(x):
    s = to_str(x).replace(" ", "").replace("\xa0", "")
    if not s or s.lower() == "nan":
        return None
    s = s.replace(",", ".")
    if s.endswith("-") and s[:-1].replace(".", "", 1).isdigit():
        s = "-" + s[:-1]
    try:
        return float(s)
    except Exception:
        return None


def fmt_money(x):
    v = parse_amount(x)
    if v is None:
        return ""
    return f"{v:,.2f}".replace(",", " ").replace(".", ",")


def format_number_with_thousands(s):
    if s is None:
        return ""
    s = str(s).strip()
    if not s:
        return ""
    core = s.replace(" ", "").replace("\xa0", "")
    m = _RE_NUMBER.fullmatch(core)
    if not m:
        return s
    if "," in core and "." in core:
        return s
    dec = None
    if "," in core:
        intp, dec = core.split(",", 1)
    elif "." in core:
        intp, dec = core.split(".", 1)
    else:
        intp = core
    try:
        intp = int(intp)
    except Exception:
        return s
    int_fmt = f"{intp:,}".replace(",", " ")
    return f"{int_fmt},{dec}" if dec is not None else int_fmt


def guess_invoice_col(cols):
    for c in map(str, cols):
        lc = c.lower().strip()
        if any(p.search(lc) for p in _INVOICE_PATS):
            return c
    return cols[1] if len(cols) > 1 else cols[0]


def guess_col(cols, *names_regex):
    for c in map(str, cols):
        lc = c.lower().strip()
        if any(re.search(rgx, lc, re.IGNORECASE) for rgx in names_regex):
            return c
    return None


def guess_net_amount_col(cols):
    pats = [
        r"nettobel(ø|o)p",
        r"netto.*bel(ø|o)p",
        r"bel(ø|o)p\s*eks",
        r"^netto$",
        r"^bel(ø|o)p$",
        r"^sum$",
        r"total",
    ]
    return guess_col(cols, *pats)


def fmt_pct(n):
    try:
        return f"{n:.1f}%"
    except Exception:
        return ""
