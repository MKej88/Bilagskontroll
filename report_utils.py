# -*- coding: utf-8 -*-
from datetime import datetime

from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

from helpers import (
    to_str,
    parse_amount,
    fmt_money,
    fmt_pct,
    format_number_with_thousands,
)


def build_metadata(app, title, body, small):
    """Bygger metadata-delen av rapporten."""
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
    return flow


def build_ledger_table(app, invoice_value, small):
    """Bygger tabell med bokføringslinjer for et fakturanummer."""
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


def build_invoice_section(app, inv, idx, styles, small):
    """Bygger seksjonen for ett bilag."""
    r = app.sample_df.iloc[idx]
    dec = app.decisions[idx] if idx < len(app.decisions) else ""
    com = app.comments[idx].strip() if idx < len(app.comments) else ""
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
    flow = [
        Paragraph(
            f"Bilag {idx+1}/{len(app.sample_df)} – Fakturanr: <b>{inv}</b>",
            styles["Heading3"],
        ),
        det_tbl,
        Spacer(1, 6),
        build_ledger_table(app, inv, small),
    ]
    return flow
