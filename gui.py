# -*- coding: utf-8 -*-
import re, os, webbrowser
from datetime import datetime

import pandas as pd
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import tkinter.font as tkfont

from helpers import (
    resource_path,
    to_str,
    only_digits,
    parse_amount,
    fmt_money,
    format_number_with_thousands,
    guess_invoice_col,
    guess_col,
    guess_net_amount_col,
    fmt_pct,
)
import report

APP_TITLE = "Bilagskontroll BETA v4"
OPEN_PO_URL = "https://go.poweroffice.net/#reports/purchases/invoice?"

# ----------------- App -----------------
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        self.title(APP_TITLE)
        self.geometry("1280x900")
        self.minsize(1180, 820)

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

        self.logo_img = None
        try:
            from PIL import Image
            img = Image.open(resource_path("Borev logo.png"))
            try:
                self.logo_img = ctk.CTkImage(light_image=img, size=(140, 30))
            except TypeError:
                self.logo_img = ctk.CTkImage(img, size=(140, 30))
        except Exception:
            pass

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.sidebar = self._build_sidebar()
        self.main = self._build_main()

        self.bind("<Left>", lambda e: self.prev())
        self.bind("<Right>", lambda e: self.next())
        self.bind("<Control-o>", lambda e: self.open_in_po())
        self.render()

    # Sidebar
    def _build_sidebar(self):
        card = ctk.CTkFrame(self, corner_radius=16)
        card.grid(row=0, column=0, sticky="nsw", padx=14, pady=14)

        ctk.CTkLabel(card, text="⚙️ Innstillinger", font=ctk.CTkFont(size=18, weight="bold"))\
            .grid(row=0, column=0, padx=14, pady=(14, 6), sticky="w")

        self.file_path_var = ctk.StringVar(master=self, value="")
        ctk.CTkButton(card, text="Velg Excel (fakturaliste)…", command=self.choose_file)\
            .grid(row=1, column=0, padx=14, pady=(4, 2), sticky="ew")
        ctk.CTkLabel(card, textvariable=self.file_path_var, wraplength=260, anchor="w", justify="left")\
            .grid(row=2, column=0, padx=14, pady=(0, 6), sticky="ew")

        self.gl_path_var = ctk.StringVar(master=self, value="")
        ctk.CTkButton(card, text="Velg Hovedbok (Excel)…", command=self.choose_gl_file)\
            .grid(row=3, column=0, padx=14, pady=(2, 2), sticky="ew")
        ctk.CTkLabel(card, textvariable=self.gl_path_var, wraplength=260, anchor="w", justify="left")\
            .grid(row=4, column=0, padx=14, pady=(0, 6), sticky="ew")

        row_utv = ctk.CTkFrame(card)
        row_utv.grid(row=5, column=0, padx=14, pady=(4, 0), sticky="ew")
        ctk.CTkLabel(row_utv, text="Antall tilfeldig utvalg").grid(row=0, column=0, sticky="w")
        self.sample_size_var = ctk.IntVar(master=self, value=10)
        ctk.CTkEntry(row_utv, width=80, textvariable=self.sample_size_var).grid(row=0, column=1, padx=(8, 0))
        ctk.CTkLabel(row_utv, text="År").grid(row=1, column=0, pady=(6, 0), sticky="w")
        self.year_var = ctk.IntVar(master=self, value=datetime.now().year)
        ctk.CTkEntry(row_utv, width=80, textvariable=self.year_var).grid(row=1, column=1, padx=(8, 0), pady=(6, 0))

        ctk.CTkButton(card, text="🎲 Lag utvalg", command=self.make_sample)\
            .grid(row=6, column=0, padx=14, pady=(8, 6), sticky="ew")

        self.lbl_filecount = ctk.CTkLabel(card, text="Antall bilag: –", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_filecount.grid(row=7, column=0, padx=14, pady=(2, 2), sticky="w")

        # Oppdragsinfo
        ctk.CTkLabel(card, text="Oppdragsinfo", font=ctk.CTkFont(size=14, weight="bold"))\
            .grid(row=8, column=0, padx=14, pady=(8, 2), sticky="w")
        opp = ctk.CTkFrame(card, corner_radius=8)
        opp.grid(row=9, column=0, padx=14, pady=(0, 8), sticky="ew")
        opp.grid_columnconfigure(0, weight=0)
        opp.grid_columnconfigure(1, weight=1)

        self.kunde_var = ctk.StringVar(master=self, value="")
        self.kundenr_var = ctk.StringVar(master=self, value="")
        try:
            default_user = os.environ.get("USERNAME") or os.environ.get("USER") or ""
        except Exception:
            default_user = ""
        self.utfort_av_var = ctk.StringVar(master=self, value=default_user)

        ctk.CTkLabel(opp, text="Kunde").grid(row=0, column=0, padx=(8,8), pady=(8,4), sticky="w")
        self.kunde_entry = ctk.CTkEntry(opp, textvariable=self.kunde_var, placeholder_text="Hentes fra fakturaliste", state="disabled")
        self.kunde_entry.grid(row=0, column=1, padx=(0,8), pady=(8,4), sticky="ew")
        ctk.CTkLabel(opp, text="Kundenr").grid(row=1, column=0, padx=(8,8), pady=(4,4), sticky="w")
        ctk.CTkEntry(opp, textvariable=self.kundenr_var).grid(row=1, column=1, padx=(0,8), pady=(4,4), sticky="ew")
        ctk.CTkLabel(opp, text="Utført av").grid(row=2, column=0, padx=(8,8), pady=(4,8), sticky="w")
        ctk.CTkEntry(opp, textvariable=self.utfort_av_var).grid(row=2, column=1, padx=(0,8), pady=(4,8), sticky="ew")

        # Spacer som presser bunnelementer ned
        card.grid_rowconfigure(20, weight=1)
        
        ctk.CTkLabel(card, text="Tema", font=ctk.CTkFont(size=13))\
            .grid(row=101, column=0, padx=14, pady=(0, 0), sticky="w")
        theme = ctk.CTkSegmentedButton(card, values=["System", "Light", "Dark"], command=self._switch_theme)
        theme.set("System")
        theme.grid(row=102, column=0, padx=14, pady=(2, 14), sticky="ew")

        # Status card
        status_card = ctk.CTkFrame(card, corner_radius=12)
        status_card.grid(row=100, column=0, padx=14, pady=(8, 14), sticky="ew")
        status_card.grid_columnconfigure(0, weight=1)

        title_font = ctk.CTkFont(size=18, weight="bold")
        body_font = ctk.CTkFont(size=14)

        ctk.CTkLabel(status_card, text="Status", font=title_font, anchor="center", justify="center")\
            .grid(row=0, column=0, sticky="ew", pady=(10, 6))

        self.lbl_st_sum_kontrollert = ctk.CTkLabel(status_card, text="Sum kontrollert: –", font=body_font, anchor="center", justify="center")
        self.lbl_st_sum_kontrollert.grid(row=1, column=0, sticky="ew", pady=(0,2))

        self.lbl_st_sum_alle = ctk.CTkLabel(status_card, text="Sum alle bilag: –", font=body_font, anchor="center", justify="center")
        self.lbl_st_sum_alle.grid(row=2, column=0, sticky="ew", pady=(0,2))

        self.lbl_st_pct = ctk.CTkLabel(status_card, text="% kontrollert av sum: –", font=body_font, anchor="center", justify="center")
        self.lbl_st_pct.grid(row=3, column=0, sticky="ew", pady=(0,8))

        self.lbl_st_godkjent = ctk.CTkLabel(status_card, text="Godkjent: –", font=body_font, anchor="center", justify="center")
        self.lbl_st_godkjent.grid(row=4, column=0, sticky="ew", pady=(0,2))

        self.lbl_st_ikkegodkjent = ctk.CTkLabel(status_card, text="Ikke godkjent: –", font=body_font, anchor="center", justify="center")
        self.lbl_st_ikkegodkjent.grid(row=5, column=0, sticky="ew", pady=(0,2))

        self.lbl_st_gjen = ctk.CTkLabel(status_card, text="Gjenstår å kontrollere: –", font=body_font, anchor="center", justify="center")
        self.lbl_st_gjen.grid(row=6, column=0, sticky="ew", pady=(6,10))

        return card

    # Main panel
    def _build_main(self):
        panel = ctk.CTkFrame(self, corner_radius=16)
        panel.grid(row=0, column=1, sticky="nsew", padx=(0, 14), pady=14)
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(2, weight=1)

        head = ctk.CTkFrame(panel)
        head.grid(row=0, column=0, sticky="ew", padx=12, pady=8)
        head.grid_columnconfigure(6, weight=1)
        self.lbl_count  = ctk.CTkLabel(head, text="Bilag: –/–",  font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_status = ctk.CTkLabel(head, text="Status: –")
        self.lbl_invoice= ctk.CTkLabel(head, text="Fakturanr: –")
        self.lbl_count.grid(row=0, column=0, padx=(4, 12))
        self.lbl_status.grid(row=0, column=1, padx=8)
        self.lbl_invoice.grid(row=0, column=2, padx=8)
        ctk.CTkButton(head, text="📋 Kopier fakturanr", command=self.copy_invoice).grid(row=0, column=3, padx=(8,0))
        self.copy_feedback = ctk.CTkLabel(head, text="", text_color="#2ecc71")
        self.copy_feedback.grid(row=0, column=4, padx=8, sticky="w")

        self.inline_status = ctk.CTkLabel(head, text="", text_color="#2ecc71")
        self.inline_status.grid(row=0, column=5, padx=8, sticky="e")

        btns = ctk.CTkFrame(panel)
        btns.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 4))
        btns.grid_columnconfigure((0,1,2,3,4), weight=1)

        ctk.CTkButton(btns, text="✅ Godkjent", fg_color="#2ecc71", hover_color="#29b765",
                      command=lambda: self.set_decision_and_next("Godkjent")).grid(row=0, column=0, padx=6, pady=6, sticky="ew")
        ctk.CTkButton(btns, text="⛔ Ikke godkjent", fg_color="#e74c3c", hover_color="#cf4334",
                      command=lambda: self.set_decision_and_next("Ikke godkjent")).grid(row=0, column=1, padx=6, pady=6, sticky="ew")
        ctk.CTkButton(btns, text="🔗 Åpne i PowerOffice", command=self.open_in_po).grid(row=0, column=2, padx=6, pady=6, sticky="ew")
        ctk.CTkButton(btns, text="⬅ Forrige", command=self.prev).grid(row=0, column=3, padx=6, pady=6, sticky="ew")
        ctk.CTkButton(btns, text="➡ Neste", command=self.next).grid(row=0, column=4, padx=6, pady=6, sticky="ew")

        paned = tk.PanedWindow(panel, orient="horizontal")
        paned.grid(row=2, column=0, sticky="nsew", padx=12, pady=(4, 6))
        left  = ctk.CTkFrame(paned)
        right = ctk.CTkFrame(paned)
        paned.add(left,  minsize=420)
        paned.add(right, minsize=420)

        ctk.CTkLabel(left, text="Detaljer for bilag", font=ctk.CTkFont(size=15, weight="bold"))\
            .grid(row=0, column=0, sticky="w", padx=8, pady=(4,4))
        left.grid_columnconfigure(0, weight=1); left.grid_rowconfigure(1, weight=1)
        self.detail_box = ctk.CTkTextbox(left, height=360, font=ctk.CTkFont(size=14))
        self.detail_box.grid(row=1, column=0, sticky="nsew", padx=(8,6), pady=(0,8))

        ctk.CTkLabel(right, text="Hovedbok (bilagslinjer)", font=ctk.CTkFont(size=15, weight="bold"))\
            .grid(row=0, column=0, sticky="w", padx=8, pady=(4,4))
        right.grid_columnconfigure(0, weight=1); right.grid_rowconfigure(1, weight=1)

        self.ledger_cols = ["Kontonr", "Konto", "Beskrivelse", "MVA", "MVA-beløp", "Beløp", "Postert av"]
        self.ledger_tree = ttk.Treeview(right, columns=self.ledger_cols, show="headings", height=10, style="Custom.Treeview")
        for col, w, anchor in [
            ("Kontonr", 90, "w"), ("Konto", 180, "w"),
            ("Beskrivelse", 260, "w"), ("MVA", 70, "w"),
            ("MVA-beløp", 110, "e"), ("Beløp", 110, "e"),
            ("Postert av", 140, "w")
        ]:
            self.ledger_tree.heading(col, text=col)
            self.ledger_tree.column(col, width=w, minwidth=60, anchor=anchor, stretch=True)

        # Themed scrollbars
        yscroll = ctk.CTkScrollbar(right, orientation="vertical", command=self.ledger_tree.yview)
        xscroll = ctk.CTkScrollbar(right, orientation="horizontal", command=self.ledger_tree.xview)
        self.ledger_tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        self.ledger_tree.grid(row=1, column=0, sticky="nsew")
        yscroll.grid(row=1, column=1, sticky="ns")
        xscroll.grid(row=2, column=0, sticky="ew")

        self._apply_treeview_theme()
        self._update_treeview_stripes()

        self.ledger_sum = ctk.CTkLabel(right, text=" ", anchor="e", justify="right")
        self.ledger_sum.grid(row=3, column=0, columnspan=2, sticky="ew", padx=(0, 12), pady=(6, 10))

        ctk.CTkLabel(right, text="Kommentar", font=ctk.CTkFont(size=15, weight="bold"))\
            .grid(row=4, column=0, columnspan=2, sticky="w", padx=0, pady=(8,4))
        self.comment_box = ctk.CTkTextbox(right, height=110, font=ctk.CTkFont(size=13))
        self.comment_box.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=0, pady=(0,0))

        bottom = ctk.CTkFrame(panel)
        bottom.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 0))
        ctk.CTkButton(bottom, text="📄 Eksporter PDF rapport", command=lambda: report.export_pdf(self)).pack(side="left")
        ctk.CTkLabel(bottom, text="").pack(side="left", expand=True, fill="x")
        if self.logo_img:
            ctk.CTkLabel(bottom, text="", image=self.logo_img).pack(side="right", padx=(8,0))
        return panel

    # Theme
    def _switch_theme(self, mode):
        ctk.set_appearance_mode("light" if mode.lower()=="light" else "dark" if mode.lower()=="dark" else "system")
        self._apply_treeview_theme()
        self._update_treeview_stripes()
        self.render()

    def _apply_treeview_theme(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        mode = ctk.get_appearance_mode().lower()
        if mode == "dark":
            bg = "#1e1e1e"; fg = "#e6e6e6"; hb = "#2a2a2a"; sel_bg = "#3a3a3a"; sel_fg = "#ffffff"
        else:
            bg = "#ffffff"; fg = "#000000"; hb = "#f0f0f0"; sel_bg = "#d0d0ff"; sel_fg = "#000000"
        style.configure("Custom.Treeview",
                        background=bg, fieldbackground=bg, foreground=fg, rowheight=24, borderwidth=0)
        style.configure("Custom.Treeview.Heading",
                        background=hb, foreground=fg, borderwidth=0)
        style.map("Custom.Treeview",
                  background=[("selected", sel_bg)],
                  foreground=[("selected", sel_fg)])
        self.ledger_tree.configure(style="Custom.Treeview")

    def _update_treeview_stripes(self):
        mode = ctk.get_appearance_mode().lower()
        if mode == "dark":
            odd = "#232323"; even = "#1e1e1e"
        else:
            odd = "#f6f6f6"; even = "#ffffff"
        self.ledger_tree.tag_configure("odd", background=odd)
        self.ledger_tree.tag_configure("even", background=even)

    # Files
    def choose_file(self):
        p = filedialog.askopenfilename(title="Velg Excel (fakturaliste)", filetypes=[("Excel","*.xlsx *.xls")])
        if not p: return
        self.file_path_var.set(p)
        self._load_excel()

    def choose_gl_file(self):
        p = filedialog.askopenfilename(title="Velg Hovedbok (Excel)", filetypes=[("Excel","*.xlsx *.xls")])
        if not p: return
        self.gl_path_var.set(p)
        self._load_gl_excel()

    # Read
    def _load_excel(self):
        path = self.file_path_var.get()
        if not path: return
        header_idx = 4
        try:
            df = pd.read_excel(path, engine="openpyxl", header=header_idx)
            self.antall_bilag = len(df.dropna(how="all"))
            self.df = df
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Klarte ikke lese Excel:\n{e}")
            self.df = None
            return

        if self.df is None or self.df.dropna(how="all").empty:
            messagebox.showwarning(APP_TITLE, "Excel-filen ser tom ut."); return

        self.invoice_col = guess_invoice_col(self.df.columns)
        self.net_amount_col = guess_net_amount_col(self.df.columns)
        # Hent kundenavn automatisk fra fakturaliste (linje 2)
        try:
            cust = self._extract_customer_from_invoice_file(path)
            if cust:
                self.kunde_var.set(cust)
            if hasattr(self, "kunde_entry"):
                self.kunde_entry.configure(state="disabled")
        except Exception:
            pass

        self.sample_df = None; self.decisions=[]; self.comments=[]; self.idx=0
        self._update_counts_labels(); self.render()

    def _load_gl_excel(self):
        path = self.gl_path_var.get()
        if not path: return
        try:
            gl = pd.read_excel(path, engine="openpyxl", header=0)
            if sum(str(c).lower().startswith("unnamed") for c in gl.columns) > len(gl.columns)/2:
                gl = pd.read_excel(path, engine="openpyxl", header=4)
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Klarte ikke lese hovedbok:\n{e}")
            return
        if gl is None or gl.dropna(how="all").empty:
            messagebox.showwarning(APP_TITLE, "Hovedboken ser tom ut."); return

        self.gl_df = gl; cols = [str(c) for c in gl.columns]
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

        self.render()

    
    def _extract_customer_from_invoice_file(self, path: str):
        """
        Leser rad 2 i fakturalista og prøver å hente ut kundenavn.
        Strategi:
          - Søk etter mønster "Kunde: <navn>" eller "Customer: <navn>" i rad 2
          - Hvis ikke funn, velg lengste ikke-numeriske tekstcelle i rad 2
        """
        try:
            raw = pd.read_excel(path, engine="openpyxl", header=None, nrows=2)
        except Exception:
            return None
        if raw is None or len(raw) < 2:
            return None
        row2 = raw.iloc[1].fillna("")
        # Direkte mønster "Kunde: X"
        for v in row2.values:
            s = str(v).strip()
            m = re.match(r"^\s*(Kunde|Customer)\s*[:\-]\s*(.+)$", s, flags=re.IGNORECASE)
            if m:
                return m.group(2).strip()
        # Velg den lengste tekstcellen som ikke ser ut som tall/dato
        candidates = []
        for v in row2.values:
            s = str(v).strip()
            if not s:
                continue
            if re.fullmatch(r"[\d\s\.,:/-]+", s):
                continue
            # unngå typiske etiketter
            if re.search(r"faktura|liste|dato|org|orgnr|organisasjonsnummer|periode|rapport|utvalg", s, re.IGNORECASE):
                continue
            candidates.append(s)
        if candidates:
            return max(candidates, key=len)
        return None
# Sampling / nav
    def _update_counts_labels(self):
        self.lbl_filecount.configure(text=f"Antall bilag: {self.antall_bilag}")
        
    def make_sample(self):
        if self.df is None:
            messagebox.showinfo(APP_TITLE, "Velg Excel først."); return
        try:
            n = max(1, min(int(self.sample_size_var.get()), len(self.df)))
            year = int(self.year_var.get())
        except Exception:
            n, year = min(len(self.df), 10), datetime.now().year
        try:
            self.sample_df = self.df.sample(n=n, random_state=year).reset_index(drop=True)
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Feil ved trekking av utvalg:\n{e}"); return
        self.decisions = [None]*len(self.sample_df); self.comments=[""]*len(self.sample_df); self.idx=0
        self.render()

    def _current_row_dict(self):
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
        webbrowser.open(OPEN_PO_URL)
        self._show_inline("Åpner PowerOffice")
    
    def copy_invoice(self):
        if self.sample_df is None: return
        inv_val = to_str(self.sample_df.iloc[self.idx].get(self.invoice_col, ""))
        digits = only_digits(inv_val)
        self.clipboard_clear(); self.clipboard_append(digits if digits else inv_val)
        self.copy_feedback.configure(text="Kopiert")
        self.after(1500, lambda: self.copy_feedback.configure(text=""))

    # Ledger
    def _ledger_rows(self, invoice_value: str):
        if self.gl_df is None or self.gl_invoice_col not in (self.gl_df.columns if self.gl_df is not None else []):
            return []
        key = only_digits(invoice_value)
        if not key: return []
        df = self.gl_df.copy()
        try: mask = df[self.gl_invoice_col].astype(str).map(only_digits) == key
        except Exception: mask = df[self.gl_invoice_col].astype(str) == invoice_value
        hits = df.loc[mask]
        rows = []
        for _, r in hits.iterrows():
            konto_nr = to_str(r.get(self.gl_accountno_col, ""))
            if not konto_nr:
                cand = to_str(r.get(self.gl_accountname_col, "")); m = re.match(r"^\s*(\d{3,6})\b", cand)
                if m: konto_nr = m.group(1)
            konto_navn = to_str(r.get(self.gl_accountname_col, ""))
            if not konto_navn:
                combo = to_str(r.get(self.gl_accountno_col, "")); m = re.match(r"^\s*(\d{3,6})\s*[-–:]?\s*(.+)$", combo)
                if m: 
                    if not konto_nr: konto_nr = m.group(1)
                    konto_navn = m.group(2)
            beskr      = to_str(r.get(self.gl_desc_col, "")) or to_str(r.get(self.gl_text_col, ""))
            mva_code   = to_str(r.get(self.gl_vatcode_col, ""))
            mva_belop  = fmt_money(r.get(self.gl_vatamount_col, ""))
            deb        = parse_amount(r.get(self.gl_debit_col)) if self.gl_debit_col else None
            kre        = parse_amount(r.get(self.gl_credit_col)) if self.gl_credit_col else None
            belop      = parse_amount(r.get(self.gl_amount_col)) if self.gl_amount_col else None
            if belop is None and (deb is not None or kre is not None):
                belop = (deb or 0.0) - (kre or 0.0)
            belop_str  = fmt_money(belop)
            postert_av = to_str(r.get(self.gl_postedby_col, ""))
            rows.append({"Kontonr": konto_nr,"Konto": konto_navn,"Beskrivelse": beskr,"MVA": mva_code,"MVA-beløp": mva_belop,"Beløp": belop_str,"Postert av": postert_av})
        return rows

    def _autofit_tree_columns(self, tree: ttk.Treeview, cols):
        body_font = tkfont.nametofont("TkDefaultFont")
        try: head_font = tkfont.nametofont("TkHeadingFont")
        except Exception: head_font = body_font
        for col in cols:
            max_px = head_font.measure(col)
            for iid in tree.get_children(""):
                txt = str(tree.set(iid, col)); px = body_font.measure(txt)
                if px > max_px: max_px = px
            max_px = max(70, min(max_px + 24, 500))
            tree.column(col, width=max_px)

    def _populate_ledger_table(self, invoice_value: str):
        for item in self.ledger_tree.get_children(): self.ledger_tree.delete(item)
        rows = self._ledger_rows(invoice_value)
        if not rows:
            msg = "Ingen hovedbok lastet." if self.gl_df is None else "Ingen bilagslinjer for dette bilagsnummeret."
            self.ledger_sum.configure(text=msg); return
        total = 0.0
        for i, r in enumerate(rows):
            tags = ["even" if i % 2 == 0 else "odd"]
            v = parse_amount(r["Beløp"]); total += (v or 0.0)
            self.ledger_tree.insert("", "end", values=[r[c] for c in self.ledger_cols], tags=tags)
        self._autofit_tree_columns(self.ledger_tree, self.ledger_cols)
        self.ledger_sum.configure(text=f"Sum beløp: {fmt_money(total)}   •   Linjer: {len(rows)}")

    # Summary / status
    def _calc_sum_kontrollert(self):
        if self.sample_df is None: return 0.0
        total = 0.0
        for i, d in enumerate(self.decisions):
            if d is None: continue
            row = self.sample_df.iloc[i]
            val = None
            if self.net_amount_col and self.net_amount_col in self.sample_df.columns:
                val = parse_amount(row.get(self.net_amount_col))
            if val is None:
                for fb in ["Beløp","Belop","Total","Sum","Nettobeløp","Netto beløp","Beløp eks mva"]:
                    if fb in self.sample_df.columns:
                        val = parse_amount(row.get(fb)); 
                        if val is not None: break
            if val is not None: total += val
        return total

    def _row_has_sum_word(self, row: pd.Series) -> bool:
        for v in row.values:
            if isinstance(v, str) and re.search(r"\bsum\b", v, re.IGNORECASE):
                return True
        return False

    def _calc_sum_net_all(self):
        if self.df is None or self.df.dropna(how="all").empty: return 0.0
        df_eff = self.df.dropna(how="all").copy()
        if len(df_eff) > 0: df_eff = df_eff.iloc[:-1]
        df_eff = df_eff.loc[~df_eff.apply(self._row_has_sum_word, axis=1)]
        col = self.net_amount_col if (self.net_amount_col in df_eff.columns) else None
        total = 0.0
        for _, r in df_eff.iterrows():
            v = parse_amount(r.get(col)) if col else None
            if v is None:
                for fb in ["Beløp","Belop","Total","Sum","Nettobeløp","Netto beløp","Beløp eks mva"]:
                    if fb in df_eff.columns:
                        v = parse_amount(r.get(fb)); 
                        if v is not None: break
            if v is not None: total += v
        return total

    def _update_status_card(self):
        sum_k = self._calc_sum_kontrollert()
        sum_a = self._calc_sum_net_all()
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

    # PDF
    # Inline
    def _show_inline(self, msg: str, ok=True):
        self.inline_status.configure(text_color=("#2ecc71" if ok else "#e74c3c"))
        self.inline_status.configure(text=msg)
        self.after(3500, lambda: self.inline_status.configure(text=""))

    # Details + render
    def _details_text_for_row(self, row_dict):
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

            self._populate_ledger_table(inv_val)

            self.comment_box.delete("0.0","end")
            if self.comments and self.idx < len(self.comments) and self.comments[self.idx]:
                self.comment_box.insert("0.0", self.comments[self.idx])
        else:
            self.lbl_count.configure(text="Bilag: –/–"); self.lbl_invoice.configure(text="Fakturanr: –"); self.lbl_status.configure(text="Status: –")
            self.detail_box.configure(state="normal"); self.detail_box.delete("0.0","end"); self.detail_box.insert("0.0","Velg Excel-fil og lag et utvalg."); self.detail_box.configure(state="disabled")
            for item in self.ledger_tree.get_children(): self.ledger_tree.delete(item)
            self.ledger_sum.configure(text="Last gjerne også inn en hovedbok for å se bilagslinjene.")
            self.comment_box.delete("0.0","end")

        self._update_status_card_safe()

# if __name__ == "__main__":
#     App().mainloop()
