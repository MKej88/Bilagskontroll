from __future__ import annotations

from PyQt5 import QtCore, QtGui, QtWidgets

from .ledger import LedgerTable
from .style import PADDING_Y, style


class PlainTextBox(QtWidgets.QPlainTextEdit):
    def __init__(self, parent: QtWidgets.QWidget, read_only: bool = False):
        super().__init__(parent)
        self.setReadOnly(read_only)
        self.setMinimumHeight(140)

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
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, style.PAD_XL, style.PAD_XL, style.PAD_XL)
        layout.setSpacing(style.PAD_LG)

        header = self._build_header()
        layout.addWidget(header)

        stats = self._build_stats_strip()
        layout.addWidget(stats)

        actions = self._build_action_buttons()
        layout.addWidget(actions)

        split = self._build_panes()
        layout.addWidget(split, 1)

        bottom = self._build_bottom()
        layout.addWidget(bottom)

    def _build_header(self) -> QtWidgets.QWidget:
        app = self._app
        frame = QtWidgets.QFrame(self)
        frame.setObjectName("HeaderFrame")
        frame.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        layout = QtWidgets.QHBoxLayout(frame)
        layout.setContentsMargins(style.PAD_XL, style.PAD_LG, style.PAD_XL, style.PAD_LG)
        layout.setSpacing(style.PAD_LG)

        title_column = QtWidgets.QVBoxLayout()
        title_column.setSpacing(style.PAD_XXS)

        headline = QtWidgets.QLabel("Bilagskontroll", frame)
        headline.setObjectName("HeaderTitle")
        title_column.addWidget(headline)

        subtitle = QtWidgets.QLabel("Kontroller og dokumenter leverandørbilag raskt", frame)
        subtitle.setObjectName("HeaderSubtitle")
        title_column.addWidget(subtitle)
        title_column.addStretch(1)

        layout.addLayout(title_column, 1)

        controls = QtWidgets.QHBoxLayout()
        controls.setSpacing(style.PAD_SM)

        theme_label = QtWidgets.QLabel("Tema", frame)
        theme_label.setProperty("role", "muted")
        controls.addWidget(theme_label)

        app.theme_menu = QtWidgets.QComboBox(frame)
        app.theme_menu.addItems(["Light", "Dark"])
        app.theme_menu.currentTextChanged.connect(app._switch_theme)
        app.theme_menu.setFixedWidth(120)
        controls.addWidget(app.theme_menu)

        layout.addLayout(controls)
        return frame

    def _build_stats_strip(self) -> QtWidgets.QWidget:
        app = self._app
        container = QtWidgets.QWidget(self)
        outer = QtWidgets.QVBoxLayout(container)
        outer.setContentsMargins(style.PAD_LG, style.PAD_MD, style.PAD_LG, style.PAD_MD)
        outer.setSpacing(style.PAD_SM)

        cards = QtWidgets.QHBoxLayout()
        cards.setSpacing(style.PAD_MD)

        count_card, count_label = self._make_stat_card(container, "Bilag i utvalg")
        app.lbl_count = count_label
        cards.addWidget(count_card)

        status_card, status_label = self._make_stat_card(container, "Status")
        app.lbl_status = status_label
        cards.addWidget(status_card)

        invoice_card, invoice_label, feedback_label = self._make_invoice_card(container)
        app.lbl_invoice = invoice_label
        app.copy_feedback = feedback_label
        cards.addWidget(invoice_card)

        outer.addLayout(cards)

        inline = QtWidgets.QLabel("", container)
        inline.setObjectName("InlineStatus")
        inline.setProperty("role", "muted")
        outer.addWidget(inline)
        app.inline_status = inline

        return container

    def _make_stat_card(
        self, parent: QtWidgets.QWidget, title: str
    ) -> tuple[QtWidgets.QFrame, QtWidgets.QLabel]:
        card = QtWidgets.QFrame(parent)
        card.setProperty("role", "card")
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(style.PAD_MD, style.PAD_MD, style.PAD_MD, style.PAD_MD)
        card_layout.setSpacing(style.PAD_XS)

        caption = QtWidgets.QLabel(title, card)
        caption.setProperty("role", "caption")
        card_layout.addWidget(caption)

        value = QtWidgets.QLabel("–", card)
        value.setObjectName("InfoCardValue")
        value.setProperty("role", "value")
        card_layout.addWidget(value)

        return card, value

    def _make_invoice_card(
        self, parent: QtWidgets.QWidget
    ) -> tuple[QtWidgets.QFrame, QtWidgets.QLabel, QtWidgets.QLabel]:
        card = QtWidgets.QFrame(parent)
        card.setProperty("role", "card")
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(style.PAD_MD, style.PAD_MD, style.PAD_MD, style.PAD_MD)
        card_layout.setSpacing(style.PAD_XS)

        caption = QtWidgets.QLabel("Aktivt bilag", card)
        caption.setProperty("role", "caption")
        card_layout.addWidget(caption)

        row = QtWidgets.QHBoxLayout()
        row.setSpacing(style.PAD_XS)

        label = QtWidgets.QLabel("Fakturanr: –", card)
        label.setObjectName("InfoCardValue")
        label.setProperty("role", "value")
        row.addWidget(label, 1)

        copy_btn = QtWidgets.QToolButton(card)
        copy_btn.setProperty("role", "icon")
        copy_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        copy_icon = card.style().standardIcon(QtWidgets.QStyle.SP_FileDialogDetailedView)
        copy_btn.setIcon(QtGui.QIcon.fromTheme("edit-copy", copy_icon))
        copy_btn.setToolTip("Kopier fakturanummer")
        copy_btn.clicked.connect(self._app.copy_invoice)
        copy_btn.setIconSize(QtCore.QSize(18, 18))
        row.addWidget(copy_btn)

        card_layout.addLayout(row)

        feedback = QtWidgets.QLabel("", card)
        feedback.setObjectName("InlineFeedback")
        feedback.setProperty("role", "muted")
        card_layout.addWidget(feedback)

        return card, label, feedback

    def _build_action_buttons(self) -> QtWidgets.QWidget:
        app = self._app
        widget = QtWidgets.QFrame(self)
        widget.setObjectName("ActionBar")
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(style.PAD_LG, 0, style.PAD_LG, 0)
        layout.setSpacing(style.PAD_SM)

        primary_group = QtWidgets.QHBoxLayout()
        primary_group.setSpacing(style.PAD_SM)

        approve = QtWidgets.QPushButton("Godkjenn", widget)
        approve.setProperty("role", "primary")
        approve.setIcon(widget.style().standardIcon(QtWidgets.QStyle.SP_DialogApplyButton))
        approve.clicked.connect(lambda: app.set_decision_and_next("Godkjent"))
        primary_group.addWidget(approve)

        reject = QtWidgets.QPushButton("Ikke godkjent", widget)
        reject.setProperty("role", "danger")
        reject.setIcon(widget.style().standardIcon(QtWidgets.QStyle.SP_DialogCancelButton))
        reject.clicked.connect(lambda: app.set_decision_and_next("Ikke godkjent"))
        primary_group.addWidget(reject)

        open_po = QtWidgets.QPushButton("Åpne PowerOffice", widget)
        open_po.setProperty("role", "secondary")
        open_po.setIcon(widget.style().standardIcon(QtWidgets.QStyle.SP_DirLinkIcon))
        open_po.clicked.connect(app.open_in_po)
        primary_group.addWidget(open_po)

        layout.addLayout(primary_group)
        layout.addStretch(1)

        nav_group = QtWidgets.QHBoxLayout()
        nav_group.setSpacing(style.PAD_SM)

        app.btn_prev = QtWidgets.QPushButton("Forrige", widget)
        app.btn_prev.setProperty("role", "ghost")
        app.btn_prev.setIcon(widget.style().standardIcon(QtWidgets.QStyle.SP_ArrowBack))
        app.btn_prev.clicked.connect(app.prev)
        app.btn_prev.setIconSize(QtCore.QSize(18, 18))
        nav_group.addWidget(app.btn_prev)

        app.btn_next = QtWidgets.QPushButton("Neste", widget)
        app.btn_next.setProperty("role", "ghost")
        app.btn_next.setIcon(widget.style().standardIcon(QtWidgets.QStyle.SP_ArrowForward))
        app.btn_next.clicked.connect(app.next)
        app.btn_next.setIconSize(QtCore.QSize(18, 18))
        nav_group.addWidget(app.btn_next)

        layout.addLayout(nav_group)
        return widget

    def _build_panes(self) -> QtWidgets.QWidget:
        app = self._app
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, self)
        splitter.setObjectName("MainSplitter")

        left = QtWidgets.QFrame(splitter)
        left_layout = QtWidgets.QVBoxLayout(left)
        left_layout.setContentsMargins(style.PAD_MD, 0, style.PAD_MD, 0)
        left_layout.setSpacing(PADDING_Y)

        detail_caption = QtWidgets.QLabel("Detaljer for bilag", left)
        detail_caption.setProperty("role", "caption")
        left_layout.addWidget(detail_caption)

        app.detail_box = PlainTextBox(left, read_only=True)
        left_layout.addWidget(app.detail_box, 1)

        right = QtWidgets.QFrame(splitter)
        right_layout = QtWidgets.QVBoxLayout(right)
        right_layout.setContentsMargins(style.PAD_MD, 0, style.PAD_MD, 0)
        right_layout.setSpacing(PADDING_Y)

        ledger_caption = QtWidgets.QLabel("Hovedbok (bilagslinjer)", right)
        ledger_caption.setProperty("role", "caption")
        right_layout.addWidget(ledger_caption)

        app.ledger_table = LedgerTable(right)
        right_layout.addWidget(app.ledger_table, 3)

        app.ledger_sum = QtWidgets.QLabel("", right)
        app.ledger_sum.setProperty("role", "muted")
        right_layout.addWidget(app.ledger_sum)

        comment_caption = QtWidgets.QLabel("Kommentar", right)
        comment_caption.setProperty("role", "caption")
        right_layout.addWidget(comment_caption)

        app.comment_box = PlainTextBox(right, read_only=False)
        right_layout.addWidget(app.comment_box, 1)

        splitter.setSizes([3, 5])
        app.right_frame = right
        return splitter

    def _build_bottom(self) -> QtWidgets.QWidget:
        app = self._app
        widget = QtWidgets.QFrame(self)
        widget.setObjectName("FooterBar")
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(style.PAD_LG, 0, style.PAD_LG, 0)
        layout.setSpacing(style.PAD_SM)

        export_btn = QtWidgets.QPushButton("Eksporter PDF", widget)
        export_btn.setProperty("role", "primary")
        export_btn.setIcon(widget.style().standardIcon(QtWidgets.QStyle.SP_DialogSaveButton))
        export_btn.clicked.connect(app.export_pdf)
        layout.addWidget(export_btn)

        app.status_label = QtWidgets.QLabel("", widget)
        app.status_label.setObjectName("StatusLabel")
        app.status_label.setProperty("role", "muted")
        layout.addWidget(app.status_label, 1)

        app.progress_bar = QtWidgets.QProgressBar(widget)
        app.progress_bar.setObjectName("StatusProgress")
        app.progress_bar.setMaximumWidth(220)
        app.progress_bar.setRange(0, 100)
        app.progress_bar.setVisible(False)
        app.progress_bar.setTextVisible(False)
        layout.addWidget(app.progress_bar)

        return widget

    def refresh_theme(self) -> None:
        # Qt stylesheets oppdateres globalt, men vi sørger for at tekstbokser følger temaet.
        for box in (self._app.detail_box, self._app.comment_box):
            if isinstance(box, PlainTextBox):
                box.viewport().setAutoFillBackground(False)
