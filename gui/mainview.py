from . import (
    FONT_TITLE,
    FONT_BODY,
    FONT_TITLE_LITE,
    FONT_TITLE_SMALL,
    FONT_SMALL,
    create_button,
    get_color,
)


def build_header(app):
    import customtkinter as ctk

    panel = app.main_panel
    head = ctk.CTkFrame(panel)
    head.grid(row=0, column=0, sticky="ew", padx=12, pady=8)
    head.grid_columnconfigure(6, weight=1)

    head_font = FONT_TITLE_LITE

    app.lbl_count = ctk.CTkLabel(head, text="Bilag: –/–", font=FONT_TITLE)
    app.lbl_status = ctk.CTkLabel(head, text="Status: –", font=head_font)
    app.lbl_invoice = ctk.CTkLabel(head, text="Fakturanr: –", font=head_font)
    app.lbl_count.grid(row=0, column=0, padx=(4, 12))
    app.lbl_status.grid(row=0, column=1, padx=8)
    app.lbl_invoice.grid(row=0, column=2, padx=8)
    create_button(head, text="📋 Kopier fakturanr", command=app.copy_invoice).grid(row=0, column=3, padx=(8,0))
    app.copy_feedback = ctk.CTkLabel(head, text="", text_color=get_color("success"))
    app.copy_feedback.grid(row=0, column=4, padx=8, sticky="w")

    app.inline_status = ctk.CTkLabel(head, text="", text_color=get_color("success"))
    app.inline_status.grid(row=0, column=5, padx=8, sticky="e")

    return head


def build_action_buttons(app):
    import customtkinter as ctk

    panel = app.main_panel
    btns = ctk.CTkFrame(panel)
    btns.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 4))
    btns.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

    create_button(
        btns,
        text="✅ Godkjent",
        fg_color=get_color("success"),
        hover_color=get_color("success_hover"),
        command=lambda: app.set_decision_and_next("Godkjent"),
    ).grid(row=0, column=0, padx=6, pady=6, sticky="ew")
    create_button(
        btns,
        text="⛔ Ikke godkjent",
        fg_color=get_color("error"),
        hover_color=get_color("error_hover"),
        command=lambda: app.set_decision_and_next("Ikke godkjent"),
    ).grid(row=0, column=1, padx=6, pady=6, sticky="ew")
    create_button(btns, text="🔗 Åpne i PowerOffice", command=app.open_in_po).grid(row=0, column=2, padx=6, pady=6, sticky="ew")
    app.btn_prev = create_button(btns, text="⬅ Forrige", command=app.prev)
    app.btn_prev.grid(row=0, column=3, padx=6, pady=6, sticky="ew")
    app.btn_next = create_button(btns, text="➡ Neste", command=app.next)
    app.btn_next.grid(row=0, column=4, padx=6, pady=6, sticky="ew")

    return btns


def build_panes(app):
    import customtkinter as ctk

    panel = app.main_panel
    paned = ctk.CTkFrame(panel)
    paned.grid(row=2, column=0, sticky="nsew", padx=12, pady=(4, 6))
    paned.grid_columnconfigure((0, 1), weight=1, minsize=420)
    paned.grid_rowconfigure(0, weight=1)

    left = ctk.CTkFrame(paned)
    right = ctk.CTkFrame(paned)
    left.grid(row=0, column=0, sticky="nsew")
    right.grid(row=0, column=1, sticky="nsew")
    app.right_frame = right

    ctk.CTkLabel(left, text="Detaljer for bilag", font=FONT_TITLE_SMALL)\
        .grid(row=0, column=0, sticky="w", padx=8, pady=(4, 4))
    left.grid_columnconfigure(0, weight=1)
    left.grid_rowconfigure(1, weight=1, minsize=120)
    app.detail_box = ctk.CTkTextbox(left, height=360, font=FONT_BODY)
    app.detail_box.grid(row=1, column=0, sticky="nsew", padx=(8, 6), pady=(0, 8))

    ctk.CTkLabel(right, text="Hovedbok (bilagslinjer)", font=FONT_TITLE_SMALL)\
        .grid(row=0, column=0, sticky="w", padx=8, pady=(4, 4))
    right.grid_columnconfigure(0, weight=1)
    right.grid_columnconfigure(1, weight=0)
    right.grid_rowconfigure(1, weight=3, minsize=150)
    right.grid_rowconfigure(5, weight=1, minsize=80)

    ctk.CTkLabel(right, text="Kommentar", font=FONT_TITLE_SMALL)\
        .grid(row=4, column=0, columnspan=2, sticky="w", padx=(8, 6), pady=(8, 4))
    app.comment_box = ctk.CTkTextbox(right, height=110, font=FONT_SMALL)
    app.comment_box.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=(8, 6), pady=(0, 0))

    return paned


def build_bottom(app):
    import customtkinter as ctk

    panel = app.main_panel
    bottom = ctk.CTkFrame(panel)
    bottom.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 0))
    app.bottom_frame = bottom

    def _export_pdf():
        from report import export_pdf

        export_pdf(app)

    create_button(bottom, text="📄 Eksporter PDF rapport", command=_export_pdf).pack(side="left")
    ctk.CTkLabel(bottom, text="").pack(side="left", expand=True, fill="x")

    return bottom


def build_main(app):
    import customtkinter as ctk

    panel = ctk.CTkFrame(app, corner_radius=16)
    panel.grid(row=0, column=1, sticky="nsew", padx=(0, 14), pady=14)
    panel.grid_columnconfigure(0, weight=1)
    panel.grid_rowconfigure(2, weight=1, minsize=300)

    app.main_panel = panel

    build_header(app)
    build_action_buttons(app)
    build_panes(app)
    build_bottom(app)

    return panel


def build_ledger_widgets(app):
    from tkinter import ttk
    import customtkinter as ctk
    from .ledger import (
        LEDGER_COLS,
        apply_treeview_theme,
        update_treeview_stripes,
        sort_treeview,
    )

    right = app.right_frame
    app.ledger_cols = LEDGER_COLS
    app.ledger_tree = ttk.Treeview(
        right, columns=LEDGER_COLS, show="headings", height=10, style="Custom.Treeview"
    )
    for col, w, anchor in [
        ("Kontonr", 90, "w"),
        ("Konto", 180, "w"),
        ("Beskrivelse", 260, "w"),
        ("MVA", 70, "w"),
        ("MVA-beløp", 110, "e"),
        ("Beløp", 110, "e"),
        ("Postert av", 140, "w"),
    ]:
        app.ledger_tree.heading(
            col,
            text=col,
            command=lambda c=col: sort_treeview(app.ledger_tree, c, False, app),
        )
        app.ledger_tree.column(col, width=w, minwidth=60, anchor=anchor, stretch=True)

    yscroll = ctk.CTkScrollbar(right, orientation="vertical", command=app.ledger_tree.yview)
    xscroll = ctk.CTkScrollbar(right, orientation="horizontal", command=app.ledger_tree.xview)
    app.ledger_tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
    app.ledger_tree.grid(row=1, column=0, sticky="nsew")
    yscroll.grid(row=1, column=1, sticky="ns")
    xscroll.grid(row=2, column=0, sticky="ew")

    apply_treeview_theme(app)
    update_treeview_stripes(app)

    app.ledger_sum = ctk.CTkLabel(right, text=" ", anchor="e", justify="right")
    app.ledger_sum.grid(row=3, column=0, columnspan=2, sticky="ew", padx=(0, 12), pady=(6, 10))
