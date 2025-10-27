from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple


# Standard padding for GUI-komponenter
PADDING_X = 10
PADDING_Y = 8


@dataclass
class Style:
    """Samler felles stilkonfigurasjon for GUI."""

    # Knappestil
    BTN_FG: Tuple[str, str] = field(
        default_factory=lambda: ("#134168", "#4b97ff")
    )
    BTN_HOVER: Tuple[str, str] = field(
        default_factory=lambda: ("#0f3656", "#357edc")
    )
    BTN_TEXT: Tuple[str, str] = field(
        default_factory=lambda: ("#ffffff", "#0b1624")
    )
    BTN_RADIUS: int = 12
    CARD_RADIUS: int = 18
    CARD_BORDER_WIDTH: int = 1

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
            "muted": {"light": "#5b6b7f", "dark": "#c2cad8"},
            "accent": {"light": "#0f4c81", "dark": "#63a9ff"},
            "accent_soft": {"light": "#dae6f5", "dark": "#233142"},
            "accent_border": {"light": "#adc4e1", "dark": "#32425a"},
            "card_bg": {"light": "#f5f7fb", "dark": "#1f2430"},
            "card_inner": {"light": "#ffffff", "dark": "#232a37"},
            "card_border": {"light": "#d7deeb", "dark": "#313a4d"},
            "pill_bg": {"light": "#e5eef9", "dark": "#283549"},
            "pill_border": {"light": "#bfd1ea", "dark": "#36445b"},
            "pill_text": {"light": "#0f4c81", "dark": "#95c5ff"},
            "btn_text": {"light": "#ffffff", "dark": "#0b1624"},
            "sidebar_bg": {"light": "#ffffff", "dark": "#212733"},
            "sidebar_border": {"light": "#dce2ed", "dark": "#323a4b"},
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

    def get_color(self, name: str) -> str:
        """Returner farge tilpasset valgt tema."""
        import customtkinter as ctk

        mode = ctk.get_appearance_mode().lower()
        try:
            return self.COLORS[name]["dark" if mode == "dark" else "light"]
        except KeyError as e:
            raise KeyError(f"Ukjent fargenavn: {name}") from e

    def get_color_pair(self, name: str) -> Tuple[str, str]:
        """Returner (lys, mørk) fargepar for CustomTkinter-komponenter."""
        try:
            col = self.COLORS[name]
            return col["light"], col["dark"]
        except KeyError as e:
            raise KeyError(f"Ukjent fargenavn: {name}") from e

    # Skrifttyper
    FONT_FAMILY: str = "Helvetica"
    # Skrifttyper (initialiseres lazily)
    FONT_TITLE: Optional[object] = None
    FONT_BODY: Optional[object] = None
    FONT_TITLE_LITE: Optional[object] = None
    FONT_TITLE_LARGE: Optional[object] = None
    FONT_TITLE_SMALL: Optional[object] = None
    FONT_BODY_BOLD: Optional[object] = None
    FONT_SMALL: Optional[object] = None
    FONT_SMALL_ITALIC: Optional[object] = None

    # Standard spacing
    PAD_XL: int = 14
    PAD_LG: int = 12
    PAD_MD: int = 8
    PAD_SM: int = 6
    PAD_XS: int = 4
    PAD_XXS: int = 2


style = Style()
