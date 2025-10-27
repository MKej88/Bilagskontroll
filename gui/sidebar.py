from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Callable

from helpers import logger

from .dropzone import DropZone
from .qt import qt_modules
from .style import style


@dataclass
class SidebarWidgets:
    container: Any
    choose_invoice_btn: Any
    invoice_drop: DropZone
    invoice_path_label: Any
    choose_gl_btn: Any
    gl_drop: DropZone
    gl_path_label: Any
    sample_size_input: Any
    year_combo: Any
    sample_button: Any
    filecount_label: Any
    customer_input: Any
    performed_by_input: Any
    status_sum_kontrollert: Any
    status_sum_alle: Any
    status_pct: Any
    status_godkjent: Any
    status_ikkegodkjent: Any
    status_gjen: Any


def _is_excel(path: str) -> bool:
    return path.lower().endswith((".xlsx", ".xls"))


def _handle_drop(paths: list[str], callback: Callable[[str], None]) -> None:
    for path in paths:
        if _is_excel(path):
            callback(path)
            return
    logger.info("Ignorerer drop uten Excel-filer")


def build_sidebar(app) -> SidebarWidgets:
    QtCore, QtGui, QtWidgets = qt_modules()
    container = QtWidgets.QFrame(app.central_widget)
    container.setObjectName("sidebar")
    layout = QtWidgets.QVBoxLayout(container)
    layout.setContentsMargins(style.PAD_XL, style.PAD_XL, style.PAD_XL, style.PAD_XL)
    layout.setSpacing(style.PAD_MD)

    title = QtWidgets.QLabel("⚙️ Datautvalg", container)
    title_font = title.font()
    title_font.setPointSize(18)
    title_font.setBold(True)
    title.setFont(title_font)
    layout.addWidget(title)

    choose_invoice_btn = app.create_button(
        container,
        text="Velg leverandørfakturaer (Excel)…",
        command=app.choose_file,
    )
    layout.addWidget(choose_invoice_btn)

    invoice_drop = DropZone(
        "Dra og slipp fakturaliste her",
        lambda paths: _handle_drop(paths, app.handle_invoice_drop),
        container,
    )
    layout.addWidget(invoice_drop)

    invoice_path_label = QtWidgets.QLabel("", container)
    invoice_path_label.setWordWrap(True)
    layout.addWidget(invoice_path_label)

    choose_gl_btn = app.create_button(
        container,
        text="Velg hovedbok (Excel)…",
        command=app.choose_gl_file,
    )
    layout.addWidget(choose_gl_btn)

    gl_drop = DropZone(
        "Dra og slipp hovedbok her",
        lambda paths: _handle_drop(paths, app.handle_gl_drop),
        container,
    )
    layout.addWidget(gl_drop)

    gl_path_label = QtWidgets.QLabel("", container)
    gl_path_label.setWordWrap(True)
    layout.addWidget(gl_path_label)

    sample_form = QtWidgets.QFormLayout()
    sample_form.setSpacing(style.PAD_SM)
    sample_form.setLabelAlignment(QtCore.Qt.AlignLeft)

    sample_size_input = QtWidgets.QLineEdit(container)
    sample_size_input.setPlaceholderText("Antall i utvalg")
    sample_size_input.setFixedWidth(120)
    sample_size_input.setValidator(app.int_validator)
    sample_form.addRow("Antall tilfeldig utvalg", sample_size_input)

    year_combo = QtWidgets.QComboBox(container)
    year_combo.setEditable(False)
    year_combo.currentTextChanged.connect(app._toggle_sample_btn)
    sample_form.addRow("År", year_combo)

    layout.addLayout(sample_form)

    sample_button = app.create_button(
        container,
        text="🎲 Lag utvalg",
        command=app.make_sample,
    )
    sample_button.setEnabled(False)
    layout.addWidget(sample_button)

    filecount_label = QtWidgets.QLabel("Antall bilag: –", container)
    layout.addWidget(filecount_label)

    info_label = QtWidgets.QLabel("Oppdragsinfo", container)
    info_font = info_label.font()
    info_font.setBold(True)
    info_label.setFont(info_font)
    layout.addWidget(info_label)

    info_grid = QtWidgets.QGridLayout()
    info_grid.setSpacing(style.PAD_SM)
    info_grid.setContentsMargins(0, 0, 0, 0)

    customer_input = QtWidgets.QLineEdit(container)
    customer_input.setPlaceholderText("Hentes automatisk")
    customer_input.setEnabled(False)
    info_grid.addWidget(QtWidgets.QLabel("Kunde", container), 0, 0)
    info_grid.addWidget(customer_input, 0, 1)

    performed_by_input = QtWidgets.QLineEdit(container)
    default_user = os.environ.get("USERNAME") or os.environ.get("USER") or ""
    performed_by_input.setText(default_user)
    info_grid.addWidget(QtWidgets.QLabel("Utført av", container), 1, 0)
    info_grid.addWidget(performed_by_input, 1, 1)

    layout.addLayout(info_grid)

    status_card = QtWidgets.QFrame(container)
    status_card.setObjectName("status_card")
    status_layout = QtWidgets.QVBoxLayout(status_card)
    status_layout.setContentsMargins(style.PAD_MD, style.PAD_MD, style.PAD_MD, style.PAD_MD)
    status_layout.setSpacing(style.PAD_XS)

    body_font = container.font()
    body_font.setPointSize(13)

    status_title = QtWidgets.QLabel("Status", status_card)
    status_title_font = status_title.font()
    status_title_font.setBold(True)
    status_title.setFont(status_title_font)
    status_title.setAlignment(QtCore.Qt.AlignCenter)
    status_layout.addWidget(status_title)

    status_sum_kontrollert = QtWidgets.QLabel("Sum kontrollert: –", status_card)
    status_sum_kontrollert.setFont(body_font)
    status_sum_kontrollert.setAlignment(QtCore.Qt.AlignCenter)
    status_layout.addWidget(status_sum_kontrollert)

    status_sum_alle = QtWidgets.QLabel("Sum alle bilag: –", status_card)
    status_sum_alle.setFont(body_font)
    status_sum_alle.setAlignment(QtCore.Qt.AlignCenter)
    status_layout.addWidget(status_sum_alle)

    status_pct = QtWidgets.QLabel("% kontrollert av sum: –", status_card)
    status_pct.setFont(body_font)
    status_pct.setAlignment(QtCore.Qt.AlignCenter)
    status_layout.addWidget(status_pct)

    status_godkjent = QtWidgets.QLabel("Godkjent: –", status_card)
    status_godkjent.setFont(body_font)
    status_godkjent.setAlignment(QtCore.Qt.AlignCenter)
    status_layout.addWidget(status_godkjent)

    status_ikkegodkjent = QtWidgets.QLabel("Ikke godkjent: –", status_card)
    status_ikkegodkjent.setFont(body_font)
    status_ikkegodkjent.setAlignment(QtCore.Qt.AlignCenter)
    status_layout.addWidget(status_ikkegodkjent)

    status_gjen = QtWidgets.QLabel("Gjenstår å kontrollere: –", status_card)
    status_gjen.setFont(body_font)
    status_gjen.setAlignment(QtCore.Qt.AlignCenter)
    status_layout.addWidget(status_gjen)

    layout.addWidget(status_card)
    layout.addStretch(1)

    return SidebarWidgets(
        container,
        choose_invoice_btn,
        invoice_drop,
        invoice_path_label,
        choose_gl_btn,
        gl_drop,
        gl_path_label,
        sample_size_input,
        year_combo,
        sample_button,
        filecount_label,
        customer_input,
        performed_by_input,
        status_sum_kontrollert,
        status_sum_alle,
        status_pct,
        status_godkjent,
        status_ikkegodkjent,
        status_gjen,
    )


def update_file_labels(app) -> None:
    if hasattr(app, "sidebar"):
        app.sidebar.invoice_path_label.setText(app.file_path or "")
        app.sidebar.gl_path_label.setText(app.gl_path or "")

