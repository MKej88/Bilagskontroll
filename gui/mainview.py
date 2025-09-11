from . import create_button
from .style import style, PADDING_Y
from .card import Card


def build_header(app):
    import customtkinter as ctk

    panel = app.main_panel
    head = ctk.CTkFrame(panel)
    head.grid(row=0, column=0, sticky="ew", padx=style.PAD_LG, pady=style.PAD_MD)
    head.grid_columnconfigure(6, weight=1)

    head_font = style.FONT_TITLE_LITE

    app.lbl_count = ctk.CTkLabel(head, text="Bilag: –/–", font=style.FONT_TITLE)
    app.lbl_status = ctk.CTkLabel(head, text="Status: –", font=head_font)
    app.lbl_invoice = ctk.CTkLabel(head, text="Fakturanr: –", font=head_font)
    app.lbl_count.grid(row=0, column=0, padx=(style.PAD_XS, style.PAD_LG))
    app.lbl_status.grid(row=0, column=1, padx=style.PAD_MD)
    app.lbl_invoice.grid(row=0, column=2, padx=style.PAD_MD)
    create_button(head, text="📋 Kopier fakturanr", command=app.copy_invoice).grid(row=0, column=3, padx=(style.PAD_MD,0))
    app.copy_feedback = ctk.CTkLabel(head, text="", text_color=style.get_color("success"))
    app.copy_feedback.grid(row=0, column=4, padx=style.PAD_MD, sticky="w")

    app.inline_status = ctk.CTkLabel(head, text="", text_color=style.get_color("success"))
    app.inline_status.grid(row=0, column=5, padx=style.PAD_MD, sticky="e")

    ctk.CTkLabel(head, text="Temavalg").grid(row=0, column=7, padx=(style.PAD_MD, style.PAD_XS))
    app.theme_var = ctk.StringVar(value="System")
    app.theme_menu = ctk.CTkOptionMenu(
        head,
        variable=app.theme_var,
        values=["System", "Light", "Dark"],
        command=app._switch_theme,
    )
    app.theme_menu.grid(row=0, column=8, padx=(0, style.PAD_MD))
    app.theme_menu.set("System")

    return head


def build_action_buttons(app):
    import customtkinter as ctk

    panel = app.main_panel
    btns = ctk.CTkFrame(panel)
    btns.grid(row=1, column=0, sticky="ew", padx=style.PAD_LG, pady=(0, style.PAD_XS))
    btns.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

    create_button(
        btns,
        text="✅ Godkjent",
        fg_color=style.get_color("success"),
        hover_color=style.get_color("success_hover"),
        command=lambda: app.set_decision_and_next("Godkjent"),
    ).grid(row=0, column=0, padx=style.PAD_SM, pady=style.PAD_SM, sticky="ew")
    create_button(
        btns,
        text="⛔ Ikke godkjent",
        fg_color=style.get_color("error"),
        hover_color=style.get_color("error_hover"),
        command=lambda: app.set_decision_and_next("Ikke godkjent"),
    ).grid(row=0, column=1, padx=style.PAD_SM, pady=style.PAD_SM, sticky="ew")
    create_button(btns, text="🔗 Åpne PowerOffice", command=app.open_in_po).grid(row=0, column=2, padx=style.PAD_SM, pady=style.PAD_SM, sticky="ew")
    app.btn_prev = create_button(btns, text="⬅ Forrige", command=app.prev)
    app.btn_prev.grid(row=0, column=3, padx=style.PAD_SM, pady=style.PAD_SM, sticky="ew")
    app.btn_next = create_button(btns, text="➡ Neste", command=app.next)
    app.btn_next.grid(row=0, column=4, padx=style.PAD_SM, pady=style.PAD_SM, sticky="ew")

    return btns


def build_panes(app):
    import customtkinter as ctk

    panel = app.main_panel
    paned = ctk.CTkFrame(panel)
    paned.grid(row=2, column=0, sticky="nsew", padx=style.PAD_LG, pady=(style.PAD_XS, style.PAD_SM))
    paned.grid_columnconfigure((0, 1), weight=1, minsize=400)
    paned.grid_rowconfigure(0, weight=1)

    left = ctk.CTkFrame(paned)
    right = ctk.CTkFrame(paned)
    left.grid(row=0, column=0, sticky="nsew")
    right.grid(row=0, column=1, sticky="nsew")
    app.right_frame = right

    ctk.CTkLabel(left, text="Detaljer for bilag", font=style.FONT_TITLE_SMALL)\
        .grid(row=0, column=0, sticky="w", padx=style.PAD_MD, pady=(style.PAD_XS, style.PAD_XS))
    left.grid_columnconfigure(0, weight=1)
    left.grid_rowconfigure(1, weight=1, minsize=120)
    app.detail_box = ctk.CTkTextbox(left, height=360, font=style.FONT_BODY)
    app.detail_box.grid(row=1, column=0, sticky="nsew", padx=(style.PAD_MD, style.PAD_SM), pady=(0, style.PAD_MD))

    ctk.CTkLabel(right, text="Hovedbok (bilagslinjer)", font=style.FONT_TITLE_SMALL)\
        .grid(row=0, column=0, sticky="w", padx=style.PAD_MD, pady=(style.PAD_XS, style.PAD_XS))
    right.grid_columnconfigure(0, weight=1)
    right.grid_columnconfigure(1, weight=0)
    right.grid_rowconfigure(1, weight=3, minsize=150)
    right.grid_rowconfigure(5, weight=1, minsize=120)

    ctk.CTkLabel(right, text="Kommentar", font=style.FONT_TITLE_SMALL)\
        .grid(row=4, column=0, columnspan=2, sticky="w", padx=(style.PAD_MD, style.PAD_SM), pady=(style.PAD_MD, style.PAD_XS))
    app.comment_box = ctk.CTkTextbox(right, font=style.FONT_SMALL)
    app.comment_box.grid(
        row=5,
        column=0,
        columnspan=2,
        sticky="nsew",
        padx=(style.PAD_MD, style.PAD_SM),
        pady=(0, style.PAD_MD),
    )

    return paned


def build_bottom(app):
    import customtkinter as ctk

    panel = app.main_panel
    bottom = ctk.CTkFrame(panel)
    bottom.grid(row=3, column=0, sticky="ew", padx=style.PAD_LG, pady=(0, style.PAD_MD))
    bottom.grid_columnconfigure(1, weight=1)
    app.bottom_frame = bottom

    def _export_pdf():
        from report import export_pdf
        from .busy import show_busy, hide_busy
        show_busy(app, "Eksporterer rapport...")
        try:
            export_pdf(app)
        finally:
            hide_busy(app)

    export_btn = create_button(
        bottom, text="📄 Eksporter PDF rapport", command=_export_pdf
    )
    export_btn.grid(
        row=0,
        column=0,
        padx=(style.PAD_MD, style.PAD_SM),
        pady=style.PAD_SM,
        sticky="w",
    )

    app.status_label = ctk.CTkLabel(bottom, text="")
    app.status_label.grid(
        row=0,
        column=1,
        padx=style.PAD_SM,
        pady=style.PAD_SM,
        sticky="ew",
    )

    app.progress_bar = ctk.CTkProgressBar(
        bottom,
        width=120,
        progress_color=style.get_color("success"),
        fg_color=style.get_color("bg"),
    )
    app.progress_bar.set(0)
    app.progress_bar.grid(
        row=0,
        column=2,
        padx=style.PAD_SM,
        pady=style.PAD_SM,
        sticky="e",
    )
    app.progress_bar.grid_remove()

    return bottom


def build_main(app):
    import customtkinter as ctk

    panel = Card(app)
    panel.grid(row=0, column=1, sticky="nsew", padx=(0, style.PAD_XL), pady=style.PAD_XL)
    panel.grid_columnconfigure(0, weight=1)
    panel.grid_rowconfigure(2, weight=1, minsize=300)

    app.main_panel = panel

    build_header(app)
    build_action_buttons(app)
    build_panes(app)
    build_bottom(app)

    return panel


def resize_ledger_columns(app):
    from . import ledger
    width = app.ledger_tree.winfo_width()
    if getattr(app, "_prev_ledger_width", None) == width:
        return

    app._prev_ledger_width = width
    app.after(
        100,
        lambda: ledger.autofit_tree_columns(
            app.ledger_tree, app.ledger_cols, width
        ),
    )


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

    app._prev_ledger_width = None
    app._ledger_configure_id = app.ledger_tree.bind(
        "<Configure>", lambda e: resize_ledger_columns(app)
    )

    apply_treeview_theme(app)
    update_treeview_stripes(app)

    if app.ledger_tree.get_children():
        sort_treeview(app.ledger_tree, app.ledger_cols[0], False, app)

    app.ledger_sum = ctk.CTkLabel(right, text=" ", anchor="e", justify="right")
    app.ledger_sum.grid(
        row=3,
        column=0,
        columnspan=2,
        sticky="ew",
        padx=(0, style.PAD_LG),
        pady=(style.PAD_SM, PADDING_Y),
    )
