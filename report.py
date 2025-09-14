# -*- coding: utf-8 -*-
import os
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, TclError
import webbrowser

from helpers import (
    to_str,
    fmt_money,
    fmt_pct,
    format_number_with_thousands,
    logger,
)

from data_utils import calc_sum_kontrollert, calc_sum_net_all
from report_utils import build_ledger_table

try:  # pragma: no cover - valgfri avhengighet
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
except ImportError:  # pragma: no cover
    A4 = SimpleDocTemplate = Paragraph = Spacer = Table = TableStyle = PageBreak = None
    getSampleStyleSheet = ParagraphStyle = colors = None


def create_info_table(app, now):
    info_rows = []
    try:
        kunde = to_str(app.kunde_var.get()) if hasattr(app, "kunde_var") else ""
        utfort = to_str(app.utfort_av_var.get()) if hasattr(app, "utfort_av_var") else ""
    except TclError:
        logger.exception("Klarte ikke hente kundedata")
        kunde = utfort = ""
    if kunde:
        info_rows.append(["Kunde", kunde])
    if utfort:
        info_rows.append(["Utført av", utfort])
    info_rows.append(["Rapport laget", now.strftime("%d.%m.%Y %H:%M")])
    flow = []
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
    return flow


def create_status_table(app, body):
    approved = sum(1 for d in app.decisions if d == "Godkjent")
    rejected = sum(1 for d in app.decisions if d == "Ikke godkjent")
    remaining = sum(1 for d in app.decisions if d is None)
    sum_k = calc_sum_kontrollert(app.sample_df, app.decisions)
    sum_a = calc_sum_net_all(app.df)
    pct = (sum_k / sum_a * 100.0) if sum_a else 0.0

    import pandas as pd
    dec_ser = pd.Series(app.decisions).reindex(app.sample_df.index)

    def _sum_for_decision(dec_value):
        if dec_value is None:
            mask = dec_ser.isna()
        else:
            mask = dec_ser == dec_value
        return float(app.sample_df.loc[mask, "_netto_float"].sum())

    sum_approved = _sum_for_decision("Godkjent")
    sum_rejected = _sum_for_decision("Ikke godkjent")
    sum_remaining = _sum_for_decision(None)

    flow = [
        Paragraph(
            (
                "<b>Status</b>:<br/>"
                f"Sum kontrollert: {fmt_money(sum_k)} kr<br/>"
                f"Sum alle bilag: {fmt_money(sum_a)} kr<br/>"
                f"% kontrollert: {fmt_pct(pct)}"
            ),
            body,
        ),
        Spacer(1, 4),
    ]

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
    return flow


def create_rejected_table(app, styles):
    rejected_rows = []
    for i, d in enumerate(app.decisions):
        if d != "Ikke godkjent":
            continue
        row = app.sample_df.iloc[i]
        inv = to_str(row.get(app.invoice_col, ""))
        val = row.get("_netto_float")
        belop = fmt_money(val) if val is not None else ""
        com = app.comments[i].strip() if i < len(app.comments) else ""
        rejected_rows.append([inv, belop, com])

    flow = []
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
    return flow


def create_invoice_section(app, styles, small):
    flow = []
    total = len(app.sample_df)
    for i in range(total):
        r = app.sample_df.iloc[i]
        inv = to_str(r.get(app.invoice_col, ""))
        dec = app.decisions[i] if i < len(app.decisions) else ""
        com = app.comments[i].strip() if i < len(app.comments) else ""
        rows = [["Felt", "Verdi"]]
        cols = [c for c in app.sample_df.columns if not str(c).startswith("_")]
        row_dict = {str(c): to_str(r[c]) for c in cols}
        for k in cols:
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
        app._set_status("Eksporterer PDF...", (i / total) * 100)
        if i < total - 1:
            flow.append(Spacer(1, 10))
            flow.append(PageBreak())
    return flow


def export_pdf(app):
    if app.sample_df is None:
        app._show_inline("Lag et utvalg først", ok=False)
        return
    if SimpleDocTemplate is None:
        app._show_inline(
            "Manglende modul: reportlab (py -m pip install reportlab)", ok=False
        )
        return

    now = datetime.now()
    save = filedialog.asksaveasfilename(
        title="Lagre PDF-rapport",
        defaultextension=".pdf",
        filetypes=[("PDF", "*.pdf")],
        initialfile=f"bilagskontroll_{now.strftime('%Y%m%d_%H%M%S')}.pdf",
    )
    if not save:
        logger.info("PDF-eksport avbrutt")
        app._show_inline("Avbrutt", ok=False)
        return

    app._set_status("Eksporterer PDF...", 0)

    styles = getSampleStyleSheet()
    title = styles["Title"]
    body = styles["BodyText"]
    body.fontSize = 9
    body.leading = 11
    small = ParagraphStyle("small", parent=body, fontSize=8, leading=10)

    flow = [Paragraph("Bilagskontroll – Rapport", title), Spacer(1, 4)]
    flow += create_info_table(app, now)
    flow += create_status_table(app, body)
    flow += create_rejected_table(app, styles)
    flow += create_invoice_section(app, styles, small)

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
        app._set_status("Eksporterer PDF...", 100)
        logger.info(f"PDF-rapport lagret til {save}")
        app._show_inline(f"Lagret PDF: {os.path.basename(save)}", ok=True)
        try:
            webbrowser.open(Path(save).resolve().as_uri())
        except (webbrowser.Error, OSError) as e:  # pragma: no cover - OS-avhengig
            logger.error(f"Kunne ikke åpne PDF: {e}")
    except Exception as e:  # pragma: no cover - direkte feil fra reportlab
        logger.exception("Feil ved PDF-generering")
        app._show_inline(f"Feil ved PDF-generering: {e}", ok=False)
    finally:
        app._set_status("")

