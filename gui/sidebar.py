import os

from . import create_button
from .style import style, PADDING_Y
from .dropzone import DropZone
from helpers import logger

SIDEBAR_LOGO_WIDTH = 200


def parse_dropped_path(event):
    """Hent og valider filsti fra et drop-event.

    Returnerer filsti dersom den peker på en Excel-fil, ellers ``None``.
    """
    path = event.data.strip("{}").strip()
    if not path.lower().endswith((".xlsx", ".xls")):
        return None
    return path


def _toggle_sample_btn(app, *_):
    state = "normal" if app.sample_size_var.get() and app.year_var.get() else "disabled"
    app.sample_btn.configure(state=state)


def build_sidebar(app):
    import customtkinter as ctk

    card = ctk.CTkFrame(
        app,
        corner_radius=style.CARD_RADIUS,
        fg_color=style.get_color("sidebar_bg"),
        border_width=1,
        border_color=style.get_color("border"),
    )
    card.grid(row=0, column=0, sticky="nsw", padx=style.PAD_XL, pady=style.PAD_XL)
    card.grid_columnconfigure(0, weight=1)
    app.sidebar_card = card
    app.sidebar_labels = []
    heading_label = ctk.CTkLabel(
        card,
        text="⚙️ Datautvalg",
        font=style.FONT_TITLE_LARGE,
        text_color=style.get_color("heading"),
    )
    heading_label.grid(row=0, column=0, padx=style.PAD_XL, pady=(style.PAD_XL, style.PAD_XXS), sticky="w")
    app.sidebar_labels.append((heading_label, "heading"))

    subtitle_label = ctk.CTkLabel(
        card,
        text="Velg hvilke filer som skal kvalitetssikres.",
        font=style.FONT_CAPTION,
        text_color=style.get_color("muted"),
    )
    subtitle_label.grid(row=1, column=0, padx=style.PAD_XL, pady=(0, style.PAD_SM), sticky="w")
    app.sidebar_labels.append((subtitle_label, "muted"))

    sources_card = ctk.CTkFrame(
        card,
        corner_radius=style.SECTION_RADIUS,
        fg_color=style.get_color("surface"),
        border_width=1,
        border_color=style.get_color("border"),
    )
    sources_card.grid(row=2, column=0, padx=style.PAD_XL, pady=(0, style.PAD_MD), sticky="ew")
    sources_card.grid_columnconfigure(0, weight=1)
    app.sources_card = sources_card

    app.file_path_var = ctk.StringVar(master=app, value="")

    create_button(
        sources_card,
        text="Velg leverandørfakturaer (Excel)…",
        command=app.choose_file,
    ).grid(row=0, column=0, padx=style.PAD_LG, pady=(style.PAD_LG, style.PAD_XS), sticky="ew")

    def _drop_invoice(event):
        path = parse_dropped_path(event)
        if not path:
            return
        app.file_path_var.set(path)
        app._load_excel()

    app.inv_drop = DropZone(sources_card, "Dra og slipp fakturaliste her", _drop_invoice)
    app.inv_drop.grid(row=1, column=0, padx=style.PAD_LG, pady=(0, style.PAD_XS), sticky="ew")
    app.invoice_path_label = ctk.CTkLabel(
        sources_card,
        textvariable=app.file_path_var,
        wraplength=260,
        anchor="w",
        justify="left",
        font=style.FONT_SMALL,
        text_color=style.get_color("muted"),
    )
    app.invoice_path_label.grid(row=2, column=0, padx=style.PAD_LG, pady=(0, style.PAD_SM), sticky="ew")
    app.sidebar_labels.append((app.invoice_path_label, "muted"))

    app.gl_path_var = ctk.StringVar(master=app, value="")
    create_button(
        sources_card,
        text="Velg hovedbok (Excel)…",
        command=app.choose_gl_file,
    ).grid(row=3, column=0, padx=style.PAD_LG, pady=(0, style.PAD_XS), sticky="ew")

    def _drop_gl(event):
        path = parse_dropped_path(event)
        if not path:
            return
        app.gl_path_var.set(path)
        app._load_gl_excel()

    app.gl_drop = DropZone(sources_card, "Dra og slipp hovedbok her", _drop_gl)
    app.gl_drop.grid(row=4, column=0, padx=style.PAD_LG, pady=(0, style.PAD_XS), sticky="ew")
    app.gl_path_label = ctk.CTkLabel(
        sources_card,
        textvariable=app.gl_path_var,
        wraplength=260,
        anchor="w",
        justify="left",
        font=style.FONT_SMALL,
        text_color=style.get_color("muted"),
    )
    app.gl_path_label.grid(row=5, column=0, padx=style.PAD_LG, pady=(0, style.PAD_LG), sticky="ew")
    app.sidebar_labels.append((app.gl_path_label, "muted"))

    app.add_drop_target(app.inv_drop, app.inv_drop.on_drop)
    app.add_drop_target(app.gl_drop, app.gl_drop.on_drop)

    sample_card = ctk.CTkFrame(
        card,
        corner_radius=style.SECTION_RADIUS,
        fg_color=style.get_color("surface"),
        border_width=1,
        border_color=style.get_color("border"),
    )
    sample_card.grid(row=3, column=0, padx=style.PAD_XL, pady=(0, style.PAD_MD), sticky="ew")
    sample_card.grid_columnconfigure(0, weight=1)
    sample_card.grid_columnconfigure(1, weight=1)
    app.sample_card = sample_card

    app.sample_title_label = ctk.CTkLabel(
        sample_card,
        text="Stikkprøve",
        font=style.FONT_TITLE_SMALL,
        text_color=style.get_color("heading"),
    )
    app.sample_title_label.grid(row=0, column=0, columnspan=2, padx=style.PAD_LG, pady=(style.PAD_LG, style.PAD_XS), sticky="w")
    app.sidebar_labels.append((app.sample_title_label, "heading"))

    app.sample_count_label = ctk.CTkLabel(
        sample_card,
        text="Antall tilfeldig utvalg",
        font=style.FONT_BODY,
        text_color=style.get_color("muted"),
    )
    app.sample_count_label.grid(row=1, column=0, padx=style.PAD_LG, pady=(0, style.PAD_XXS), sticky="w")
    app.sidebar_labels.append((app.sample_count_label, "muted"))

    def _validate_int(P: str) -> bool:
        return P.isdigit() or P == ""

    vcmd_int = app.register(_validate_int)
    app.sample_size_var = ctk.StringVar(master=app, value="")
    ctk.CTkEntry(
        sample_card,
        width=100,
        textvariable=app.sample_size_var,
        validate="key",
        validatecommand=(vcmd_int, "%P"),
    ).grid(row=1, column=1, padx=(style.PAD_SM, style.PAD_LG), pady=(0, style.PAD_XXS), sticky="ew")

    app.sample_year_label = ctk.CTkLabel(
        sample_card,
        text="År",
        font=style.FONT_BODY,
        text_color=style.get_color("muted"),
    )
    app.sample_year_label.grid(row=2, column=0, padx=style.PAD_LG, pady=(style.PAD_SM, 0), sticky="w")
    app.sidebar_labels.append((app.sample_year_label, "muted"))

    app.year_var = ctk.StringVar(master=app, value="")
    app.year_combo = ctk.CTkComboBox(
        sample_card,
        width=100,
        variable=app.year_var,
        values=[],
        state="readonly",
        command=lambda _: _toggle_sample_btn(app),
    )
    app.year_combo.grid(row=2, column=1, padx=(style.PAD_SM, style.PAD_LG), pady=(style.PAD_SM, 0), sticky="ew")

    app.sample_btn = create_button(
        sample_card,
        text="🎲 Lag utvalg",
        command=app.make_sample,
        state="disabled",
    )
    app.sample_btn.grid(row=3, column=0, columnspan=2, padx=style.PAD_LG, pady=(style.PAD_MD, style.PAD_LG), sticky="ew")

    app.sample_size_var.trace_add("write", lambda *_: _toggle_sample_btn(app))
    app._update_year_options()

    app.lbl_filecount = ctk.CTkLabel(
        card,
        text="Antall bilag: –",
        font=style.FONT_TITLE,
        text_color=style.get_color("heading"),
    )
    app.lbl_filecount.grid(row=4, column=0, padx=style.PAD_XL, pady=(0, style.PAD_SM), sticky="w")

    opp_label = ctk.CTkLabel(
        card,
        text="Oppdragsinfo",
        font=style.FONT_TITLE_SMALL,
        text_color=style.get_color("heading"),
    )
    opp_label.grid(row=5, column=0, padx=style.PAD_XL, pady=(0, style.PAD_XS), sticky="w")
    app.sidebar_labels.append((opp_label, "heading"))
    opp = ctk.CTkFrame(
        card,
        corner_radius=style.SECTION_RADIUS,
        fg_color=style.get_color("surface"),
        border_width=1,
        border_color=style.get_color("border"),
    )
    opp.grid(row=6, column=0, padx=style.PAD_XL, pady=(0, style.PAD_MD), sticky="ew")
    opp.grid_columnconfigure(0, weight=0)
    opp.grid_columnconfigure(1, weight=1)
    app.assignment_card = opp

    app.kunde_var = ctk.StringVar(master=app, value="")
    default_user = os.environ.get("USERNAME") or os.environ.get("USER") or ""
    app.utfort_av_var = ctk.StringVar(master=app, value=default_user)

    kunde_label = ctk.CTkLabel(
        opp,
        text="Kunde",
        font=style.FONT_BODY,
        text_color=style.get_color("muted"),
    )
    kunde_label.grid(
        row=0,
        column=0,
        padx=(style.PAD_LG, style.PAD_MD),
        pady=(style.PAD_LG, style.PAD_XS),
        sticky="w",
    )
    app.sidebar_labels.append((kunde_label, "muted"))
    app.kunde_entry = ctk.CTkEntry(
        opp,
        textvariable=app.kunde_var,
        placeholder_text="Hentes automatisk",
        state="disabled",
    )
    app.kunde_entry.grid(
        row=0,
        column=1,
        padx=(0, style.PAD_LG),
        pady=(style.PAD_LG, style.PAD_XS),
        sticky="ew",
    )
    utf_label = ctk.CTkLabel(
        opp,
        text="Utført av",
        font=style.FONT_BODY,
        text_color=style.get_color("muted"),
    )
    utf_label.grid(
        row=1,
        column=0,
        padx=(style.PAD_LG, style.PAD_MD),
        pady=(style.PAD_XS, style.PAD_LG),
        sticky="w",
    )
    app.sidebar_labels.append((utf_label, "muted"))
    ctk.CTkEntry(opp, textvariable=app.utfort_av_var).grid(
        row=1,
        column=1,
        padx=(0, style.PAD_LG),
        pady=(style.PAD_XS, style.PAD_LG),
        sticky="ew",
    )
    info_lbl = ctk.CTkLabel(
        opp,
        text="Kundenavn hentes automatisk",
        font=style.FONT_SMALL_ITALIC,
        anchor="w",
        justify="left",
        wraplength=240,
        text_color=style.get_color("muted_alt"),
    )
    info_lbl.grid(
        row=2,
        column=0,
        columnspan=2,
        padx=(style.PAD_LG, style.PAD_LG),
        pady=(0, style.PAD_LG),
        sticky="w",
    )
    app.assignment_hint_label = info_lbl
    app.sidebar_labels.append((info_lbl, "muted_alt"))

    card.grid_rowconfigure(40, weight=1)

    status_card = ctk.CTkFrame(
        card,
        corner_radius=style.SECTION_RADIUS,
        fg_color=style.get_color("surface"),
        border_width=1,
        border_color=style.get_color("border"),
    )
    status_card.grid(
        row=100,
        column=0,
        padx=style.PAD_XL,
        pady=(style.PAD_SM, PADDING_Y),
        sticky="ew",
    )
    status_card.grid_columnconfigure(0, weight=1)
    app.status_card = status_card

    title_font = style.FONT_TITLE_SMALL
    body_font = style.FONT_BODY

    app.status_title_label = ctk.CTkLabel(
        status_card,
        text="Status",
        font=title_font,
        anchor="center",
        justify="center",
        text_color=style.get_color("heading"),
    )
    app.status_title_label.grid(row=0, column=0, sticky="ew", pady=(PADDING_Y, style.PAD_SM))
    app.sidebar_labels.append((app.status_title_label, "heading"))

    app.lbl_st_sum_kontrollert = ctk.CTkLabel(
        status_card,
        text="Sum kontrollert: –",
        font=body_font,
        anchor="center",
        justify="center",
        text_color=style.get_color("muted"),
    )
    app.lbl_st_sum_kontrollert.grid(row=1, column=0, sticky="ew", pady=(0, style.PAD_XXS))

    app.lbl_st_sum_alle = ctk.CTkLabel(
        status_card,
        text="Sum alle bilag: –",
        font=body_font,
        anchor="center",
        justify="center",
        text_color=style.get_color("muted"),
    )
    app.lbl_st_sum_alle.grid(row=2, column=0, sticky="ew", pady=(0, style.PAD_XXS))

    app.lbl_st_pct = ctk.CTkLabel(
        status_card,
        text="% kontrollert av sum: –",
        font=body_font,
        anchor="center",
        justify="center",
        text_color=style.get_color("muted"),
    )
    app.lbl_st_pct.grid(row=3, column=0, sticky="ew", pady=(0, style.PAD_MD))

    app.lbl_st_godkjent = ctk.CTkLabel(
        status_card,
        text="Godkjent: –",
        font=body_font,
        anchor="center",
        justify="center",
        text_color=style.get_color("muted"),
    )
    app.lbl_st_godkjent.grid(row=4, column=0, sticky="ew", pady=(0, style.PAD_XXS))

    app.lbl_st_ikkegodkjent = ctk.CTkLabel(
        status_card,
        text="Ikke godkjent: –",
        font=body_font,
        anchor="center",
        justify="center",
        text_color=style.get_color("muted"),
    )
    app.lbl_st_ikkegodkjent.grid(row=5, column=0, sticky="ew", pady=(0, style.PAD_XXS))

    app.lbl_st_gjen = ctk.CTkLabel(
        status_card,
        text="Gjenstår å kontrollere: –",
        font=body_font,
        anchor="center",
        justify="center",
        text_color=style.get_color("muted"),
    )
    app.lbl_st_gjen.grid(row=6, column=0, sticky="ew", pady=(style.PAD_SM, PADDING_Y))

    try:
        from PIL import Image
        from helpers_path import resource_path

        img_light = Image.open(resource_path("icons/borev_logo_lightmode.png"))
        img_dark = Image.open(resource_path("icons/borev_logo_darkmode.png"))

        w, h = img_light.size
        scaled_h = int(h * (SIDEBAR_LOGO_WIDTH / w))
        app.sidebar_logo_img = ctk.CTkImage(
            light_image=img_light,
            dark_image=img_dark,
            size=(SIDEBAR_LOGO_WIDTH, scaled_h),
        )
        ctk.CTkLabel(
            card,
            text="",
            image=app.sidebar_logo_img,
            font=style.FONT_BODY,
        ).grid(
            row=101,
            column=0,
            padx=style.PAD_XL,
            pady=(0, PADDING_Y),
            sticky="ew",
        )
    except (ImportError, OSError):
        logger.exception("Kunne ikke laste sidebar-logo")

    return card

