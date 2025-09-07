import pandas as pd
import gui
from gui import App

class DummyApp:
    def __init__(self):
        self.sample_df = pd.DataFrame([
            {"Faktura": 1, "_netto_float": 408}
        ])
        self.idx = 0
    def _ensure_helpers(self):
        gui.to_str = str
        gui.format_number_with_thousands = lambda x: x

def test_netto_float_hidden_in_details():
    app = DummyApp()
    row = App._current_row_dict(app)
    assert "_netto_float" not in row
    text = App._details_text_for_row(app, row)
    assert "_netto_float" not in text
    assert "Faktura: 1" in text
