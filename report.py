# -*- coding: utf-8 -*-
import os
from datetime import datetime
from tkinter import filedialog

from helpers import to_str


def export_pdf(app):
    """Eksporter rapport til PDF."""
    if app.sample_df is None:
        app._show_inline("Lag et utvalg først", ok=False)
        return
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
    except ImportError:
        app._show_inline("Manglende modul: reportlab (py -m pip install reportlab)", ok=False)
        return

    from report_utils import build_metadata, build_invoice_section

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

    flow = []
    flow.extend(build_metadata(app, title, body, small))

    total = len(app.sample_df)
    for i in range(total):
        r = app.sample_df.iloc[i]
        inv = to_str(r.get(app.invoice_col, ""))
        flow.extend(build_invoice_section(app, inv, i, styles, small))
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
