import pandas as pd
import gui
from gui import App
import report
from reportlab.lib.styles import getSampleStyleSheet

class DummyApp:
    def __init__(self):
        self.sample_df = pd.DataFrame([
            {"Faktura": 1, "_netto_float": 408}
        ])
        self.idx = 0
        self.decisions = [None]
        self.comments = [""]
        self.invoice_col = "Faktura"
    def _ensure_helpers(self):
        gui.to_str = str
        gui.format_number_with_thousands = lambda x: x
    def _set_status(self, *args, **kwargs):
        pass

def test_netto_float_hidden_in_details():
    app = DummyApp()
    row = App._current_row_dict(app)
    assert "_netto_float" not in row
    text = App._details_text_for_row(app, row)
    assert "_netto_float" not in text
    assert "Faktura: 1" in text


def test_netto_float_hidden_in_pdf(monkeypatch):
    app = DummyApp()
    styles = getSampleStyleSheet()
    monkeypatch.setattr(report, "build_ledger_table", lambda *args, **kwargs: "ledger")
    flow = report.create_invoice_section(app, styles, styles["BodyText"])
    table = flow[1]
    assert "_netto_float" not in [row[0] for row in table._cellvalues]
