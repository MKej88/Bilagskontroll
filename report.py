# -*- coding: utf-8 -*-
import os
from datetime import datetime
from tkinter import filedialog

from helpers import (
    to_str,
    parse_amount,
    fmt_money,
    fmt_pct,
    format_number_with_thousands,
)


def export_pdf(app):
    if app.sample_df is None:
        app._show_inline("Lag et utvalg først", ok=False)
        return
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
            PageBreak,
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
    except ImportError:
        app._show_inline("Manglende modul: reportlab (py -m pip install reportlab)", ok=False)
        return

    save = filedialog.asksaveasfilename(
        title="Lagre PDF-rapport",
        defaultextension=".pdf",
        filetypes=[("PDF", "*.pdf")],
        initialfile=f"bilagskontroll_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
    )
    if not save:
        app._show_inline("Avbrutt", ok=False)
        return

    styles = getSampleStyleSheet()
    title = styles["Title"]
    body = styles["BodyText"]
    body.fontSize = 9
    body.leading = 11
    small = ParagraphStyle("small", parent=body, fontSize=8, leading=10)

    approved = sum(1 for d in app.decisions if d == "Godkjent")
    rejected = sum(1 for d in app.decisions if d == "Ikke godkjent")
    remaining = sum(1 for d in app.decisions if d is None)
    sum_k = app._calc_sum_kontrollert()
    sum_a = app._calc_sum_net_all()
    pct = (sum_k / sum_a * 100.0) if sum_a else 0.0

    flow = []
    flow.append(Paragraph("Bilagskontroll – Rapport", title))
    flow.append(Paragraph(datetime.now().strftime("%d.%m.%Y %H:%M"), body))
    flow.append(Spacer(1, 4))
    try:
        kunde = to_str(app.kunde_var.get()) if hasattr(app, "kunde_var") else ""
        kundenr = to_str(app.kundenr_var.get()) if hasattr(app, "kundenr_var") else ""
        utfort = to_str(app.utfort_av_var.get()) if hasattr(app, "utfort_av_var") else ""
    except Exception:
        kunde = kundenr = utfort = ""
    info_rows = []
    if kunde:
        info_rows.append(["Kunde", kunde])
    if kundenr:
        info_rows.append(["Kundenr", kundenr])
    if utfort:
        info_rows.append(["Utført av", utfort])
    if info_rows:
        info_tbl = Table(info_rows, colWidths=[80, 440], hAlign="LEFT")
        info_tbl.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        flow.append(info_tbl)
        flow.append(Spacer(1, 6))
    flow.append(
        Paragraph(
            f"<b>Status</b>: Sum kontrollert: {fmt_money(sum_k)} kr  •  "
            f"Sum alle bilag: {fmt_money(sum_a)} kr  •  "
            f"% kontrollert: {fmt_pct(pct)}  •  "
            f"Godkjent: {approved}  •  Ikke godkjent: {rejected}  •  Gjenstår: {remaining}",
            body,
        )
    )
    flow.append(Spacer(1, 8))

    def ledger_table_for_invoice(invoice_value: str):
        rows = app._ledger_rows(invoice_value)
        if not rows:
            return Paragraph("Ingen bokføringslinjer for dette fakturanummeret.", small)
        data = [["Kontonr", "Konto", "MVA", "MVA-beløp", "Beløp", "Postert av"]]
        total = 0.0
        for r in rows:
            v = parse_amount(r["Beløp"])
            total += v or 0.0
            data.append(
                [
                    r["Kontonr"],
                    r["Konto"],
                    r["MVA"],
                    r["MVA-beløp"],
                    r["Beløp"],
                    r["Postert av"],
                ]
            )
        data.append(["", "", "", "Sum:", fmt_money(total), ""])
        colw = [60, 200, 35, 70, 70, 88]
        tbl = Table(data, colWidths=colw, repeatRows=1, hAlign="LEFT")
        tbl.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (4, 1), (5, -2), "RIGHT"),
                    ("ALIGN", (4, -1), (5, -1), "RIGHT"),
                    ("SPAN", (0, -1), (3, -1)),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                    ("BACKGROUND", (0, 2), (-1, 2), colors.white),
                ]
            )
        )
        return tbl

    total = len(app.sample_df)
    for i in range(total):
        r = app.sample_df.iloc[i]
        inv = to_str(r.get(app.invoice_col, ""))
        dec = app.decisions[i] if i < len(app.decisions) else ""
        com = app.comments[i].strip() if i < len(app.comments) else ""
        rows = [["Felt", "Verdi"]]
        row_dict = {str(c): to_str(r[c]) for c in app.sample_df.columns}
        for k in app.sample_df.columns:
            key = str(k)
            val = to_str(row_dict.get(key, ""))
            if not val:
                continue
            disp = (
                val
                if (key.lower().startswith("faktura") and "nr" in key.lower())
                else format_number_with_thousands(val)
            )
            rows.append([key, disp])
        rows += [["Beslutning", dec or ""], ["Kommentar", com or ""]]
        det_tbl = Table(rows, colWidths=[160, 360])
        det_tbl.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        flow.append(
            Paragraph(
                f"Bilag {i+1}/{total} – Fakturanr: <b>{inv}</b>",
                styles["Heading3"],
            )
        )
        flow.append(det_tbl)
        flow.append(Spacer(1, 6))
        flow.append(ledger_table_for_invoice(inv))
        if i < total - 1:
            flow.append(Spacer(1, 10))
        if (i + 1) % 2 == 0 and i < total - 1:
            flow.append(PageBreak())

    doc = SimpleDocTemplate(
        save,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    try:
        doc.build(flow)
        app._show_inline(f"Lagret PDF: {os.path.basename(save)}", ok=True)
    except Exception as e:
        app._show_inline(f"Feil ved PDF-generering: {e}", ok=False)
