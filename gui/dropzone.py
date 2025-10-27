from __future__ import annotations

from typing import Callable

from .style import style
from .qt import qt_modules


QtCore, _, QtWidgets = qt_modules()


class DropZone(QtWidgets.QFrame):
    """Dra-og-slipp-felt for filer."""

    def __init__(self, text: str, drop_callback: Callable[[list[str]], None], parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.drop_callback = drop_callback
        self.setMinimumHeight(70)
        self.setObjectName("drop_zone")

        light, dark = style.get_color_pair("dnd_bg")
        border_light, border_dark = style.get_color_pair("dnd_border")
        self._bg_normal = light if style.mode == "light" else dark
        self._border_normal = border_light if style.mode == "light" else border_dark

        success_light, success_dark = style.get_color_pair("success")
        self._bg_highlight = success_light if style.mode == "light" else success_dark

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(style.PAD_MD, style.PAD_MD, style.PAD_MD, style.PAD_MD)
        layout.setSpacing(style.PAD_SM)

        self.label = QtWidgets.QLabel(text, self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.label)

        self._apply_colors(self._bg_normal, self._border_normal)

    def _apply_colors(self, bg: str, border: str) -> None:
        self.setStyleSheet(
            (
                f"QFrame#drop_zone {{"
                f"background-color: {bg};"
                f"border: 2px dashed {border};"
                f"border-radius: {style.BTN_RADIUS}px;"
                f"}}"
            )
        )

    def dragEnterEvent(self, event) -> None:  # noqa: N802
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._apply_colors(self._bg_highlight, self._bg_highlight)
        else:
            event.ignore()

    def dragLeaveEvent(self, event) -> None:  # noqa: N802
        del event
        self._apply_colors(self._bg_normal, self._border_normal)

    def dropEvent(self, event) -> None:  # noqa: N802
        self._apply_colors(self._bg_normal, self._border_normal)
        if not event.mimeData().hasUrls():
            event.ignore()
            return
        paths = []
        for url in event.mimeData().urls():
            local_path = url.toLocalFile()
            if local_path:
                paths.append(local_path)
        if paths and self.drop_callback:
            self.drop_callback(paths)
        event.acceptProposedAction()

