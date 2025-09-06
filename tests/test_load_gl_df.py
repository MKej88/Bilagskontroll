from openpyxl import Workbook

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
