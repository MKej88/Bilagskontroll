import re
import customtkinter as ctk
from tkinter import ttk
import tkinter.font as tkfont
from helpers import to_str, only_digits, parse_amount, fmt_money

LEDGER_COLS = ["Kontonr", "Konto", "Beskrivelse", "MVA", "MVA-beløp", "Beløp", "Postert av"]


def apply_treeview_theme(app):
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
    font = app.detail_box.cget("font") if hasattr(app, "detail_box") else ctk.CTkFont(size=14)
    style.configure(
        "Custom.Treeview",
        background=bg,
        fieldbackground=bg,
        foreground=fg,
        rowheight=24,
        borderwidth=0,
        font=font,
    )
    style.configure("Custom.Treeview.Heading",
                    background=hb, foreground=fg, borderwidth=0)
    style.map("Custom.Treeview",
              background=[("selected", sel_bg)],
              foreground=[("selected", sel_fg)])
    app.ledger_tree.configure(style="Custom.Treeview")


def update_treeview_stripes(app):
    mode = ctk.get_appearance_mode().lower()
    if mode == "dark":
        odd = "#232323"; even = "#1e1e1e"
    else:
        odd = "#f6f6f6"; even = "#ffffff"
    app.ledger_tree.tag_configure("odd", background=odd)
    app.ledger_tree.tag_configure("even", background=even)


def ledger_rows(app, invoice_value: str):
    """Hent bilagslinjer for gitt bilagsnummer uten å endre ``gl_df``."""
    if app.gl_df is None or app.gl_invoice_col not in (app.gl_df.columns if app.gl_df is not None else []):
        return []
    key = only_digits(invoice_value)
    if not key:
        return []
    # Funksjonen muterer ikke app.gl_df, så kopi er unødvendig
    try:
        mask = app.gl_df[app.gl_invoice_col].astype(str).map(only_digits) == key
    except Exception:
        mask = app.gl_df[app.gl_invoice_col].astype(str) == invoice_value
    hits = app.gl_df.loc[mask]
    rows = []
    for _, r in hits.iterrows():
        konto_nr = to_str(r.get(app.gl_accountno_col, ""))
        if not konto_nr:
            cand = to_str(r.get(app.gl_accountname_col, ""))
            m = re.match(r"^\s*(\d{3,6})\b", cand)
            if m:
                konto_nr = m.group(1)
        konto_navn = to_str(r.get(app.gl_accountname_col, ""))
        if not konto_navn:
            combo = to_str(r.get(app.gl_accountno_col, ""))
            m = re.match(r"^\s*(\d{3,6})\s*[-–:]?\s*(.+)$", combo)
            if m:
                if not konto_nr:
                    konto_nr = m.group(1)
                konto_navn = m.group(2)
        beskr = to_str(r.get(app.gl_desc_col, "")) or to_str(r.get(app.gl_text_col, ""))
        mva_code = to_str(r.get(app.gl_vatcode_col, ""))
        mva_belop = fmt_money(r.get(app.gl_vatamount_col, ""))
        deb = parse_amount(r.get(app.gl_debit_col)) if app.gl_debit_col else None
        kre = parse_amount(r.get(app.gl_credit_col)) if app.gl_credit_col else None
        belop = parse_amount(r.get(app.gl_amount_col)) if app.gl_amount_col else None
        if belop is None and (deb is not None or kre is not None):
            belop = (deb or 0.0) - (kre or 0.0)
        belop_str = fmt_money(belop)
        postert_av = to_str(r.get(app.gl_postedby_col, ""))
        rows.append({
            "Kontonr": konto_nr,
            "Konto": konto_navn,
            "Beskrivelse": beskr,
            "MVA": mva_code,
            "MVA-beløp": mva_belop,
            "Beløp": belop_str,
            "Postert av": postert_av,
        })
    return rows


def autofit_tree_columns(tree: ttk.Treeview, cols):
    body_font = tkfont.nametofont("TkDefaultFont")
    try:
        head_font = tkfont.nametofont("TkHeadingFont")
    except Exception:
        head_font = body_font
    for col in cols:
        max_px = head_font.measure(col)
        for iid in tree.get_children(""):
            txt = str(tree.set(iid, col))
            px = body_font.measure(txt)
            if px > max_px:
                max_px = px
        max_px = max(70, min(max_px + 24, 500))
        tree.column(col, width=max_px)


def populate_ledger_table(app, invoice_value: str):
    for item in app.ledger_tree.get_children():
        app.ledger_tree.delete(item)
    rows = ledger_rows(app, invoice_value)
    if not rows:
        msg = "Ingen hovedbok lastet." if app.gl_df is None else "Ingen bilagslinjer for dette bilagsnummeret."
        app.ledger_sum.configure(text=msg)
        return
    total = 0.0
    for i, r in enumerate(rows):
        tags = ["even" if i % 2 == 0 else "odd"]
        v = parse_amount(r["Beløp"])
        total += (v or 0.0)
        app.ledger_tree.insert("", "end", values=[r[c] for c in app.ledger_cols], tags=tags)
    autofit_tree_columns(app.ledger_tree, app.ledger_cols)
    app.ledger_sum.configure(text=f"Sum beløp: {fmt_money(total)}   •   Linjer: {len(rows)}")
