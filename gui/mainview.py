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
        fg_color=style.get_color_pair("card_bg"),
        border_width=style.CARD_BORDER_WIDTH,
        border_color=style.get_color_pair("card_border"),
    )
    head.grid(
        row=0,
        column=0,
        sticky="ew",
        padx=style.PAD_LG,
        pady=(style.PAD_LG, style.PAD_SM),
    )
    head.grid_columnconfigure(0, weight=1)
    head.grid_columnconfigure(1, weight=0)

    content = ctk.CTkFrame(head, fg_color="transparent")
    content.grid(row=0, column=0, columnspan=2, sticky="nsew")
    content.grid_columnconfigure(0, weight=1)
    content.grid_columnconfigure(1, weight=0)

    info = ctk.CTkFrame(content, fg_color="transparent")
    info.grid(row=0, column=0, sticky="nsew", padx=style.PAD_LG, pady=style.PAD_LG)
    info.grid_columnconfigure(1, weight=1)

    app.lbl_count = ctk.CTkLabel(
        info,
        text="Bilag: –/–",
        font=style.FONT_TITLE_LARGE,
        text_color=style.get_color("accent"),
    )
    app.lbl_count.grid(row=0, column=0, sticky="w")

    status_chip = ctk.CTkFrame(
        info,
        fg_color=style.get_color_pair("pill_bg"),
        border_color=style.get_color_pair("pill_border"),
        border_width=style.CARD_BORDER_WIDTH,
        corner_radius=999,
    )
    status_chip.grid(row=0, column=1, sticky="w", padx=(style.PAD_MD, 0))

    app.lbl_status_label = ctk.CTkLabel(
        status_chip,
        text="Status",
        font=style.FONT_SMALL,
        text_color=style.get_color("muted"),
    )
    app.lbl_status_label.pack(side="left", padx=(style.PAD_MD, style.PAD_XXS), pady=style.PAD_XS)
    app.lbl_status = ctk.CTkLabel(
        status_chip,
        text="–",
        font=style.FONT_BODY_BOLD,
        text_color=style.get_color("pill_text"),
    )
    app.lbl_status.pack(side="left", padx=(0, style.PAD_MD), pady=style.PAD_XS)

    app.lbl_invoice = ctk.CTkLabel(
        info,
        text="Fakturanr: –",
        font=style.FONT_TITLE_LITE,
        text_color=style.get_color("fg"),
    )
    app.lbl_invoice.grid(row=1, column=0, columnspan=2, sticky="w", pady=(style.PAD_XXS, 0))

    actions_row = ctk.CTkFrame(info, fg_color="transparent")
    actions_row.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(style.PAD_SM, 0))
    actions_row.grid_columnconfigure(1, weight=1)
    actions_row.grid_columnconfigure(2, weight=0)

    create_button(
        actions_row,
        text="📋 Kopier fakturanr",
        command=app.copy_invoice,
    ).grid(row=0, column=0, padx=(0, style.PAD_MD))

    app.copy_feedback = ctk.CTkLabel(
        actions_row,
        text="",
        text_color=style.get_color("success"),
        font=style.FONT_SMALL,
        anchor="w",
    )
    app.copy_feedback.grid(row=0, column=1, sticky="w")

    app.inline_status = ctk.CTkLabel(
        actions_row,
        text="",
        text_color=style.get_color("accent"),
        font=style.FONT_SMALL,
        anchor="e",
    )
    app.inline_status.grid(row=0, column=2, sticky="e")

    controls = ctk.CTkFrame(content, fg_color="transparent")
    controls.grid(row=0, column=1, sticky="ne", padx=(0, style.PAD_LG), pady=style.PAD_LG)

    ctk.CTkLabel(
        controls,
        text="Temavalg",
        font=style.FONT_SMALL,
        text_color=style.get_color("muted"),
    ).grid(row=0, column=0, sticky="e", pady=(0, style.PAD_XXS))
    default_theme_label = DEFAULT_APPEARANCE_MODE.title()
    app.theme_var = ctk.StringVar(value=default_theme_label)
    app.theme_menu = ctk.CTkOptionMenu(
        controls,
        variable=app.theme_var,
        values=["Light", "Dark"],
        command=app._switch_theme,
        anchor="center",
    )
    app.theme_menu.grid(row=1, column=0, sticky="e")
    app.theme_menu.set(default_theme_label)

    return head


def build_action_buttons(app):
    """Opprett handling- og navigasjonsknapper."""

    import customtkinter as ctk

    panel = app.main_panel
    btns = ctk.CTkFrame(
        panel,
        corner_radius=style.CARD_RADIUS,
        fg_color=style.get_color_pair("card_bg"),
        border_width=style.CARD_BORDER_WIDTH,
        border_color=style.get_color_pair("card_border"),
    )
    btns.grid(
        row=1,
        column=0,
        sticky="ew",
        padx=style.PAD_LG,
        pady=(0, style.PAD_SM),
    )
    btns.grid_columnconfigure(0, weight=1)

    header = ctk.CTkLabel(
        btns,
        text="Behandling av bilag",
        font=style.FONT_TITLE_SMALL,
        text_color=style.get_color("muted"),
        anchor="w",
    )
    header.grid(row=0, column=0, sticky="ew", padx=style.PAD_LG, pady=(style.PAD_LG, style.PAD_XS))

    row = ctk.CTkFrame(btns, fg_color="transparent")
    row.grid(row=1, column=0, sticky="ew", padx=style.PAD_LG, pady=(0, style.PAD_LG))
    row.grid_columnconfigure((0, 1, 2, 3, 4), weight=1, uniform="actions")

    create_button(
        row,
        text="✅ Godkjent",
        fg_color=style.get_color_pair("success"),
        hover_color=style.get_color_pair("success_hover"),
        command=lambda: app.set_decision_and_next("Godkjent"),
    ).grid(row=0, column=0, padx=style.PAD_SM, sticky="ew")

    create_button(
        row,
        text="⛔ Ikke godkjent",
        fg_color=style.get_color_pair("error"),
        hover_color=style.get_color_pair("error_hover"),
        command=lambda: app.set_decision_and_next("Ikke godkjent"),
    ).grid(row=0, column=1, padx=style.PAD_SM, sticky="ew")

    create_button(
        row,
        text="🔗 Åpne PowerOffice",
        command=app.open_in_po,
    ).grid(row=0, column=2, padx=style.PAD_SM, sticky="ew")

    app.btn_prev = create_button(row, text="⬅ Forrige", command=app.prev)
    app.btn_prev.grid(row=0, column=3, padx=style.PAD_SM, sticky="ew")

    app.btn_next = create_button(row, text="➡ Neste", command=app.next)
    app.btn_next.grid(row=0, column=4, padx=style.PAD_SM, sticky="ew")

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
        pady=(style.PAD_SM, style.PAD_SM),
    )
    paned.grid_columnconfigure((0, 1), weight=1, minsize=400)
    paned.grid_rowconfigure(0, weight=1)

    left = ctk.CTkFrame(paned, fg_color="transparent")
    right = ctk.CTkFrame(paned, fg_color="transparent")
    left.grid(row=0, column=0, sticky="nsew")
    right.grid(row=0, column=1, sticky="nsew")
    app.right_frame = right

    ctk.CTkLabel(
        left,
        text="Detaljer for bilag",
        font=style.FONT_TITLE_SMALL,
        text_color=style.get_color("muted"),
    ).grid(row=0, column=0, sticky="w", padx=style.PAD_MD, pady=(0, style.PAD_XS))
    left.grid_columnconfigure(0, weight=1)
    left.grid_rowconfigure(1, weight=1, minsize=120)

    detail_card = ctk.CTkFrame(
        left,
        corner_radius=style.CARD_RADIUS,
        fg_color=style.get_color_pair("card_inner"),
        border_width=style.CARD_BORDER_WIDTH,
        border_color=style.get_color_pair("card_border"),
    )
    detail_card.grid(
        row=1,
        column=0,
        sticky="nsew",
        padx=(style.PAD_MD, style.PAD_SM),
        pady=(0, style.PAD_MD),
    )
    detail_card.grid_rowconfigure(0, weight=1)
    detail_card.grid_columnconfigure(0, weight=1)

    app.detail_box = ctk.CTkTextbox(
        detail_card,
        height=360,
        font=style.FONT_BODY,
        fg_color=style.get_color_pair("card_inner"),
        border_width=0,
    )
    app.detail_box.grid(
        row=0,
        column=0,
        sticky="nsew",
        padx=style.PAD_MD,
        pady=style.PAD_MD,
    )

    ctk.CTkLabel(
        right,
        text="Hovedbok (bilagslinjer)",
        font=style.FONT_TITLE_SMALL,
        text_color=style.get_color("muted"),
    ).grid(row=0, column=0, sticky="w", padx=style.PAD_MD, pady=(0, style.PAD_XS))
    right.grid_columnconfigure(0, weight=1)
    right.grid_rowconfigure(1, weight=3, minsize=150)
    right.grid_rowconfigure(3, weight=1, minsize=120)

    ledger_card = ctk.CTkFrame(
        right,
        corner_radius=style.CARD_RADIUS,
        fg_color=style.get_color_pair("card_inner"),
        border_width=style.CARD_BORDER_WIDTH,
        border_color=style.get_color_pair("card_border"),
    )
    ledger_card.grid(
        row=1,
        column=0,
        sticky="nsew",
        padx=(style.PAD_MD, style.PAD_SM),
        pady=(0, style.PAD_MD),
    )
    ledger_card.grid_columnconfigure(0, weight=1)
    ledger_card.grid_columnconfigure(1, weight=0)
    ledger_card.grid_rowconfigure(0, weight=1)
    ledger_card.grid_rowconfigure(1, weight=0)
    ledger_card.grid_rowconfigure(2, weight=0)
    app.ledger_container = ledger_card

    ctk.CTkLabel(
        right,
        text="Kommentar",
        font=style.FONT_TITLE_SMALL,
        text_color=style.get_color("muted"),
    ).grid(
        row=2,
        column=0,
        sticky="w",
        padx=(style.PAD_MD, style.PAD_SM),
        pady=(0, style.PAD_XS),
    )

    comment_card = ctk.CTkFrame(
        right,
        corner_radius=style.CARD_RADIUS,
        fg_color=style.get_color_pair("card_inner"),
        border_width=style.CARD_BORDER_WIDTH,
        border_color=style.get_color_pair("card_border"),
    )
    comment_card.grid(
        row=3,
        column=0,
        sticky="nsew",
        padx=(style.PAD_MD, style.PAD_SM),
        pady=(0, style.PAD_SM),
    )
    comment_card.grid_rowconfigure(0, weight=1)
    comment_card.grid_columnconfigure(0, weight=1)

    app.comment_box = ctk.CTkTextbox(
        comment_card,
        font=style.FONT_SMALL,
        fg_color=style.get_color_pair("card_inner"),
        border_width=0,
    )
    app.comment_box.grid(
        row=0,
        column=0,
        sticky="nsew",
        padx=style.PAD_MD,
        pady=style.PAD_MD,
    )

    return paned


def build_bottom(app):
    """Lag bunnseksjonen med eksportknapp og statusvisning."""

    import customtkinter as ctk

    panel = app.main_panel
    bottom = ctk.CTkFrame(
        panel,
        corner_radius=style.CARD_RADIUS,
        fg_color=style.get_color_pair("card_bg"),
        border_width=style.CARD_BORDER_WIDTH,
        border_color=style.get_color_pair("card_border"),
    )
    bottom.grid(
        row=3,
        column=0,
        sticky="ew",
        padx=style.PAD_LG,
        pady=(0, style.PAD_LG),
    )
    bottom.grid_columnconfigure(0, weight=0)
    bottom.grid_columnconfigure(1, weight=1)
    bottom.grid_columnconfigure(2, weight=0)
    app.bottom_frame = bottom

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

    content = ctk.CTkFrame(bottom, fg_color="transparent")
    content.grid(row=0, column=0, columnspan=3, sticky="ew", padx=style.PAD_LG, pady=style.PAD_LG)
    content.grid_columnconfigure(1, weight=1)

    export_btn = create_button(
        content,
        text="📄 Eksporter PDF rapport",
        command=_export_pdf,
    )
    export_btn.grid(row=0, column=0, padx=(0, style.PAD_MD))

    app.status_label = ctk.CTkLabel(
        content,
        text="",
        font=style.FONT_BODY,
        text_color=style.get_color("muted"),
        anchor="w",
    )
    app.status_label.grid(row=0, column=1, sticky="ew")

    app.progress_bar = ctk.CTkProgressBar(
        content,
        width=180,
        progress_color=style.get_color("success"),
        fg_color=style.get_color("bg"),
    )
    app.progress_bar.set(0)
    app.progress_bar_grid = {
        "row": 0,
        "column": 2,
        "padx": (style.PAD_MD, 0),
        "pady": (0, 0),
        "sticky": "e",
    }

    return bottom


def build_main(app):
    """Sett sammen hovedpanelet av alle delkomponenter."""

    import customtkinter as ctk

    panel = ctk.CTkFrame(
        app,
        corner_radius=style.CARD_RADIUS,
        fg_color=style.get_color_pair("card_bg"),
        border_width=style.CARD_BORDER_WIDTH,
        border_color=style.get_color_pair("card_border"),
    )
    panel.grid(
        row=0,
        column=1,
        sticky="nsew",
        padx=(0, style.PAD_XL),
        pady=style.PAD_XL,
    )
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

    container = getattr(app, "ledger_container", app.right_frame)
    container.grid_columnconfigure(0, weight=1)
    container.grid_columnconfigure(1, weight=0)
    container.grid_rowconfigure(0, weight=1)
    container.grid_rowconfigure(1, weight=0)
    container.grid_rowconfigure(2, weight=0)
    app.ledger_cols = LEDGER_COLS
    app.ledger_tree = ttk.Treeview(
        container,
        columns=LEDGER_COLS,
        show="headings",
        height=10,
        style="Custom.Treeview",
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

    yscroll = ctk.CTkScrollbar(container, orientation="vertical", command=app.ledger_tree.yview)
    xscroll = ctk.CTkScrollbar(container, orientation="horizontal", command=app.ledger_tree.xview)
    app.ledger_tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
    app.ledger_tree.grid(row=0, column=0, sticky="nsew", padx=(style.PAD_MD, 0), pady=(style.PAD_MD, 0))
    yscroll.grid(row=0, column=1, sticky="ns", pady=(style.PAD_MD, style.PAD_MD))
    xscroll.grid(row=1, column=0, sticky="ew", padx=(style.PAD_MD, 0))

    app._prev_ledger_width = None
    app._ledger_configure_id = app.ledger_tree.bind(
        "<Configure>", lambda e: resize_ledger_columns(app)
    )

    apply_treeview_theme(app)
    update_treeview_stripes(app)

    if app.ledger_tree.get_children():
        sort_treeview(app.ledger_tree, app.ledger_cols[0], False, app)

    app.ledger_sum = ctk.CTkLabel(
        container,
        text=" ",
        anchor="e",
        justify="right",
        font=style.FONT_BODY,
        text_color=style.get_color("muted"),
    )
    app.ledger_sum.grid(
        row=2,
        column=0,
        columnspan=2,
        sticky="ew",
        padx=(style.PAD_MD, style.PAD_MD),
        pady=(style.PAD_SM, PADDING_Y),
    )
