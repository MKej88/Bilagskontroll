LEDGER_COLS = ["Kontonr", "Konto", "Beskrivelse", "MVA", "MVA-beløp", "Beløp", "Postert av"]


def apply_treeview_theme(app):
    from tkinter import ttk
    import customtkinter as ctk
    from .style import style

    ttk_style = ttk.Style()
    try:
        ttk_style.theme_use("clam")
    except Exception:
        pass
    font = app.detail_box.cget("font") if hasattr(app, "detail_box") else ctk.CTkFont(size=14)
    bg = style.get_color("table_bg")
    fg = style.get_color("table_fg")
    hb = style.get_color("table_header_bg")
    sel_bg = style.get_color("table_sel_bg")
    sel_fg = style.get_color("table_sel_fg")
    ttk_style.configure(
        "Custom.Treeview",
        background=bg,
        fieldbackground=bg,
        foreground=fg,
        rowheight=24,
        borderwidth=0,
        font=font,
    )
    ttk_style.configure(
        "Custom.Treeview.Heading",
        background=hb,
        foreground=fg,
        borderwidth=0,
    )
    ttk_style.map(
        "Custom.Treeview",
        background=[("selected", sel_bg)],
        foreground=[("selected", sel_fg)],
    )
    app.ledger_tree.configure(style="Custom.Treeview")


def update_treeview_stripes(app):
    from .style import style

    odd = style.get_color("table_row_odd")
    even = style.get_color("table_row_even")
    app.ledger_tree.tag_configure("odd", background=odd)
    app.ledger_tree.tag_configure("even", background=even)


def sort_treeview(tree, col, reverse, app):
    """Sorter rader i ``tree`` etter valgt kolonne."""
    from helpers import parse_amount

    data = []
    for iid in tree.get_children(""):
        cell = tree.set(iid, col)
        num = parse_amount(cell)
        sort_val = num if num is not None else str(cell).lower()
        data.append((sort_val, iid))
    data.sort(reverse=reverse)
    for idx, (_, iid) in enumerate(data):
        tree.move(iid, "", idx)
    for idx, iid in enumerate(tree.get_children("")):
        tag = "even" if idx % 2 == 0 else "odd"
        tree.item(iid, tags=(tag,))
    arrow = "↓" if reverse else "↑"
    for c in LEDGER_COLS:
        if c == col:
            tree.heading(
                c,
                text=f"{c} {arrow}",
                command=lambda c=c: sort_treeview(tree, c, not reverse, app),
            )
        else:
            tree.heading(
                c, text=c, command=lambda c=c: sort_treeview(tree, c, False, app)
            )
    update_treeview_stripes(app)


def ledger_rows(app, invoice_value: str):
    """Hent bilagslinjer for gitt bilagsnummer uten å endre ``gl_df``."""
    import re
    from helpers import to_str, only_digits, parse_amount, fmt_money

    if app.gl_df is None or not hasattr(app, "gl_index"):
        return []
    key = only_digits(invoice_value)
    if not key:
        return []
    idxs = app.gl_index.get(key)
    if idxs is None or len(idxs) == 0:
        return []
    # ``groupby().indices`` returnerer numpy-arrays; ``len`` fungerer for å
    # sjekke tomme treff uten å utløse "ambiguous truth value".
    hits = app.gl_df.loc[idxs]
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


def autofit_tree_columns(tree, cols, total_width=None):
    import tkinter.font as tkfont

    body_font = tkfont.nametofont("TkDefaultFont")
    try:
        head_font = tkfont.nametofont("TkHeadingFont")
    except Exception:
        head_font = body_font

    widths: list[int] = []
    for col in cols:
        max_px = head_font.measure(col)
        for iid in tree.get_children(""):
            txt = str(tree.set(iid, col))
            px = body_font.measure(txt)
            if px > max_px:
                max_px = px
        max_px = max(70, min(max_px + 24, 500))
        widths.append(max_px)

    if total_width:
        total_content = sum(widths)
        if total_content < total_width:
            extra = (total_width - total_content) // len(widths)
            widths = [w + extra for w in widths]

    for col, w in zip(cols, widths):
        tree.column(col, width=w)


def populate_ledger_table(app, invoice_value: str):
    from helpers import parse_amount, fmt_money

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
