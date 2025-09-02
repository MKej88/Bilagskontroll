import os
import customtkinter as ctk


def build_sidebar(app):
    card = ctk.CTkFrame(app, corner_radius=16)
    card.grid(row=0, column=0, sticky="nsw", padx=14, pady=14)

    ctk.CTkLabel(card, text="⚙️ Innstillinger", font=ctk.CTkFont(size=18, weight="bold"))\
        .grid(row=0, column=0, padx=14, pady=(14, 6), sticky="w")

    app.file_path_var = ctk.StringVar(master=app, value="")
    ctk.CTkButton(card, text="Velg leverandørfakturaer (Excel)…", command=app.choose_file)\
        .grid(row=1, column=0, padx=14, pady=(4, 2), sticky="ew")
    app.file_path_lbl = ctk.CTkLabel(card, textvariable=app.file_path_var, wraplength=260, anchor="w", justify="left")
    app.file_path_lbl.grid(row=2, column=0, padx=14, pady=(0, 6), sticky="ew")

    app.gl_path_var = ctk.StringVar(master=app, value="")
    ctk.CTkButton(card, text="Velg hovedbok (Excel)…", command=app.choose_gl_file)\
        .grid(row=3, column=0, padx=14, pady=(2, 2), sticky="ew")
    app.gl_path_lbl = ctk.CTkLabel(card, textvariable=app.gl_path_var, wraplength=260, anchor="w", justify="left")
    app.gl_path_lbl.grid(row=4, column=0, padx=14, pady=(0, 6), sticky="ew")

    row_utv = ctk.CTkFrame(card)
    row_utv.grid(row=5, column=0, padx=14, pady=(4, 0), sticky="ew")
    ctk.CTkLabel(row_utv, text="Antall tilfeldig utvalg").grid(row=0, column=0, sticky="w")

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
    ).grid(row=0, column=1, padx=(8, 0))

    ctk.CTkLabel(row_utv, text="År").grid(row=1, column=0, pady=(6, 0), sticky="w")

    def _validate_year(P: str) -> bool:
        if P == "":
            return True
        if not P.isdigit() or len(P) > 4:
            return False
        if len(P) == 4 and not 1900 <= int(P) <= 2100:
            return False
        return True

    vcmd_year = app.register(_validate_year)
    app.year_var = ctk.StringVar(master=app, value="")
    ctk.CTkEntry(
        row_utv,
        width=80,
        textvariable=app.year_var,
        validate="key",
        validatecommand=(vcmd_year, "%P"),
    ).grid(row=1, column=1, padx=(8, 0), pady=(6, 0))

    app.sample_btn = ctk.CTkButton(card, text="🎲 Lag utvalg", command=app.make_sample, state="disabled")
    app.sample_btn.grid(row=6, column=0, padx=14, pady=(8, 6), sticky="ew")

    def _toggle_sample_btn(*_):
        state = "normal" if app.sample_size_var.get() and app.year_var.get() else "disabled"
        app.sample_btn.configure(state=state)

    app.sample_size_var.trace_add("write", _toggle_sample_btn)
    app.year_var.trace_add("write", _toggle_sample_btn)

    app.lbl_filecount = ctk.CTkLabel(card, text="Antall bilag: –", font=ctk.CTkFont(size=16, weight="bold"))
    app.lbl_filecount.grid(row=7, column=0, padx=14, pady=(2, 2), sticky="w")

    ctk.CTkLabel(card, text="Oppdragsinfo", font=ctk.CTkFont(size=14, weight="bold"))\
        .grid(row=8, column=0, padx=14, pady=(8, 2), sticky="w")
    opp = ctk.CTkFrame(card, corner_radius=8)
    opp.grid(row=9, column=0, padx=14, pady=(0, 8), sticky="ew")
    opp.grid_columnconfigure(0, weight=0)
    opp.grid_columnconfigure(1, weight=1)

    app.kunde_var = ctk.StringVar(master=app, value="")
    app.kundenr_var = ctk.StringVar(master=app, value="")
    try:
        default_user = os.environ.get("USERNAME") or os.environ.get("USER") or ""
    except Exception:
        default_user = ""
    app.utfort_av_var = ctk.StringVar(master=app, value=default_user)

    ctk.CTkLabel(opp, text="Kunde").grid(row=0, column=0, padx=(8,8), pady=(8,4), sticky="w")
    app.kunde_entry = ctk.CTkEntry(
        opp,
        textvariable=app.kunde_var,
        placeholder_text="Hentes automatisk",
        state="disabled",
    )
    app.kunde_entry.grid(row=0, column=1, padx=(0,8), pady=(8,4), sticky="ew")
    ctk.CTkLabel(opp, text="Kundenr").grid(row=1, column=0, padx=(8,8), pady=(4,4), sticky="w")
    ctk.CTkEntry(opp, textvariable=app.kundenr_var).grid(row=1, column=1, padx=(0,8), pady=(4,4), sticky="ew")
    ctk.CTkLabel(opp, text="Utført av").grid(row=2, column=0, padx=(8,8), pady=(4,8), sticky="w")
    ctk.CTkEntry(opp, textvariable=app.utfort_av_var).grid(row=2, column=1, padx=(0,8), pady=(4,8), sticky="ew")
    info_lbl = ctk.CTkLabel(
        opp,
        text="Kundenavn hentes automatisk",
        font=ctk.CTkFont(size=12, slant="italic"),
        anchor="w",
        justify="left",
        wraplength=240,
    )
    info_lbl.grid(row=3, column=0, columnspan=2, padx=(8,8), pady=(0,8), sticky="w")

    card.grid_rowconfigure(20, weight=1)

    ctk.CTkLabel(card, text="Tema", font=ctk.CTkFont(size=13))\
        .grid(row=101, column=0, padx=14, pady=(0, 0), sticky="w")
    theme = ctk.CTkSegmentedButton(card, values=["System", "Light", "Dark"], command=app._switch_theme)
    theme.set("System")
    theme.grid(row=102, column=0, padx=14, pady=(2, 14), sticky="ew")

    status_card = ctk.CTkFrame(card, corner_radius=12)
    status_card.grid(row=100, column=0, padx=14, pady=(8, 14), sticky="ew")
    status_card.grid_columnconfigure(0, weight=1)

    title_font = ctk.CTkFont(size=18, weight="bold")
    body_font = ctk.CTkFont(size=14)

    ctk.CTkLabel(status_card, text="Status", font=title_font, anchor="center", justify="center")\
        .grid(row=0, column=0, sticky="ew", pady=(10, 6))

    app.lbl_st_sum_kontrollert = ctk.CTkLabel(status_card, text="Sum kontrollert: –", font=body_font, anchor="center", justify="center")
    app.lbl_st_sum_kontrollert.grid(row=1, column=0, sticky="ew", pady=(0,2))

    app.lbl_st_sum_alle = ctk.CTkLabel(status_card, text="Sum alle bilag: –", font=body_font, anchor="center", justify="center")
    app.lbl_st_sum_alle.grid(row=2, column=0, sticky="ew", pady=(0,2))

    app.lbl_st_pct = ctk.CTkLabel(status_card, text="% kontrollert av sum: –", font=body_font, anchor="center", justify="center")
    app.lbl_st_pct.grid(row=3, column=0, sticky="ew", pady=(0,8))

    app.lbl_st_godkjent = ctk.CTkLabel(status_card, text="Godkjent: –", font=body_font, anchor="center", justify="center")
    app.lbl_st_godkjent.grid(row=4, column=0, sticky="ew", pady=(0,2))

    app.lbl_st_ikkegodkjent = ctk.CTkLabel(status_card, text="Ikke godkjent: –", font=body_font, anchor="center", justify="center")
    app.lbl_st_ikkegodkjent.grid(row=5, column=0, sticky="ew", pady=(0,2))

    app.lbl_st_gjen = ctk.CTkLabel(status_card, text="Gjenstår å kontrollere: –", font=body_font, anchor="center", justify="center")
    app.lbl_st_gjen.grid(row=6, column=0, sticky="ew", pady=(6,10))

    return card
