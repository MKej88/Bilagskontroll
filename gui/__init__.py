# -*- coding: utf-8 -*-
import webbrowser
from datetime import datetime

import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox


from helpers import (
    resource_path,
    to_str,
    only_digits,
    fmt_money,
    format_number_with_thousands,
    guess_invoice_col,
    guess_col,
    guess_net_amount_col,
    fmt_pct,
)
from data_utils import (
    load_invoice_df,
    load_gl_df,
    extract_customer_from_invoice_file,
    calc_sum_kontrollert,
    calc_sum_net_all,
)
import report
from .sidebar import build_sidebar
from .mainview import build_main
from .ledger import apply_treeview_theme, update_treeview_stripes, populate_ledger_table

APP_TITLE = "Bilagskontroll BETA v2"
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
        try:
            self.iconbitmap(resource_path("icons/bilagskontroll_logo.ico"))
        except Exception:
            try:
                self.app_icon_img = tk.PhotoImage(file=resource_path("icons/bilagskontroll_logo_256.png"))
                self.iconphoto(False, self.app_icon_img)
            except Exception:
                pass

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
            img = Image.open(resource_path("icons/bilagskontroll_logo_256.png"))
            try:
                self.logo_img = ctk.CTkImage(light_image=img, size=(32, 32))
            except TypeError:
                self.logo_img = ctk.CTkImage(img, size=(32, 32))
        except Exception:
            pass

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.sidebar = build_sidebar(self)
        self.sample_size_var.set("")
        self.year_var.set("")
        self.main = build_main(self)

        self.bind("<Left>", lambda e: self.prev())
        self.bind("<Right>", lambda e: self.next())
        self.bind("<Control-o>", lambda e: self.open_in_po())
        self.render()

    # Theme
    def _switch_theme(self, mode):
        ctk.set_appearance_mode("light" if mode.lower()=="light" else "dark" if mode.lower()=="dark" else "system")
        apply_treeview_theme(self)
        update_treeview_stripes(self)
        self.render()

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
            df = load_invoice_df(path, header_idx)
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
            cust = extract_customer_from_invoice_file(path)
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
            gl = load_gl_df(path)
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
# Sampling / nav
    def _update_counts_labels(self):
        self.lbl_filecount.configure(text=f"Antall bilag: {self.antall_bilag}")
        
    def make_sample(self):
        if self.df is None:
            messagebox.showinfo(APP_TITLE, "Velg Excel først."); return
        try:
            n = int(self.sample_size_var.get())
            year = int(self.year_var.get())
        except Exception:
            messagebox.showinfo(APP_TITLE, "Oppgi antall og år.")
            return
        n = max(1, min(n, len(self.df)))
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
    # Summary / status
    def _update_status_card(self):
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

            populate_ledger_table(self, inv_val)

            self.comment_box.delete("0.0","end")
            if self.comments and self.idx < len(self.comments) and self.comments[self.idx]:
                self.comment_box.insert("0.0", self.comments[self.idx])
        else:
            self.lbl_count.configure(text="Bilag: –/–"); self.lbl_invoice.configure(text="Fakturanr: –"); self.lbl_status.configure(text="Status: –")
            self.detail_box.configure(state="normal"); self.detail_box.delete("0.0","end"); self.detail_box.insert("0.0","Velg Excel-fil og lag et utvalg."); self.detail_box.configure(state="disabled")
            for item in self.ledger_tree.get_children(): self.ledger_tree.delete(item)
            self.ledger_sum.configure(text="Last gjerne også inn en hovedbok for å se bilagslinjene.")
            self.comment_box.delete("0.0","end")

        if self.sample_df is None or len(self.sample_df) == 0:
            self.btn_prev.configure(state="disabled")
            self.btn_next.configure(state="disabled")
        else:
            self.btn_prev.configure(state="normal" if self.idx > 0 else "disabled")
            self.btn_next.configure(state="normal" if self.idx < len(self.sample_df) - 1 else "disabled")

        self._update_status_card_safe()

if __name__ == "__main__":
    App().mainloop()
