from __future__ import annotations

from PyQt5 import QtWidgets

from .ledger import LedgerTable
from .style import PADDING_Y, style


class PlainTextBox(QtWidgets.QPlainTextEdit):
    def __init__(self, parent: QtWidgets.QWidget, read_only: bool = False):
        super().__init__(parent)
        self.setReadOnly(read_only)
        self.setMinimumHeight(120)

    # Tk-kompatible hjelpere
    def configure(self, **kwargs):
        state = kwargs.get("state")
        if state == "disabled":
            self.setReadOnly(True)
        elif state == "normal":
            self.setReadOnly(False)

    def delete(self, *_):
        self.clear()

    def insert(self, *_args):
        text = _args[-1] if _args else ""
        self.setPlainText(text)

    def get(self, *_):
        return self.toPlainText()


class MainView(QtWidgets.QWidget):
    def __init__(self, app: "App"):
        super().__init__(app)
        self._app = app

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, style.PAD_XL, style.PAD_XL, style.PAD_XL)
        layout.setSpacing(style.PAD_MD)

        header = self._build_header()
        layout.addWidget(header)

        actions = self._build_action_buttons()
        layout.addWidget(actions)

        split = self._build_panes()
        layout.addWidget(split, 1)

        bottom = self._build_bottom()
        layout.addWidget(bottom)

    def _build_header(self) -> QtWidgets.QWidget:
        app = self._app
        widget = QtWidgets.QWidget(self)
        layout = QtWidgets.QGridLayout(widget)
        layout.setContentsMargins(style.PAD_LG, style.PAD_MD, style.PAD_LG, style.PAD_MD)
        layout.setHorizontalSpacing(style.PAD_MD)
        layout.setColumnStretch(6, 1)

        app.lbl_count = QtWidgets.QLabel("Bilag: –/–", widget)
        layout.addWidget(app.lbl_count, 0, 0)

        app.lbl_status_label = QtWidgets.QLabel("Status:", widget)
        layout.addWidget(app.lbl_status_label, 0, 1)

        app.lbl_status = QtWidgets.QLabel("–", widget)
        layout.addWidget(app.lbl_status, 0, 2)

        app.lbl_invoice = QtWidgets.QLabel("Fakturanr: –", widget)
        layout.addWidget(app.lbl_invoice, 0, 3)

        copy_btn = QtWidgets.QPushButton("📋 Kopier fakturanr", widget)
        copy_btn.clicked.connect(app.copy_invoice)
        layout.addWidget(copy_btn, 0, 4)

        app.copy_feedback = QtWidgets.QLabel("", widget)
        layout.addWidget(app.copy_feedback, 0, 5)

        app.inline_status = QtWidgets.QLabel("", widget)
        layout.addWidget(app.inline_status, 0, 6)

        theme_label = QtWidgets.QLabel("Tema", widget)
        layout.addWidget(theme_label, 0, 7)

        app.theme_menu = QtWidgets.QComboBox(widget)
        app.theme_menu.addItems(["Light", "Dark"])
        app.theme_menu.currentTextChanged.connect(app._switch_theme)
        layout.addWidget(app.theme_menu, 0, 8)

        return widget

    def _build_action_buttons(self) -> QtWidgets.QWidget:
        app = self._app
        widget = QtWidgets.QWidget(self)
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(style.PAD_LG, 0, style.PAD_LG, 0)
        layout.setSpacing(style.PAD_SM)

        approve = QtWidgets.QPushButton("✅ Godkjent", widget)
        approve.clicked.connect(lambda: app.set_decision_and_next("Godkjent"))
        layout.addWidget(approve)

        reject = QtWidgets.QPushButton("⛔ Ikke godkjent", widget)
        reject.clicked.connect(lambda: app.set_decision_and_next("Ikke godkjent"))
        layout.addWidget(reject)

        open_po = QtWidgets.QPushButton("🔗 Åpne PowerOffice", widget)
        open_po.clicked.connect(app.open_in_po)
        layout.addWidget(open_po)

        app.btn_prev = QtWidgets.QPushButton("⬅ Forrige", widget)
        app.btn_prev.clicked.connect(app.prev)
        layout.addWidget(app.btn_prev)

        app.btn_next = QtWidgets.QPushButton("➡ Neste", widget)
        app.btn_next.clicked.connect(app.next)
        layout.addWidget(app.btn_next)

        return widget

    def _build_panes(self) -> QtWidgets.QWidget:
        app = self._app
        widget = QtWidgets.QWidget(self)
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(style.PAD_LG, 0, style.PAD_LG, 0)
        layout.setSpacing(style.PAD_MD)

        # Venstre panel
        left = QtWidgets.QWidget(widget)
        left_layout = QtWidgets.QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(PADDING_Y)

        left_layout.addWidget(QtWidgets.QLabel("Detaljer for bilag", left))

        app.detail_box = PlainTextBox(left, read_only=True)
        left_layout.addWidget(app.detail_box, 1)

        layout.addWidget(left, 1)

        # Høyre panel
        right = QtWidgets.QWidget(widget)
        right_layout = QtWidgets.QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(PADDING_Y)

        right_layout.addWidget(QtWidgets.QLabel("Hovedbok (bilagslinjer)", right))

        app.ledger_table = LedgerTable(right)
        right_layout.addWidget(app.ledger_table, 3)

        app.ledger_sum = QtWidgets.QLabel("", right)
        right_layout.addWidget(app.ledger_sum)

        right_layout.addWidget(QtWidgets.QLabel("Kommentar", right))

        app.comment_box = PlainTextBox(right, read_only=False)
        right_layout.addWidget(app.comment_box, 1)

        layout.addWidget(right, 1)
        app.right_frame = right
        return widget

    def _build_bottom(self) -> QtWidgets.QWidget:
        app = self._app
        widget = QtWidgets.QWidget(self)
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(style.PAD_LG, 0, style.PAD_LG, 0)
        layout.setSpacing(style.PAD_SM)

        export_btn = QtWidgets.QPushButton("📄 Eksporter PDF rapport", widget)
        export_btn.clicked.connect(app.export_pdf)
        layout.addWidget(export_btn)

        app.status_label = QtWidgets.QLabel("", widget)
        layout.addWidget(app.status_label, 1)

        app.progress_bar = QtWidgets.QProgressBar(widget)
        app.progress_bar.setMaximumWidth(200)
        app.progress_bar.setRange(0, 100)
        app.progress_bar.setVisible(False)
        layout.addWidget(app.progress_bar)

        return widget
