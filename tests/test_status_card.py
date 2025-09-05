import pandas as pd
import gui
from gui import App

class DummyWidget:
    def __init__(self):
        self.cfg = {}
    def configure(self, **kwargs):
        self.cfg.update(kwargs)
    def delete(self, *args, **kwargs):
        pass
    def insert(self, *args, **kwargs):
        pass
    def get_children(self):
        return []

class FakeApp:
    def __init__(self):
        self.df = pd.DataFrame({'Faktura':[1], 'Beløp':[100]})
        self.sample_df = self.df.copy()
        self.idx = 0
        self.invoice_col = 'Faktura'
        self.net_amount_col = 'Beløp'
        self.decisions = [None]
        self.comments = [None]
        self.lbl_count = DummyWidget()
        self.lbl_invoice = DummyWidget()
        self.lbl_status = DummyWidget()
        self.detail_box = DummyWidget()
        self.ledger_tree = DummyWidget()
        self.ledger_sum = DummyWidget()
        self.comment_box = DummyWidget()
        self.btn_prev = DummyWidget()
        self.btn_next = DummyWidget()
        self.status_card_called = False
    def _ensure_helpers(self):
        gui.to_str = str
        gui.format_number_with_thousands = lambda x: x
    def _update_counts_labels(self):
        pass
    def _current_row_dict(self):
        return self.sample_df.iloc[self.idx].to_dict()
    def _details_text_for_row(self, row_dict):
        return ""
    def _update_status_card_safe(self):
        self.status_card_called = True


def test_status_card_updates_after_sample():
    app = FakeApp()
    App.render(app)
    assert app.status_card_called is True
