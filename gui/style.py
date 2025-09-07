from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple


@dataclass
class Style:
    """Samler felles stilkonfigurasjon for GUI."""

    # Knappestil
    BTN_FG: str = "#1f6aa5"
    BTN_HOVER: str = "#185a8b"
    BTN_RADIUS: int = 8

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
