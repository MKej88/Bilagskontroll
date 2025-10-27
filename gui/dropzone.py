from PyQt5 import QtCore, QtGui, QtWidgets

from .style import style, PADDING_X, PADDING_Y


class DropZone(QtWidgets.QFrame):
    """En enkel PyQt-dra-og-slipp-sone med visuell tilbakemelding."""

    dropped = QtCore.pyqtSignal(str)

    def __init__(self, parent: QtWidgets.QWidget, text: str):
        super().__init__(parent)
        self._normal_border = style.get_color("dnd_border")
        self._normal_bg = style.get_color("dnd_bg")
        self._highlight = style.get_color("success")
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setAcceptDrops(True)
        self.setObjectName("dropZone")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(PADDING_X * 2, PADDING_Y * 2, PADDING_X * 2, PADDING_Y * 2)
        layout.setSpacing(PADDING_Y)

        self._label = QtWidgets.QLabel(text, self)
        self._label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self._label)

        self._update_colors(self._normal_bg, self._normal_border)

    def refresh_theme(self) -> None:
        self._normal_border = style.get_color("dnd_border")
        self._normal_bg = style.get_color("dnd_bg")
        self._highlight = style.get_color("success")
        self._update_colors(self._normal_bg, self._normal_border)

    def _update_colors(self, bg: str, border: str) -> None:
        self.setStyleSheet(
            f"#dropZone {{background-color: {bg}; border: 2px dashed {border}; border-radius: 8px;}}"
            f"#dropZone QLabel {{color: {border};}}"
        )

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:  # noqa: N802
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._update_colors(self._highlight, self._highlight)
            self._label.setStyleSheet(f"color: {style.get_color('fg')}")
        else:
            event.ignore()

    def dragLeaveEvent(self, event: QtGui.QDragLeaveEvent) -> None:  # noqa: N802
        super().dragLeaveEvent(event)
        self._label.setStyleSheet("")
        self._update_colors(self._normal_bg, self._normal_border)

    def dropEvent(self, event: QtGui.QDropEvent) -> None:  # noqa: N802
        event.setDropAction(QtCore.Qt.CopyAction)
        event.accept()
        self._label.setStyleSheet("")
        self._update_colors(self._normal_bg, self._normal_border)
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path:
                self.dropped.emit(path)
                break
