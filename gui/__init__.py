# -*- coding: utf-8 -*-
"""GUI-moduler for Bilagskontroll."""

import os
import re

from .style import style

# CustomTkinter importeres ved behov for raskere oppstart.
_ctk_mod = None


def _ctk():
    """Importer ``customtkinter`` ved første kall og returner modulen."""
    global _ctk_mod
    if _ctk_mod is None:
        import customtkinter as ctk

        _ctk_mod = ctk
    return _ctk_mod

# Tkinter og CustomTkinter importeres lazily for raskere oppstart.

APP_TITLE = "Bilagskontroll"
OPEN_PO_URL = "https://go.poweroffice.net/#reports/purchases/invoice?"

# For bakoverkompatibilitet
get_color = style.get_color


def create_button(master, **kwargs):
    """Opprett en knapp med felles stil."""
    ctk = _ctk()

    options = {
        "fg_color": style.BTN_FG,
        "hover_color": style.BTN_HOVER,
        "font": style.FONT_BODY,
        "corner_radius": style.BTN_RADIUS,
    }
    options.update(kwargs)
    return ctk.CTkButton(master, **options)

# ----------------- App -----------------
class App:
    def __init__(self):
        import tkinter as tk
        ctk = _ctk()

        globals().update(tk=tk, ctk=ctk)

        # Endre klassen dynamisk slik at den arver fra ``CTk``.
        cls = self.__class__
        self.__class__ = type(cls.__name__, (ctk.CTk, cls), {})
        ctk.CTk.__init__(self)

        # Hjelpefunksjoner fra helpers importeres først ved behov for å
        # unngå unødvendig overhead ved oppstart.
        self._helpers_loaded = False

        self._dnd_ready = False
        self._icon_ready = False
        self.title(APP_TITLE)

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        origin_x = 0
        origin_y = 0
        if os.name == "nt":
            import ctypes

            work_area = ctypes.wintypes.RECT()
            SPI_GETWORKAREA = 0x0030
            if ctypes.windll.user32.SystemParametersInfoW(
                SPI_GETWORKAREA, 0, ctypes.byref(work_area), 0
            ):
                screen_w = work_area.right - work_area.left
                screen_h = work_area.bottom - work_area.top
                origin_x = work_area.left
                origin_y = work_area.top
        width = int(screen_w * 0.8)
        height = int(screen_h * 0.9)
        x = origin_x + max((screen_w - width) // 2, 0)
        y = origin_y + max((screen_h - height) // 2, 0)
        self.geometry(f"{width}x{height}+{x}+{y}")
        min_w = int(screen_w * 0.6)
        min_h = int(screen_h * 0.7)
        self.minsize(min_w, min_h)

        self.app_icon_img = None

        self.df = None
        self.sample_df = None
        self.decisions, self.comments = [], []
        self.idx = 0
        self.invoice_col = None
        self.net_amount_col = None
        self.antall_bilag = 0

        # GL
        self.gl_df = None
        self.gl_invoice_col = None
        self.gl_accountno_col = None
        self.gl_accountname_col = None
        self.gl_text_col = None
        self.gl_desc_col = None
        self.gl_vatcode_col = None
        self.gl_vatamount_col = None
        self.gl_debit_col = None
        self.gl_credit_col = None
        self.gl_amount_col = None
        self.gl_postedby_col = None

        # Framdriftsindikator
        self._progress_job = None
        self._progress_running = False
        self._progress_val = 0
        self._progress_msg = ""

        self.logo_img = None
        self._theme_initialized = False
        self.after_idle(self._build_ui)

    def _init_fonts(self):
        ctk = _ctk()
        s = style
        if s.FONT_TITLE is None:
            s.FONT_TITLE = ctk.CTkFont(size=16, weight="bold")
        if s.FONT_BODY is None:
            s.FONT_BODY = ctk.CTkFont(size=14)
        if s.FONT_TITLE_LITE is None:
            s.FONT_TITLE_LITE = ctk.CTkFont(size=16)
        if s.FONT_TITLE_LARGE is None:
            s.FONT_TITLE_LARGE = ctk.CTkFont(size=18, weight="bold")
        if s.FONT_TITLE_SMALL is None:
            s.FONT_TITLE_SMALL = ctk.CTkFont(size=15, weight="bold")
        if s.FONT_BODY_BOLD is None:
            s.FONT_BODY_BOLD = ctk.CTkFont(size=14, weight="bold")
        if s.FONT_SMALL is None:
            s.FONT_SMALL = ctk.CTkFont(size=13)
        if s.FONT_SMALL_ITALIC is None:
            s.FONT_SMALL_ITALIC = ctk.CTkFont(size=12, slant="italic")

    def _ensure_helpers(self):
        """Importer tunge hjelpefunksjoner fra ``helpers`` ved første behov."""
        if getattr(self, "_helpers_loaded", False):
            return
        from helpers import (
            to_str,
            fmt_money,
            format_number_with_thousands,
            guess_invoice_col,
            guess_col,
            guess_net_amount_col,
            fmt_pct,
            logger,
        )
        globals().update(
            to_str=to_str,
            fmt_money=fmt_money,
            format_number_with_thousands=format_number_with_thousands,
            guess_invoice_col=guess_invoice_col,
            guess_col=guess_col,
            guess_net_amount_col=guess_net_amount_col,
            fmt_pct=fmt_pct,
            logger=logger,
        )
        self._helpers_loaded = True

    def _build_ui(self):
        """Startar eit minimums-UI og utset tunge delar."""
        self._init_fonts()
        self._init_ui()
        self.after(0, self._build_sidebar)
        self.after(0, self._build_main)
        self.after_idle(self._post_init)

    def _init_ui(self):
        try:
            from tkinterdnd2 import TkinterDnD
        except Exception:
            TkinterDnD = None

        self._TkinterDnD = TkinterDnD

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.bind("<Left>", lambda e: self.prev())
        self.bind("<Right>", lambda e: self.next())
        self.bind("<Control-o>", lambda e: self.open_in_po())

        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _build_sidebar(self):
        from .sidebar import build_sidebar

        self.sidebar = build_sidebar(self)
        self.sample_size_var.set("")
        self.year_var.set("")

    def _build_main(self):
        from .mainview import build_main

        self.main = build_main(self)
        if self.gl_df is not None:
            self.after(0, self._build_ledger_widgets)
        self.render()

    def _build_ledger_widgets(self):
        from .mainview import build_ledger_widgets

        build_ledger_widgets(self)

    def _post_init(self):
        self.after(200, self._init_theme)
        self.after(200, self.load_logo_images)
        self._init_dnd()
        self.after(200, self._init_icon)

    def _init_dnd(self):
        TkinterDnD = getattr(self, "_TkinterDnD", None)
        if not TkinterDnD:
            return

        self.__class__ = type(
            self.__class__.__name__, (self.__class__, TkinterDnD.DnDWrapper), {}
        )
        TkinterDnD.DnDWrapper.__init__(self)
        TkinterDnD._require(self)
        self._dnd = TkinterDnD
        self.drop_target_register("DND_Files")
        self.dnd_bind("<<Drop>>", self._on_drop)
        self._dnd_ready = True

    def _init_icon(self):
        self._update_icon()
        self._icon_ready = True

    # Theme
    def _init_theme(self):
        ctk = _ctk()
        if getattr(self, "_theme_initialized", False):
            return
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        self._theme_initialized = True

    def _switch_theme(self, mode):
        ctk = _ctk()
        self._init_theme()
        modes = {"light": "light", "dark": "dark"}
        ctk.set_appearance_mode(modes.get(mode.lower(), "system"))
        if self._icon_ready:
            self._update_icon()
        from .ledger import apply_treeview_theme, update_treeview_stripes

        apply_treeview_theme(self)
        update_treeview_stripes(self)
        self.render()

    def _update_icon(self):
        ctk = _ctk()
        from helpers import resource_path
        try:
            dark = ctk.get_appearance_mode().lower() == "dark"
        except Exception:
            dark = False
        ico = "icons/bilagskontroll_icon_darkmode.ico" if dark else "icons/bilagskontroll_logo.ico"
        png = "icons/bilagskontroll_icon_darkmode_256.png" if dark else "icons/bilagskontroll_logo_256.png"
        try:
            self.iconbitmap(resource_path(ico))
        except Exception:
            pass
        try:
            self.app_icon_img = tk.PhotoImage(file=resource_path(png))
            self.iconphoto(False, self.app_icon_img)
        except Exception:
            pass

    def load_logo_images(self):
        ctk = _ctk()
        from helpers import resource_path
        try:
            from PIL import Image
            img_light = Image.open(resource_path("icons/bilagskontroll_logo_256.png"))
            try:
                img_dark = Image.open(resource_path("icons/bilagskontroll_icon_darkmode_256.png"))
            except Exception:
                img_dark = None
            try:
                if img_dark:
                    self.logo_img = ctk.CTkImage(light_image=img_light, dark_image=img_dark, size=(32, 32))
                else:
                    self.logo_img = ctk.CTkImage(light_image=img_light, size=(32, 32))
            except TypeError:
                self.logo_img = ctk.CTkImage(img_light, size=(32, 32))
        except Exception:
            self.logo_img = None
            return
        if hasattr(self, "bottom_frame"):
            ctk.CTkLabel(self.bottom_frame, text="", image=self.logo_img).pack(side="right", padx=(style.PAD_MD, 0))

    def _on_drop(self, event):
        path = event.data.strip("{}").strip()
        if not path.lower().endswith((".xlsx", ".xls")):
            return
        if "hovedbok" in os.path.basename(path).lower():
            self.gl_path_var.set(path)
            self._load_gl_excel()
        else:
            self.file_path_var.set(path)
            self._load_excel()

    # Files
    def choose_file(self):
        from tkinter import filedialog
        p = filedialog.askopenfilename(title="Velg Excel (fakturaliste)", filetypes=[("Excel","*.xlsx *.xls")])
        if not p: return
        self.file_path_var.set(p)
        self._load_excel()

    def choose_gl_file(self):
        from tkinter import filedialog
        p = filedialog.askopenfilename(title="Velg Hovedbok (Excel)", filetypes=[("Excel","*.xlsx *.xls")])
        if not p: return
        self.gl_path_var.set(p)
        self._load_gl_excel()

    def destroy(self):
        ctk = _ctk()
        try:
            ctk.ScalingTracker.remove_window(self.destroy, self)
        except Exception:
            pass
        if self._dnd_ready:
            try:
                self._dnd.Tk.destroy(self)
            except Exception:
                pass

    # Read
    def _load_excel(self):
        from tkinter import messagebox
        import threading

        self._ensure_helpers()
        from data_utils import load_invoice_df

        path = self.file_path_var.get()
        if not path:
            return
        logger.info(f"Laster fakturaliste fra {path}")
        header_idx = 4
        big = os.path.getsize(path) > 5 * 1024 * 1024
        if big and hasattr(self, "inline_status"):
            self.inline_status.configure(text="laster inn fil...")
            self.inline_status.update_idletasks()
        self._start_progress("Laster fakturaliste...")

        def finalize():
            if big and hasattr(self, "inline_status"):
                self.inline_status.configure(text="")
            self._finish_progress()

        def worker():
            try:
                df, cust = load_invoice_df(path, header_idx)
            except Exception as e:
                def err():
                    messagebox.showerror(APP_TITLE, f"Klarte ikke lese Excel:\n{e}")
                    finalize()
                self.after(0, err)
                return

            def success():
                self.antall_bilag = len(df.dropna(how="all"))
                self.df = df
                if cust:
                    self.kunde_var.set(cust)
                    if hasattr(self, "kunde_entry"):
                        self.kunde_entry.configure(state="disabled")
                if self.df is None or self.df.dropna(how="all").empty:
                    messagebox.showwarning(APP_TITLE, "Excel-filen ser tom ut.")
                    finalize()
                    return
                self.invoice_col = guess_invoice_col(self.df.columns)
                self.net_amount_col = guess_net_amount_col(self.df.columns)
                self.sample_df = None; self.decisions=[]; self.comments=[]; self.idx=0
                self._update_counts_labels()
                self.render()
                finalize()

            self.after(0, success)

        threading.Thread(target=worker, daemon=True).start()

    def _load_gl_excel(self):
        from tkinter import messagebox
        import threading

        self._ensure_helpers()
        from data_utils import load_gl_df

        path = self.gl_path_var.get()
        if not path:
            return
        logger.info(f"Laster hovedbok fra {path}")
        big = os.path.getsize(path) > 5 * 1024 * 1024
        if big and hasattr(self, "inline_status"):
            self.inline_status.configure(text="laster inn fil...")
            self.inline_status.update_idletasks()
        self._start_progress("Laster hovedbok...")

        def finalize():
            if big and hasattr(self, "inline_status"):
                self.inline_status.configure(text="")
            self._finish_progress()

        def worker():
            try:
                gl = load_gl_df(path, nrows=10)
            except Exception as e:
                def err():
                    messagebox.showerror(APP_TITLE, f"Klarte ikke lese hovedbok:\n{e}")
                    finalize()
                self.after(0, err)
                return

            def success():
                if gl is None or gl.dropna(how="all").empty:
                    messagebox.showwarning(APP_TITLE, "Hovedboken ser tom ut.")
                    finalize()
                    return

                self.gl_df = gl
                cols = [str(c) for c in gl.columns]
                self.gl_invoice_col     = guess_invoice_col(cols)
                self.gl_accountno_col   = guess_col(cols, r"^kontonr\.?$", r"konto.*nummer", r"account.*(number|no)", r"acct.*no")
                self.gl_accountname_col = guess_col(cols, r"^kontonavn$", r"konto\s*navn", r"^konto$", r"account.*name", r"(?:^| )navn$")
                self.gl_text_col        = guess_col(cols, r"^tekst$", r"text", r"posteringstekst")
                self.gl_desc_col        = guess_col(cols, r"beskrivelse", r"description", r"forklaring")
                self.gl_vatcode_col     = guess_col(cols, r"^mva(?!-)|mva[- ]?kode", r"^vat(?!.*amount)|tax code")
                self.gl_vatamount_col   = guess_col(cols, r"mva[- ]?bel(ø|o)p", r"vat amount", r"tax amount")
                self.gl_debit_col       = guess_col(cols, r"^debet$", r"debit")
                self.gl_credit_col      = guess_col(cols, r"^kredit$", r"credit")
                self.gl_amount_col      = guess_col(cols, r"^bel(ø|o)p$", r"amount", r"sum")
                self.gl_postedby_col    = guess_col(cols, r"postert\s*av", r"bokf(ø|o)rt\s*av", r"registrert\s*av", r"posted\s*by", r"created\s*by")

                from helpers import only_digits
                if self.gl_invoice_col in self.gl_df.columns:
                    self.gl_df["_inv_norm"] = self.gl_df[self.gl_invoice_col].map(only_digits)
                else:
                    self.gl_df["_inv_norm"] = ""

                from .ledger import populate_ledger_table
                from .mainview import build_ledger_widgets
                self.populate_ledger_table = populate_ledger_table

                if not hasattr(self, "ledger_tree"):
                    build_ledger_widgets(self)

                if self.sample_df is not None:
                    self.render()
                finalize()

            self.after(0, success)

        threading.Thread(target=worker, daemon=True).start()
# Sampling / nav
    def _update_counts_labels(self):
        self.lbl_filecount.configure(text=f"Antall bilag: {self.antall_bilag}")
        
    def make_sample(self):
        from tkinter import messagebox
        self._ensure_helpers()
        if self.df is None:
            messagebox.showinfo(APP_TITLE, "Velg Excel først."); return
        try:
            n = int(self.sample_size_var.get())
            year = int(self.year_var.get())
        except Exception:
            messagebox.showinfo(APP_TITLE, "Oppgi antall og år.")
            return
        n = max(1, min(n, len(self.df)))
        logger.info(f"Trekker utvalg på {n} bilag for år {year}")
        try:
            self.sample_df = self.df.sample(n=n, random_state=year).reset_index(drop=True)
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Feil ved trekking av utvalg:\n{e}"); return
        self.decisions = [None]*len(self.sample_df); self.comments=[""]*len(self.sample_df); self.idx=0
        self.render()

    def _current_row_dict(self):
        self._ensure_helpers()
        row = self.sample_df.iloc[self.idx]
        return {str(c): to_str(row[c]) for c in self.sample_df.columns}

    def set_decision_and_next(self, val, advance=True):
        if self.sample_df is None: return
        self.comments[self.idx] = self.comment_box.get("0.0", "end").strip()
        self.decisions[self.idx] = val
        if advance and self.idx < len(self.sample_df) - 1:
            self.idx += 1
        self.render()

    def prev(self):
        if self.sample_df is None: return
        self.comments[self.idx] = self.comment_box.get("0.0", "end").strip()
        self.idx = max(0, self.idx - 1)
        self.render()

    def next(self):
        if self.sample_df is None: return
        self.comments[self.idx] = self.comment_box.get("0.0", "end").strip()
        self.idx = min(len(self.sample_df) - 1, self.idx + 1)
        self.render()

    # Open in PO: only open the URL present in current row
    
    def open_in_po(self):
        # Åpner alltid standard PowerOffice-rapport (uten å lete etter lenker i data)
        import webbrowser

        webbrowser.open(OPEN_PO_URL)
        self._show_inline("Åpner PowerOffice")
    
    def copy_invoice(self):
        self._ensure_helpers()
        if self.sample_df is None: return
        inv_val = to_str(self.sample_df.iloc[self.idx].get(self.invoice_col, ""))
        cleaned = re.sub(r"[^\d-]", "", inv_val)
        self.clipboard_clear(); self.clipboard_append(cleaned if cleaned else inv_val)
        self.copy_feedback.configure(text="Kopiert")
        self.after(1500, lambda: self.copy_feedback.configure(text=""))

    # Ledger
    # Summary / status
    def _update_status_card(self):
        self._ensure_helpers()
        from data_utils import calc_sum_kontrollert, calc_sum_net_all

        sum_k = calc_sum_kontrollert(self.sample_df, self.decisions, self.net_amount_col)
        sum_a = calc_sum_net_all(self.df, self.net_amount_col)
        pct = (sum_k / sum_a * 100.0) if sum_a else 0.0
        self.lbl_st_sum_kontrollert.configure(text=f"Sum kontrollert: {fmt_money(sum_k)} kr")
        self.lbl_st_sum_alle.configure(text=f"Sum alle bilag: {fmt_money(sum_a)} kr")
        self.lbl_st_pct.configure(text=f"% kontrollert av sum: {fmt_pct(pct)}")
        if self.sample_df is not None:
            approved = sum(1 for d in self.decisions if d == "Godkjent")
            rejected = sum(1 for d in self.decisions if d == "Ikke godkjent")
            remaining = sum(1 for d in self.decisions if d is None)
            self.lbl_st_godkjent.configure(text=f"Godkjent: {approved}")
            self.lbl_st_ikkegodkjent.configure(text=f"Ikke godkjent: {rejected}")
            self.lbl_st_gjen.configure(text=f"Gjenstår å kontrollere: {remaining}")
        else:
            self.lbl_st_godkjent.configure(text="Godkjent: –")
            self.lbl_st_ikkegodkjent.configure(text="Ikke godkjent: –")
            self.lbl_st_gjen.configure(text="Gjenstår å kontrollere: –")

    # Status
    def _start_progress(self, msg: str):
        self._progress_msg = msg
        self._progress_val = 0
        self._progress_running = True
        self._set_status(msg, 0)
        self._progress_job = self.after(100, self._progress_step)

    def _progress_step(self):
        if not self._progress_running:
            return
        self._progress_val = min(95, self._progress_val + 2)
        self._set_status(self._progress_msg, self._progress_val)
        self._progress_job = self.after(100, self._progress_step)

    def _finish_progress(self):
        self._progress_running = False
        if self._progress_job is not None:
            self.after_cancel(self._progress_job)
            self._progress_job = None
        self._set_status(self._progress_msg, 100)
        self.after(500, lambda: self._set_status(""))

    def _set_status(self, msg: str, progress: float | None = None):
        if hasattr(self, "status_label"):
            if progress is not None:
                self.status_label.configure(text=f"{msg} {progress:.0f}%")
            else:
                self.status_label.configure(text=msg)
            self.status_label.update_idletasks()
        if hasattr(self, "progress_bar"):
            if progress is not None:
                self.progress_bar.pack(side="right", padx=style.PAD_SM)
                self.progress_bar.configure(value=max(0, min(100, progress)))
                self.progress_bar.update_idletasks()
            else:
                self.progress_bar.pack_forget()

    # PDF
    # Inline
    def _show_inline(self, msg: str, ok=True):
        self.inline_status.configure(
            text_color=(style.get_color("success") if ok else style.get_color("error"))
        )
        self.inline_status.configure(text=msg)
        self.after(3500, lambda: self.inline_status.configure(text=""))

    # Details + render
    def _details_text_for_row(self, row_dict):
        self._ensure_helpers()
        lines=[]
        for k in self.sample_df.columns:
            key=str(k); val=to_str(row_dict.get(key,"")).strip()
            if not val: continue
            disp = val if (key.lower().startswith("faktura") and "nr" in key.lower()) else format_number_with_thousands(val)
            lines.append(f"{key}: {disp}")
        return "\n".join(lines).strip()

    def _update_status_card_safe(self):
        try: self._update_status_card()
        except Exception: pass

    def render(self):
        self._ensure_helpers()
        self._update_counts_labels()
        if self.sample_df is not None and len(self.sample_df)>0:
            self.lbl_count.configure(text=f"Bilag: {self.idx+1}/{len(self.sample_df)}")
            inv_val = to_str(self.sample_df.iloc[self.idx].get(self.invoice_col, "")) if len(self.sample_df)>0 else "—"
            self.lbl_invoice.configure(text=f"Fakturanr: {inv_val or '—'}")
            st = self.decisions[self.idx] if (self.decisions and self.idx < len(self.decisions)) else None
            self.lbl_status.configure(text=f"Status: {st or '—'}")

            row_dict = self._current_row_dict()
            self.detail_box.configure(state="normal"); self.detail_box.delete("0.0","end")
            self.detail_box.insert("0.0", self._details_text_for_row(row_dict)); self.detail_box.configure(state="disabled")

            if hasattr(self, "populate_ledger_table") and hasattr(self, "ledger_tree"):
                self.populate_ledger_table(self, inv_val)
            else:
                if hasattr(self, "ledger_tree"):
                    for item in self.ledger_tree.get_children():
                        self.ledger_tree.delete(item)
                if hasattr(self, "ledger_sum"):
                    self.ledger_sum.configure(
                        text="Last gjerne også inn en hovedbok for å se bilagslinjene."
                    )

            self.comment_box.delete("0.0","end")
            if self.comments and self.idx < len(self.comments) and self.comments[self.idx]:
                self.comment_box.insert("0.0", self.comments[self.idx])
        else:
            self.lbl_count.configure(text="Bilag: –/–"); self.lbl_invoice.configure(text="Fakturanr: –"); self.lbl_status.configure(text="Status: –")
            self.detail_box.configure(state="normal"); self.detail_box.delete("0.0","end"); self.detail_box.insert("0.0","Velg Excel-fil og lag et utvalg."); self.detail_box.configure(state="disabled")
            if hasattr(self, "ledger_tree"):
                for item in self.ledger_tree.get_children():
                    self.ledger_tree.delete(item)
            if hasattr(self, "ledger_sum"):
                self.ledger_sum.configure(
                    text="Last gjerne også inn en hovedbok for å se bilagslinjene."
                )
            self.comment_box.delete("0.0","end")

        if self.sample_df is None or len(self.sample_df) == 0:
            self.btn_prev.configure(state="disabled")
            self.btn_next.configure(state="disabled")
        else:
            self.btn_prev.configure(state="normal" if self.idx > 0 else "disabled")
            self.btn_next.configure(state="normal" if self.idx < len(self.sample_df) - 1 else "disabled")

        if (
            (self.df is not None and len(self.df) > 0)
            or (self.sample_df is not None and len(self.sample_df) > 0)
        ):
            self._update_status_card_safe()

if __name__ == "__main__":
    App().mainloop()
