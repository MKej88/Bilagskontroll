from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


# Standard padding for GUI-komponenter
PADDING_X = 12
PADDING_Y = 10


@dataclass
class Style:
    """Samler felles stilkonfigurasjon for GUI."""

    # Knappestil
    BTN_RADIUS: int = 10

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
            "text_muted": {"light": "#6b7280", "dark": "#9ca3b0"},
            "accent": {"light": "#2563eb", "dark": "#4f8bff"},
            "accent_hover": {"light": "#1d4ed8", "dark": "#3a7cff"},
            "muted": {"light": "#e2e8f0", "dark": "#2d3340"},
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
            # Overflater
            "panel_bg": {"light": "#ffffff", "dark": "#1b1d24"},
            "panel_border": {"light": "#d5dae3", "dark": "#2a2e38"},
            "sidebar_bg": {"light": "#f3f5fa", "dark": "#12141a"},
            "header_bg": {"light": "#1f2937", "dark": "#0f172a"},
            "header_bg_alt": {"light": "#111827", "dark": "#172554"},
            "header_fg": {"light": "#f9fafb", "dark": "#e2e8f0"},
            "button_bg": {"light": "#eef2f7", "dark": "#2a2f3a"},
            "button_fg": {"light": "#1f2933", "dark": "#e5e7eb"},
            "button_hover": {"light": "#e0e7ef", "dark": "#363c49"},
            "outline": {"light": "#cbd5f5", "dark": "#334155"},
            "badge_bg": {"light": "#1f2937", "dark": "#1e40af"},
            "progress_bg": {"light": "#e5e7eb", "dark": "#2a2f3a"},
            "progress_chunk": {"light": "#2563eb", "dark": "#4f8bff"},
        }
    )

    # Skrifttyper
    FONT_FAMILY: str = "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
    BASE_FONT_SIZE: int = 14

    # Standard spacing
    PAD_XL: int = 14
    PAD_LG: int = 12
    PAD_MD: int = 8
    PAD_SM: int = 6
    PAD_XS: int = 4
    PAD_XXS: int = 2
    CARD_RADIUS: int = 14

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


def build_stylesheet() -> str:
    """Lag en global Qt-stylesheet basert på valgt tema."""

    accent = style.get_color("accent")
    accent_hover = style.get_color("accent_hover")
    danger = style.get_color("error")
    danger_hover = style.get_color("error_hover")
    text_muted = style.get_color("text_muted")
    panel_bg = style.get_color("panel_bg")
    border = style.get_color("panel_border")
    header_bg = style.get_color("header_bg")
    header_bg_alt = style.get_color("header_bg_alt")
    header_fg = style.get_color("header_fg")
    button_bg = style.get_color("button_bg")
    button_fg = style.get_color("button_fg")
    button_hover = style.get_color("button_hover")
    progress_bg = style.get_color("progress_bg")
    progress_chunk = style.get_color("progress_chunk")
    outline = style.get_color("outline")

    pad_sm = style.PAD_SM
    pad_md = style.PAD_MD
    pad_lg = style.PAD_LG
    pad_xs = style.PAD_XS
    card_radius = style.CARD_RADIUS
    btn_radius = style.BTN_RADIUS
    font = style.FONT_FAMILY
    base_size = style.BASE_FONT_SIZE

    return f"""
    QWidget {{
        font-family: {font};
        font-size: {base_size}px;
        color: {style.get_color('fg')};
        background-color: {style.get_color('bg')};
    }}

    QMainWindow {{
        background-color: {style.get_color('bg')};
    }}

    QLabel[role="muted"] {{
        color: {text_muted};
    }}

    QFrame#HeaderFrame {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {header_bg}, stop:1 {header_bg_alt});
        border-radius: {card_radius}px;
        padding: 0;
    }}

    QFrame#HeaderFrame QLabel {{
        color: {header_fg};
    }}

    QLabel#HeaderTitle {{
        font-size: 26px;
        font-weight: 600;
    }}

    QLabel#HeaderSubtitle {{
        font-size: 13px;
        color: {header_fg}cc;
    }}

    QFrame[role="card"] {{
        background-color: {panel_bg};
        border-radius: {card_radius}px;
        border: 1px solid {border};
    }}

    QFrame[role="card"] QLabel[role="caption"] {{
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-size: 11px;
        color: {text_muted};
    }}

    QFrame[role="card"] QLabel[role="value"] {{
        font-size: 20px;
        font-weight: 600;
    }}

    QLabel#InlineStatus, QLabel#InlineFeedback {{
        font-size: 12px;
        color: {text_muted};
    }}

    QFrame#Sidebar {{
        background-color: {style.get_color('sidebar_bg')};
        border-top-right-radius: {card_radius}px;
        border-bottom-right-radius: {card_radius}px;
        border: 1px solid {border};
    }}

    QLabel#SidebarTitle {{
        font-size: 18px;
        font-weight: 600;
    }}

    QLabel#SidebarDescription {{
        color: {text_muted};
        font-size: 12px;
    }}

    QLabel#PathLabel {{
        color: {text_muted};
        font-size: 12px;
    }}

    QGroupBox {{
        border: 1px solid {border};
        border-radius: {card_radius}px;
        margin-top: {pad_md}px;
        background-color: {panel_bg};
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        left: {pad_md}px;
        padding: 0 {pad_md}px;
        text-transform: uppercase;
        font-size: 12px;
        letter-spacing: 0.12em;
        color: {text_muted};
    }}

    QPushButton {{
        border: none;
        border-radius: {btn_radius}px;
        padding: {pad_sm + 2}px {pad_lg + 2}px;
        background-color: {button_bg};
        color: {button_fg};
        font-weight: 500;
    }}

    QPushButton:hover {{
        background-color: {button_hover};
    }}

    QPushButton:disabled {{
        background-color: {button_bg};
        color: {text_muted};
    }}

    QPushButton[role="primary"] {{
        background-color: {accent};
        color: #ffffff;
        font-weight: 600;
    }}

    QPushButton[role="primary"]:hover {{
        background-color: {accent_hover};
    }}

    QPushButton[role="danger"] {{
        background-color: {danger};
        color: #ffffff;
    }}

    QPushButton[role="danger"]:hover {{
        background-color: {danger_hover};
    }}

    QPushButton[role="ghost"] {{
        background-color: transparent;
        border: 1px solid {border};
    }}

    QPushButton[role="ghost"]:hover {{
        background-color: {button_hover};
    }}

    QPushButton[role="secondary"] {{
        background-color: {button_bg};
        color: {button_fg};
        border: 1px solid transparent;
    }}

    QPushButton[role="secondary"]:hover {{
        border: 1px solid {border};
    }}

    QToolButton[role="icon"] {{
        border: none;
        border-radius: {btn_radius}px;
        padding: {pad_xs}px;
        background: transparent;
    }}

    QToolButton[role="icon"]:hover {{
        background-color: {button_hover};
        color: {accent};
    }}

    QPlainTextEdit {{
        border: 1px solid {border};
        border-radius: {card_radius}px;
        padding: {pad_md}px;
        background-color: {panel_bg};
    }}

    QTableWidget {{
        background-color: {panel_bg};
        border: 1px solid {border};
        border-radius: {card_radius}px;
        gridline-color: {border};
    }}

    QHeaderView::section {{
        background-color: {button_bg};
        color: {button_fg};
        padding: {pad_sm}px {pad_md}px;
        border: none;
        font-weight: 600;
    }}

    QTableWidget::item:selected {{
        background-color: {style.get_color('table_sel_bg')};
        color: {style.get_color('table_sel_fg')};
    }}

    QProgressBar {{
        border: 1px solid {border};
        border-radius: {btn_radius}px;
        background-color: {progress_bg};
        padding: 0;
        text-align: center;
    }}

    QProgressBar::chunk {{
        border-radius: {btn_radius}px;
        background-color: {progress_chunk};
    }}

    QDialog#BusyDialog {{
        background-color: {panel_bg};
        border-radius: {card_radius}px;
    }}

    QSplitter::handle {{
        background-color: {outline};
        margin: 0 {pad_xs}px;
        width: 2px;
    }}

    QSplitter::handle:pressed {{
        background-color: {accent};
    }}

    QLabel#StatusLabel {{
        color: {text_muted};
    }}
    """


def apply_stylesheet(app) -> None:
    """Påfør stylesheet basert på aktivt tema."""

    app.setStyleSheet(build_stylesheet())
