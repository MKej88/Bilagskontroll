import os
from . import create_button
from .style import style, PADDING_Y


def _toggle_sample_btn(app, *_):
    state = "normal" if app.sample_size_var.get() and app.year_var.get() else "disabled"
    app.sample_btn.configure(state=state)


def build_sidebar(app):
    import customtkinter as ctk

    card = ctk.CTkFrame(app, corner_radius=16)
    card.grid(row=0, column=0, sticky="nsw", padx=style.PAD_XL, pady=style.PAD_XL)

    ctk.CTkLabel(card, text="⚙️ Datautvalg", font=style.FONT_TITLE_LARGE)\
        .grid(row=0, column=0, padx=style.PAD_XL, pady=(style.PAD_XL, style.PAD_SM), sticky="w")

    app.file_path_var = ctk.StringVar(master=app, value="")
    create_button(card, text="Velg leverandørfakturaer (Excel)…", command=app.choose_file)\
        .grid(row=1, column=0, padx=style.PAD_XL, pady=(style.PAD_XS, style.PAD_XXS), sticky="ew")
    def _create_drop_zone(parent, text):
        frame = ctk.CTkFrame(
            parent,
            height=70,
            corner_radius=style.BTN_RADIUS,
            fg_color=style.get_color_pair("dnd_bg"),
            border_color=style.get_color_pair("dnd_border"),
            border_width=2,
        )
        ctk.CTkLabel(
            frame,
            text=text,
            anchor="center",
            text_color=style.get_color_pair("dnd_border"),
        ).pack(expand=True, fill="both", padx=style.PAD_MD, pady=style.PAD_SM)
        return frame

    app.inv_drop = _create_drop_zone(card, "Dra og slipp fakturaliste her")
    app.inv_drop.grid(row=2, column=0, padx=style.PAD_XL, pady=(0, style.PAD_XXS), sticky="ew")
    ctk.CTkLabel(card, textvariable=app.file_path_var, wraplength=260, anchor="w", justify="left")\
        .grid(row=3, column=0, padx=style.PAD_XL, pady=(0, style.PAD_SM), sticky="ew")

    app.gl_path_var = ctk.StringVar(master=app, value="")
    create_button(card, text="Velg hovedbok (Excel)…", command=app.choose_gl_file)\
        .grid(row=4, column=0, padx=style.PAD_XL, pady=(style.PAD_XXS, style.PAD_XXS), sticky="ew")
    app.gl_drop = _create_drop_zone(card, "Dra og slipp hovedbok her")
    app.gl_drop.grid(row=5, column=0, padx=style.PAD_XL, pady=(0, style.PAD_XXS), sticky="ew")
    ctk.CTkLabel(card, textvariable=app.gl_path_var, wraplength=260, anchor="w", justify="left")\
        .grid(row=6, column=0, padx=style.PAD_XL, pady=(0, style.PAD_SM), sticky="ew")

    def _drop_invoice(event):
        path = event.data.strip("{}").strip()
        if not path.lower().endswith((".xlsx", ".xls")):
            return
        app.file_path_var.set(path)
        app._load_excel()

    def _drop_gl(event):
        path = event.data.strip("{}").strip()
        if not path.lower().endswith((".xlsx", ".xls")):
            return
        app.gl_path_var.set(path)
        app._load_gl_excel()

    app.add_drop_target(app.inv_drop, _drop_invoice)
    app.add_drop_target(app.gl_drop, _drop_gl)

    row_utv = ctk.CTkFrame(card)
    row_utv.grid(row=7, column=0, padx=style.PAD_XL, pady=(style.PAD_XS, 0), sticky="ew")
    ctk.CTkLabel(row_utv, text="Antall tilfeldig utvalg").grid(
        row=0, column=0, padx=(style.PAD_MD, 0), sticky="w"
    )

    def _validate_int(P: str) -> bool:
        return P.isdigit() or P == ""

    vcmd_int = app.register(_validate_int)
    app.sample_size_var = ctk.StringVar(master=app, value="")
    ctk.CTkEntry(
        row_utv,
        width=80,
        textvariable=app.sample_size_var,
        validate="key",
        validatecommand=(vcmd_int, "%P"),
    ).grid(row=0, column=1, padx=(style.PAD_MD, 0))

    ctk.CTkLabel(row_utv, text="År").grid(row=1, column=0, padx=(style.PAD_MD, 0), pady=(style.PAD_SM, 0), sticky="w")

    app.year_var = ctk.StringVar(master=app, value="")
    app.year_combo = ctk.CTkComboBox(
        row_utv,
        width=80,
        variable=app.year_var,
        values=[],
        state="readonly",
        command=lambda _: _toggle_sample_btn(app),
    )
    app.year_combo.grid(row=1, column=1, padx=(style.PAD_MD, 0), pady=(style.PAD_SM, 0))

    app.sample_btn = create_button(card, text="🎲 Lag utvalg", command=app.make_sample, state="disabled")
    app.sample_btn.grid(row=8, column=0, padx=style.PAD_XL, pady=(style.PAD_MD, style.PAD_SM), sticky="ew")

    app.sample_size_var.trace_add("write", lambda *_: _toggle_sample_btn(app))
    app._update_year_options()

    app.lbl_filecount = ctk.CTkLabel(card, text="Antall bilag: –", font=style.FONT_TITLE)
    app.lbl_filecount.grid(row=9, column=0, padx=style.PAD_XL, pady=(style.PAD_XXS, style.PAD_XXS), sticky="w")

    ctk.CTkLabel(card, text="Oppdragsinfo", font=style.FONT_BODY_BOLD)\
        .grid(row=10, column=0, padx=style.PAD_XL, pady=(style.PAD_MD, style.PAD_XXS), sticky="w")
    opp = ctk.CTkFrame(card, corner_radius=8)
    opp.grid(row=11, column=0, padx=style.PAD_XL, pady=(0, style.PAD_MD), sticky="ew")
    opp.grid_columnconfigure(0, weight=0)
    opp.grid_columnconfigure(1, weight=1)

    app.kunde_var = ctk.StringVar(master=app, value="")
    try:
        default_user = os.environ.get("USERNAME") or os.environ.get("USER") or ""
    except Exception:
        default_user = ""
    app.utfort_av_var = ctk.StringVar(master=app, value=default_user)

    ctk.CTkLabel(opp, text="Kunde").grid(row=0, column=0, padx=(style.PAD_MD, style.PAD_MD), pady=(style.PAD_MD, style.PAD_XS), sticky="w")
    app.kunde_entry = ctk.CTkEntry(
        opp,
        textvariable=app.kunde_var,
        placeholder_text="Hentes automatisk",
        state="disabled",
    )
    app.kunde_entry.grid(row=0, column=1, padx=(0, style.PAD_MD), pady=(style.PAD_MD, style.PAD_XS), sticky="ew")
    ctk.CTkLabel(opp, text="Utført av").grid(row=1, column=0, padx=(style.PAD_MD, style.PAD_MD), pady=(style.PAD_XS, style.PAD_MD), sticky="w")
    ctk.CTkEntry(opp, textvariable=app.utfort_av_var).grid(row=1, column=1, padx=(0, style.PAD_MD), pady=(style.PAD_XS, style.PAD_MD), sticky="ew")
    info_lbl = ctk.CTkLabel(
        opp,
        text="Kundenavn hentes automatisk",
        font=style.FONT_SMALL_ITALIC,
        anchor="w",
        justify="left",
        wraplength=240,
    )
    info_lbl.grid(row=2, column=0, columnspan=2, padx=(style.PAD_MD, style.PAD_MD), pady=(0, style.PAD_MD), sticky="w")

    status_card = ctk.CTkFrame(card, corner_radius=12)
    status_card.grid(row=12, column=0, padx=style.PAD_XL, pady=(style.PAD_MD, style.PAD_MD), sticky="ew")
    status_card.grid_columnconfigure(0, weight=1)

    card.grid_rowconfigure(13, weight=1)

    title_font = style.FONT_TITLE_LARGE
    body_font = style.FONT_BODY

    ctk.CTkLabel(status_card, text="Status", font=title_font, anchor="center", justify="center")\
        .grid(row=0, column=0, sticky="ew", pady=(PADDING_Y, style.PAD_SM))

    app.lbl_st_sum_kontrollert = ctk.CTkLabel(status_card, text="Sum kontrollert: –", font=body_font, anchor="center", justify="center")
    app.lbl_st_sum_kontrollert.grid(row=1, column=0, sticky="ew", pady=(0, style.PAD_XXS))

    app.lbl_st_sum_alle = ctk.CTkLabel(status_card, text="Sum alle bilag: –", font=body_font, anchor="center", justify="center")
    app.lbl_st_sum_alle.grid(row=2, column=0, sticky="ew", pady=(0, style.PAD_XXS))

    app.lbl_st_pct = ctk.CTkLabel(status_card, text="% kontrollert av sum: –", font=body_font, anchor="center", justify="center")
    app.lbl_st_pct.grid(row=3, column=0, sticky="ew", pady=(0, style.PAD_MD))

    app.lbl_st_godkjent = ctk.CTkLabel(status_card, text="Godkjent: –", font=body_font, anchor="center", justify="center")
    app.lbl_st_godkjent.grid(row=4, column=0, sticky="ew", pady=(0, style.PAD_XXS))

    app.lbl_st_ikkegodkjent = ctk.CTkLabel(status_card, text="Ikke godkjent: –", font=body_font, anchor="center", justify="center")
    app.lbl_st_ikkegodkjent.grid(row=5, column=0, sticky="ew", pady=(0, style.PAD_XXS))

    app.lbl_st_gjen = ctk.CTkLabel(status_card, text="Gjenstår å kontrollere: –", font=body_font, anchor="center", justify="center")
    app.lbl_st_gjen.grid(row=6, column=0, sticky="ew", pady=(style.PAD_SM, PADDING_Y))

    from PIL import Image

    light_logo = Image.open("icons/borev_logo_lightmode.png")
    dark_logo = Image.open("icons/borev_logo_darkmode.png")
    logo_width = 260
    aspect_ratio = light_logo.height / light_logo.width
    logo_height = int(logo_width * aspect_ratio)
    app.sidebar_logo = ctk.CTkImage(
        light_image=light_logo,
        dark_image=dark_logo,
        size=(logo_width, logo_height),
    )
    ctk.CTkLabel(card, image=app.sidebar_logo, text="").grid(
        row=14,
        column=0,
        padx=style.PAD_XL,
        pady=(0, style.PAD_XL),
        sticky="ew",
    )

    return card
