from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Colors:
    """Fargeoppsett for ulike tema og knapper."""

    palette: Dict[str, Dict[str, str]] = field(
        default_factory=lambda: {
            "success": {"light": "#2ecc71", "dark": "#27ae60"},
            "success_hover": {"light": "#29b765", "dark": "#219150"},
            "error": {"light": "#e74c3c", "dark": "#c0392b"},
            "error_hover": {"light": "#cf4334", "dark": "#992d22"},
        }
    )
    btn_fg: str = "#1f6aa5"
    btn_hover: str = "#185a8b"
    btn_radius: int = 8


@dataclass
class Fonts:
    """Plassholdere for skrifttyper som initialiseres senere."""

    title: Any = None
    body: Any = None
    title_lite: Any = None
    title_large: Any = None
    title_small: Any = None
    body_bold: Any = None
    small: Any = None
    small_italic: Any = None


@dataclass(frozen=True)
class Spacing:
    """Standard spacing i appen."""

    padx: int = 14
    pady: int = 14


@dataclass
class Style:
    colors: Colors = field(default_factory=Colors)
    fonts: Fonts = field(default_factory=Fonts)
    spacing: Spacing = field(default_factory=Spacing)


style = Style()
