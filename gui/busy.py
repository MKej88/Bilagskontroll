from __future__ import annotations

import threading

from helpers import logger

from .style import PADDING_X, PADDING_Y
from .qt import qt_modules


def run_in_thread(func, *args):
    """Start ``func`` i bakgrunnstråd."""

    thread = threading.Thread(target=func, args=args, daemon=True)
    thread.start()
    return thread


def show_busy(app, message: str):
    QtCore, QtGui, QtWidgets = qt_modules()
    dialog = QtWidgets.QDialog(app)
    dialog.setWindowModality(QtCore.Qt.ApplicationModal)
    dialog.setWindowTitle("")
    dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    dialog.setFixedWidth(320)

    layout = QtWidgets.QVBoxLayout(dialog)
    layout.setContentsMargins(PADDING_X * 2, PADDING_Y * 2, PADDING_X * 2, PADDING_Y * 2)
    layout.setSpacing(PADDING_Y)

    progress = QtWidgets.QProgressBar(dialog)
    progress.setRange(0, 0)
    layout.addWidget(progress)

    layout.addWidget(QtWidgets.QLabel(message, dialog))

    dialog.show()
    dialog.activateWindow()

    app._busy_dialog = dialog
    return dialog


def hide_busy(app) -> None:
    dialog = getattr(app, "_busy_dialog", None)
    if dialog is not None:
        try:
            dialog.close()
        except Exception as exc:  # pragma: no cover - Qt-specifikke feil
            logger.debug(f"Kunne ikke lukke ventedialog: {exc}")
        finally:
            app._busy_dialog = None

