import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from .ledger import LEDGER_COLS, apply_treeview_theme, update_treeview_stripes


def build_main(app):
    panel = ctk.CTkFrame(app, corner_radius=16)
    panel.grid(row=0, column=1, sticky="nsew", padx=(0, 14), pady=14)
    panel.grid_columnconfigure(0, weight=1)
    panel.grid_rowconfigure(2, weight=1, minsize=300)

    head = ctk.CTkFrame(panel)
    head.grid(row=0, column=0, sticky="ew", padx=12, pady=8)
    head.grid_columnconfigure(6, weight=1)
    app.lbl_count = ctk.CTkLabel(head, text="Bilag: –/–", font=ctk.CTkFont(size=16, weight="bold"))
    app.lbl_status = ctk.CTkLabel(head, text="Status: –")
    app.lbl_invoice = ctk.CTkLabel(head, text="Fakturanr: –")
    app.lbl_count.grid(row=0, column=0, padx=(4, 12))
    app.lbl_status.grid(row=0, column=1, padx=8)
    app.lbl_invoice.grid(row=0, column=2, padx=8)
    ctk.CTkButton(head, text="📋 Kopier fakturanr", command=app.copy_invoice).grid(row=0, column=3, padx=(8,0))
    app.copy_feedback = ctk.CTkLabel(head, text="", text_color="#2ecc71")
    app.copy_feedback.grid(row=0, column=4, padx=8, sticky="w")

    app.inline_status = ctk.CTkLabel(head, text="", text_color="#2ecc71")
    app.inline_status.grid(row=0, column=5, padx=8, sticky="e")

    btns = ctk.CTkFrame(panel)
    btns.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 4))
    btns.grid_columnconfigure((0,1,2,3,4), weight=1)

    ctk.CTkButton(btns, text="✅ Godkjent", fg_color="#2ecc71", hover_color="#29b765",
                  command=lambda: app.set_decision_and_next("Godkjent")).grid(row=0, column=0, padx=6, pady=6, sticky="ew")
    ctk.CTkButton(btns, text="⛔ Ikke godkjent", fg_color="#e74c3c", hover_color="#cf4334",
                  command=lambda: app.set_decision_and_next("Ikke godkjent")).grid(row=0, column=1, padx=6, pady=6, sticky="ew")
    ctk.CTkButton(btns, text="🔗 Åpne i PowerOffice", command=app.open_in_po).grid(row=0, column=2, padx=6, pady=6, sticky="ew")
    app.btn_prev = ctk.CTkButton(btns, text="⬅ Forrige", command=app.prev)
    app.btn_prev.grid(row=0, column=3, padx=6, pady=6, sticky="ew")
    app.btn_next = ctk.CTkButton(btns, text="➡ Neste", command=app.next)
    app.btn_next.grid(row=0, column=4, padx=6, pady=6, sticky="ew")

    paned = tk.PanedWindow(panel, orient="horizontal")
    paned.grid(row=2, column=0, sticky="nsew", padx=12, pady=(4, 6))
    left = ctk.CTkFrame(paned)
    right = ctk.CTkFrame(paned)
    paned.add(left,  minsize=420)
    paned.add(right, minsize=420)
    paned.paneconfigure(left, stretch="always")
    paned.paneconfigure(right, stretch="always")

    ctk.CTkLabel(left, text="Detaljer for bilag", font=ctk.CTkFont(size=15, weight="bold"))\
        .grid(row=0, column=0, sticky="w", padx=8, pady=(4,4))
    left.grid_columnconfigure(0, weight=1)
    left.grid_rowconfigure(1, weight=1, minsize=120)
    app.detail_box = ctk.CTkTextbox(left, height=360, font=ctk.CTkFont(size=14))
    app.detail_box.grid(row=1, column=0, sticky="nsew", padx=(8,6), pady=(0,8))

    ctk.CTkLabel(right, text="Hovedbok (bilagslinjer)", font=ctk.CTkFont(size=15, weight="bold"))\
        .grid(row=0, column=0, sticky="w", padx=8, pady=(4,4))
    right.grid_columnconfigure(0, weight=1)
    right.grid_columnconfigure(1, weight=0)
    right.grid_rowconfigure(1, weight=3, minsize=150)
    right.grid_rowconfigure(5, weight=1, minsize=80)

    app.ledger_cols = LEDGER_COLS
    app.ledger_tree = ttk.Treeview(right, columns=LEDGER_COLS, show="headings", height=10, style="Custom.Treeview")
    for col, w, anchor in [
        ("Kontonr", 90, "w"), ("Konto", 180, "w"),
        ("Beskrivelse", 260, "w"), ("MVA", 70, "w"),
        ("MVA-beløp", 110, "e"), ("Beløp", 110, "e"),
        ("Postert av", 140, "w")
    ]:
        app.ledger_tree.heading(col, text=col)
        app.ledger_tree.column(col, width=w, minwidth=60, anchor=anchor, stretch=True)

    yscroll = ctk.CTkScrollbar(right, orientation="vertical", command=app.ledger_tree.yview)
    xscroll = ctk.CTkScrollbar(right, orientation="horizontal", command=app.ledger_tree.xview)
    app.ledger_tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
    app.ledger_tree.grid(row=1, column=0, sticky="nsew")
    yscroll.grid(row=1, column=1, sticky="ns")
    xscroll.grid(row=2, column=0, sticky="ew")

    apply_treeview_theme(app)
    update_treeview_stripes(app)
    # Farger for radene basert på beslutning
    app.ledger_tree.tag_configure("approved", foreground="#2ecc71")
    app.ledger_tree.tag_configure("rejected", foreground="#e74c3c")

    app.ledger_sum = ctk.CTkLabel(right, text=" ", anchor="e", justify="right")
    app.ledger_sum.grid(row=3, column=0, columnspan=2, sticky="ew", padx=(0, 12), pady=(6, 10))

    ctk.CTkLabel(right, text="Kommentar", font=ctk.CTkFont(size=15, weight="bold"))\
        .grid(row=4, column=0, columnspan=2, sticky="w", padx=0, pady=(8,4))
    app.comment_box = ctk.CTkTextbox(right, height=110, font=ctk.CTkFont(size=13))
    app.comment_box.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=0, pady=(0,0))

    bottom = ctk.CTkFrame(panel)
    bottom.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 0))
    app.bottom_frame = bottom

    def _export_pdf():
        from report import export_pdf
        export_pdf(app)

    ctk.CTkButton(bottom, text="📄 Eksporter PDF rapport", command=_export_pdf).pack(side="left")
    ctk.CTkLabel(bottom, text="").pack(side="left", expand=True, fill="x")
    return panel


def update_decision_colors(app):
    """Oppdater radfarger i hovedboktabellen etter beslutning."""
    decision = None
    if getattr(app, "decisions", None) and app.idx < len(app.decisions):
        decision = app.decisions[app.idx]
    tag = None
    if decision == "Godkjent":
        tag = "approved"
    elif decision == "Ikke godkjent":
        tag = "rejected"
    for item in app.ledger_tree.get_children():
        tags = [t for t in app.ledger_tree.item(item, "tags") if t not in ("approved", "rejected")]
        if tag:
            tags.append(tag)
        app.ledger_tree.item(item, tags=tags)
