# Bilagskontroll

<p align="center">
  <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAAKUlEQVR4nO3NMQEAAAjDMMC/MGRhgn2pgKa3sk34DwAAAAAAAAAAAN46CP0BCMDA+XQAAAAASUVORK5CYII=" alt="Ikon" />
  <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIwAAAAeCAIAAABxDGEhAAABdElEQVR4nO3ZMWvCYBSF4ZvQRltLoUsrFIeCUFIQERrFTdz9EU4qgji4+j8cHNyym13i5hYQxclKi4OUiiLFqjWxQ4rgFB3SevE8U0wcDrz4CSoQtQiOm/jfA8AZIjGASAwgEgOIxAAiMeAcaT5XdF1uNp8MI5RK3RDRdPpsPwoEJMMI+f3n7m48eWeO71itNolEj4jC4ct6/VHTJvZ9r1dU1WAuNxiNvt3dePIOOO7a7fl6vdm+rFQearWPVuvThVWw44BIyeR1sfhqXxcK/sXCqlbf3VkFO5yPO0kSdF32eERF8TUaM02bSJKQz9/1el9/sA9on0+S/Z0Uj3cjkU40ekVEprlRlI7PJ2azt+4vhEOOu/F43e8viMg0aTYz0+mXcvleli9c2wa/9j3uLIuIKJMZbO8Ph6tS6U1Vg7FYd7m03JsIAv6qOH74xYEBRGIAkRhAJAYQiQFEYgCRGEAkBhCJAURiAJEYQCQGEIkBRGLgB064ZKDo/EQ8AAAAAElFTkSuQmCC" alt="Logo" />
</p>

Bilagskontroll er et skrivebordverktøy for å kontrollere leverandørbilag. Programmet gir et grafisk brukergrensesnitt for å trekke tilfeldige bilagsutvalg, gjennomgå hvert bilag og generere en rapport.

Programmet er skrevet i Python og bruker `pandas` til å lese og filtrere Excel‑data, `customtkinter` for et moderne og responsivt grensesnitt og `reportlab` for å lage PDF‑rapporter.

## Struktur

| Fil | Beskrivelse |
| --- | ----------- |
| `bilagskontroll.py` | Startfil som åpner GUI‑applikasjonen |
| `gui/__init__.py`    | `App`‑klassen og sammensetting av grensesnittet |
| `gui/sidebar.py`     | Sidepanel med filvalg og innstillinger |
| `gui/mainview.py`    | Hovedvisning for kontroll av bilag |
| `gui/ledger.py`      | Viser bilagslinjer fra hovedboken |
| `data_utils.py`      | Data- og beregningslogikk |
| `helpers.py`         | Hjelpefunksjoner for tekst, tall og kolonnevalg |
| `report.py`          | Generering av PDF‑rapport |
| `report_utils.py`    | Hjelpefunksjoner for PDF‑rapporten |

## Funksjoner

- Moderne GUI basert på CustomTkinter og Tkinter
- Vindustittel “Bilagskontroll BETA v4” for enkel identifikasjon
- Trekker et tilfeldig utvalg av bilag og registrerer antall bilag i datakilden
- Viser bilagslinjer fra hovedboken for valgt faktura
- Hurtiglenke som åpner fakturaen i PowerOffice direkte fra appen
- Eksport av en PDF‑rapport med status og detaljert informasjon for hvert bilag
- Deaktiverer navigasjonsknappene ved første og siste bilag for å hindre ugyldig navigering
- Validerer tallfelt i grensesnittet for å sikre gyldige inputverdier
- PDF‑rapporten viser tidspunkt for når den ble generert

## Avhengigheter

- Python 3.x
- [pandas](https://pypi.org/project/pandas/) – leser og håndterer Excel‑data
- [customtkinter](https://pypi.org/project/customtkinter/) – gir et moderne brukergrensesnitt
- [reportlab](https://pypi.org/project/reportlab/) – genererer PDF‑rapporten

## Installasjon

```bash
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate på Windows
pip install pandas customtkinter reportlab
```

## Bruk

1. Start programmet:
   ```bash
   python bilagskontroll.py
   ```
2. Velg Excel-fil(er) for bilag og hovedbok.
3. Angi størrelse på utvalg og år, og trykk **🎲 Lag utvalg**.
4. Gå gjennom hvert bilag, marker status og legg inn eventuelle kommentarer.
5. Eksporter PDF-rapport når kontrollen er ferdig.

## Bidra

Bidrag og forslag til forbedringer er velkomne. Lag gjerne en pull request med en kort beskrivelse av endringen.

## Lisens
Prosjektet er lisensiert under MIT-lisensen.
