import threading
from tkinter import TclError

from helpers import logger
from . import _ctk
from .style import PADDING_X, PADDING_Y


def run_in_thread(func, *args):
    """Start ``func`` i en bakgrunnstråd og returner trådobjektet."""
    thread = threading.Thread(target=func, args=args, daemon=True)
    thread.start()
    return thread


def show_busy(app, message: str):
    """Vis en modal ventedialog med en spinner og tekst."""
    ctk = _ctk()
    win = ctk.CTkToplevel(app)
    win.title("")
    win.resizable(False, False)
    win.transient(app)
    win.grab_set()

    progress = ctk.CTkProgressBar(win, mode="indeterminate")
    progress.pack(padx=PADDING_X * 2, pady=(PADDING_Y * 2, PADDING_Y), fill="x")
    progress.start()
    ctk.CTkLabel(win, text=message).pack(padx=PADDING_X * 2, pady=(0, PADDING_Y * 2))

    app._busy_win = win
    win.update_idletasks()
    x = app.winfo_x() + app.winfo_width() // 2 - win.winfo_width() // 2
    y = app.winfo_y() + app.winfo_height() // 2 - win.winfo_height() // 2
    win.geometry(f"+{x}+{y}")
    return win


def hide_busy(app):
    """Lukk ventedialogen hvis den er åpen."""
    win = getattr(app, "_busy_win", None)
    if win is not None:
        try:
            win.grab_release()
        except TclError:
            logger.debug("Kunne ikke frigjøre vinduets grab")
        win.destroy()
        app._busy_win = None
