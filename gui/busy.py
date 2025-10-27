from __future__ import annotations

import threading
from typing import Callable, Optional

from PyQt5 import QtCore, QtWidgets

from .style import PADDING_X, PADDING_Y


class _Worker(QtCore.QThread):
    finished = QtCore.pyqtSignal(object)
    failed = QtCore.pyqtSignal(Exception)

    def __init__(self, func: Callable, *args, **kwargs) -> None:
        super().__init__()
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def run(self) -> None:  # noqa: D401 - PyQt signatur
        try:
            result = self._func(*self._args, **self._kwargs)
        except Exception as exc:  # pragma: no cover - propagert til GUI
            self.failed.emit(exc)
        else:
            self.finished.emit(result)


def run_in_thread(func: Callable, *args, **kwargs) -> threading.Thread:
    """Behold API fra Tk-versjonen for bakoverkompatibilitet."""

    thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
    thread.start()
    return thread


def start_worker(func: Callable, *args, on_success: Callable[[object], None], on_error: Callable[[Exception], None], **kwargs) -> _Worker:
    worker = _Worker(func, *args, **kwargs)
    worker.finished.connect(on_success)
    worker.failed.connect(on_error)
    worker.start()
    return worker


def show_busy(parent: QtWidgets.QWidget, message: str) -> QtWidgets.QDialog:
    dialog = QtWidgets.QDialog(parent)
    dialog.setModal(True)
    dialog.setWindowTitle("")
    dialog.setWindowFlags(dialog.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

    layout = QtWidgets.QVBoxLayout(dialog)
    layout.setContentsMargins(PADDING_X * 2, PADDING_Y * 2, PADDING_X * 2, PADDING_Y * 2)
    layout.setSpacing(PADDING_Y * 2)

    label = QtWidgets.QLabel(message, dialog)
    layout.addWidget(label)

    progress = QtWidgets.QProgressBar(dialog)
    progress.setRange(0, 0)
    layout.addWidget(progress)

    dialog.resize(label.sizeHint().width() + PADDING_X * 4, dialog.sizeHint().height())
    dialog.show()
    parent._busy_dialog = dialog
    return dialog


def hide_busy(parent: QtWidgets.QWidget) -> None:
    dialog: Optional[QtWidgets.QDialog] = getattr(parent, "_busy_dialog", None)
    if dialog is not None:
        dialog.accept()
        parent._busy_dialog = None
