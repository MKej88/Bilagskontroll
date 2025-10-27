from __future__ import annotations

import re
from decimal import Decimal
from typing import List

from helpers import fmt_money, only_digits, parse_amount, to_str

LEDGER_COLS: List[str] = [
    "Kontonr",
    "Konto",
    "Beskrivelse",
    "MVA",
    "MVA-beløp",
    "Beløp",
    "Postert av",
]


def ledger_rows(app, invoice_value: str):
    """Hent bilagslinjer for gitt bilagsnummer uten å endre ``gl_df``."""

    if app.gl_df is None or not hasattr(app, "gl_index"):
        return []

    key = only_digits(invoice_value)
    if not key:
        return []

    idxs = app.gl_index.get(key)
    if idxs is None or len(idxs) == 0:
        return []

    hits = app.gl_df.loc[idxs]
    rows = []
    for _, r in hits.iterrows():
        konto_nr = to_str(r.get(app.gl_accountno_col, ""))
        if not konto_nr:
            cand = to_str(r.get(app.gl_accountname_col, ""))
            m = re.match(r"^\s*(\d{3,6})\b", cand)
            if m:
                konto_nr = m.group(1)
        konto_navn = to_str(r.get(app.gl_accountname_col, ""))
        if not konto_navn:
            combo = to_str(r.get(app.gl_accountno_col, ""))
            m = re.match(r"^\s*(\d{3,6})\s*[-–:]?\s*(.+)$", combo)
            if m:
                if not konto_nr:
                    konto_nr = m.group(1)
                konto_navn = m.group(2)
        beskr = to_str(r.get(app.gl_desc_col, "")) or to_str(r.get(app.gl_text_col, ""))
        mva_code = to_str(r.get(app.gl_vatcode_col, ""))
        mva_belop = fmt_money(r.get(app.gl_vatamount_col, ""))
        deb = parse_amount(r.get(app.gl_debit_col)) if app.gl_debit_col else None
        kre = parse_amount(r.get(app.gl_credit_col)) if app.gl_credit_col else None
        belop = parse_amount(r.get(app.gl_amount_col)) if app.gl_amount_col else None
        if belop is None and (deb is not None or kre is not None):
            belop = (
                (deb if deb is not None else Decimal("0"))
                - (kre if kre is not None else Decimal("0"))
            )
        belop_str = fmt_money(belop)
        postert_av = to_str(r.get(app.gl_postedby_col, ""))
        rows.append(
            {
                "Kontonr": konto_nr,
                "Konto": konto_navn,
                "Beskrivelse": beskr,
                "MVA": mva_code,
                "MVA-beløp": mva_belop,
                "Beløp": belop_str,
                "Postert av": postert_av,
            }
        )
    return rows

