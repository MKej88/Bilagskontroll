from . import DEFAULT_APPEARANCE_MODE, create_button
from .style import style
from .style import PADDING_Y


def build_header(app):
    """Bygg overskrift med status, fakturanr og temavalg."""

    import customtkinter as ctk

    panel = app.main_panel
    head = ctk.CTkFrame(
        panel,
        corner_radius=style.CARD_RADIUS,
        fg_color=style.get_color("card_bg"),
        border_width=1,
        border_color=style.get_color("card_border"),
    )
    head.grid(
        row=0,
        column=0,
        sticky="ew",
        padx=style.PAD_LG,
        pady=(style.PAD_LG, style.PAD_SM),
    )
    head.grid_columnconfigure(0, weight=1)

    accent = ctk.CTkFrame(head, height=6, fg_color=style.get_color("accent"))
    accent.grid(row=0, column=0, sticky="ew")
    accent.grid_propagate(False)

    content = ctk.CTkFrame(head, fg_color="transparent")
    content.grid(row=1, column=0, sticky="ew", padx=style.PAD_XL, pady=style.PAD_MD)
    content.grid_columnconfigure(5, weight=1)

    head_font = style.FONT_TITLE_LITE

    app.lbl_count = ctk.CTkLabel(content, text="Bilag: –/–", font=style.FONT_TITLE)
    status_frame = ctk.CTkFrame(content, fg_color="transparent")
    status_frame.grid(row=0, column=1, padx=(style.PAD_SM, style.PAD_LG), sticky="w")
    app.lbl_status_label = ctk.CTkLabel(status_frame, text="Status:", font=head_font)
    app.lbl_status_label.grid(row=0, column=0, padx=(0, style.PAD_XXS))
    app.lbl_status = ctk.CTkLabel(
        status_frame,
        text="–",
        font=head_font,
        text_color=style.get_color("fg"),
    )
    app.lbl_status.grid(row=0, column=1)
    app.lbl_invoice = ctk.CTkLabel(content, text="Fakturanr: –", font=head_font)
    app.lbl_count.grid(row=0, column=0, padx=(0, style.PAD_SM))
    app.lbl_invoice.grid(row=0, column=2, padx=(0, style.PAD_MD))
    create_button(content, text="📋 Kopier fakturanr", command=app.copy_invoice).grid(
        row=0,
        column=3,
        padx=(style.PAD_MD, style.PAD_SM),
    )
    app.copy_feedback = ctk.CTkLabel(
        content,
        text="",
        text_color=style.get_color("success"),
        font=style.FONT_BODY,
    )
    app.copy_feedback.grid(row=0, column=4, padx=(0, style.PAD_SM), sticky="w")

    app.inline_status = ctk.CTkLabel(
        content,
        text="",
        text_color=style.get_color("success"),
        font=style.FONT_BODY,
    )
    app.inline_status.grid(row=0, column=5, padx=(0, style.PAD_LG), sticky="e")

    ctk.CTkLabel(content, text="Temavalg", font=style.FONT_BODY).grid(
        row=0,
        column=6,
        padx=(0, style.PAD_XS),
    )
    default_theme_label = DEFAULT_APPEARANCE_MODE.title()
    app.theme_var = ctk.StringVar(value=default_theme_label)
    app.theme_menu = ctk.CTkOptionMenu(
        content,
        variable=app.theme_var,
        values=["Light", "Dark"],
        command=app._switch_theme,
    )
    app.theme_menu.grid(row=0, column=7, padx=(0, style.PAD_XS))
    app.theme_menu.set(default_theme_label)

    return head


def build_action_buttons(app):
    """Opprett handling- og navigasjonsknapper."""

    import customtkinter as ctk

    panel = app.main_panel
    btns = ctk.CTkFrame(
        panel,
        corner_radius=style.CARD_RADIUS,
        fg_color=style.get_color("card_bg"),
        border_width=1,
        border_color=style.get_color("card_border"),
    )
    btns.grid(
        row=1,
        column=0,
        sticky="ew",
        padx=style.PAD_LG,
        pady=(0, style.PAD_MD),
    )
    btns.grid_columnconfigure(0, weight=1)

    toolbar = ctk.CTkFrame(btns, fg_color="transparent")
    toolbar.grid(row=0, column=0, sticky="ew", padx=style.PAD_XL, pady=style.PAD_MD)
    toolbar.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

    create_button(
        toolbar,
        text="✅ Godkjent",
        fg_color=style.get_color("success"),
        hover_color=style.get_color("success_hover"),
        command=lambda: app.set_decision_and_next("Godkjent"),
    ).grid(row=0, column=0, padx=(0, style.PAD_SM), sticky="ew")
    create_button(
        toolbar,
        text="⛔ Ikke godkjent",
        fg_color=style.get_color("error"),
        hover_color=style.get_color("error_hover"),
        command=lambda: app.set_decision_and_next("Ikke godkjent"),
    ).grid(row=0, column=1, padx=style.PAD_SM, sticky="ew")
    create_button(toolbar, text="🔗 Åpne PowerOffice", command=app.open_in_po).grid(
        row=0,
        column=2,
        padx=style.PAD_SM,
        sticky="ew",
    )
    app.btn_prev = create_button(toolbar, text="⬅ Forrige", command=app.prev)
    app.btn_prev.grid(row=0, column=3, padx=style.PAD_SM, sticky="ew")
    app.btn_next = create_button(toolbar, text="➡ Neste", command=app.next)
    app.btn_next.grid(row=0, column=4, padx=(style.PAD_SM, 0), sticky="ew")

    return btns


def build_panes(app):
    """Bygg venstre og høyre panel for detaljer og hovedbok."""

    import customtkinter as ctk

    panel = app.main_panel
    paned = ctk.CTkFrame(panel, fg_color="transparent")
    paned.grid(
        row=2,
        column=0,
        sticky="nsew",
        padx=style.PAD_LG,
        pady=(0, style.PAD_MD),
    )
    paned.grid_columnconfigure((0, 1), weight=1, minsize=400)
    paned.grid_rowconfigure(0, weight=1)

    left_card = ctk.CTkFrame(
        paned,
        corner_radius=style.CARD_RADIUS,
        fg_color=style.get_color("card_bg"),
        border_width=1,
        border_color=style.get_color("card_border"),
    )
    left_card.grid(row=0, column=0, sticky="nsew", padx=(0, style.PAD_SM))
    left_card.grid_rowconfigure(1, weight=1)

    left_accent = ctk.CTkFrame(left_card, height=6, fg_color=style.get_color("accent"))
    left_accent.grid(row=0, column=0, sticky="ew")
    left_accent.grid_propagate(False)

    left = ctk.CTkFrame(left_card, fg_color="transparent")
    left.grid(row=1, column=0, sticky="nsew", padx=style.PAD_LG, pady=style.PAD_MD)
    left.grid_columnconfigure(0, weight=1)
    left.grid_rowconfigure(1, weight=1, minsize=120)

    ctk.CTkLabel(left, text="Detaljer for bilag", font=style.FONT_TITLE_SMALL).grid(
        row=0,
        column=0,
        sticky="w",
        pady=(0, style.PAD_SM),
    )
    app.detail_box = ctk.CTkTextbox(
        left,
        height=360,
        font=style.FONT_BODY,
        fg_color=style.get_color("bg"),
        text_color=style.get_color("fg"),
        border_width=0,
    )
    app.detail_box.grid(
        row=1,
        column=0,
        sticky="nsew",
        pady=(0, style.PAD_MD),
    )

    right_card = ctk.CTkFrame(
        paned,
        corner_radius=style.CARD_RADIUS,
        fg_color=style.get_color("card_bg"),
        border_width=1,
        border_color=style.get_color("card_border"),
    )
    right_card.grid(row=0, column=1, sticky="nsew", padx=(style.PAD_SM, 0))
    right_card.grid_rowconfigure(1, weight=1)

    right_accent = ctk.CTkFrame(right_card, height=6, fg_color=style.get_color("accent"))
    right_accent.grid(row=0, column=0, sticky="ew")
    right_accent.grid_propagate(False)

    right = ctk.CTkFrame(right_card, fg_color="transparent")
    right.grid(row=1, column=0, sticky="nsew", padx=style.PAD_LG, pady=style.PAD_MD)
    right.grid_columnconfigure(0, weight=1)
    right.grid_columnconfigure(1, weight=0)
    right.grid_rowconfigure(1, weight=3, minsize=150)
    right.grid_rowconfigure(5, weight=1, minsize=120)
    app.right_frame = right

    ctk.CTkLabel(right, text="Hovedbok (bilagslinjer)", font=style.FONT_TITLE_SMALL).grid(
        row=0,
        column=0,
        sticky="w",
        pady=(0, style.PAD_SM),
    )

    ctk.CTkLabel(right, text="Kommentar", font=style.FONT_TITLE_SMALL).grid(
        row=4,
        column=0,
        columnspan=2,
        sticky="w",
        pady=(style.PAD_MD, style.PAD_XS),
    )
    app.comment_box = ctk.CTkTextbox(
        right,
        font=style.FONT_SMALL,
        fg_color=style.get_color("bg"),
        text_color=style.get_color("fg"),
        border_width=0,
    )
    app.comment_box.grid(
        row=5,
        column=0,
        columnspan=2,
        sticky="nsew",
        pady=(0, style.PAD_MD),
    )

    return paned


def build_bottom(app):
    """Lag bunnseksjonen med eksportknapp og statusvisning."""

    import customtkinter as ctk

    panel = app.main_panel
    bottom = ctk.CTkFrame(
        panel,
        corner_radius=style.CARD_RADIUS,
        fg_color=style.get_color("card_bg"),
        border_width=1,
        border_color=style.get_color("card_border"),
    )
    bottom.grid(
        row=3,
        column=0,
        sticky="ew",
        padx=style.PAD_LG,
        pady=(0, style.PAD_LG),
    )
    bottom.grid_columnconfigure(0, weight=1)

    bottom_inner = ctk.CTkFrame(bottom, fg_color="transparent")
    bottom_inner.grid(row=0, column=0, sticky="ew", padx=style.PAD_XL, pady=style.PAD_MD)
    bottom_inner.grid_columnconfigure(1, weight=1)
    bottom_inner.grid_columnconfigure(2, weight=0)
    app.bottom_frame = bottom_inner

    def _export_pdf():
        from report import export_pdf
        from .busy import show_busy, hide_busy, run_in_thread

        show_busy(app, "Eksporterer rapport...")

        def finalize():
            app._finish_progress()
            hide_busy(app)

        def worker():
            app.after(0, lambda: app._start_progress("Eksporterer rapport..."))
            try:
                export_pdf(app)
            finally:
                app.after(0, finalize)

        run_in_thread(worker)

    export_btn = create_button(
        bottom_inner, text="📄 Eksporter PDF rapport", command=_export_pdf
    )
    export_btn.grid(
        row=0,
        column=0,
        padx=(0, style.PAD_SM),
        sticky="w",
    )

    app.status_label = ctk.CTkLabel(bottom_inner, text="", font=style.FONT_BODY)
    app.status_label.grid(
        row=0,
        column=1,
        padx=style.PAD_SM,
        sticky="ew",
    )

    app.progress_bar = ctk.CTkProgressBar(
        bottom_inner,
        width=160,
        progress_color=style.get_color("success"),
        fg_color=style.get_color("bg"),
    )
    app.progress_bar.set(0)
    app.progress_bar_grid = {
        "row": 0,
        "column": 2,
        "padx": (style.PAD_SM, 0),
        "pady": 0,
        "sticky": "e",
    }

    return bottom


def build_main(app):
    """Sett sammen hovedpanelet av alle delkomponenter."""

    import customtkinter as ctk

    panel = ctk.CTkFrame(app, corner_radius=16)
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
    """Tilpass kolonner i hovedboktabellen ved endring av bredde."""

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
    """Bygg trevisning for hovedbok med rullefelt og summering."""

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

    app.ledger_sum = ctk.CTkLabel(
        right,
        text=" ",
        anchor="e",
        justify="right",
        font=style.FONT_BODY,
    )
    app.ledger_sum.grid(
        row=3,
        column=0,
        columnspan=2,
        sticky="ew",
        padx=(0, style.PAD_LG),
        pady=(style.PAD_SM, PADDING_Y),
    )
