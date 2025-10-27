from dataclasses import dataclass, field
from typing import Dict


# Standard padding for GUI-komponenter
PADDING_X = 10
PADDING_Y = 8


@dataclass
class Style:
    """Samler felles stilkonfigurasjon for GUI."""

    # Knappestil
    BTN_FG: str = "#1f6aa5"
    BTN_HOVER: str = "#185a8b"
    BTN_RADIUS: int = 8

    theme: str = "light"

    # Farger per tema
    COLORS: Dict[str, Dict[str, str]] = field(
        default_factory=lambda: {
            "success": {"light": "#2ecc71", "dark": "#27ae60"},
            "success_hover": {"light": "#29b765", "dark": "#219150"},
            "error": {"light": "#e74c3c", "dark": "#c0392b"},
            "error_hover": {"light": "#cf4334", "dark": "#992d22"},
            # Generelle farger
            "bg": {"light": "#ffffff", "dark": "#1e1e1e"},
            "fg": {"light": "#000000", "dark": "#e6e6e6"},
            # Dra-og-slipp felt
            "dnd_bg": {"light": "#f5f6f7", "dark": "#2b2b2b"},
            "dnd_border": {"light": "#a8b1bb", "dark": "#4a4f55"},
            # Tabellfarger
            "table_bg": {"light": "#ffffff", "dark": "#1e1e1e"},
            "table_fg": {"light": "#000000", "dark": "#e6e6e6"},
            "table_header_bg": {"light": "#f0f0f0", "dark": "#2a2a2a"},
            "table_sel_bg": {"light": "#d0d0ff", "dark": "#3a3a3a"},
            "table_sel_fg": {"light": "#000000", "dark": "#ffffff"},
            "table_row_odd": {"light": "#f6f6f6", "dark": "#232323"},
            "table_row_even": {"light": "#ffffff", "dark": "#1e1e1e"},
        }
    )

    # Skrifttyper
    FONT_FAMILY: str = "Helvetica"

    # Standard spacing
    PAD_XL: int = 14
    PAD_LG: int = 12
    PAD_MD: int = 8
    PAD_SM: int = 6
    PAD_XS: int = 4
    PAD_XXS: int = 2

    def set_theme(self, mode: str) -> None:
        mode = (mode or "").strip().lower()
        if mode not in {"light", "dark"}:
            mode = "light"
        self.theme = mode

    def get_color(self, name: str) -> str:
        try:
            return self.COLORS[name]["dark" if self.theme == "dark" else "light"]
        except KeyError as exc:
            raise KeyError(f"Ukjent fargenavn: {name}") from exc


style = Style()


def apply_palette(app) -> None:
    """Oppdater Qt-paletten basert på valgt tema."""

    from PyQt5 import QtGui

    palette = app.palette()
    bg = QtGui.QColor(style.get_color("bg"))
    fg = QtGui.QColor(style.get_color("fg"))
    palette.setColor(palette.Window, bg)
    palette.setColor(palette.WindowText, fg)
    palette.setColor(palette.Base, bg)
    palette.setColor(palette.AlternateBase, QtGui.QColor(style.get_color("table_row_odd")))
    palette.setColor(palette.ToolTipBase, bg)
    palette.setColor(palette.ToolTipText, fg)
    palette.setColor(palette.Text, fg)
    palette.setColor(palette.Button, bg)
    palette.setColor(palette.ButtonText, fg)
    palette.setColor(palette.Highlight, QtGui.QColor(style.get_color("table_sel_bg")))
    palette.setColor(palette.HighlightedText, QtGui.QColor(style.get_color("table_sel_fg")))
    app.setPalette(palette)
