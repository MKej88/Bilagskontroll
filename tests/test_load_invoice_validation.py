import pandas as pd
import gui
from gui import App


def test_warning_on_missing_columns(monkeypatch):
    warnings = {}
    import tkinter.messagebox as mb
    monkeypatch.setattr(mb, "showwarning", lambda title, message: warnings.setdefault("msg", message))

    import gui.busy as busy
    monkeypatch.setattr(busy, "hide_busy", lambda app: None)

    monkeypatch.setattr(gui.os.path, "getsize", lambda p: 0)

    class DummyThread:
        def __init__(self, target, daemon=True):
            self.target = target
        def start(self):
            self.target()
    import threading
    monkeypatch.setattr(threading, "Thread", lambda target, daemon=True: DummyThread(target, daemon))

    df = pd.DataFrame({"A": [1], "B": [2]})
    import data_utils
    monkeypatch.setattr(data_utils, "load_invoice_df", lambda path, header_idx: (df, None))

    class DummyVar:
        def __init__(self, value):
            self.value = value
        def get(self):
            return self.value

    class FakeApp:
        def __init__(self):
            self.file_path_var = DummyVar("dummy.xlsx")
            self.decisions = []
            self.comments = []
            self.idx = 0
        def _ensure_helpers(self):
            from helpers import guess_invoice_col, guess_net_amount_col, logger
            gui.guess_invoice_col = guess_invoice_col
            gui.guess_net_amount_col = guess_net_amount_col
            gui.logger = logger
        def _start_progress(self, *a, **kw):
            pass
        def _finish_progress(self, *a, **kw):
            pass
        def after(self, delay, func, *args):
            func(*args)
        def render(self):
            pass
        def _update_counts_labels(self):
            pass
        def _update_year_options(self):
            pass

    app = FakeApp()
    App._load_excel(app)
    assert "msg" in warnings
