# -*- coding: utf-8 -*-
"""GUI-moduler for Bilagskontroll med PySide6."""

from __future__ import annotations

import json
import os
import re
from decimal import Decimal
from pathlib import Path
from typing import Optional

from helpers import logger

from .busy import hide_busy, run_in_thread, show_busy
from .ledger import LEDGER_COLS
from .mainview import MainWidgets, build_main, populate_ledger_table
from .sidebar import SidebarWidgets, build_sidebar, update_file_labels
from .style import style
from .qt import qt_modules

QtCore, QtGui, QtWidgets = qt_modules()

APP_TITLE = "Bilagskontroll"
OPEN_PO_URL = "https://go.poweroffice.net/#reports/purchases/invoice?"
MAX_APP_WIDTH = 1600
MIN_APP_WIDTH = 1200
DEFAULT_APPEARANCE_MODE = "light"

if os.name == "nt":
    _CONFIG_DIR = Path(os.getenv("APPDATA") or Path.home()) / "Bilagskontroll"
else:
    _CONFIG_DIR = Path.home() / ".bilagskontroll"

WINDOW_CONFIG_FILE = _CONFIG_DIR / "settings.json"

# Plassholdere for helper-funksjoner. Disse fylles via ``_ensure_helpers``.
to_str = None
fmt_money = None
format_number_with_thousands = None
guess_invoice_col = None
guess_col = None
guess_net_amount_col = None
fmt_pct = None


def _ensure_qapp():
    _, _, QtWidgets = qt_modules()
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    return app


class App(QtWidgets.QMainWindow):
    """Hovedapplikasjon for Bilagskontroll basert på PySide6."""

    def __init__(self) -> None:
        self._qapp = _ensure_qapp()
        QtCore, QtGui, QtWidgets = qt_modules()
        super().__init__()
        self.QtCore = QtCore
        self.QtGui = QtGui
        self.QtWidgets = QtWidgets

        self.setWindowTitle(APP_TITLE)
        self._timers: set = set()
        self._helpers_loaded = False
        self._progress_job: Optional[object] = None
        self._progress_running = False
        self._progress_val = 0
        self._progress_msg = ""
        self._pdf_prompt_shown = False
        self._busy_dialog = None

        self.df = None
        self.sample_df = None
        self.decisions: list[Optional[str]] = []
        self.comments: list[Optional[str]] = []
        self.idx = 0
        self.invoice_col: Optional[str] = None
        self.net_amount_col: Optional[str] = None
        self.antall_bilag = 0

        self.gl_df = None
        self.gl_invoice_col: Optional[str] = None
        self.gl_accountno_col: Optional[str] = None
        self.gl_accountname_col: Optional[str] = None
        self.gl_text_col: Optional[str] = None
        self.gl_desc_col: Optional[str] = None
        self.gl_vatcode_col: Optional[str] = None
        self.gl_vatamount_col: Optional[str] = None
        self.gl_debit_col: Optional[str] = None
        self.gl_credit_col: Optional[str] = None
        self.gl_amount_col: Optional[str] = None
        self.gl_postedby_col: Optional[str] = None
        self.gl_index = None

        self.file_path: str = ""
        self.gl_path: str = ""

        self.ledger_cols = LEDGER_COLS

        self.int_validator = self.QtGui.QIntValidator(0, 999999, self)

        self._init_fonts()
        self._setup_window_geometry()
        self._build_ui()
        self._apply_theme(DEFAULT_APPEARANCE_MODE)
        self._setup_shortcuts()

    # ------------------------------------------------------------------
    # Qt-hjelpere
    def create_button(self, parent, *, text: str, command=None, fg_color: Optional[str] = None, hover_color: Optional[str] = None):
        btn = self.QtWidgets.QPushButton(text, parent)
        btn.setCursor(self.QtCore.Qt.PointingHandCursor)
        palette_color = fg_color or style.BTN_FG
        btn.setStyleSheet(
            (
                f"QPushButton {{"
                f"background-color: {palette_color};"
                f"color: white;"
                f"border-radius: {style.BTN_RADIUS}px;"
                f"padding: 8px 14px;"
                f"}}"
                f"QPushButton:hover {{ background-color: {hover_color or style.BTN_HOVER}; }}"
                f"QPushButton:disabled {{ background-color: #a0a0a0; color: #444; }}"
            )
        )
        if command:
            btn.clicked.connect(command)  # type: ignore[attr-defined]
        return btn

    def after(self, ms: int, callback):
        timer = self.QtCore.QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(callback)
        timer.start(max(0, ms))
        self._timers.add(timer)
        timer.destroyed.connect(lambda: self._timers.discard(timer))
        return timer

    def after_idle(self, callback):
        return self.after(0, callback)

    def after_cancel(self, timer) -> None:
        if timer in self._timers:
            timer.stop()
            timer.deleteLater()
            self._timers.discard(timer)

    # Kompatibilitet mot gamle Tk-widgeter brukt i tester
    @staticmethod
    def _set_label_text(widget, text: str) -> None:
        if hasattr(widget, "setText"):
            widget.setText(text)
        elif hasattr(widget, "configure"):
            widget.configure(text=text)

    @staticmethod
    def _set_label_color(widget, color: str) -> None:
        if hasattr(widget, "setStyleSheet"):
            widget.setStyleSheet(f"color: {color};")
        elif hasattr(widget, "configure"):
            widget.configure(text_color=color)

    @staticmethod
    def _set_text_area(widget, text: str, *, readonly: bool = False) -> None:
        if hasattr(widget, "setPlainText"):
            widget.setPlainText(text)
        elif hasattr(widget, "delete") and hasattr(widget, "insert"):
            if hasattr(widget, "configure") and readonly:
                widget.configure(state="normal")
            widget.delete("0.0", "end")
            widget.insert("0.0", text)
            if hasattr(widget, "configure") and readonly:
                widget.configure(state="disabled")

    @staticmethod
    def _get_text_area(widget) -> str:
        if hasattr(widget, "toPlainText"):
            return widget.toPlainText()
        if hasattr(widget, "get"):
            return str(widget.get("0.0", "end")).strip()
        return ""

    @staticmethod
    def _set_button_enabled(widget, enabled: bool) -> None:
        if hasattr(widget, "setEnabled"):
            widget.setEnabled(enabled)
        elif hasattr(widget, "configure"):
            widget.configure(state="normal" if enabled else "disabled")

    # ------------------------------------------------------------------
    # Initiering
    def _setup_shortcuts(self) -> None:
        self.QtWidgets.QShortcut(self.QtGui.QKeySequence(self.QtCore.Qt.Key_Left), self, activated=self.prev)
        self.QtWidgets.QShortcut(self.QtGui.QKeySequence(self.QtCore.Qt.Key_Right), self, activated=self.next)
        self.QtWidgets.QShortcut(self.QtGui.QKeySequence("Ctrl+O"), self, activated=self.open_in_po)

    def _setup_window_geometry(self) -> None:
        screen = self.QtGui.QGuiApplication.primaryScreen()
        available = screen.availableGeometry() if screen else None
        screen_w = available.width() if available else 1600
        screen_h = available.height() if available else 900
        origin_x = available.x() if available else 0
        origin_y = available.y() if available else 0

        width = min(int(screen_w * 0.8), MAX_APP_WIDTH)
        height = int(screen_h * 0.9)
        min_w = min(int(screen_w * 0.6), MIN_APP_WIDTH)
        min_h = int(screen_h * 0.7)

        width, height = self._load_window_size(width, height, min_w, min_h, screen_w, screen_h)
        x = origin_x + max((screen_w - width) // 2, 0)
        y = origin_y + max((screen_h - height) // 2, 0)

        self.resize(width, height)
        self.move(x, y)
        self.setMinimumSize(min_w, min_h)

    def _init_fonts(self) -> None:
        s = style
        family = s.FONT_FAMILY

        def build(size: int, *, bold: bool = False, italic: bool = False):
            font = self.QtGui.QFont(family, pointSize=size)
            font.setBold(bold)
            font.setItalic(italic)
            return font

        if s.FONT_TITLE is None:
            s.FONT_TITLE = build(16, bold=True)
        if s.FONT_BODY is None:
            s.FONT_BODY = build(14)
        if s.FONT_TITLE_LITE is None:
            s.FONT_TITLE_LITE = build(16)
        if s.FONT_TITLE_LARGE is None:
            s.FONT_TITLE_LARGE = build(18, bold=True)
        if s.FONT_TITLE_SMALL is None:
            s.FONT_TITLE_SMALL = build(15, bold=True)
        if s.FONT_BODY_BOLD is None:
            s.FONT_BODY_BOLD = build(14, bold=True)
        if s.FONT_SMALL is None:
            s.FONT_SMALL = build(13)
        if s.FONT_SMALL_ITALIC is None:
            s.FONT_SMALL_ITALIC = build(12, italic=True)

    def _build_ui(self) -> None:
        self.central_widget = self.QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)
        layout = self.QtWidgets.QHBoxLayout(self.central_widget)
        layout.setContentsMargins(style.PAD_LG, style.PAD_LG, style.PAD_LG, style.PAD_LG)
        layout.setSpacing(style.PAD_LG)

        self.sidebar: SidebarWidgets = build_sidebar(self)
        self.main_widgets: MainWidgets = build_main(self)

        layout.addWidget(self.sidebar.container)
        layout.addWidget(self.main_widgets.container, 1)

        update_file_labels(self)
        self._bind_main_widgets()
        self.render()

    def _bind_main_widgets(self) -> None:
        header = self.main_widgets.header
        self.main_panel = self.main_widgets.container
        self.lbl_count = header.count_label
        self.lbl_status_label = header.status_label
        self.lbl_status = header.status_value
        self.lbl_invoice = header.invoice_label
        self.copy_feedback = header.copy_feedback
        self.inline_status = header.inline_status
        self.theme_menu = header.theme_menu
        self.theme_menu.currentTextChanged.connect(self._switch_theme)

        actions = self.main_widgets.actions
        self.btn_prev = actions.prev_button
        self.btn_next = actions.next_button

        panes = self.main_widgets.panes
        self.detail_box = panes.detail_box
        self.comment_box = panes.comment_box
        self.ledger_table = panes.ledger_table
        self.ledger_sum = panes.ledger_sum
        self.ledger_tree = self.ledger_table

        bottom = self.main_widgets.bottom
        self.status_label = bottom.status_label
        self.progress_bar = bottom.progress_bar

        self.lbl_st_sum_kontrollert = self.sidebar.status_sum_kontrollert
        self.lbl_st_sum_alle = self.sidebar.status_sum_alle
        self.lbl_st_pct = self.sidebar.status_pct
        self.lbl_st_godkjent = self.sidebar.status_godkjent
        self.lbl_st_ikkegodkjent = self.sidebar.status_ikkegodkjent
        self.lbl_st_gjen = self.sidebar.status_gjen

    # ------------------------------------------------------------------
    # Tema og ikoner
    def _apply_theme(self, mode: str) -> None:
        style.set_mode(mode)
        palette = self._qapp.palette()
        bg = self.QtGui.QColor(style.get_color("bg"))
        fg = self.QtGui.QColor(style.get_color("fg"))
        palette.setColor(self.QtGui.QPalette.Window, bg)
        palette.setColor(self.QtGui.QPalette.WindowText, fg)
        self._qapp.setPalette(palette)

    def _switch_theme(self, mode: str) -> None:
        mode = mode.strip().lower()
        if mode.startswith("m"):
            mode = "dark"
        else:
            mode = "light"
        self._apply_theme(mode)
        self.render()

    # ------------------------------------------------------------------
    # Helper lasting
    def _ensure_helpers(self) -> None:
        global to_str, fmt_money, format_number_with_thousands, guess_invoice_col, guess_col, guess_net_amount_col, fmt_pct
        if self._helpers_loaded:
            return
        from helpers import (
            fmt_money as _fmt_money,
            fmt_pct as _fmt_pct,
            format_number_with_thousands as _format_number_with_thousands,
            guess_col as _guess_col,
            guess_invoice_col as _guess_invoice_col,
            guess_net_amount_col as _guess_net_amount_col,
            to_str as _to_str,
        )

        to_str = _to_str
        fmt_money = _fmt_money
        format_number_with_thousands = _format_number_with_thousands
        guess_invoice_col = _guess_invoice_col
        guess_col = _guess_col
        guess_net_amount_col = _guess_net_amount_col
        fmt_pct = _fmt_pct
        self._helpers_loaded = True

    # ------------------------------------------------------------------
    # Filoperasjoner
    def choose_file(self) -> None:
        path, _ = self.QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Velg Excel (fakturaliste)",
            "",
            "Excel-filer (*.xlsx *.xls)",
        )
        if path:
            self.handle_invoice_drop(path)

    def choose_gl_file(self) -> None:
        path, _ = self.QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Velg hovedbok (Excel)",
            "",
            "Excel-filer (*.xlsx *.xls)",
        )
        if path:
            self.handle_gl_drop(path)

    def handle_invoice_drop(self, path: str) -> None:
        if not path.lower().endswith((".xlsx", ".xls")):
            return
        self.file_path = path
        update_file_labels(self)
        self._load_excel()

    def handle_gl_drop(self, path: str) -> None:
        if not path.lower().endswith((".xlsx", ".xls")):
            return
        self.gl_path = path
        update_file_labels(self)
        self._load_gl_excel()

    # ------------------------------------------------------------------
    # Lagring av vindusstørrelse
    def _load_window_size(self, width, height, min_w, min_h, screen_w, screen_h):
        try:
            with WINDOW_CONFIG_FILE.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
        except FileNotFoundError:
            return width, height
        except (OSError, json.JSONDecodeError) as exc:
            logger.debug(f"Kunne ikke lese vindustørrelse: {exc}")
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
        width = max(1, self.width())
        height = max(1, self.height())
        if width <= 1 or height <= 1:
            return
        try:
            with WINDOW_CONFIG_FILE.open("r", encoding="utf-8") as fh:
                loaded = json.load(fh)
                data = loaded if isinstance(loaded, dict) else {}
        except FileNotFoundError:
            data = {}
        except (OSError, json.JSONDecodeError) as exc:
            logger.debug(f"Kunne ikke lese eksisterende innstillinger: {exc}")
            data = {}

        data["window"] = {"width": width, "height": height}
        try:
            WINDOW_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with WINDOW_CONFIG_FILE.open("w", encoding="utf-8") as fh:
                json.dump(data, fh)
        except OSError as exc:
            logger.debug(f"Kunne ikke lagre vindustørrelse: {exc}")

    # ------------------------------------------------------------------
    # Datahåndtering
    def _update_year_options(self) -> None:
        from datetime import datetime

        years: set[int] = set()
        for df in (self.df, self.gl_df):
            if df is None or "Fakturadato" not in df.columns:
                continue
            for val in df["Fakturadato"].dropna().astype(str):
                match = re.search(r"(19|20)\d{2}", val)
                if match:
                    years.add(int(match.group(0)))

        now = datetime.now().year
        if years:
            filtered = sorted([y for y in years if y >= now - 1], reverse=True)
            if not filtered:
                filtered = sorted(years, reverse=True)[:2]
            values = [str(y) for y in filtered]
        else:
            values = [str(now), str(now - 1)]

        combo = self.sidebar.year_combo
        combo.blockSignals(True)
        combo.clear()
        combo.addItems(values)
        combo.blockSignals(False)
        if combo.currentText() not in values and values:
            combo.setCurrentIndex(0)
        self._toggle_sample_btn()

    def _toggle_sample_btn(self) -> None:
        size_ok = bool(self.sidebar.sample_size_input.text())
        year_ok = bool(self.sidebar.year_combo.currentText())
        self.sidebar.sample_button.setEnabled(size_ok and year_ok)

    def _load_excel(self) -> None:
        if not self.file_path:
            return
        self._ensure_helpers()
        from data_utils import _net_amount_from_row, load_invoice_df

        path = self.file_path
        logger.info(f"Laster fakturaliste fra {path}")
        big = os.path.getsize(path) > 5 * 1024 * 1024
        if big:
            self._show_inline("Laster inn fil…")

        busy = show_busy(self, "Laster fakturaliste…")

        def finalize():
            if big:
                self._show_inline("", ok=True)
            self._finish_progress()
            hide_busy(self)

        def worker():
            self.after(0, lambda: self._start_progress("Laster fakturaliste…"))
            try:
                df, customer = load_invoice_df(path, header_idx=4)
            except (OSError, ValueError) as exc:
                logger.error(f"Klarte ikke lese Excel: {exc}")
                self.after(0, lambda: (self.QtWidgets.QMessageBox.critical(self, APP_TITLE, f"Klarte ikke lese Excel:\n{exc}"), finalize()))
                return

            def success():
                self.antall_bilag = len(df.dropna(how="all"))
                self.df = df
                if customer:
                    self.sidebar.customer_input.setText(customer)
                if self.df.dropna(how="all").empty:
                    self.QtWidgets.QMessageBox.warning(self, APP_TITLE, "Excel-filen ser tom ut.")
                    finalize()
                    return

                self.invoice_col = guess_invoice_col(self.df.columns)
                self.net_amount_col = guess_net_amount_col(self.df.columns)
                try:
                    self.df["_netto_float"] = self.df.apply(
                        _net_amount_from_row,
                        axis=1,
                        args=(self.net_amount_col,),
                    )
                except (TypeError, ValueError):
                    logger.exception("Kunne ikke beregne nettobeløp")
                    self.df["_netto_float"] = None
                self.sample_df = None
                self.decisions = []
                self.comments = []
                self.idx = 0
                self._update_counts_labels()
                self.render()
                self._update_year_options()
                finalize()

            self.after(0, success)

        run_in_thread(worker)

    def _load_gl_excel(self) -> None:
        if not self.gl_path:
            return
        self._ensure_helpers()
        from data_utils import load_gl_df

        path = self.gl_path
        logger.info(f"Laster hovedbok fra {path}")
        big = os.path.getsize(path) > 5 * 1024 * 1024
        if big:
            self._show_inline("Laster inn fil…")

        busy = show_busy(self, "Laster hovedbok…")

        def finalize():
            if big:
                self._show_inline("", ok=True)
            self._finish_progress()
            hide_busy(self)

        def worker():
            self.after(0, lambda: self._start_progress("Laster hovedbok…"))
            try:
                gl = load_gl_df(path, nrows=10)
            except (OSError, ValueError) as exc:
                logger.error(f"Klarte ikke lese hovedbok: {exc}")
                self.after(0, lambda: (self.QtWidgets.QMessageBox.critical(self, APP_TITLE, f"Klarte ikke lese hovedbok:\n{exc}"), finalize()))
                return

            def success():
                if gl is None or gl.dropna(how="all").empty:
                    self.QtWidgets.QMessageBox.warning(self, APP_TITLE, "Hovedboken ser tom ut.")
                    finalize()
                    return

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
                    from helpers import only_digits

                    self.gl_df["_inv_norm"] = self.gl_df[self.gl_invoice_col].map(only_digits)
                else:
                    self.gl_df["_inv_norm"] = ""
                self.gl_index = self.gl_df.groupby("_inv_norm").indices

                if self.sample_df is not None:
                    self.render()
                self._update_year_options()
                finalize()

            self.after(0, success)

        run_in_thread(worker)

    # ------------------------------------------------------------------
    # Utvalg og navigasjon
    def _update_counts_labels(self) -> None:
        self.sidebar.filecount_label.setText(f"Antall bilag: {self.antall_bilag}")

    def make_sample(self) -> None:
        self._ensure_helpers()
        if self.df is None:
            self.QtWidgets.QMessageBox.information(self, APP_TITLE, "Velg Excel først.")
            return
        try:
            n = int(self.sidebar.sample_size_input.text())
            year = int(self.sidebar.year_combo.currentText())
        except ValueError:
            self.QtWidgets.QMessageBox.information(self, APP_TITLE, "Oppgi antall og år.")
            return

        n = max(1, min(n, len(self.df)))
        logger.info(f"Trekker utvalg på {n} bilag for år {year}")
        try:
            sample = self.df.sample(n=n, random_state=year).reset_index(drop=True).copy()
        except ValueError as exc:
            logger.error(f"Feil ved trekking av utvalg: {exc}")
            self.QtWidgets.QMessageBox.critical(self, APP_TITLE, f"Feil ved trekking av utvalg:\n{exc}")
            return

        self.sample_df = sample
        self.decisions = [None] * len(sample)
        self.comments = [""] * len(sample)
        self.idx = 0
        self.render()

    def _current_row_dict(self):
        self._ensure_helpers()
        row = self.sample_df.iloc[self.idx]
        return {
            str(col): to_str(row[col])
            for col in self.sample_df.columns
            if not str(col).startswith("_")
        }

    def set_decision_and_next(self, value: str, advance: bool = True) -> None:
        if self.sample_df is None:
            return
        self.comments[self.idx] = App._get_text_area(self.comment_box)
        self.decisions[self.idx] = value
        if advance and self.idx < len(self.sample_df) - 1:
            self.idx += 1
        self.render()

    def prev(self) -> None:
        if self.sample_df is None:
            return
        self.comments[self.idx] = App._get_text_area(self.comment_box)
        self.idx = max(0, self.idx - 1)
        self.render()

    def next(self) -> None:
        if self.sample_df is None:
            return
        self.comments[self.idx] = App._get_text_area(self.comment_box)
        self.idx = min(len(self.sample_df) - 1, self.idx + 1)
        self.render()

    # ------------------------------------------------------------------
    # Handlinger
    def open_in_po(self) -> None:
        import webbrowser

        webbrowser.open(OPEN_PO_URL)
        self._show_inline("Åpner PowerOffice")

    def copy_invoice(self) -> None:
        self._ensure_helpers()
        if self.sample_df is None:
            return
        inv_val = to_str(self.sample_df.iloc[self.idx].get(self.invoice_col, ""))
        cleaned = re.sub(r"[^\d-]", "", inv_val)
        self.QtGui.QGuiApplication.clipboard().setText(cleaned if cleaned else inv_val)
        App._set_label_text(self.copy_feedback, "Kopiert")
        self.after(1500, lambda: App._set_label_text(self.copy_feedback, ""))

    def export_pdf(self) -> None:
        from report import export_pdf

        if self.sample_df is None:
            self.QtWidgets.QMessageBox.information(self, APP_TITLE, "Lag et utvalg først.")
            return

        show_busy(self, "Eksporterer rapport…")

        def finalize():
            self._finish_progress()
            hide_busy(self)

        def worker():
            self.after(0, lambda: self._start_progress("Eksporterer rapport…"))
            try:
                export_pdf(self)
            finally:
                self.after(0, finalize)

        run_in_thread(worker)

    # ------------------------------------------------------------------
    # Status og fremdrift
    def _update_status_card(self) -> None:
        from data_utils import calc_sum_kontrollert, calc_sum_net_all

        self._ensure_helpers()
        sum_k = calc_sum_kontrollert(self.sample_df, self.decisions)
        sum_a = calc_sum_net_all(self.df)
        pct = (sum_k / sum_a * Decimal("100")) if sum_a else Decimal("0")
        App._set_label_text(self.lbl_st_sum_kontrollert, f"Sum kontrollert: {fmt_money(sum_k)} kr")
        App._set_label_text(self.lbl_st_sum_alle, f"Sum alle bilag: {fmt_money(sum_a)} kr")
        App._set_label_text(self.lbl_st_pct, f"% kontrollert av sum: {fmt_pct(pct)}")
        if self.sample_df is not None:
            approved = sum(1 for d in self.decisions if d == "Godkjent")
            rejected = sum(1 for d in self.decisions if d == "Ikke godkjent")
            remaining = sum(1 for d in self.decisions if d is None)
            App._set_label_text(self.lbl_st_godkjent, f"Godkjent: {approved}")
            App._set_label_text(self.lbl_st_ikkegodkjent, f"Ikke godkjent: {rejected}")
            App._set_label_text(self.lbl_st_gjen, f"Gjenstår å kontrollere: {remaining}")
        else:
            App._set_label_text(self.lbl_st_godkjent, "Godkjent: –")
            App._set_label_text(self.lbl_st_ikkegodkjent, "Ikke godkjent: –")
            App._set_label_text(self.lbl_st_gjen, "Gjenstår å kontrollere: –")

    def _start_progress(self, msg: str) -> None:
        self._progress_msg = msg
        self._progress_val = 0
        self._progress_running = True
        self._set_status(msg, 0)
        self._progress_job = self.after(100, self._progress_step)

    def _progress_step(self) -> None:
        if not self._progress_running:
            return
        self._progress_val = min(95, self._progress_val + 2)
        self._set_status(self._progress_msg, self._progress_val)
        self._progress_job = self.after(100, self._progress_step)

    def _finish_progress(self) -> None:
        self._progress_running = False
        if self._progress_job is not None:
            self.after_cancel(self._progress_job)
            self._progress_job = None
        self._set_status(self._progress_msg, 100)
        self.after(500, lambda: self._set_status(""))

    def _set_status(self, msg: str, progress: Optional[float] = None) -> None:
        if progress is not None:
            App._set_label_text(self.status_label, f"{msg} {progress:.0f}%")
            if hasattr(self.progress_bar, "setVisible"):
                self.progress_bar.setVisible(True)
                if hasattr(self.progress_bar, "setRange"):
                    self.progress_bar.setRange(0, 100)
                if hasattr(self.progress_bar, "setValue"):
                    self.progress_bar.setValue(int(progress))
        else:
            App._set_label_text(self.status_label, msg)
            if hasattr(self.progress_bar, "setVisible"):
                self.progress_bar.setVisible(False)

    def _show_inline(self, msg: str, ok: bool = True) -> None:
        color = style.get_color("success" if ok else "error")
        App._set_label_color(self.inline_status, color)
        App._set_label_text(self.inline_status, msg)
        if msg:
            self.after(3500, lambda: App._set_label_text(self.inline_status, ""))

    def _details_text_for_row(self, row_dict):
        self._ensure_helpers()
        lines = []
        for key in self.sample_df.columns:
            key_str = str(key)
            if key_str.startswith("_"):
                continue
            val = to_str(row_dict.get(key_str, "")).strip()
            if not val:
                continue
            if key_str.lower().startswith("faktura") and "nr" in key_str.lower():
                disp = val
            else:
                disp = format_number_with_thousands(val)
            lines.append(f"{key_str}: {disp}")
        return "\n".join(lines).strip()

    def _update_status_label(self, status: Optional[str], placeholder: str = "—") -> None:
        text = status if status else placeholder
        if status == "Godkjent":
            color = style.get_color("success")
        elif status == "Ikke godkjent":
            color = style.get_color("error")
        else:
            color = style.get_color("fg")
        App._set_label_color(self.lbl_status, color)
        App._set_label_text(self.lbl_status, text)

    def _update_status_card_safe(self) -> None:
        try:
            self._update_status_card()
        except Exception:  # pragma: no cover - defensive
            logger.exception("Feil ved oppdatering av statuskort")

    # ------------------------------------------------------------------
    # Rendering
    def render(self) -> None:
        self._ensure_helpers()
        self._update_counts_labels()
        gl_df = getattr(self, "gl_df", None)
        table_widget = getattr(self, "ledger_table", getattr(self, "ledger_tree", None))
        if self.sample_df is not None and len(self.sample_df) > 0:
            App._set_label_text(self.lbl_count, f"Bilag: {self.idx + 1}/{len(self.sample_df)}")
            inv_val = to_str(self.sample_df.iloc[self.idx].get(self.invoice_col, "")) if len(self.sample_df) > 0 else "—"
            App._set_label_text(self.lbl_invoice, f"Fakturanr: {inv_val or '—'}")
            status = self.decisions[self.idx] if (self.decisions and self.idx < len(self.decisions)) else None
            self._update_status_label(status)

            row_dict = self._current_row_dict()
            App._set_text_area(self.detail_box, self._details_text_for_row(row_dict), readonly=True)

            if gl_df is not None and inv_val:
                populate_ledger_table(self, inv_val)
            else:
                if hasattr(table_widget, "setRowCount"):
                    table_widget.setRowCount(0)
                msg = (
                    "Last gjerne også inn en hovedbok for å se bilagslinjene." if gl_df is None else ""
                )
                App._set_label_text(self.ledger_sum, msg)

            current_comment = self.comments[self.idx] if self.comments and self.idx < len(self.comments) else ""
            App._set_text_area(self.comment_box, current_comment)
        else:
            App._set_label_text(self.lbl_count, "Bilag: –/–")
            App._set_label_text(self.lbl_invoice, "Fakturanr: –")
            self._update_status_label(None, placeholder="–")
            App._set_text_area(self.detail_box, "Velg Excel-fil og lag et utvalg.", readonly=True)
            if hasattr(table_widget, "setRowCount"):
                table_widget.setRowCount(0)
            msg = (
                "Last gjerne også inn en hovedbok for å se bilagslinjene." if gl_df is None else "Trekk utvalg for å se bilagslinjene."
            )
            App._set_label_text(self.ledger_sum, msg)
            App._set_text_area(self.comment_box, "")

        if self.sample_df is None or len(self.sample_df) == 0:
            App._set_button_enabled(self.btn_prev, False)
            App._set_button_enabled(self.btn_next, False)
        else:
            App._set_button_enabled(self.btn_prev, self.idx > 0)
            App._set_button_enabled(self.btn_next, self.idx < len(self.sample_df) - 1)

        if (self.df is not None and len(self.df) > 0) or (self.sample_df is not None and len(self.sample_df) > 0):
            self._update_status_card_safe()

    # ------------------------------------------------------------------
    # Qt overrides
    def closeEvent(self, event) -> None:  # noqa: D401
        self._save_window_size()
        super().closeEvent(event)

    # ------------------------------------------------------------------
    # Løp løkke
    def mainloop(self) -> int:
        self.show()
        return self._qapp.exec()


__all__ = ["App", "style", "DEFAULT_APPEARANCE_MODE"]

