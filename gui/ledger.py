from __future__ import annotations

from decimal import Decimal
from typing import List

from PyQt5 import QtCore, QtGui, QtWidgets

from helpers import fmt_money, only_digits, parse_amount, to_str
from .style import style, PADDING_X, PADDING_Y

LEDGER_COLS: List[str] = [
    "Kontonr",
    "Konto",
    "Beskrivelse",
    "MVA",
    "MVA-beløp",
    "Beløp",
    "Postert av",
]


class LedgerTable(QtWidgets.QTableWidget):
    """Tabell med hjelpefunksjoner for å etterligne Tkinter-API."""

    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(0, len(LEDGER_COLS), parent)
        self.setHorizontalHeaderLabels(LEDGER_COLS)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setHighlightSections(False)
        self.refresh_theme()

    # Tk-kompatible hjelpere
    def get_children(self):  # noqa: D401 - beholder API
        return range(self.rowCount())

    def delete(self, row, *_):  # noqa: D401 - beholder API
        self.removeRow(row)

    def insert(self, _parent, _index, values, tags=None):  # noqa: ANN001 - Tk API
        row = self.rowCount()
        self.insertRow(row)
        for col, value in enumerate(values):
            item = QtWidgets.QTableWidgetItem(str(value))
            item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
            self.setItem(row, col, item)
        if tags:
            if "odd" in tags:
                self.setRowBackground(row, style.get_color("table_row_odd"))
            elif "even" in tags:
                self.setRowBackground(row, style.get_color("table_row_even"))

    def setRowBackground(self, row: int, color: str) -> None:  # noqa: N802 - Qt navnestil
        for col in range(self.columnCount()):
            item = self.item(row, col)
            if item:
                item.setBackground(QtGui.QColor(color))

    def refresh_theme(self) -> None:
        self.setStyleSheet(
            "QTableWidget {border: 1px solid transparent;}"
            f"QHeaderView::section {{background-color: {style.get_color('table_header_bg')};"
            f" padding: {PADDING_Y}px {PADDING_X}px; border: 0px;}}"
        )


def ledger_rows(app, invoice_value: str):
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
        konto_navn = to_str(r.get(app.gl_accountname_col, ""))
        if not konto_nr and konto_navn:
            parts = konto_navn.split()
            if parts and parts[0].isdigit():
                konto_nr = parts[0]
        if not konto_navn and konto_nr:
            konto_navn = konto_nr
        beskr = to_str(r.get(app.gl_desc_col, "")) or to_str(r.get(app.gl_text_col, ""))
        mva_code = to_str(r.get(app.gl_vatcode_col, ""))
        mva_belop = fmt_money(r.get(app.gl_vatamount_col, ""))
        belop = parse_amount(r.get(app.gl_amount_col)) if app.gl_amount_col else None
        if belop is None:
            deb = parse_amount(r.get(app.gl_debit_col)) if app.gl_debit_col else None
            kre = parse_amount(r.get(app.gl_credit_col)) if app.gl_credit_col else None
            belop = (deb or Decimal("0")) - (kre or Decimal("0"))
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


def populate_ledger_table(app, invoice_value: str):
    table: LedgerTable = app.ledger_table
    while table.rowCount():
        table.removeRow(0)
    rows = ledger_rows(app, invoice_value)
    if not rows:
        msg = "Ingen hovedbok lastet." if app.gl_df is None else "Ingen bilagslinjer for dette bilagsnummeret."
        app.ledger_sum.setText(msg)
        return
    total = Decimal("0")
    for i, r in enumerate(rows):
        tags = ["even" if i % 2 == 0 else "odd"]
        val = parse_amount(r["Beløp"])
        total += val or Decimal("0")
        table.insert("", "end", [r[c] for c in LEDGER_COLS], tags=tags)
    table.resizeColumnsToContents()
    app.ledger_sum.setText(f"Sum beløp: {fmt_money(total)}   •   Linjer: {len(rows)}")
