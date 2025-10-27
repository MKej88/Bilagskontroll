from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .style import style
from .qt import qt_modules


@dataclass
class HeaderWidgets:
    container: Any
    count_label: Any
    status_label: Any
    status_value: Any
    invoice_label: Any
    copy_button: Any
    copy_feedback: Any
    inline_status: Any
    theme_label: Any
    theme_menu: Any


@dataclass
class ActionWidgets:
    container: Any
    approve_button: Any
    reject_button: Any
    open_po_button: Any
    prev_button: Any
    next_button: Any


@dataclass
class PaneWidgets:
    container: Any
    splitter: Any
    detail_box: Any
    ledger_table: Any
    ledger_sum: Any
    comment_box: Any


@dataclass
class BottomWidgets:
    container: Any
    export_button: Any
    status_label: Any
    progress_bar: Any


@dataclass
class MainWidgets:
    container: Any
    header: HeaderWidgets
    actions: ActionWidgets
    panes: PaneWidgets
    bottom: BottomWidgets


def _set_contents(layout, left: int, top: int, right: int, bottom: int) -> None:
    layout.setContentsMargins(left, top, right, bottom)
    layout.setSpacing(style.PAD_SM)


def _set_heading_font(label: QLabel, bold: bool = True) -> None:
    _, QtGui, _ = qt_modules()
    font = QtGui.QFont(style.FONT_FAMILY, 15 if bold else 14)
    font.setBold(bold)
    label.setFont(font)


def build_header(app) -> HeaderWidgets:
    QtCore, QtGui, QtWidgets = qt_modules()
    container = QtWidgets.QFrame(app.main_panel)
    layout = QtWidgets.QGridLayout(container)
    _set_contents(
        layout,
        style.PAD_MD,
        style.PAD_MD,
        style.PAD_MD,
        style.PAD_MD,
    )
    layout.setHorizontalSpacing(style.PAD_LG)

    count_label = QtWidgets.QLabel("Bilag: –/–", container)
    _set_heading_font(count_label)
    layout.addWidget(count_label, 0, 0)

    status_label = QtWidgets.QLabel("Status:", container)
    _set_heading_font(status_label, bold=False)
    layout.addWidget(status_label, 0, 1)

    status_value = QtWidgets.QLabel("–", container)
    status_value.setFont(QtGui.QFont(style.FONT_FAMILY, 15))
    layout.addWidget(status_value, 0, 2)

    invoice_label = QtWidgets.QLabel("Fakturanr: –", container)
    _set_heading_font(invoice_label, bold=False)
    layout.addWidget(invoice_label, 0, 3)

    copy_button = app.create_button(
        container,
        text="📋 Kopier fakturanr",
        command=app.copy_invoice,
    )
    layout.addWidget(copy_button, 0, 4)

    copy_feedback = QtWidgets.QLabel("", container)
    copy_feedback.setFont(QtGui.QFont(style.FONT_FAMILY, 13))
    layout.addWidget(copy_feedback, 0, 5)

    inline_status = QtWidgets.QLabel("", container)
    inline_status.setFont(QtGui.QFont(style.FONT_FAMILY, 13))
    layout.addWidget(inline_status, 0, 6)

    theme_label = QtWidgets.QLabel("Temavalg", container)
    theme_label.setFont(QtGui.QFont(style.FONT_FAMILY, 13))
    layout.addWidget(theme_label, 0, 7)

    theme_menu = QtWidgets.QComboBox(container)
    theme_menu.addItems(["Lys", "Mørk"])
    layout.addWidget(theme_menu, 0, 8)

    container.setObjectName("header")

    return HeaderWidgets(
        container,
        count_label,
        status_label,
        status_value,
        invoice_label,
        copy_button,
        copy_feedback,
        inline_status,
        theme_label,
        theme_menu,
    )


def build_action_buttons(app) -> ActionWidgets:
    QtCore, QtGui, QtWidgets = qt_modules()
    container = QtWidgets.QFrame(app.main_panel)
    layout = QtWidgets.QHBoxLayout(container)
    _set_contents(
        layout,
        style.PAD_MD,
        style.PAD_SM,
        style.PAD_MD,
        style.PAD_SM,
    )

    approve_button = app.create_button(
        container,
        text="✅ Godkjent",
        command=lambda: app.set_decision_and_next("Godkjent"),
        fg_color=style.get_color("success"),
        hover_color=style.get_color("success_hover"),
    )
    layout.addWidget(approve_button)

    reject_button = app.create_button(
        container,
        text="⛔ Ikke godkjent",
        command=lambda: app.set_decision_and_next("Ikke godkjent"),
        fg_color=style.get_color("error"),
        hover_color=style.get_color("error_hover"),
    )
    layout.addWidget(reject_button)

    open_po_button = app.create_button(
        container,
        text="🔗 Åpne PowerOffice",
        command=app.open_in_po,
    )
    layout.addWidget(open_po_button)

    prev_button = app.create_button(
        container,
        text="⬅ Forrige",
        command=app.prev,
    )
    layout.addWidget(prev_button)

    next_button = app.create_button(
        container,
        text="➡ Neste",
        command=app.next,
    )
    layout.addWidget(next_button)

    for widget in (
        approve_button,
        reject_button,
        open_po_button,
        prev_button,
        next_button,
    ):
        widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

    container.setObjectName("actions")

    return ActionWidgets(
        container,
        approve_button,
        reject_button,
        open_po_button,
        prev_button,
        next_button,
    )


def build_panes(app) -> PaneWidgets:
    QtCore, QtGui, QtWidgets = qt_modules()
    container = QtWidgets.QFrame(app.main_panel)
    layout = QtWidgets.QVBoxLayout(container)
    _set_contents(
        layout,
        style.PAD_MD,
        style.PAD_SM,
        style.PAD_MD,
        style.PAD_SM,
    )

    splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, container)
    splitter.setChildrenCollapsible(False)
    splitter.setObjectName("main_splitter")

    # Venstre panel – detaljer
    left_panel = QtWidgets.QFrame(splitter)
    left_layout = QtWidgets.QVBoxLayout(left_panel)
    _set_contents(
        left_layout,
        style.PAD_MD,
        style.PAD_SM,
        style.PAD_MD,
        style.PAD_SM,
    )
    details_label = QtWidgets.QLabel("Detaljer for bilag", left_panel)
    _set_heading_font(details_label)
    left_layout.addWidget(details_label)

    detail_box = QtWidgets.QTextEdit(left_panel)
    detail_box.setReadOnly(True)
    detail_box.setMinimumHeight(200)
    left_layout.addWidget(detail_box, 1)

    # Høyre panel – hovedbok
    right_panel = QtWidgets.QFrame(splitter)
    right_layout = QtWidgets.QVBoxLayout(right_panel)
    _set_contents(
        right_layout,
        style.PAD_MD,
        style.PAD_SM,
        style.PAD_MD,
        style.PAD_SM,
    )
    ledger_label = QtWidgets.QLabel("Hovedbok (bilagslinjer)", right_panel)
    _set_heading_font(ledger_label)
    right_layout.addWidget(ledger_label)

    ledger_table = QtWidgets.QTableWidget(right_panel)
    ledger_table.setColumnCount(len(app.ledger_cols))
    ledger_table.setHorizontalHeaderLabels(app.ledger_cols)
    ledger_table.setAlternatingRowColors(True)
    ledger_table.horizontalHeader().setStretchLastSection(True)
    ledger_table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
    ledger_table.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
    right_layout.addWidget(ledger_table, 4)

    comment_label = QtWidgets.QLabel("Kommentar", right_panel)
    _set_heading_font(comment_label, bold=False)
    right_layout.addWidget(comment_label)

    comment_box = QtWidgets.QTextEdit(right_panel)
    comment_box.setMinimumHeight(120)
    right_layout.addWidget(comment_box, 1)

    ledger_sum = QtWidgets.QLabel("", right_panel)
    ledger_sum.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
    right_layout.addWidget(ledger_sum)

    splitter.addWidget(left_panel)
    splitter.addWidget(right_panel)
    splitter.setSizes([600, 600])

    layout.addWidget(splitter, 1)

    container.setObjectName("panes")

    return PaneWidgets(
        container,
        splitter,
        detail_box,
        ledger_table,
        ledger_sum,
        comment_box,
    )


def build_bottom(app) -> BottomWidgets:
    QtCore, QtGui, QtWidgets = qt_modules()
    container = QtWidgets.QFrame(app.main_panel)
    layout = QtWidgets.QGridLayout(container)
    _set_contents(
        layout,
        style.PAD_MD,
        style.PAD_SM,
        style.PAD_MD,
        style.PAD_SM,
    )

    export_button = app.create_button(
        container,
        text="📄 Eksporter PDF rapport",
        command=app.export_pdf,
    )
    export_button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
    layout.addWidget(export_button, 0, 0)

    status_label = QtWidgets.QLabel("", container)
    layout.addWidget(status_label, 0, 1)

    progress_bar = QtWidgets.QProgressBar(container)
    progress_bar.setValue(0)
    progress_bar.setVisible(False)
    layout.addWidget(progress_bar, 0, 2)

    layout.setColumnStretch(1, 1)

    container.setObjectName("bottom")

    return BottomWidgets(container, export_button, status_label, progress_bar)


def build_main(app) -> MainWidgets:
    QtCore, QtGui, QtWidgets = qt_modules()
    container = QtWidgets.QFrame(app.central_widget)
    container.setObjectName("main_view")
    layout = QtWidgets.QVBoxLayout(container)
    _set_contents(
        layout,
        0,
        0,
        0,
        0,
    )
    layout.setSpacing(style.PAD_MD)

    header = build_header(app)
    actions = build_action_buttons(app)
    panes = build_panes(app)
    bottom = build_bottom(app)

    layout.addWidget(header.container)
    layout.addWidget(actions.container)
    layout.addWidget(panes.container, 1)
    layout.addWidget(bottom.container)

    return MainWidgets(container, header, actions, panes, bottom)


def populate_ledger_table(app, invoice_value: str) -> None:
    from helpers import parse_amount, fmt_money
    from .ledger import ledger_rows

    QtCore, QtGui, QtWidgets = qt_modules()
    table = getattr(app, "ledger_table", getattr(app, "ledger_tree", None))
    rows = ledger_rows(app, invoice_value)

    def _set_label(widget, text: str) -> None:
        if hasattr(widget, "setText"):
            widget.setText(text)
        elif hasattr(widget, "configure"):
            widget.configure(text=text)

    if table is None:
        _set_label(app.ledger_sum, "")
        return

    if hasattr(table, "setRowCount"):
        table.setRowCount(0)
        if not rows:
            message = (
                "Ingen hovedbok lastet." if app.gl_df is None else "Ingen bilagslinjer for dette bilagsnummeret."
            )
            _set_label(app.ledger_sum, message)
            return

        total = 0
        table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            for col_idx, col in enumerate(app.ledger_cols):
                item = QtWidgets.QTableWidgetItem(str(row.get(col, "")))
                if col in {"Beløp", "MVA-beløp"}:
                    item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                table.setItem(row_idx, col_idx, item)
            value = parse_amount(row.get("Beløp"))
            if value is not None:
                total += value
        _set_label(app.ledger_sum, f"Sum beløp: {fmt_money(total)}   •   Linjer: {len(rows)}")
        table.resizeColumnsToContents()
        return

    # Fallback for tester som bruker Tk-lignende stubs
    for item in getattr(table, "get_children", lambda: [])():
        table.delete(item)
    if not rows:
        message = (
            "Ingen hovedbok lastet." if app.gl_df is None else "Ingen bilagslinjer for dette bilagsnummeret."
        )
        _set_label(app.ledger_sum, message)
        return

    total = 0
    for row in rows:
        values = [row.get(col, "") for col in app.ledger_cols]
        table.insert("", "end", values=values)
        value = parse_amount(row.get("Beløp"))
        if value is not None:
            total += value
    _set_label(app.ledger_sum, f"Sum beløp: {fmt_money(total)}   •   Linjer: {len(rows)}")


def resize_splitter_to_content(splitter) -> None:
    sizes = splitter.sizes()
    if not sizes:
        return
    total = sum(sizes)
    if total <= 0:
        splitter.setSizes([600, 600])

