from openpyxl import Workbook
import pandas as pd

from data_utils import load_gl_df


def _write_gl(path, header_row):
    wb = Workbook()
    ws = wb.active
    for _ in range(header_row - 1):
        ws.append([])
    ws.append(["A", "B"])
    ws.append([1, 2])
    wb.save(path)


def test_load_gl_df_detects_header(tmp_path):
    # Header på første rad
    path1 = tmp_path / "gl1.xlsx"
    _write_gl(path1, header_row=1)
    df1 = load_gl_df(str(path1))
    assert list(df1.columns) == ["A", "B"]

    # Header etter fire tomme rader
    path2 = tmp_path / "gl2.xlsx"
    _write_gl(path2, header_row=5)
    df2 = load_gl_df(str(path2))
    assert list(df2.columns) == ["A", "B"]


def test_load_gl_df_leser_arbeidsboken_bare_en_gang(tmp_path, monkeypatch):
    path = tmp_path / "gl.xlsx"
    _write_gl(path, header_row=5)
    original_read_excel = pd.read_excel
    calls = []

    def counted_read_excel(*args, **kwargs):
        calls.append(args[0])
        return original_read_excel(*args, **kwargs)

    monkeypatch.setattr(pd, "read_excel", counted_read_excel)

    df = load_gl_df(str(path))

    assert list(df.columns) == ["A", "B"]
    assert len(calls) == 1


def test_load_gl_df_bevarer_unike_navn_for_duplikate_kolonner(tmp_path):
    path = tmp_path / "duplikate_kolonner.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.append([None, "A", "A", "A.1"])
    ws.append([1, 2, 3, 4])
    wb.save(path)

    df = load_gl_df(str(path))

    assert list(df.columns) == ["Unnamed: 0", "A", "A.2", "A.1"]
