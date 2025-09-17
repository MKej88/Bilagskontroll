# -*- coding: utf-8 -*-
"""GUI-moduler for Bilagskontroll."""

import json
import os
import re

from decimal import Decimal
from pathlib import Path

from .style import style
from helpers import logger
from tkinter import TclError

try:
    from settings import UI_SCALING
except Exception as e:  # pragma: no cover - valfri innstilling
    logger.warning(f"UI_SCALING kunne ikke lastes: {e}")
    UI_SCALING = None

# CustomTkinter importeres ved behov for raskere oppstart.
_ctk_mod = None

# Standard tema som brukes dersom brukeren ikke velger noe annet.
DEFAULT_APPEARANCE_MODE = "light"


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
MAX_APP_WIDTH = 1600
MIN_APP_WIDTH = 1200

if os.name == "nt":
    _CONFIG_DIR = Path(os.getenv("APPDATA") or Path.home()) / "Bilagskontroll"
else:
    _CONFIG_DIR = Path.home() / ".bilagskontroll"

WINDOW_CONFIG_FILE = _CONFIG_DIR / "settings.json"

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
        self._ui_scale = self._detect_ui_scale(screen_w, screen_h)
        scale_ratio = getattr(self, "_ui_scale_ratio", 1.0)
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
        width = min(int(screen_w * 0.8), MAX_APP_WIDTH)
        height = int(screen_h * 0.9)
        min_w = min(int(screen_w * 0.6), MIN_APP_WIDTH)
        min_h = int(screen_h * 0.7)
        if getattr(self, "_small_screen", False):
            width = min(width, int(screen_w * 0.65))
            height = min(height, int(screen_h * 0.85))
            min_w = min(min_w, int(screen_w * 0.55))
            min_h = min(min_h, int(screen_h * 0.75))
            if scale_ratio < 1:
                width = int(width * scale_ratio)
                height = int(height * scale_ratio)
                min_w = int(min_w * scale_ratio)
                min_h = int(min_h * scale_ratio)
        min_w = max(min_w, 900)
        min_h = max(min_h, 650)
        width = min(max(width, min_w), screen_w)
        height = min(max(height, min_h), screen_h)
        width, height = self._load_window_size(width, height, min_w, min_h, screen_w, screen_h)
        x = origin_x + max((screen_w - width) // 2, 0)
        y = origin_y + max((screen_h - height) // 2, 0)
        self.geometry(f"{width}x{height}+{x}+{y}")
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
        self._pdf_prompt_shown = False

        self.logo_img = None
        self._theme_initialized = False
        self.after_idle(self._build_ui)

    def _init_fonts(self):
        ctk = _ctk()
        s = style
        kwargs = {"family": s.FONT_FAMILY}
        if s.FONT_TITLE is None:
            s.FONT_TITLE = ctk.CTkFont(size=16, weight="bold", **kwargs)
        if s.FONT_BODY is None:
            s.FONT_BODY = ctk.CTkFont(size=14, **kwargs)
        if s.FONT_TITLE_LITE is None:
            s.FONT_TITLE_LITE = ctk.CTkFont(size=16, **kwargs)
        if s.FONT_TITLE_LARGE is None:
            s.FONT_TITLE_LARGE = ctk.CTkFont(size=18, weight="bold", **kwargs)
        if s.FONT_TITLE_SMALL is None:
            s.FONT_TITLE_SMALL = ctk.CTkFont(size=15, weight="bold", **kwargs)
        if s.FONT_BODY_BOLD is None:
            s.FONT_BODY_BOLD = ctk.CTkFont(size=14, weight="bold", **kwargs)
        if s.FONT_SMALL is None:
            s.FONT_SMALL = ctk.CTkFont(size=13, **kwargs)
        if s.FONT_SMALL_ITALIC is None:
            s.FONT_SMALL_ITALIC = ctk.CTkFont(size=12, slant="italic", **kwargs)

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
        except ImportError as e:
            logger.warning(f"tkinterdnd2 ikke tilgjengelig: {e}")
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

    def add_drop_target(self, widget, func):
        """Registrer eit widget som mål for dra-og-slipp."""

        def _register():
            if getattr(self, "_dnd_ready", False):
                try:
                    widget.drop_target_register("DND_Files")
                    widget.dnd_bind("<<Drop>>", func)
                except TclError as e:
                    logger.debug(f"DnD-registrering feilet: {e}")
            else:
                self.after(200, _register)

        _register()

    def _init_icon(self):
        self._update_icon()
        self._icon_ready = True

    # Theme
    def _init_theme(self):
        ctk = _ctk()
        if getattr(self, "_theme_initialized", False):
            return
        ctk.set_appearance_mode(DEFAULT_APPEARANCE_MODE)
        ctk.set_default_color_theme("blue")
        scale = getattr(self, "_ui_scale", None) or UI_SCALING or (self.winfo_fpixels("1i") / 96)
        if hasattr(ctk, "set_widget_scaling"):
            ctk.set_widget_scaling(scale)
        elif hasattr(ctk, "set_scaling"):
            ctk.set_scaling(scale)
        if hasattr(ctk, "set_spacing_scaling"):
            ctk.set_spacing_scaling(scale)
        elif hasattr(ctk, "set_window_scaling"):
            ctk.set_window_scaling(scale)
        self._theme_initialized = True

    def _detect_ui_scale(self, screen_w: int, screen_h: int) -> float:
        """Bestem skalering tilpasset skjermstørrelse."""

        self._small_screen = False
        self._ui_scale_ratio = 1.0
        if UI_SCALING:
            self._ui_base_scale = UI_SCALING
            return UI_SCALING

        try:
            dpi = float(self.winfo_fpixels("1i"))
        except (TclError, ValueError):
            dpi = 96.0

        if dpi <= 0:
            dpi = 96.0

        base_scale = dpi / 96.0
        self._ui_base_scale = base_scale

        diag_in = None
        try:
            mm_w = float(self.winfo_screenmmwidth())
            mm_h = float(self.winfo_screenmmheight())
        except (TclError, ValueError):
            mm_w = mm_h = 0.0

        if mm_w > 0 and mm_h > 0:
            diag_in = ((mm_w ** 2 + mm_h ** 2) ** 0.5) / 25.4

        if not diag_in:
            try:
                width_in = screen_w / dpi
                height_in = screen_h / dpi
                diag_in = (width_in ** 2 + height_in ** 2) ** 0.5
            except Exception:
                diag_in = None

        target_scale = base_scale
        considered_small = False

        if diag_in:
            if diag_in < 15.5 and base_scale >= 1.15:
                considered_small = True
                target_scale = base_scale * 0.68
            elif diag_in < 17.3 and base_scale >= 1.2:
                considered_small = True
                target_scale = base_scale * 0.72
            elif diag_in < 18.6 and base_scale >= 1.25:
                considered_small = True
                target_scale = base_scale * 0.8
        else:
            diag_px = (screen_w ** 2 + screen_h ** 2) ** 0.5
            full_hd_diag = (1920 ** 2 + 1080 ** 2) ** 0.5
            if diag_px <= full_hd_diag and base_scale >= 1.3:
                considered_small = True
                target_scale = base_scale * 0.75

        if considered_small:
            self._small_screen = True
            target_scale = min(target_scale, base_scale)
            if base_scale <= 1.05:
                target_scale = base_scale
        else:
            if base_scale >= 2.2:
                target_scale = min(base_scale * 0.85, base_scale)

        if base_scale >= 1.15:
            target_scale = max(target_scale, 0.85)
        else:
            target_scale = max(target_scale, 0.9)

        if base_scale > 0:
            ratio = min(target_scale / base_scale, 1.0)
        else:
            ratio = 1.0
        if ratio <= 0:
            ratio = 1.0
        self._ui_scale_ratio = ratio

        return target_scale

    def _switch_theme(self, mode):
        ctk = _ctk()
        self._init_theme()
        mode = str(mode).strip().lower()
        if mode not in {"light", "dark"}:
            mode = DEFAULT_APPEARANCE_MODE
        ctk.set_appearance_mode(mode)
        if hasattr(self, "theme_var"):
            self.theme_var.set(mode.title())
        if self._icon_ready:
            self._update_icon()
        from .ledger import apply_treeview_theme, update_treeview_stripes

        apply_treeview_theme(self)
        update_treeview_stripes(self)
        self.render()

    def _update_icon(self):
        ctk = _ctk()
        from helpers_path import resource_path
        try:
            ctk.get_appearance_mode()
        except (AttributeError, TclError) as e:
            logger.debug(f"Klarte ikke hente tema: {e}")
        ico = "icons/bilagskontroll_logo_all.ico"
        ico_path = resource_path(ico)
        try:
            self.iconbitmap(ico_path)
        except (TclError, OSError) as e:
            logger.debug(f"Kunne ikke sette ikon: {e}")
        try:
            from PIL import Image, ImageTk

            with Image.open(ico_path) as icon_img:
                icon_rgba = icon_img.convert("RGBA")
                self.app_icon_img = ImageTk.PhotoImage(icon_rgba)
            self.iconphoto(False, self.app_icon_img)
        except ImportError as e:
            logger.debug(f"Kunne ikke importere PIL for ikon: {e}")
        except (TclError, OSError) as e:
            logger.debug(f"Kunne ikke laste ikonbilde: {e}")
        except Exception as e:  # pragma: no cover - uventa PIL-feil
            logger.debug(f"Kunne ikke konvertere ikon: {e}")

    def load_logo_images(self):
        ctk = _ctk()
        from helpers_path import resource_path
        try:
            from PIL import Image
            img = Image.open(resource_path("icons/bilagskontroll_logo_all.ico"))
            try:
                self.logo_img = ctk.CTkImage(light_image=img, size=(32, 32))
            except TypeError:
                self.logo_img = ctk.CTkImage(img, size=(32, 32))
        except (ImportError, OSError) as e:
            logger.error(f"Kunne ikke laste logo: {e}")
            self.logo_img = None
            return

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
        self._save_window_size()
        try:
            if hasattr(self, "ledger_tree") and hasattr(self, "_ledger_configure_id"):
                self.ledger_tree.unbind("<Configure>", self._ledger_configure_id)
        except TclError as e:
            logger.debug(f"Kunne ikke unbinde ledger: {e}")
        try:
            ctk.ScalingTracker.remove_window(self.destroy, self)
        except ValueError as e:
            logger.debug(f"ScalingTracker.remove_window feilet: {e}")
        if self._dnd_ready:
            try:
                self._dnd.Tk.destroy(self)
            except TclError as e:
                logger.debug(f"DnD-destroy feilet: {e}")

    def _load_window_size(self, width, height, min_w, min_h, screen_w, screen_h):
        try:
            with WINDOW_CONFIG_FILE.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
        except FileNotFoundError:
            return width, height
        except (OSError, json.JSONDecodeError) as e:
            logger.debug(f"Kunne ikke lese vindustørrelse: {e}")
            return width, height

        win_cfg = data.get("window", {}) if isinstance(data, dict) else {}
        try:
            saved_w = int(win_cfg.get("width", width))
            saved_h = int(win_cfg.get("height", height))
        except (TypeError, ValueError):
            return width, height

        saved_w = max(min(saved_w, screen_w), min_w)
        saved_h = max(min(saved_h, screen_h), min_h)
        return saved_w or width, saved_h or height

    def _save_window_size(self):
        try:
            self.update_idletasks()
            width = int(self.winfo_width())
            height = int(self.winfo_height())
        except (TclError, ValueError) as e:
            logger.debug(f"Kunne ikke hente vindustørrelse: {e}")
            return

        if width <= 1 or height <= 1:
            return

        try:
            with WINDOW_CONFIG_FILE.open("r", encoding="utf-8") as fh:
                loaded = json.load(fh)
                data = loaded if isinstance(loaded, dict) else {}
        except FileNotFoundError:
            data = {}
        except (OSError, json.JSONDecodeError) as e:
            logger.debug(f"Kunne ikke lese eksisterende innstillinger: {e}")
            data = {}

        data["window"] = {"width": width, "height": height}

        try:
            WINDOW_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with WINDOW_CONFIG_FILE.open("w", encoding="utf-8") as fh:
                json.dump(data, fh)
        except OSError as e:
            logger.debug(f"Kunne ikke lagre vindustørrelse: {e}")

    # Read
    def _update_year_options(self):
        from datetime import datetime
        years: set[int] = set()
        for df in (getattr(self, "df", None), getattr(self, "gl_df", None)):
            if df is None or "Fakturadato" not in df.columns:
                continue
            for val in df["Fakturadato"].dropna().astype(str):
                m = re.search(r"(19|20)\d{2}", val)
                if m:
                    years.add(int(m.group(0)))

        now = datetime.now().year
        if years:
            filtered = sorted([y for y in years if y >= now - 1], reverse=True)
            if not filtered:
                filtered = sorted(years, reverse=True)[:2]
            values = [str(y) for y in filtered]
        else:
            values = [str(now), str(now - 1)]

        if hasattr(self, "year_combo"):
            self.year_combo.configure(values=values)
        if getattr(self, "year_var", None) and self.year_var.get() not in values:
            self.year_var.set(values[0] if values else "")
        from .sidebar import _toggle_sample_btn
        _toggle_sample_btn(self)

    def _load_excel(self):
        from tkinter import messagebox

        self._ensure_helpers()
        from data_utils import load_invoice_df, _net_amount_from_row
        from .busy import show_busy, hide_busy, run_in_thread

        path = self.file_path_var.get()
        if not path:
            return
        logger.info(f"Laster fakturaliste fra {path}")
        header_idx = 4
        big = os.path.getsize(path) > 5 * 1024 * 1024
        if big and hasattr(self, "inline_status"):
            self.inline_status.configure(text="laster inn fil...")
            self.inline_status.update_idletasks()
        show_busy(self, "Laster fakturaliste...")

        def finalize():
            if big and hasattr(self, "inline_status"):
                self.inline_status.configure(text="")
            self._finish_progress()
            hide_busy(self)

        def worker():
            self.after(0, lambda: self._start_progress("Laster fakturaliste..."))
            try:
                df, cust = load_invoice_df(path, header_idx)
            except (OSError, ValueError) as e:
                logger.error(f"Klarte ikke lese Excel: {e}")
                self.after(0, lambda: (messagebox.showerror(APP_TITLE, f"Klarte ikke lese Excel:\n{e}"), finalize()))
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
                try:
                    self.df["_netto_float"] = self.df.apply(
                        _net_amount_from_row, axis=1, args=(self.net_amount_col,)
                    )
                except (TypeError, ValueError):
                    logger.exception("Kunne ikke beregne nettobeløp")
                    self.df["_netto_float"] = None
                self.sample_df = None; self.decisions=[]; self.comments=[]; self.idx=0
                self._update_counts_labels()
                self.render()
                self._update_year_options()
                finalize()

            self.after(0, success)

        run_in_thread(worker)

    def _load_gl_excel(self):
        from tkinter import messagebox

        self._ensure_helpers()
        from data_utils import load_gl_df
        from .busy import show_busy, hide_busy, run_in_thread

        path = self.gl_path_var.get()
        if not path:
            return
        logger.info(f"Laster hovedbok fra {path}")
        big = os.path.getsize(path) > 5 * 1024 * 1024
        if big and hasattr(self, "inline_status"):
            self.inline_status.configure(text="laster inn fil...")
            self.inline_status.update_idletasks()
        show_busy(self, "Laster hovedbok...")

        def finalize():
            if big and hasattr(self, "inline_status"):
                self.inline_status.configure(text="")
            self._finish_progress()
            hide_busy(self)

        def worker():
            self.after(0, lambda: self._start_progress("Laster hovedbok..."))
            try:
                gl = load_gl_df(path, nrows=10)
            except (OSError, ValueError) as e:
                logger.error(f"Klarte ikke lese hovedbok: {e}")
                self.after(0, lambda: (messagebox.showerror(APP_TITLE, f"Klarte ikke lese hovedbok:\n{e}"), finalize()))
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
                self.gl_index = self.gl_df.groupby("_inv_norm").indices

                from .ledger import populate_ledger_table
                from .mainview import build_ledger_widgets
                self.populate_ledger_table = populate_ledger_table

                if not hasattr(self, "ledger_tree"):
                    build_ledger_widgets(self)

                if self.sample_df is not None:
                    self.render()
                self._update_year_options()
                finalize()

            self.after(0, success)

        run_in_thread(worker)
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
        except ValueError:
            messagebox.showinfo(APP_TITLE, "Oppgi antall og år.")
            return
        n = max(1, min(n, len(self.df)))
        logger.info(f"Trekker utvalg på {n} bilag for år {year}")
        try:
            self.sample_df = (
                self.df.sample(n=n, random_state=year)
                .reset_index(drop=True)
                .copy()
            )
        except ValueError as e:
            logger.error(f"Feil ved trekking av utvalg: {e}")
            messagebox.showerror(APP_TITLE, f"Feil ved trekking av utvalg:\n{e}"); return
        self.decisions = [None]*len(self.sample_df); self.comments=[""]*len(self.sample_df); self.idx=0
        self.render()

    def _current_row_dict(self):
        self._ensure_helpers()
        row = self.sample_df.iloc[self.idx]
        return {
            str(c): to_str(row[c])
            for c in self.sample_df.columns
            if not str(c).startswith("_")
        }

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
        sum_k = calc_sum_kontrollert(self.sample_df, self.decisions)
        sum_a = calc_sum_net_all(self.df)
        pct = (sum_k / sum_a * Decimal("100")) if sum_a else Decimal("0")
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
            if remaining == 0 and not self._pdf_prompt_shown:
                from tkinter import messagebox
                from report import export_pdf
                from .busy import show_busy, hide_busy, run_in_thread

                self._pdf_prompt_shown = True
                if messagebox.askyesno(APP_TITLE, "Ønsker du å eksportere PDF rapport?"):
                    show_busy(self, "Eksporterer rapport...")

                    def finalize():
                        self._finish_progress()
                        hide_busy(self)

                    def worker():
                        self.after(0, lambda: self._start_progress("Eksporterer rapport..."))
                        try:
                            export_pdf(self)
                        finally:
                            self.after(0, finalize)

                    run_in_thread(worker)
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
                self.progress_bar.grid(**getattr(self, "progress_bar_grid", {}))
                self.progress_bar.set(max(0, min(1, progress / 100)))
                self.progress_bar.update_idletasks()
            else:
                self.progress_bar.grid_remove()

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
            key=str(k)
            if key.startswith("_"):
                continue
            val=to_str(row_dict.get(key,"")).strip()
            if not val: continue
            disp = val if (key.lower().startswith("faktura") and "nr" in key.lower()) else format_number_with_thousands(val)
            lines.append(f"{key}: {disp}")
        return "\n".join(lines).strip()

    def _update_status_label(self, status: str | None, placeholder: str = "—"):
        if not hasattr(self, "lbl_status"):
            return

        text = status if status else placeholder

        if status == "Godkjent":
            font = style.FONT_TITLE or style.FONT_TITLE_LITE or style.FONT_BODY
            color = style.get_color("success")
        elif status == "Ikke godkjent":
            font = style.FONT_TITLE or style.FONT_TITLE_LITE or style.FONT_BODY
            color = style.get_color("error")
        else:
            font = style.FONT_TITLE_LITE or style.FONT_BODY
            color = style.get_color("fg")

        self.lbl_status.configure(text=text, font=font, text_color=color)

    def _update_status_card_safe(self):
        try:
            self._update_status_card()
        except Exception:
            logger.exception("Feil ved oppdatering av statuskort")

    def render(self):
        self._ensure_helpers()
        self._update_counts_labels()
        if self.sample_df is not None and len(self.sample_df)>0:
            self.lbl_count.configure(text=f"Bilag: {self.idx+1}/{len(self.sample_df)}")
            inv_val = to_str(self.sample_df.iloc[self.idx].get(self.invoice_col, "")) if len(self.sample_df)>0 else "—"
            self.lbl_invoice.configure(text=f"Fakturanr: {inv_val or '—'}")
            st = self.decisions[self.idx] if (self.decisions and self.idx < len(self.decisions)) else None
            self._update_status_label(st)

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
                    msg = (
                        "Last gjerne også inn en hovedbok for å se bilagslinjene."
                        if getattr(self, "gl_df", None) is None
                        else ""
                    )
                    self.ledger_sum.configure(text=msg)

            self.comment_box.delete("0.0","end")
            if self.comments and self.idx < len(self.comments) and self.comments[self.idx]:
                self.comment_box.insert("0.0", self.comments[self.idx])
        else:
            self.lbl_count.configure(text="Bilag: –/–")
            self.lbl_invoice.configure(text="Fakturanr: –")
            self._update_status_label(None, placeholder="–")
            self.detail_box.configure(state="normal"); self.detail_box.delete("0.0","end"); self.detail_box.insert("0.0","Velg Excel-fil og lag et utvalg."); self.detail_box.configure(state="disabled")
            if hasattr(self, "ledger_tree"):
                for item in self.ledger_tree.get_children():
                    self.ledger_tree.delete(item)
            if hasattr(self, "ledger_sum"):
                msg = (
                    "Last gjerne også inn en hovedbok for å se bilagslinjene."
                    if getattr(self, "gl_df", None) is None
                    else "Trekk utvalg for å se bilagslinjene."
                )
                self.ledger_sum.configure(text=msg)
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
