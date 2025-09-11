import customtkinter as ctk
from .style import style, PADDING_X, PADDING_Y


class Card(ctk.CTkFrame):
    """Standardisert kort med felles stil."""

    def __init__(self, master, *args, **kwargs):
        kwargs.setdefault("corner_radius", 16)
        kwargs.setdefault("fg_color", style.get_color_pair("dnd_bg"))
        super().__init__(master, *args, **kwargs)

    def grid(self, *args, **kwargs):  # type: ignore[override]
        kwargs.setdefault("padx", PADDING_X)
        kwargs.setdefault("pady", PADDING_Y)
        return super().grid(*args, **kwargs)
