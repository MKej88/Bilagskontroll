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
        fg_color=style.get_color("surface_card"),
        border_width=1,
        border_color=style.get_color("surface_border"),
    )
    head.grid(row=0, column=0, sticky="ew", padx=style.PAD_LG, pady=style.PAD_MD)
    head.grid_columnconfigure(1, weight=1)

    accent = ctk.CTkFrame(
        head,
        width=style.PAD_MD,
        fg_color=style.get_color("accent"),
        corner_radius=style.CARD_RADIUS,
    )
    accent.grid(
        row=0,
        column=0,
        rowspan=3,
        sticky="ns",
        padx=(style.PAD_MD, style.PAD_LG),
        pady=style.PAD_LG,
    )
    accent.grid_propagate(False)

    content = ctk.CTkFrame(head, fg_color="transparent")
    content.grid(row=0, column=1, sticky="nsew", pady=(style.PAD_LG, style.PAD_MD))
    content.grid_columnconfigure(0, weight=1)

    title_row = ctk.CTkFrame(content, fg_color="transparent")
    title_row.grid(row=0, column=0, sticky="ew", padx=(0, style.PAD_LG))
    title_row.grid_columnconfigure(1, weight=1)
    ctk.CTkLabel(
        title_row,
        text="Bilagskontroll",
        font=style.FONT_DISPLAY,
    ).grid(row=0, column=0, sticky="w")
    ctk.CTkLabel(
        title_row,
        text="Profesjonell oversikt over bilagskontroll og status.",
        font=style.FONT_SMALL,
        text_color=style.get_color("muted"),
    ).grid(row=1, column=0, sticky="w", pady=(style.PAD_XXS, 0))

    metrics = ctk.CTkFrame(
        content,
        corner_radius=style.BTN_RADIUS,
        fg_color=style.get_color("surface_muted"),
    )
    metrics.grid(
        row=1,
        column=0,
        sticky="ew",
        padx=(0, style.PAD_LG),
        pady=(style.PAD_SM, 0),
    )
    metrics.grid_columnconfigure((0, 1, 2), weight=1)

    def _stat_column(column: int, label: str, attr_name: str, default: str):
        wrapper = ctk.CTkFrame(metrics, fg_color="transparent")
        wrapper.grid(
            row=0,
            column=column,
            sticky="nsew",
            padx=style.PAD_SM,
            pady=style.PAD_SM,
        )
        caption = ctk.CTkLabel(
            wrapper,
            text=label,
            font=style.FONT_SMALL,
            text_color=style.get_color("muted"),
        )
        caption.grid(row=0, column=0, sticky="w")
        value_lbl = ctk.CTkLabel(wrapper, text=default, font=style.FONT_TITLE_LITE)
        value_lbl.grid(row=1, column=0, sticky="w", pady=(style.PAD_XXS, 0))
        setattr(app, attr_name, value_lbl)
        if attr_name == "lbl_status":
            app.lbl_status_label = caption
        return wrapper

    _stat_column(0, "Bilag", "lbl_count", "–/–")
    _stat_column(1, "Fakturanr", "lbl_invoice", "–")
    _stat_column(2, "Status", "lbl_status", "–")

    feedback_row = ctk.CTkFrame(content, fg_color="transparent")
    feedback_row.grid(
        row=2,
        column=0,
        sticky="ew",
        padx=(0, style.PAD_LG),
        pady=(style.PAD_SM, 0),
    )
    feedback_row.grid_columnconfigure(2, weight=1)

    create_button(
        feedback_row,
        text="📋 Kopier fakturanr",
        command=app.copy_invoice,
    ).grid(row=0, column=0, padx=(0, style.PAD_SM))
    app.copy_feedback = ctk.CTkLabel(
        feedback_row,
        text="",
        text_color=style.get_color("success"),
        font=style.FONT_SMALL,
    )
    app.copy_feedback.grid(row=0, column=1, padx=(0, style.PAD_SM), sticky="w")

    app.inline_status = ctk.CTkLabel(
        feedback_row,
        text="",
        text_color=style.get_color("success"),
        font=style.FONT_SMALL,
    )
    app.inline_status.grid(row=0, column=2, sticky="e")

    theme = ctk.CTkFrame(head, fg_color="transparent")
    theme.grid(
        row=0,
        column=2,
        sticky="ne",
        padx=(0, style.PAD_LG),
        pady=(style.PAD_LG, style.PAD_MD),
    )
    ctk.CTkLabel(
        theme,
        text="Tema",
        font=style.FONT_SMALL,
        text_color=style.get_color("muted"),
    ).grid(row=0, column=0, sticky="w", pady=(0, style.PAD_XXS))
    default_theme_label = DEFAULT_APPEARANCE_MODE.title()
    app.theme_var = ctk.StringVar(value=default_theme_label)
    app.theme_menu = ctk.CTkOptionMenu(
        theme,
        variable=app.theme_var,
        values=["Light", "Dark"],
        command=app._switch_theme,
        fg_color=style.get_color("surface_muted"),
        button_color=style.get_color("accent"),
        button_hover_color=style.get_color("accent"),
    )
    app.theme_menu.grid(row=1, column=0, sticky="ew")
    app.theme_menu.set(default_theme_label)

    return head


def build_action_buttons(app):
    """Opprett handling- og navigasjonsknapper."""

    import customtkinter as ctk

    panel = app.main_panel
    card = ctk.CTkFrame(
        panel,
        corner_radius=style.CARD_RADIUS,
        fg_color=style.get_color("surface_card"),
        border_width=1,
        border_color=style.get_color("surface_border"),
    )
    card.grid(row=1, column=0, sticky="ew", padx=style.PAD_LG, pady=(0, style.PAD_XS))
    card.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(card, text="Handlinger", font=style.FONT_TITLE_SMALL).grid(
        row=0,
        column=0,
        sticky="w",
        padx=style.PAD_LG,
        pady=(style.PAD_MD, style.PAD_XS),
    )
    ctk.CTkLabel(
        card,
        text="Velg ønsket handling for neste bilag.",
        font=style.FONT_SMALL,
        text_color=style.get_color("muted"),
    ).grid(row=1, column=0, sticky="w", padx=style.PAD_LG, pady=(0, style.PAD_SM))

    btns = ctk.CTkFrame(card, fg_color="transparent")
    btns.grid(row=2, column=0, sticky="ew", padx=style.PAD_LG, pady=(0, style.PAD_SM))
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
    create_button(
        btns,
        text="🔗 Åpne PowerOffice",
        command=app.open_in_po,
    ).grid(row=0, column=2, padx=style.PAD_SM, pady=style.PAD_SM, sticky="ew")
    app.btn_prev = create_button(btns, text="⬅ Forrige", command=app.prev)
    app.btn_prev.grid(row=0, column=3, padx=style.PAD_SM, pady=style.PAD_SM, sticky="ew")
    app.btn_next = create_button(btns, text="➡ Neste", command=app.next)
    app.btn_next.grid(row=0, column=4, padx=style.PAD_SM, pady=style.PAD_SM, sticky="ew")

    return card


def build_panes(app):
    """Bygg venstre og høyre panel for detaljer og hovedbok."""

    import customtkinter as ctk

    panel = app.main_panel
    paned = ctk.CTkFrame(panel, fg_color="transparent")
    paned.grid(row=2, column=0, sticky="nsew", padx=style.PAD_LG, pady=(style.PAD_XS, style.PAD_SM))
    paned.grid_columnconfigure((0, 1), weight=1, minsize=400)
    paned.grid_rowconfigure(0, weight=1)

    left = ctk.CTkFrame(
        paned,
        corner_radius=style.CARD_RADIUS,
        fg_color=style.get_color("surface_card"),
        border_width=1,
        border_color=style.get_color("surface_border"),
    )
    right = ctk.CTkFrame(
        paned,
        corner_radius=style.CARD_RADIUS,
        fg_color=style.get_color("surface_card"),
        border_width=1,
        border_color=style.get_color("surface_border"),
    )
    left.grid(row=0, column=0, sticky="nsew", padx=(0, style.PAD_SM))
    right.grid(row=0, column=1, sticky="nsew", padx=(style.PAD_SM, 0))
    app.right_frame = right

    left.grid_columnconfigure(0, weight=1)
    left.grid_rowconfigure(1, weight=1, minsize=120)

    left_header = ctk.CTkFrame(left, fg_color="transparent")
    left_header.grid(row=0, column=0, sticky="ew", padx=style.PAD_LG, pady=(style.PAD_MD, style.PAD_XS))
    ctk.CTkLabel(left_header, text="Detaljer for bilag", font=style.FONT_TITLE_SMALL).grid(
        row=0,
        column=0,
        sticky="w",
    )
    app.detail_box = ctk.CTkTextbox(
        left,
        height=360,
        font=style.FONT_BODY,
        fg_color=style.get_color("surface_muted"),
        text_color=style.get_color("fg"),
        corner_radius=style.BTN_RADIUS,
        border_width=0,
    )
    app.detail_box.grid(
        row=1,
        column=0,
        sticky="nsew",
        padx=(style.PAD_LG, style.PAD_LG),
        pady=(0, style.PAD_LG),
    )

    right.grid_columnconfigure(0, weight=1)
    right.grid_columnconfigure(1, weight=0)
    right.grid_rowconfigure(1, weight=3, minsize=150)
    right.grid_rowconfigure(5, weight=1, minsize=120)

    right_header = ctk.CTkFrame(right, fg_color="transparent")
    right_header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=style.PAD_LG, pady=(style.PAD_MD, style.PAD_XS))
    ctk.CTkLabel(
        right_header,
        text="Hovedbok (bilagslinjer)",
        font=style.FONT_TITLE_SMALL,
    ).grid(row=0, column=0, sticky="w")

    ctk.CTkLabel(
        right,
        text="Kommentar",
        font=style.FONT_TITLE_SMALL,
    ).grid(
        row=4,
        column=0,
        columnspan=2,
        sticky="w",
        padx=(style.PAD_LG, style.PAD_LG),
        pady=(style.PAD_MD, style.PAD_XS),
    )
    app.comment_box = ctk.CTkTextbox(
        right,
        font=style.FONT_SMALL,
        fg_color=style.get_color("surface_muted"),
        text_color=style.get_color("fg"),
        corner_radius=style.BTN_RADIUS,
        border_width=0,
    )
    app.comment_box.grid(
        row=5,
        column=0,
        columnspan=2,
        sticky="nsew",
        padx=(style.PAD_LG, style.PAD_LG),
        pady=(0, style.PAD_LG),
    )

    return paned


def build_bottom(app):
    """Lag bunnseksjonen med eksportknapp og statusvisning."""

    import customtkinter as ctk

    panel = app.main_panel
    bottom = ctk.CTkFrame(panel, fg_color="transparent")
    bottom.grid(row=3, column=0, sticky="ew", padx=style.PAD_LG, pady=(0, style.PAD_MD))
    bottom.grid_columnconfigure(0, weight=1)
    app.bottom_frame = bottom

    card = ctk.CTkFrame(
        bottom,
        corner_radius=style.CARD_RADIUS,
        fg_color=style.get_color("surface_card"),
        border_width=1,
        border_color=style.get_color("surface_border"),
    )
    card.grid(row=0, column=0, sticky="ew")
    card.grid_columnconfigure(2, weight=1)

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
        card, text="📄 Eksporter PDF rapport", command=_export_pdf
    )
    export_btn.grid(
        row=0,
        column=0,
        padx=(style.PAD_LG, style.PAD_SM),
        pady=(style.PAD_MD, style.PAD_SM),
        sticky="w",
    )

    app.status_label = ctk.CTkLabel(
        card,
        text="",
        font=style.FONT_SMALL,
        text_color=style.get_color("muted"),
    )
    app.status_label.grid(
        row=0,
        column=1,
        padx=(0, style.PAD_SM),
        pady=(style.PAD_MD, style.PAD_SM),
        sticky="w",
    )

    app.progress_bar = ctk.CTkProgressBar(
        card,
        width=160,
        progress_color=style.get_color("success"),
        fg_color=style.get_color("surface_muted"),
    )
    app.progress_bar.set(0)
    app.progress_bar_grid = {
        "row": 0,
        "column": 2,
        "padx": style.PAD_SM,
        "pady": style.PAD_SM,
        "sticky": "e",
    }

    return bottom


def build_main(app):
    """Sett sammen hovedpanelet av alle delkomponenter."""

    import customtkinter as ctk

    panel = ctk.CTkFrame(
        app,
        corner_radius=style.CARD_RADIUS,
        fg_color=style.get_color("surface_muted"),
    )
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
    right.grid_columnconfigure(0, weight=1)
    right.grid_columnconfigure(1, weight=0)

    table_container = ctk.CTkFrame(
        right,
        corner_radius=style.BTN_RADIUS,
        fg_color=style.get_color("surface_muted"),
    )
    table_container.grid(
        row=1,
        column=0,
        columnspan=2,
        sticky="nsew",
        padx=(style.PAD_LG, style.PAD_LG),
        pady=(0, style.PAD_SM),
    )
    table_container.grid_columnconfigure(0, weight=1)
    table_container.grid_rowconfigure(0, weight=1)

    app.ledger_cols = LEDGER_COLS
    app.ledger_tree = ttk.Treeview(
        table_container,
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

    yscroll = ctk.CTkScrollbar(table_container, orientation="vertical", command=app.ledger_tree.yview)
    xscroll = ctk.CTkScrollbar(table_container, orientation="horizontal", command=app.ledger_tree.xview)
    app.ledger_tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
    app.ledger_tree.grid(row=0, column=0, sticky="nsew", padx=(style.PAD_SM, 0), pady=(style.PAD_SM, 0))
    yscroll.grid(row=0, column=1, sticky="ns", pady=style.PAD_SM, padx=(style.PAD_XXS, style.PAD_XXS))
    xscroll.grid(row=1, column=0, sticky="ew", padx=(style.PAD_SM, style.PAD_SM), pady=(style.PAD_XXS, style.PAD_SM))

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
        text_color=style.get_color("muted"),
    )
    app.ledger_sum.grid(
        row=3,
        column=0,
        columnspan=2,
        sticky="ew",
        padx=(style.PAD_LG, style.PAD_LG),
        pady=(style.PAD_SM, PADDING_Y),
    )
