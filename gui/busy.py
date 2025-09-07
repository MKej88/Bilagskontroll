from . import _ctk


def show_busy(app, message: str):
    """Vis en modal ventedialog med en spinner og tekst."""
    ctk = _ctk()
    win = ctk.CTkToplevel(app)
    win.title("")
    win.resizable(False, False)
    win.transient(app)
    win.grab_set()

    progress = ctk.CTkProgressBar(win, mode="indeterminate")
    progress.pack(padx=20, pady=(20, 10), fill="x")
    progress.start()
    ctk.CTkLabel(win, text=message).pack(padx=20, pady=(0, 20))

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
        except Exception:
            pass
        win.destroy()
        app._busy_win = None
