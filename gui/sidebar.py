from __future__ import annotations

from typing import Optional

from PyQt5 import QtCore, QtGui, QtWidgets

from helpers import logger
from helpers_path import resource_path

from .dropzone import DropZone
from .style import PADDING_Y, style

SIDEBAR_LOGO_WIDTH = 200


def parse_dropped_path(path: str) -> Optional[str]:
    path = (path or "").strip().strip("{}")
    if not path.lower().endswith((".xlsx", ".xls")):
        return None
    return path


class SidebarWidget(QtWidgets.QWidget):
    def __init__(self, app: "App"):
        super().__init__(app)
        self._app = app

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(style.PAD_XL, style.PAD_XL, style.PAD_XL, style.PAD_XL)
        layout.setSpacing(style.PAD_MD)

        title = QtWidgets.QLabel("⚙️ Datautvalg", self)
        title.setStyleSheet("font-weight: bold; font-size: 18px;")
        layout.addWidget(title)

        self.file_btn = QtWidgets.QPushButton("Velg leverandørfakturaer (Excel)…", self)
        self.file_btn.clicked.connect(app.choose_file)
        layout.addWidget(self.file_btn)

        self.inv_drop = DropZone(self, "Dra og slipp fakturaliste her")
        self.inv_drop.dropped.connect(self._on_invoice_drop)
        layout.addWidget(self.inv_drop)

        self.file_path_label = QtWidgets.QLabel("", self)
        self.file_path_label.setWordWrap(True)
        layout.addWidget(self.file_path_label)

        self.gl_btn = QtWidgets.QPushButton("Velg hovedbok (Excel)…", self)
        self.gl_btn.clicked.connect(app.choose_gl_file)
        layout.addWidget(self.gl_btn)

        self.gl_drop = DropZone(self, "Dra og slipp hovedbok her")
        self.gl_drop.dropped.connect(self._on_gl_drop)
        layout.addWidget(self.gl_drop)

        self.gl_path_label = QtWidgets.QLabel("", self)
        self.gl_path_label.setWordWrap(True)
        layout.addWidget(self.gl_path_label)

        # Sample ruter
        sample_box = QtWidgets.QGroupBox("Tilfeldig utvalg", self)
        sample_layout = QtWidgets.QFormLayout(sample_box)
        sample_layout.setContentsMargins(style.PAD_MD, style.PAD_MD, style.PAD_MD, style.PAD_MD)
        sample_layout.setSpacing(style.PAD_SM)

        self.sample_size_edit = QtWidgets.QLineEdit(self)
        self.sample_size_edit.setValidator(QtGui.QIntValidator(0, 999999, self))
        self.sample_size_edit.textChanged.connect(self._toggle_sample_btn)
        sample_layout.addRow("Antall", self.sample_size_edit)

        self.year_combo = QtWidgets.QComboBox(self)
        self.year_combo.currentTextChanged.connect(self._toggle_sample_btn)
        sample_layout.addRow("År", self.year_combo)

        layout.addWidget(sample_box)

        self.sample_btn = QtWidgets.QPushButton("🎲 Lag utvalg", self)
        self.sample_btn.setEnabled(False)
        self.sample_btn.clicked.connect(app.make_sample)
        layout.addWidget(self.sample_btn)

        self.filecount_label = QtWidgets.QLabel("Antall bilag: –", self)
        layout.addWidget(self.filecount_label)

        info_title = QtWidgets.QLabel("Oppdragsinfo", self)
        info_title.setStyleSheet("font-weight: bold;")
        layout.addWidget(info_title)

        info_frame = QtWidgets.QGroupBox(self)
        info_layout = QtWidgets.QFormLayout(info_frame)
        info_layout.setContentsMargins(style.PAD_MD, style.PAD_MD, style.PAD_MD, style.PAD_MD)
        info_layout.setSpacing(style.PAD_SM)

        self.kunde_edit = QtWidgets.QLineEdit(self)
        self.kunde_edit.setPlaceholderText("Hentes automatisk")
        self.kunde_edit.setEnabled(False)
        info_layout.addRow("Kunde", self.kunde_edit)

        self.utfort_av_edit = QtWidgets.QLineEdit(self)
        self.utfort_av_edit.textChanged.connect(lambda text: app.utfort_av_var.set(text))
        info_layout.addRow("Utført av", self.utfort_av_edit)

        info_hint = QtWidgets.QLabel("Kundenavn hentes automatisk", self)
        info_hint.setWordWrap(True)
        info_layout.addRow("", info_hint)

        layout.addWidget(info_frame)

        layout.addStretch(1)

        status_frame = QtWidgets.QGroupBox("Status", self)
        status_layout = QtWidgets.QVBoxLayout(status_frame)
        status_layout.setContentsMargins(style.PAD_MD, style.PAD_MD, style.PAD_MD, style.PAD_MD)
        status_layout.setSpacing(PADDING_Y)

        self.lbl_st_sum_kontrollert = QtWidgets.QLabel("Sum kontrollert: –", self)
        self.lbl_st_sum_alle = QtWidgets.QLabel("Sum alle bilag: –", self)
        self.lbl_st_pct = QtWidgets.QLabel("% kontrollert av sum: –", self)
        self.lbl_st_godkjent = QtWidgets.QLabel("Godkjent: –", self)
        self.lbl_st_ikkegodkjent = QtWidgets.QLabel("Ikke godkjent: –", self)
        self.lbl_st_gjen = QtWidgets.QLabel("Gjenstår å kontrollere: –", self)

        for lbl in (
            self.lbl_st_sum_kontrollert,
            self.lbl_st_sum_alle,
            self.lbl_st_pct,
            self.lbl_st_godkjent,
            self.lbl_st_ikkegodkjent,
            self.lbl_st_gjen,
        ):
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            status_layout.addWidget(lbl)

        layout.addWidget(status_frame)

        # Logo
        try:
            logo_path = resource_path("icons/borev_logo_lightmode.png")
            pix = QtGui.QPixmap(logo_path)
            if not pix.isNull():
                scaled = pix.scaledToWidth(SIDEBAR_LOGO_WIDTH, QtCore.Qt.SmoothTransformation)
                logo = QtWidgets.QLabel(self)
                logo.setPixmap(scaled)
                logo.setAlignment(QtCore.Qt.AlignCenter)
                layout.addWidget(logo)
        except Exception:  # pragma: no cover - bare logging
            logger.exception("Kunne ikke laste sidebar-logo")

        self._sync_from_app()

    def _sync_from_app(self) -> None:
        app = self._app
        self.file_path_label.setText(app.file_path_var.get())
        self.gl_path_label.setText(app.gl_path_var.get())
        self.sample_size_edit.setText(app.sample_size_var.get())
        self.year_combo.setCurrentText(app.year_var.get())
        self.kunde_edit.setText(app.kunde_var.get())
        self.utfort_av_edit.setText(app.utfort_av_var.get())
        app.lbl_st_sum_kontrollert = self.lbl_st_sum_kontrollert
        app.lbl_st_sum_alle = self.lbl_st_sum_alle
        app.lbl_st_pct = self.lbl_st_pct
        app.lbl_st_godkjent = self.lbl_st_godkjent
        app.lbl_st_ikkegodkjent = self.lbl_st_ikkegodkjent
        app.lbl_st_gjen = self.lbl_st_gjen
        app.sample_btn = self.sample_btn
        app.year_combo = self.year_combo
        app.kunde_entry = self.kunde_edit
        app.utfort_av_edit = self.utfort_av_edit
        app.lbl_filecount = self.filecount_label

    def _toggle_sample_btn(self) -> None:
        text = self.sample_size_edit.text().strip()
        year = self.year_combo.currentText().strip()
        enabled = bool(text) and bool(year)
        self.sample_btn.setEnabled(enabled)
        self._app.sample_size_var.set(text)
        self._app.year_var.set(year)

    def _on_invoice_drop(self, path: str) -> None:
        valid = parse_dropped_path(path)
        if valid:
            self._app.file_path_var.set(valid)
            self.file_path_label.setText(valid)
            self._app._load_excel()

    def _on_gl_drop(self, path: str) -> None:
        valid = parse_dropped_path(path)
        if valid:
            self._app.gl_path_var.set(valid)
            self.gl_path_label.setText(valid)
            self._app._load_gl_excel()

    # API for App
    def update_invoice_path(self, path: str) -> None:
        self.file_path_label.setText(path)

    def update_gl_path(self, path: str) -> None:
        self.gl_path_label.setText(path)

    def set_year_options(self, options: list[str]) -> None:
        self.year_combo.blockSignals(True)
        self.year_combo.clear()
        self.year_combo.addItems(options)
        self.year_combo.blockSignals(False)
        if options:
            self.year_combo.setCurrentIndex(0)

    def refresh_theme(self) -> None:
        self.inv_drop.refresh_theme()
        self.gl_drop.refresh_theme()
