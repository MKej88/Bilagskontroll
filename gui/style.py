from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple


# Standard padding for GUI-komponenter
PADDING_X = 10
PADDING_Y = 8


@dataclass
class Style:
    """Samler felles stilkonfigurasjon for GUI."""

    # Knappestil
    BTN_FG: str = "#0b4b8f"
    BTN_HOVER: str = "#093d73"
    BTN_RADIUS: int = 10

    # Farger per tema
    COLORS: Dict[str, Dict[str, str]] = field(
        default_factory=lambda: {
            "success": {"light": "#1f8b4c", "dark": "#2ecc71"},
            "success_hover": {"light": "#1a7441", "dark": "#27ae60"},
            "error": {"light": "#c94c4c", "dark": "#e06666"},
            "error_hover": {"light": "#a93f3f", "dark": "#cc5252"},
            # Generelle farger
            "bg": {"light": "#ffffff", "dark": "#0f141b"},
            "background": {"light": "#f1f4f9", "dark": "#101620"},
            "surface": {"light": "#ffffff", "dark": "#18212b"},
            "surface_alt": {"light": "#f7f9fc", "dark": "#141b24"},
            "border": {"light": "#d8e1ec", "dark": "#283240"},
            "muted": {"light": "#5c6b80", "dark": "#9aa8bc"},
            "fg": {"light": "#0f1b2b", "dark": "#e6edf7"},
            "button_text": {"light": "#f5f7fb", "dark": "#f5f7fb"},
            "accent": {"light": "#0d63c6", "dark": "#4ba3ff"},
            # Dra-og-slipp felt
            "dnd_bg": {"light": "#f4f7fb", "dark": "#1a2330"},
            "dnd_border": {"light": "#9fb2cc", "dark": "#37506f"},
            # Tabellfarger
            "table_bg": {"light": "#ffffff", "dark": "#18212b"},
            "table_fg": {"light": "#0f1b2b", "dark": "#e6edf7"},
            "table_header_bg": {"light": "#e6edf7", "dark": "#1f2a38"},
            "table_sel_bg": {"light": "#d1e3ff", "dark": "#2b3b52"},
            "table_sel_fg": {"light": "#0f1b2b", "dark": "#ffffff"},
            "table_row_odd": {"light": "#f5f8fc", "dark": "#202c3a"},
            "table_row_even": {"light": "#ffffff", "dark": "#1b2533"},
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
    FONT_FAMILY: str = "Segoe UI"
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
    PAD_XL: int = 16
    PAD_LG: int = 12
    PAD_MD: int = 8
    PAD_SM: int = 6
    PAD_XS: int = 4
    PAD_XXS: int = 2

    CARD_RADIUS: int = 16
    SECTION_RADIUS: int = 14
    OUTLINE_WIDTH: int = 1


style = Style()
