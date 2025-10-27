from . import DEFAULT_APPEARANCE_MODE, create_button
from .style import style
from .style import PADDING_Y


def build_header(app):
    """Bygg overskrift med status, fakturanr og temavalg."""

    import customtkinter as ctk

    panel = app.main_panel
    head = ctk.CTkFrame(
        panel,
        corner_radius=20,
        fg_color=style.get_color("card_bg"),
        border_width=1,
        border_color=style.get_color("card_border"),
    )
    head.grid(row=0, column=0, sticky="ew", padx=style.PAD_LG, pady=style.PAD_MD)
    head.grid_columnconfigure(0, weight=1)

    accent = ctk.CTkFrame(head, height=6, fg_color=style.get_color("accent"))
    accent.grid(row=0, column=0, sticky="ew")
    accent.grid_propagate(False)

    content = ctk.CTkFrame(head, fg_color="transparent")
    content.grid(
        row=1,
        column=0,
        sticky="ew",
        padx=style.PAD_XL,
        pady=(style.PAD_LG, style.PAD_LG),
    )
    content.grid_columnconfigure(0, weight=1)
    content.grid_columnconfigure(1, weight=0)

    title_block = ctk.CTkFrame(content, fg_color="transparent")
    title_block.grid(row=0, column=0, sticky="w")
    ctk.CTkLabel(
        title_block,
        text="Bilagskontroll",
        font=style.FONT_DISPLAY,
        text_color=style.get_color("accent"),
    ).grid(row=0, column=0, sticky="w")
    ctk.CTkLabel(
        title_block,
        text="Revisjonsoversikt for leverandørfakturaer",
        font=style.FONT_BODY,
        text_color=style.get_color("muted_fg"),
    ).grid(row=1, column=0, sticky="w", pady=(style.PAD_XXS, 0))

    controls = ctk.CTkFrame(
        content,
        fg_color=style.get_color("surface_alt"),
        corner_radius=style.BTN_RADIUS,
    )
    controls.grid(row=0, column=1, sticky="ne", padx=(style.PAD_LG, 0))
    controls.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        controls,
        text="Temamodus",
        font=style.FONT_CAPTION,
        text_color=style.get_color("muted_fg"),
    ).grid(row=0, column=0, sticky="w", padx=(style.PAD_MD, style.PAD_MD), pady=(style.PAD_MD, 0))
    default_theme_label = DEFAULT_APPEARANCE_MODE.title()
    app.theme_var = ctk.StringVar(value=default_theme_label)
    app.theme_menu = ctk.CTkOptionMenu(
        controls,
        variable=app.theme_var,
        values=["Light", "Dark"],
        command=app._switch_theme,
    )
    app.theme_menu.grid(
        row=1,
        column=0,
        sticky="ew",
        padx=(style.PAD_MD, style.PAD_MD),
        pady=(style.PAD_XS, 0),
    )
    app.theme_menu.set(default_theme_label)

    create_button(controls, text="📋 Kopier fakturanr", command=app.copy_invoice).grid(
        row=2,
        column=0,
        sticky="ew",
        padx=(style.PAD_MD, style.PAD_MD),
        pady=(style.PAD_SM, 0),
    )
    app.copy_feedback = ctk.CTkLabel(
        controls,
        text="",
        text_color=style.get_color("success"),
        font=style.FONT_SMALL,
    )
    app.copy_feedback.grid(
        row=3,
        column=0,
        sticky="w",
        padx=(style.PAD_MD, style.PAD_MD),
        pady=(style.PAD_XXS, style.PAD_MD),
    )

    metrics = ctk.CTkFrame(
        content,
        fg_color=style.get_color("surface_alt"),
        corner_radius=style.BTN_RADIUS,
        border_width=1,
        border_color=style.get_color("card_border"),
    )
    metrics.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(style.PAD_MD, 0))
    metrics.grid_columnconfigure((0, 1, 2), weight=1)

    def _metric(column: int, title: str, attr: str, default: str, emphasize: bool = False):
        container = ctk.CTkFrame(metrics, fg_color="transparent")
        container.grid(
            row=0,
            column=column,
            sticky="ew",
            padx=style.PAD_MD,
            pady=(style.PAD_MD, style.PAD_MD),
        )
        ctk.CTkLabel(
            container,
            text=title,
            font=style.FONT_CAPTION,
            text_color=style.get_color("muted_fg"),
        ).grid(row=0, column=0, sticky="w")
        label_kwargs = {
            "font": style.FONT_TITLE_SMALL,
            "text_color": style.get_color("fg"),
        }
        if emphasize:
            label_kwargs.update(
                font=style.FONT_TITLE_LARGE,
                text_color=style.get_color("accent"),
            )
        value = ctk.CTkLabel(container, text=default, **label_kwargs)
        value.grid(row=1, column=0, sticky="w", pady=(style.PAD_XXS, 0))
        setattr(app, attr, value)
        return value

    _metric(0, "Bilag", "lbl_count", "–/–", emphasize=True)
    _metric(1, "Fakturanummer", "lbl_invoice", "–")

    status_container = ctk.CTkFrame(metrics, fg_color="transparent")
    status_container.grid(
        row=0,
        column=2,
        sticky="ew",
        padx=style.PAD_MD,
        pady=(style.PAD_MD, style.PAD_MD),
    )
    ctk.CTkLabel(
        status_container,
        text="Status",
        font=style.FONT_CAPTION,
        text_color=style.get_color("muted_fg"),
    ).grid(row=0, column=0, sticky="w")
    app.lbl_status = ctk.CTkLabel(
        status_container,
        text="–",
        font=style.FONT_BODY_BOLD,
        text_color=style.get_color("accent_fg"),
        fg_color=style.get_color("accent_soft"),
        corner_radius=style.BTN_RADIUS,
        padx=style.PAD_MD,
        pady=style.PAD_XXS,
    )
    app.lbl_status.grid(row=1, column=0, sticky="w", pady=(style.PAD_XXS, 0))

    app.inline_status = ctk.CTkLabel(
        content,
        text="",
        text_color=style.get_color("success"),
        font=style.FONT_BODY_BOLD,
    )
    app.inline_status.grid(
        row=2,
        column=0,
        columnspan=2,
        sticky="w",
        pady=(style.PAD_SM, 0),
    )

    return head


def build_action_buttons(app):
    """Opprett handling- og navigasjonsknapper."""

    import customtkinter as ctk

    panel = app.main_panel
    btns = ctk.CTkFrame(
        panel,
        corner_radius=18,
        fg_color=style.get_color("card_bg"),
        border_width=1,
        border_color=style.get_color("card_border"),
    )
    btns.grid(row=1, column=0, sticky="ew", padx=style.PAD_LG, pady=(0, style.PAD_SM))
    btns.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

    ctk.CTkLabel(
        btns,
        text="Handlinger",
        font=style.FONT_CAPTION,
        text_color=style.get_color("muted_fg"),
    ).grid(
        row=0,
        column=0,
        columnspan=5,
        sticky="w",
        padx=style.PAD_XL,
        pady=(style.PAD_LG, style.PAD_XS),
    )

    create_button(
        btns,
        text="✅ Godkjent",
        fg_color=style.get_color("success"),
        hover_color=style.get_color("success_hover"),
        command=lambda: app.set_decision_and_next("Godkjent"),
    ).grid(row=1, column=0, padx=style.PAD_SM, pady=(0, style.PAD_LG), sticky="ew")
    create_button(
        btns,
        text="⛔ Ikke godkjent",
        fg_color=style.get_color("error"),
        hover_color=style.get_color("error_hover"),
        command=lambda: app.set_decision_and_next("Ikke godkjent"),
    ).grid(row=1, column=1, padx=style.PAD_SM, pady=(0, style.PAD_LG), sticky="ew")
    create_button(btns, text="🔗 Åpne PowerOffice", command=app.open_in_po).grid(
        row=1,
        column=2,
        padx=style.PAD_SM,
        pady=(0, style.PAD_LG),
        sticky="ew",
    )
    app.btn_prev = create_button(btns, text="⬅ Forrige", command=app.prev)
    app.btn_prev.grid(row=1, column=3, padx=style.PAD_SM, pady=(0, style.PAD_LG), sticky="ew")
    app.btn_next = create_button(btns, text="➡ Neste", command=app.next)
    app.btn_next.grid(row=1, column=4, padx=style.PAD_SM, pady=(0, style.PAD_LG), sticky="ew")

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

    left = ctk.CTkFrame(
        paned,
        corner_radius=18,
        fg_color=style.get_color("card_bg"),
        border_width=1,
        border_color=style.get_color("card_border"),
    )
    right = ctk.CTkFrame(
        paned,
        corner_radius=18,
        fg_color=style.get_color("card_bg"),
        border_width=1,
        border_color=style.get_color("card_border"),
    )
    left.grid(row=0, column=0, sticky="nsew", padx=(0, style.PAD_SM))
    right.grid(row=0, column=1, sticky="nsew", padx=(style.PAD_SM, 0))
    app.right_frame = right

    ctk.CTkLabel(
        left,
        text="Detaljer for bilag",
        font=style.FONT_TITLE_SMALL,
        text_color=style.get_color("muted_fg"),
    ).grid(row=0, column=0, sticky="w", padx=style.PAD_LG, pady=(style.PAD_LG, style.PAD_SM))
    left.grid_columnconfigure(0, weight=1)
    left.grid_rowconfigure(1, weight=1, minsize=120)
    app.detail_box = ctk.CTkTextbox(left, height=360, font=style.FONT_BODY)
    app.detail_box.grid(
        row=1,
        column=0,
        sticky="nsew",
        padx=(style.PAD_LG, style.PAD_LG),
        pady=(0, style.PAD_LG),
    )

    ctk.CTkLabel(
        right,
        text="Hovedbok (bilagslinjer)",
        font=style.FONT_TITLE_SMALL,
        text_color=style.get_color("muted_fg"),
    ).grid(row=0, column=0, sticky="w", padx=style.PAD_LG, pady=(style.PAD_LG, style.PAD_SM))
    right.grid_columnconfigure(0, weight=1)
    right.grid_columnconfigure(1, weight=0)
    right.grid_rowconfigure(1, weight=3, minsize=150)
    right.grid_rowconfigure(5, weight=1, minsize=120)

    ctk.CTkLabel(
        right,
        text="Kommentar",
        font=style.FONT_TITLE_SMALL,
        text_color=style.get_color("muted_fg"),
    ).grid(
        row=4,
        column=0,
        columnspan=2,
        sticky="w",
        padx=(style.PAD_LG, style.PAD_SM),
        pady=(style.PAD_MD, style.PAD_XS),
    )
    app.comment_box = ctk.CTkTextbox(right, font=style.FONT_SMALL)
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
    bottom = ctk.CTkFrame(
        panel,
        corner_radius=18,
        fg_color=style.get_color("card_bg"),
        border_width=1,
        border_color=style.get_color("card_border"),
    )
    bottom.grid(row=3, column=0, sticky="ew", padx=style.PAD_LG, pady=(0, style.PAD_MD))
    bottom.grid_columnconfigure(1, weight=1)
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

    export_btn = create_button(
        bottom, text="📄 Eksporter PDF rapport", command=_export_pdf
    )
    export_btn.grid(
        row=1,
        column=0,
        padx=(style.PAD_LG, style.PAD_SM),
        pady=(0, style.PAD_MD),
        sticky="w",
    )

    ctk.CTkLabel(
        bottom,
        text="Rapportering",
        font=style.FONT_CAPTION,
        text_color=style.get_color("muted_fg"),
    ).grid(
        row=0,
        column=0,
        columnspan=3,
        sticky="w",
        padx=style.PAD_LG,
        pady=(style.PAD_LG, style.PAD_XS),
    )

    app.status_label = ctk.CTkLabel(
        bottom,
        text="",
        font=style.FONT_BODY,
        text_color=style.get_color("muted_fg"),
    )
    app.status_label.grid(
        row=1,
        column=1,
        padx=style.PAD_SM,
        pady=(0, style.PAD_MD),
        sticky="ew",
    )

    app.progress_bar = ctk.CTkProgressBar(
        bottom,
        width=120,
        progress_color=style.get_color("success"),
        fg_color=style.get_color("surface_alt"),
    )
    app.progress_bar.set(0)
    app.progress_bar_grid = {
        "row": 1,
        "column": 2,
        "padx": style.PAD_SM,
        "pady": (0, style.PAD_MD),
        "sticky": "e",
    }

    return bottom


def build_main(app):
    """Sett sammen hovedpanelet av alle delkomponenter."""

    import customtkinter as ctk

    panel = ctk.CTkFrame(
        app,
        corner_radius=16,
        fg_color=style.get_color("surface"),
    )
    panel.grid(row=0, column=1, sticky="nsew", padx=(0, style.PAD_XL), pady=style.PAD_XL)
    panel.grid_columnconfigure(0, weight=1)
    panel.grid_rowconfigure(2, weight=1, minsize=300)

    app.main_panel = panel
    app.configure(fg_color=style.get_color("surface"))

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
