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

from report_utils import build_ledger_table
from data_utils import calc_sum_kontrollert, calc_sum_net_all


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

    now = datetime.now()
    save = filedialog.asksaveasfilename(
        title="Lagre PDF-rapport",
        defaultextension=".pdf",
        filetypes=[("PDF", "*.pdf")],
        initialfile=f"bilagskontroll_{now.strftime('%Y%m%d_%H%M%S')}.pdf",
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
    sum_k = calc_sum_kontrollert(app.sample_df, app.decisions, app.net_amount_col)
    sum_a = calc_sum_net_all(app.df, app.net_amount_col)
    pct = (sum_k / sum_a * 100.0) if sum_a else 0.0

    def _sum_for_decision(dec_value):
        total = 0.0
        for i, d in enumerate(app.decisions):
            if dec_value == "Godkjent" and d != "Godkjent":
                continue
            if dec_value == "Ikke godkjent" and d != "Ikke godkjent":
                continue
            if dec_value is None and d is not None:
                continue
            row = app.sample_df.iloc[i]
            val = None
            if app.net_amount_col and app.net_amount_col in app.sample_df.columns:
                val = parse_amount(row.get(app.net_amount_col))
            if val is None:
                for fb in [
                    "Beløp",
                    "Belop",
                    "Total",
                    "Sum",
                    "Nettobeløp",
                    "Netto beløp",
                    "Beløp eks mva",
                ]:
                    if fb in app.sample_df.columns:
                        val = parse_amount(row.get(fb))
                        if val is not None:
                            break
            if val is not None:
                total += val
        return total

    sum_approved = _sum_for_decision("Godkjent")
    sum_rejected = _sum_for_decision("Ikke godkjent")
    sum_remaining = _sum_for_decision(None)

    flow = []
    flow.append(Paragraph("Bilagskontroll – Rapport", title))
    flow.append(Paragraph(now.strftime("%d.%m.%Y %H:%M"), body))
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
    info_rows.append(["Rapport laget", now.strftime("%d.%m.%Y %H:%M")])
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
            (
                "<b>Status</b>:<br/>"
                f"Sum kontrollert: {fmt_money(sum_k)} kr<br/>"
                f"Sum alle bilag: {fmt_money(sum_a)} kr<br/>"
                f"% kontrollert: {fmt_pct(pct)}"
            ),
            body,
        )
    )
    flow.append(Spacer(1, 4))
    status_rows = [
        ["Status", "Antall", "Beløp"],
        ["Godkjent", approved, fmt_money(sum_approved)],
        ["Ikke godkjent", rejected, fmt_money(sum_rejected)],
        ["Gjenstår", remaining, fmt_money(sum_remaining)],
    ]
    status_tbl = Table(status_rows, colWidths=[120, 60, 80], hAlign="LEFT")
    status_tbl.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("BACKGROUND", (0, 1), (-1, 1), colors.whitesmoke),
                ("BACKGROUND", (0, 2), (-1, 2), colors.white),
                ("BACKGROUND", (0, 3), (-1, 3), colors.whitesmoke),
            ]
        )
    )
    flow.append(status_tbl)
    flow.append(Spacer(1, 8))

    rejected_rows = []
    for i, d in enumerate(app.decisions):
        if d != "Ikke godkjent":
            continue
        row = app.sample_df.iloc[i]
        inv = to_str(row.get(app.invoice_col, ""))
        val = None
        if app.net_amount_col and app.net_amount_col in app.sample_df.columns:
            val = parse_amount(row.get(app.net_amount_col))
        if val is None:
            for fb in [
                "Beløp",
                "Belop",
                "Total",
                "Sum",
                "Nettobeløp",
                "Netto beløp",
                "Beløp eks mva",
            ]:
                if fb in app.sample_df.columns:
                    val = parse_amount(row.get(fb))
                    if val is not None:
                        break
        belop = fmt_money(val) if val is not None else ""
        com = app.comments[i].strip() if i < len(app.comments) else ""
        rejected_rows.append([inv, belop, com])

    if rejected_rows:
        flow.append(Paragraph("Ikke godkjent", styles["Heading3"]))
        rej_tbl = Table(
            [["Fakturanr", "Beløp", "Kommentar"]] + rejected_rows,
            colWidths=[120, 80, 320],
            hAlign="LEFT",
        )
        rej_tbl.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        flow.append(rej_tbl)
        flow.append(Spacer(1, 8))

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
        flow.append(build_ledger_table(app, inv, small))
        if i < total - 1:
            flow.append(Spacer(1, 10))
        if i < total - 1:
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
