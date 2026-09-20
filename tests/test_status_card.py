import pandas as pd
from decimal import Decimal
import threading
import gui
import data_utils
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
        self.df = pd.DataFrame({'Faktura':[1], 'Beløp':[Decimal('100')]})
        self.df['_netto_float'] = self.df['Beløp']
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
    def _update_status_label(self, status, placeholder="—"):
        text = status if status else placeholder
        self.lbl_status.configure(text=text)


def test_status_card_updates_after_sample():
    app = FakeApp()
    App.render(app)
    assert app.status_card_called is True


def test_status_card_uses_cached_total(monkeypatch):
    app = FakeApp()
    app._sum_net_all = Decimal("100")
    app._pdf_prompt_shown = False
    app.lbl_st_sum_kontrollert = DummyWidget()
    app.lbl_st_sum_alle = DummyWidget()
    app.lbl_st_pct = DummyWidget()
    app.lbl_st_godkjent = DummyWidget()
    app.lbl_st_ikkegodkjent = DummyWidget()
    app.lbl_st_gjen = DummyWidget()
    monkeypatch.setattr(gui, "fmt_money", str, raising=False)
    monkeypatch.setattr(gui, "fmt_pct", str, raising=False)

    def fail_if_recalculated(_df):
        raise AssertionError("Totalsummen ble beregnet på nytt")

    monkeypatch.setattr(data_utils, "calc_sum_net_all", fail_if_recalculated)

    App._update_status_card(app)

    assert app.lbl_st_sum_alle.cfg["text"] == "Sum alle bilag: 100 kr"


def test_automatisk_pdf_eksport_kjorer_pa_hovedtraden(monkeypatch):
    app = FakeApp()
    app.decisions = ["Godkjent"]
    app._sum_net_all = Decimal("100")
    app._pdf_prompt_shown = False
    app.lbl_st_sum_kontrollert = DummyWidget()
    app.lbl_st_sum_alle = DummyWidget()
    app.lbl_st_pct = DummyWidget()
    app.lbl_st_godkjent = DummyWidget()
    app.lbl_st_ikkegodkjent = DummyWidget()
    app.lbl_st_gjen = DummyWidget()
    app._show_inline = lambda *_args, **_kwargs: None
    app._set_status = lambda *_args, **_kwargs: None
    app._start_progress = lambda *_args, **_kwargs: None
    app._finish_progress = lambda: None
    app.after = lambda _delay, callback: callback()
    monkeypatch.setattr(gui, "fmt_money", str, raising=False)
    monkeypatch.setattr(gui, "fmt_pct", str, raising=False)
    monkeypatch.setattr("tkinter.messagebox.askyesno", lambda *_args: True)
    monkeypatch.setattr("gui.busy.show_busy", lambda *_args: None)
    monkeypatch.setattr("gui.busy.hide_busy", lambda *_args: None)

    export_thread_ids = []
    export_finished = threading.Event()

    def record_export_thread(_app):
        export_thread_ids.append(threading.get_ident())
        export_finished.set()

    monkeypatch.setattr(
        "report.export_pdf",
        record_export_thread,
    )

    main_thread_id = threading.get_ident()
    App._update_status_card(app)

    assert export_finished.wait(timeout=1)
    assert export_thread_ids == [main_thread_id]
