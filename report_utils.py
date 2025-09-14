from helpers import parse_amount, fmt_money
from gui.ledger import ledger_rows
from decimal import Decimal


def build_ledger_table(app, invoice_value: str, style_small):
    from reportlab.platypus import Table, TableStyle, Paragraph
    from reportlab.lib import colors
    rows = ledger_rows(app, invoice_value)
    if not rows:
        return Paragraph("Ingen bokføringslinjer for dette fakturanummeret.", style_small)
    data = [["Kontonr", "Konto", "MVA", "MVA-beløp", "Beløp", "Postert av"]]
    total = Decimal("0")
    for r in rows:
        v = parse_amount(r["Beløp"])
        total += v if v is not None else Decimal("0")
        data.append([
            r["Kontonr"],
            r["Konto"],
            r["MVA"],
            r["MVA-beløp"],
            r["Beløp"],
            r["Postert av"],
        ])
    data.append(["", "", "", "Sum:", fmt_money(total), ""])
    colw = [60, 200, 35, 70, 70, 88]
    tbl = Table(data, colWidths=colw, repeatRows=1, hAlign="LEFT")
    tbl.setStyle(
        TableStyle([
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
        ])
    )
    return tbl


def save_pdf(flow, output_path: str):
    """
    Lagre en PDF-rapport til en angitt filsti.

    :param output_path: Full sti til filen PDF-en skal lagres som.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    doc.build(flow)
