# -*- coding: utf-8 -*-
"""PyQt-basert GUI for Bilagskontroll."""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from PyQt5 import QtCore, QtGui, QtWidgets

from data_utils import (
    _net_amount_from_row,
    calc_sum_kontrollert,
    calc_sum_net_all,
    load_gl_df,
    load_invoice_df,
)
from helpers import (
    fmt_money,
    fmt_pct,
    format_number_with_thousands,
    guess_col,
    guess_invoice_col,
    guess_net_amount_col,
    logger,
    only_digits,
    to_str,
)
from .busy import hide_busy, show_busy, start_worker
from .ledger import populate_ledger_table
from .mainview import MainView
from .sidebar import SidebarWidget
from .style import apply_palette, apply_stylesheet, style

if TYPE_CHECKING:  # pragma: no cover - kun for typehinting
    import pandas as pd

APP_TITLE = "Bilagskontroll"
OPEN_PO_URL = "https://go.poweroffice.net/#reports/purchases/invoice?"
MAX_APP_WIDTH = 1600
MIN_APP_WIDTH = 1200

if os.name == "nt":
    _CONFIG_DIR = Path(os.getenv("APPDATA") or Path.home()) / "Bilagskontroll"
else:
    _CONFIG_DIR = Path.home() / ".bilagskontroll"

WINDOW_CONFIG_FILE = _CONFIG_DIR / "settings.json"


@dataclass
class SimpleVar:
    value: str = ""

    def get(self) -> str:
        return self.value

    def set(self, value: str) -> None:
        self.value = value


def _set_text(widget: Any, text: str) -> None:
    if hasattr(widget, "configure"):
        widget.configure(text=text)
    elif hasattr(widget, "setText"):
        widget.setText(text)


def _set_enabled(widget: Any, enabled: bool) -> None:
    if hasattr(widget, "configure"):
        widget.configure(state="normal" if enabled else "disabled")
    elif hasattr(widget, "setEnabled"):
        widget.setEnabled(enabled)


def _clear_text(widget: Any) -> None:
    if hasattr(widget, "delete"):
        widget.delete("0.0", "end")
    elif hasattr(widget, "clear"):
        widget.clear()


def _insert_text(widget: Any, text: str) -> None:
    if hasattr(widget, "insert"):
        widget.insert("0.0", text)
    elif hasattr(widget, "setPlainText"):
        widget.setPlainText(text)


def _get_text(widget: Any) -> str:
    if hasattr(widget, "get"):
        return widget.get("0.0", "end") if callable(widget.get) else str(widget.get)
    if hasattr(widget, "toPlainText"):
        return widget.toPlainText()
    if hasattr(widget, "text"):
        return widget.text()
    return ""


class App(QtWidgets.QMainWindow):
    def __init__(self):
        self._qt_app = QtWidgets.QApplication.instance()
        self._owns_qt_app = False
        if self._qt_app is None:
            self._qt_app = QtWidgets.QApplication(sys.argv or ["Bilagskontroll"])
            self._owns_qt_app = True
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        self._workers: list[QtCore.QThread] = []
        self._progress_timer: Optional[QtCore.QTimer] = None
        self._progress_running = False
        self._progress_msg = ""
        self._progress_val = 0
        self._pdf_prompt_shown = False
        self._busy_dialog: Optional[QtWidgets.QDialog] = None

        self.df: Optional[pd.DataFrame] = None
        self.sample_df: Optional[pd.DataFrame] = None
        self.gl_df: Optional[pd.DataFrame] = None
        self.gl_index: dict[str, Any] = {}
        self.decisions: list[Optional[str]] = []
        self.comments: list[str] = []
        self.idx = 0
        self.invoice_col: Optional[str] = None
        self.net_amount_col: Optional[str] = None
        self.gl_invoice_col = None
        self.gl_accountno_col = None
        self.gl_accountname_col = None
        self.gl_text_col = None
        self.gl_desc_col = None
        self.gl_vatcode_col = None
        self.gl_vatamount_col = None
        self.gl_debit_col = None
        self.gl_credit_col = None
        self.gl_amount_col = None
        self.gl_postedby_col = None
        self.antall_bilag = 0

        default_user = os.environ.get("USERNAME") or os.environ.get("USER") or ""
        self.file_path_var = SimpleVar()
        self.gl_path_var = SimpleVar()
        self.sample_size_var = SimpleVar()
        self.year_var = SimpleVar()
        self.kunde_var = SimpleVar()
        self.utfort_av_var = SimpleVar(default_user)

        self._init_theme("Light")
        self._init_geometry()
        self._build_ui()
        self._init_shortcuts()
        QtCore.QTimer.singleShot(0, self._after_init)

    # Init
    def _init_theme(self, default: str) -> None:
        style.set_theme(default.lower())
        apply_palette(self._qt_app)
        apply_stylesheet(self._qt_app)

    def _after_init(self) -> None:
        self.render()
        if hasattr(self.sidebar, "refresh_theme"):
            self.sidebar.refresh_theme()
        if hasattr(self.main_view, "refresh_theme"):
            self.main_view.refresh_theme()

    def _init_geometry(self) -> None:
        screen = QtWidgets.QDesktopWidget().availableGeometry(self)
        width = min(int(screen.width() * 0.8), MAX_APP_WIDTH)
        height = int(screen.height() * 0.9)
        min_w = min(int(screen.width() * 0.6), MIN_APP_WIDTH)
        min_h = int(screen.height() * 0.7)
        saved = self._load_window_size(width, height, min_w, min_h, screen.width(), screen.height())
        self.resize(*saved)
        self.setMinimumSize(min_w, min_h)
        self.move(screen.center() - self.rect().center())

    def _build_ui(self) -> None:
        central = QtWidgets.QWidget(self)
        layout = QtWidgets.QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setCentralWidget(central)

        self.sidebar = SidebarWidget(self)
        layout.addWidget(self.sidebar)

        self.main_view = MainView(self)
        layout.addWidget(self.main_view, 1)

    def _init_shortcuts(self) -> None:
        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Left), self, self.prev)
        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Right), self, self.next)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+O"), self, self.open_in_po)

    # Konfig lagring
    def _load_window_size(self, width, height, min_w, min_h, screen_w, screen_h):
        try:
            with WINDOW_CONFIG_FILE.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return width, height

        win_cfg = data.get("window", {}) if isinstance(data, dict) else {}
        try:
            saved_w = int(win_cfg.get("width", width))
            saved_h = int(win_cfg.get("height", height))
        except (TypeError, ValueError):
            return width, height

        saved_w = max(min(saved_w, screen_w), min_w)
        saved_h = max(min(saved_h, screen_h), min_h)
        return saved_w or width, saved_h or height

    def _save_window_size(self) -> None:
        try:
            WINDOW_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            data = {}
            if WINDOW_CONFIG_FILE.exists():
                with WINDOW_CONFIG_FILE.open("r", encoding="utf-8") as fh:
                    loaded = json.load(fh)
                    data = loaded if isinstance(loaded, dict) else {}
            data["window"] = {"width": self.width(), "height": self.height()}
            with WINDOW_CONFIG_FILE.open("w", encoding="utf-8") as fh:
                json.dump(data, fh)
        except OSError:
            logger.debug("Kunne ikke lagre vindusstørrelse")

    # Qt hooks
    def closeEvent(self, event: QtGui.QCloseEvent) -> None:  # noqa: D401
        self._save_window_size()
        super().closeEvent(event)

    # Offentlige APIer
    def mainloop(self):
        self.show()
        if self._owns_qt_app:
            self._qt_app.exec_()

    # Filhåndtering
    def choose_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Velg Excel (fakturaliste)", "", "Excel (*.xlsx *.xls)"
        )
        if path:
            self.file_path_var.set(path)
            self.sidebar.update_invoice_path(path)
            self._load_excel()

    def choose_gl_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Velg Hovedbok (Excel)", "", "Excel (*.xlsx *.xls)"
        )
        if path:
            self.gl_path_var.set(path)
            self.sidebar.update_gl_path(path)
            self._load_gl_excel()

    def _load_excel(self):
        path = self.file_path_var.get()
        if not path:
            return
        self._start_progress("Laster fakturaliste...")
        self._busy_dialog = show_busy(self, "Laster fakturaliste...")

        def worker():
            df, cust = load_invoice_df(path, header_idx=4)
            invoice_col = guess_invoice_col(df.columns)
            net_amount_col = guess_net_amount_col(df.columns)
            try:
                df["_netto_float"] = df.apply(_net_amount_from_row, axis=1, args=(net_amount_col,))
            except (TypeError, ValueError):
                logger.exception("Kunne ikke beregne nettobeløp")
                df["_netto_float"] = None
            antall = len(df.dropna(how="all"))
            return df, cust, invoice_col, net_amount_col, antall

        def on_success(result):
            df, cust, invoice_col, net_amount_col, antall = result
            self.df = df
            self.sample_df = None
            self.decisions = []
            self.comments = []
            self.idx = 0
            self.antall_bilag = antall
            self.invoice_col = invoice_col
            self.net_amount_col = net_amount_col
            if cust:
                self.kunde_var.set(cust)
                self.sidebar.kunde_edit.setText(cust)
            self._update_counts_labels()
            self.render()
            self._update_year_options()
            self._finish_progress()
            hide_busy(self)

        def on_error(exc: Exception):
            hide_busy(self)
            self._finish_progress()
            QtWidgets.QMessageBox.critical(self, APP_TITLE, f"Klarte ikke lese Excel:\n{exc}")

        worker_thread = start_worker(worker, on_success=on_success, on_error=on_error)
        self._workers.append(worker_thread)

        def _cleanup():
            try:
                self._workers.remove(worker_thread)
            except ValueError:
                pass

        worker_thread.finished.connect(_cleanup)

    def _load_gl_excel(self):
        path = self.gl_path_var.get()
        if not path:
            return
        self._start_progress("Laster hovedbok...")
        self._busy_dialog = show_busy(self, "Laster hovedbok...")

        def worker():
            gl = load_gl_df(path, nrows=10)
            return gl

        def on_success(gl: pd.DataFrame):
            if gl is None or gl.dropna(how="all").empty:
                QtWidgets.QMessageBox.warning(self, APP_TITLE, "Hovedboken ser tom ut.")
            else:
                self.gl_df = gl
                cols = [str(c) for c in gl.columns]
                self.gl_invoice_col = guess_invoice_col(cols)
                self.gl_accountno_col = guess_col(cols, r"^kontonr\.?$", r"konto.*nummer", r"account.*(number|no)", r"acct.*no")
                self.gl_accountname_col = guess_col(cols, r"^kontonavn$", r"konto\s*navn", r"^konto$", r"account.*name", r"(?:^| )navn$")
                self.gl_text_col = guess_col(cols, r"^tekst$", r"text", r"posteringstekst")
                self.gl_desc_col = guess_col(cols, r"beskrivelse", r"description", r"forklaring")
                self.gl_vatcode_col = guess_col(cols, r"^mva(?!-)|mva[- ]?kode", r"^vat(?!.*amount)|tax code")
                self.gl_vatamount_col = guess_col(cols, r"mva[- ]?bel(ø|o)p", r"vat amount", r"tax amount")
                self.gl_debit_col = guess_col(cols, r"^debet$", r"debit")
                self.gl_credit_col = guess_col(cols, r"^kredit$", r"credit")
                self.gl_amount_col = guess_col(cols, r"^bel(ø|o)p$", r"amount", r"sum")
                self.gl_postedby_col = guess_col(cols, r"postert\s*av", r"bokf(ø|o)rt\s*av", r"registrert\s*av", r"posted\s*by", r"created\s*by")
                if self.gl_invoice_col in self.gl_df.columns:
                    self.gl_df["_inv_norm"] = self.gl_df[self.gl_invoice_col].map(only_digits)
                else:
                    self.gl_df["_inv_norm"] = ""
                self.gl_index = self.gl_df.groupby("_inv_norm").indices
                if self.sample_df is not None:
                    self.render()
                self._update_year_options()
            self._finish_progress()
            hide_busy(self)

        def on_error(exc: Exception):
            hide_busy(self)
            self._finish_progress()
            QtWidgets.QMessageBox.critical(self, APP_TITLE, f"Klarte ikke lese hovedbok:\n{exc}")

        worker_thread = start_worker(worker, on_success=on_success, on_error=on_error)
        self._workers.append(worker_thread)

        def _cleanup_gl():
            try:
                self._workers.remove(worker_thread)
            except ValueError:
                pass

        worker_thread.finished.connect(_cleanup_gl)

    # Årsliste
    def _update_year_options(self):
        from datetime import datetime

        years: set[int] = set()
        for df in (self.df, self.gl_df):
            if df is None or "Fakturadato" not in df.columns:
                continue
            for val in df["Fakturadato"].dropna().astype(str):
                m = re.search(r"(19|20)\d{2}", val)
                if m:
                    years.add(int(m.group(0)))
        now = datetime.now().year
        if years:
            filtered = sorted([y for y in years if y >= now - 1], reverse=True)
            if not filtered:
                filtered = sorted(years, reverse=True)[:2]
            values = [str(y) for y in filtered]
        else:
            values = [str(now), str(now - 1)]
        self.sidebar.set_year_options(values)
        if values:
            self.year_var.set(values[0])

    # Utvalg
    def _update_counts_labels(self):
        if hasattr(self, "lbl_filecount"):
            _set_text(self.lbl_filecount, f"Antall bilag: {self.antall_bilag}")

    def make_sample(self):
        if self.df is None:
            QtWidgets.QMessageBox.information(self, APP_TITLE, "Velg Excel først.")
            return
        try:
            n = int(self.sample_size_var.get())
            year = int(self.year_var.get())
        except ValueError:
            QtWidgets.QMessageBox.information(self, APP_TITLE, "Oppgi antall og år.")
            return
        n = max(1, min(n, len(self.df)))
        try:
            self.sample_df = self.df.sample(n=n, random_state=year).reset_index(drop=True).copy()
        except ValueError as exc:
            QtWidgets.QMessageBox.critical(self, APP_TITLE, f"Feil ved trekking av utvalg:\n{exc}")
            return
        self.decisions = [None] * len(self.sample_df)
        self.comments = [""] * len(self.sample_df)
        self.idx = 0
        self.render()

    def _current_row_dict(self):
        row = self.sample_df.iloc[self.idx]
        return {
            str(c): to_str(row[c])
            for c in self.sample_df.columns
            if not str(c).startswith("_")
        }

    def set_decision_and_next(self, val: str, advance: bool = True):
        if self.sample_df is None:
            return
        self.comments[self.idx] = _get_text(self.comment_box).strip()
        self.decisions[self.idx] = val
        if advance and self.idx < len(self.sample_df) - 1:
            self.idx += 1
        self.render()

    def prev(self):
        if self.sample_df is None:
            return
        self.comments[self.idx] = _get_text(self.comment_box).strip()
        self.idx = max(0, self.idx - 1)
        self.render()

    def next(self):
        if self.sample_df is None:
            return
        self.comments[self.idx] = _get_text(self.comment_box).strip()
        self.idx = min(len(self.sample_df) - 1, self.idx + 1)
        self.render()

    # Diverse handlinger
    def open_in_po(self):
        import webbrowser

        webbrowser.open(OPEN_PO_URL)
        self._show_inline("Åpner PowerOffice")

    def copy_invoice(self):
        if self.sample_df is None:
            return
        inv_val = to_str(self.sample_df.iloc[self.idx].get(self.invoice_col, ""))
        cleaned = re.sub(r"[^\d-]", "", inv_val)
        QtWidgets.QApplication.clipboard().setText(cleaned if cleaned else inv_val)
        _set_text(self.copy_feedback, "Kopiert")
        QtCore.QTimer.singleShot(1500, lambda: _set_text(self.copy_feedback, ""))

    def export_pdf(self):
        from report import export_pdf

        export_pdf(self)

    # Statuskort
    def _update_status_card(self):
        sum_k = calc_sum_kontrollert(self.sample_df, self.decisions)
        sum_a = calc_sum_net_all(self.df)
        pct = (sum_k / sum_a * Decimal("100")) if sum_a else Decimal("0")
        _set_text(self.lbl_st_sum_kontrollert, f"Sum kontrollert: {fmt_money(sum_k)} kr")
        _set_text(self.lbl_st_sum_alle, f"Sum alle bilag: {fmt_money(sum_a)} kr")
        _set_text(self.lbl_st_pct, f"% kontrollert av sum: {fmt_pct(pct)}")
        if self.sample_df is not None:
            approved = sum(1 for d in self.decisions if d == "Godkjent")
            rejected = sum(1 for d in self.decisions if d == "Ikke godkjent")
            remaining = sum(1 for d in self.decisions if d is None)
            _set_text(self.lbl_st_godkjent, f"Godkjent: {approved}")
            _set_text(self.lbl_st_ikkegodkjent, f"Ikke godkjent: {rejected}")
            _set_text(self.lbl_st_gjen, f"Gjenstår å kontrollere: {remaining}")
            if remaining == 0 and not self._pdf_prompt_shown:
                self._pdf_prompt_shown = True
                if QtWidgets.QMessageBox.question(
                    self,
                    APP_TITLE,
                    "Ønsker du å eksportere PDF rapport?",
                ) == QtWidgets.QMessageBox.Yes:
                    self.export_pdf()
        else:
            _set_text(self.lbl_st_godkjent, "Godkjent: –")
            _set_text(self.lbl_st_ikkegodkjent, "Ikke godkjent: –")
            _set_text(self.lbl_st_gjen, "Gjenstår å kontrollere: –")

    # Statuslinje
    def _start_progress(self, msg: str) -> None:
        self._progress_msg = msg
        self._progress_val = 0
        self._progress_running = True
        self._set_status(msg, 0)
        if self._progress_timer is None:
            self._progress_timer = QtCore.QTimer(self)
            self._progress_timer.timeout.connect(self._progress_step)
        self._progress_timer.start(100)

    def _progress_step(self) -> None:
        if not self._progress_running:
            return
        self._progress_val = min(95, self._progress_val + 2)
        self._set_status(self._progress_msg, self._progress_val)

    def _finish_progress(self) -> None:
        self._progress_running = False
        if self._progress_timer:
            self._progress_timer.stop()
        self._set_status(self._progress_msg, 100)
        QtCore.QTimer.singleShot(500, lambda: self._set_status(""))

    def _set_status(self, msg: str, progress: Optional[float] = None) -> None:
        if hasattr(self, "status_label"):
            if progress is not None:
                _set_text(self.status_label, f"{msg} {progress:.0f}%")
            else:
                _set_text(self.status_label, msg)
        if hasattr(self, "progress_bar"):
            if progress is not None:
                self.progress_bar.setVisible(True)
                self.progress_bar.setValue(int(max(0, min(100, progress))))
            else:
                self.progress_bar.setVisible(False)

    # Inline
    def _show_inline(self, msg: str, ok: bool = True) -> None:
        color = style.get_color("success" if ok else "error")
        if hasattr(self.inline_status, "setStyleSheet"):
            self.inline_status.setStyleSheet(f"color: {color};")
        _set_text(self.inline_status, msg)
        QtCore.QTimer.singleShot(3500, lambda: _set_text(self.inline_status, ""))

    # Detaljer
    def _details_text_for_row(self, row_dict):
        lines = []
        for key, val in row_dict.items():
            if key.startswith("_"):
                continue
            disp = val
            if not key.lower().startswith("faktura") or "nr" not in key.lower():
                disp = format_number_with_thousands(val)
            lines.append(f"{key}: {disp}")
        return "\n".join(lines).strip()

    def _update_status_label(self, status: Optional[str], placeholder: str = "—"):
        text = status if status else placeholder
        color = style.get_color("fg")
        if status == "Godkjent":
            color = style.get_color("success")
        elif status == "Ikke godkjent":
            color = style.get_color("error")
        if hasattr(self.lbl_status, "setStyleSheet"):
            self.lbl_status.setStyleSheet(f"color: {color}; font-weight: bold;")
        _set_text(self.lbl_status, text)

    def _update_status_card_safe(self):
        try:
            self._update_status_card()
        except Exception:
            logger.exception("Feil ved oppdatering av statuskort")

    def render(self):
        self._update_counts_labels()
        if self.sample_df is not None and len(self.sample_df) > 0:
            _set_text(self.lbl_count, f"Bilag: {self.idx + 1}/{len(self.sample_df)}")
            inv_val = to_str(self.sample_df.iloc[self.idx].get(self.invoice_col, ""))
            _set_text(self.lbl_invoice, f"Fakturanr: {inv_val or '—'}")
            st = self.decisions[self.idx] if (self.decisions and self.idx < len(self.decisions)) else None
            self._update_status_label(st)
            row_dict = self._current_row_dict()
            _clear_text(self.detail_box)
            _insert_text(self.detail_box, self._details_text_for_row(row_dict))
            if hasattr(self, "ledger_table") and self.gl_df is not None:
                populate_ledger_table(self, inv_val)
            else:
                if hasattr(self, "ledger_table"):
                    while self.ledger_table.rowCount():
                        self.ledger_table.removeRow(0)
                if hasattr(self, "ledger_sum"):
                    msg = (
                        "Last gjerne også inn en hovedbok for å se bilagslinjene."
                        if self.gl_df is None
                        else ""
                    )
                    _set_text(self.ledger_sum, msg)
            _clear_text(self.comment_box)
            if self.comments and self.idx < len(self.comments) and self.comments[self.idx]:
                _insert_text(self.comment_box, self.comments[self.idx])
        else:
            _set_text(self.lbl_count, "Bilag: –/–")
            _set_text(self.lbl_invoice, "Fakturanr: –")
            self._update_status_label(None, placeholder="–")
            _clear_text(self.detail_box)
            _insert_text(self.detail_box, "Velg Excel-fil og lag et utvalg.")
            if hasattr(self, "ledger_table"):
                while self.ledger_table.rowCount():
                    self.ledger_table.removeRow(0)
            if hasattr(self, "ledger_sum"):
                msg = (
                    "Last gjerne også inn en hovedbok for å se bilagslinjene."
                    if self.gl_df is None
                    else "Trekk utvalg for å se bilagslinjene."
                )
                _set_text(self.ledger_sum, msg)
            _clear_text(self.comment_box)

        if self.sample_df is None or len(self.sample_df) == 0:
            _set_enabled(self.btn_prev, False)
            _set_enabled(self.btn_next, False)
        else:
            _set_enabled(self.btn_prev, self.idx > 0)
            _set_enabled(self.btn_next, self.idx < len(self.sample_df) - 1)

        if (self.df is not None and len(self.df) > 0) or (self.sample_df is not None and len(self.sample_df) > 0):
            self._update_status_card_safe()

    def _switch_theme(self, mode: str) -> None:
        mode = (mode or "").strip()
        style.set_theme(mode.lower())
        apply_palette(self._qt_app)
        apply_stylesheet(self._qt_app)
        if hasattr(self.theme_menu, "blockSignals"):
            self.theme_menu.blockSignals(True)
            idx = 0 if mode.lower() != "dark" else 1
            self.theme_menu.setCurrentIndex(idx)
            self.theme_menu.blockSignals(False)
        if hasattr(self.sidebar, "refresh_theme"):
            self.sidebar.refresh_theme()
        if hasattr(self.main_view, "refresh_theme"):
            self.main_view.refresh_theme()
        if hasattr(self, "ledger_table") and hasattr(self.ledger_table, "refresh_theme"):
            self.ledger_table.refresh_theme()
        self.render()


__all__ = ["App", "SimpleVar"]
