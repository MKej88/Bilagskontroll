# Bilagskontroll

Bilagskontroll er et skrivebordverktøy for å kontrollere leverandørbilag. Programmet gir et grafisk brukergrensesnitt for å trekke tilfeldige bilagsutvalg, gjennomgå hvert bilag og generere en rapport.

Programmet er skrevet i Python og bruker `pandas` til å lese og filtrere Excel‑data, `customtkinter` for et moderne og responsivt grensesnitt og `reportlab` for å lage PDF‑rapporter.

## Struktur

| Fil | Beskrivelse |
| --- | ----------- |
| `Bilagskontroll v1.py` | Startfil som åpner GUI‑applikasjonen |
| `gui.py`              | All GUI‑logikk og `App`‑klassen |
| `helpers.py`          | Hjelpefunksjoner for tekst, tall og kolonnevalg |
| `report.py`           | Generering av PDF‑rapport |

## Funksjoner

- Moderne GUI basert på CustomTkinter og Tkinter
- Vindustittel “Bilagskontroll BETA v4” for enkel identifikasjon
- Trekker et tilfeldig utvalg av bilag og registrerer antall bilag i datakilden
- Hurtiglenke som åpner fakturaen i PowerOffice direkte fra appen
- Eksport av en PDF‑rapport med status og detaljert informasjon for hvert bilag

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

(Angi gjeldende lisens for prosjektet)
