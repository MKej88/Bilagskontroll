from openpyxl import Workbook

import pandas as pd

from data_utils import load_invoice_df


def test_load_invoice_df_leser_arbeidsboken_direkte(tmp_path, monkeypatch):
    path = tmp_path / "fakturaliste.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["Rapport"])
    sheet.append(["Kunde: Eksempel AS"])
    sheet.append([])
    sheet.append([])
    sheet.append(["Fakturanr", "Nettobeløp", "Tom verdi"])
    sheet.append([123, 456.5, None])
    workbook.save(path)

    def unexpected_read_excel(*_args, **_kwargs):
        raise AssertionError("pandas.read_excel skal ikke brukes")

    monkeypatch.setattr(pd, "read_excel", unexpected_read_excel)

    invoice_df, customer = load_invoice_df(str(path))

    assert customer == "Eksempel AS"
    assert list(invoice_df.columns) == ["Fakturanr", "Nettobeløp", "Tom verdi"]
    assert invoice_df.iloc[0]["Fakturanr"] == "123"
    assert invoice_df.iloc[0]["Nettobeløp"] == "456.5"
    assert pd.isna(invoice_df.iloc[0]["Tom verdi"])
