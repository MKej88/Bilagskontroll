from decimal import Decimal
from types import SimpleNamespace

import pandas as pd

from gui.ledger import ledger_rows, sort_treeview
from helpers import only_digits, parse_amount


class FakeApp:
    def __init__(self, rows):
        self.gl_df = pd.DataFrame(rows)
        self.gl_invoice_col = "Fakturanr"
        self.gl_accountno_col = "Kontonr"
        self.gl_accountname_col = "Kontonavn"
        self.gl_text_col = None
        self.gl_desc_col = None
        self.gl_vatcode_col = None
        self.gl_vatamount_col = None
        self.gl_debit_col = "Debet"
        self.gl_credit_col = "Kredit"
        self.gl_amount_col = None
        self.gl_postedby_col = None
        self.gl_df["_inv_norm"] = self.gl_df[self.gl_invoice_col].map(only_digits)
        self.gl_index = self.gl_df.groupby("_inv_norm").indices


class FakeTree:
    def __init__(self):
        self.rows = {
            "numeric": {"Beløp": "100,00"},
            "missing": {"Beløp": ""},
            "smaller": {"Beløp": "20,00"},
        }
        self.order = list(self.rows)

    def get_children(self, _parent=""):
        return tuple(self.order)

    def set(self, item_id, column):
        return self.rows[item_id][column]

    def move(self, item_id, _parent, index):
        self.order.remove(item_id)
        self.order.insert(index, item_id)

    def item(self, _item_id, **_kwargs):
        pass

    def heading(self, _column, **_kwargs):
        pass

    def tag_configure(self, _tag, **_kwargs):
        pass


def test_ledger_rows_beholder_alle_linjene_for_samme_bilag():
    app = FakeApp(
        [
            {
                "Fakturanr": "F-1001",
                "Kontonr": "4000",
                "Kontonavn": "Varekjøp",
                "Debet": "100,00",
                "Kredit": None,
            },
            {
                "Fakturanr": "F-1001",
                "Kontonr": "2710",
                "Kontonavn": "Inngående mva",
                "Debet": "25,00",
                "Kredit": None,
            },
        ]
    )

    rows = ledger_rows(app, "F-1001")

    assert [row["Kontonr"] for row in rows] == ["4000", "2710"]
    assert sum(
        (parse_amount(row["Beløp"]) for row in rows), start=Decimal("0")
    ) == Decimal("125.00")


def test_ledger_rows_beregner_belop_nar_belopskolonnen_mangler():
    app = FakeApp(
        [
            {
                "Fakturanr": "1002",
                "Kontonr": "2400",
                "Kontonavn": "Leverandørgjeld",
                "Debet": None,
                "Kredit": "1 234,50",
            }
        ]
    )

    rows = ledger_rows(app, "1002")

    assert len(rows) == 1
    assert rows[0]["Beløp"] == "-1 234,50"
    assert rows[0]["MVA"] == ""
    assert rows[0]["Postert av"] == ""


def test_sort_treeview_handterer_bade_belop_og_tomme_felt():
    tree = FakeTree()

    sort_treeview(tree, "Beløp", False, SimpleNamespace(ledger_tree=tree))

    assert tree.order == ["smaller", "numeric", "missing"]
