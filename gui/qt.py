from __future__ import annotations

import os
from typing import Tuple

os.environ.setdefault("QT_QPA_PLATFORM", os.environ.get("QT_QPA_PLATFORM", "offscreen"))
os.environ.setdefault("QT_OPENGL", "software")

QtCore = None
QtGui = None
QtWidgets = None


def qt_modules():
    global QtCore, QtGui, QtWidgets
    if QtCore is None or QtGui is None or QtWidgets is None:
        from PySide6 import QtCore as _QtCore, QtGui as _QtGui, QtWidgets as _QtWidgets

        QtCore = _QtCore
        QtGui = _QtGui
        QtWidgets = _QtWidgets
    return QtCore, QtGui, QtWidgets

