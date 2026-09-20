from decimal import Decimal

import pandas as pd

import data_utils
import gui
from gui import App


class DummyVar:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


class FakeApp:
    def __init__(self):
        self.file_path_var = DummyVar("tom.xlsx")
        self.df = pd.DataFrame({"Fakturanr": ["gammel"]})
        self.sample_df = self.df.copy()
        self.decisions = ["Godkjent"]
        self.comments = ["Kontrollert"]
        self.idx = 0
        self.antall_bilag = 1
        self._sum_net_all = Decimal("100")

    def _ensure_helpers(self):
        gui.guess_invoice_col = lambda columns: columns[0]
        gui.guess_net_amount_col = lambda columns: None

    def after(self, _delay, callback):
        callback()

    def _start_progress(self, _message):
        pass

    def _finish_progress(self):
        pass

    def _update_counts_labels(self):
        pass

    def render(self):
        pass

    def _update_year_options(self):
        pass


def test_tom_fakturaliste_fjerner_gammelt_utvalg(monkeypatch):
    empty_df = pd.DataFrame(columns=["Fakturanr"])
    monkeypatch.setattr(data_utils, "load_invoice_df", lambda *_: (empty_df, None))
    monkeypatch.setattr(data_utils, "calculate_net_amounts", lambda df, _column: None)
    monkeypatch.setattr(data_utils, "calc_sum_net_all", lambda _df: Decimal("0"))
    monkeypatch.setattr("gui.busy.show_busy", lambda *_: None)
    monkeypatch.setattr("gui.busy.hide_busy", lambda *_: None)
    monkeypatch.setattr("gui.busy.run_in_thread", lambda worker: worker())
    monkeypatch.setattr("tkinter.messagebox.showwarning", lambda *_: None)
    monkeypatch.setattr("os.path.getsize", lambda _path: 0)

    app = FakeApp()

    App._load_excel(app)

    assert app.df.empty
    assert app.sample_df is None
    assert app.decisions == []
    assert app.comments == []
    assert app.antall_bilag == 0
    assert app._sum_net_all == Decimal("0")
