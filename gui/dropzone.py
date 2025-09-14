from . import _ctk
from .style import style

ctk = _ctk()


class DropZone(ctk.CTkFrame):
    """En ramme for dra-og-slipp med fargeendring ved drag hendelser."""

    def __init__(self, parent, text: str, drop_callback):
        dnd_bg = style.get_color_pair("dnd_bg")
        dnd_border = style.get_color_pair("dnd_border")
        highlight = style.get_color_pair("success")

        super().__init__(
            parent,
            height=70,
            corner_radius=style.BTN_RADIUS,
            fg_color=dnd_bg,
            border_color=dnd_border,
            border_width=2,
        )

        self._dnd_bg = dnd_bg
        self._dnd_border = dnd_border
        self._highlight = highlight
        self.drop_callback = drop_callback
        self._label_text_color = dnd_border

        self.label = ctk.CTkLabel(
            self,
            text=text,
            anchor="center",
            text_color=self._label_text_color,
        )
        self.label.pack(expand=True, fill="both", padx=style.PAD_MD, pady=style.PAD_SM)

        for evt in ("<<DragEnter>>", "<<DropEnter>>"):
            self.dnd_bind(evt, self._on_drag_enter)
        for evt in ("<<DragLeave>>", "<<DropLeave>>"):
            self.dnd_bind(evt, self.reset_colors)

    def _on_drag_enter(self, _):
        self.configure(fg_color=self._highlight, border_color=self._highlight)
        self.label.configure(text_color=style.get_color_pair("fg"))

    def reset_colors(self, _=None):
        self.configure(fg_color=self._dnd_bg, border_color=self._dnd_border)
        self.label.configure(text_color=self._label_text_color)

    def on_drop(self, event):
        self.reset_colors()
        if self.drop_callback:
            return self.drop_callback(event)
