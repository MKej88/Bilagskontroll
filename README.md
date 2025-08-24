# Bilagskontroll

Bilagskontroll er et skrivebordverktøy for å kontrollere leverandørbilag. Programmet gir et grafisk brukergrensesnitt for å trekke tilfeldige bilagsutvalg, gjennomgå hvert bilag og generere en rapport.

## Funksjoner

- Moderne GUI basert på CustomTkinter og Tkinter
- Vindustittel “Bilagskontroll BETA v4” for enkel identifikasjon
- Trekker et tilfeldig utvalg av bilag og registrerer antall bilag i datakilden
- Hurtiglenke som åpner fakturaen i PowerOffice direkte fra appen
- Eksport av en PDF‑rapport med status og detaljert informasjon for hvert bilag

## Avhengigheter

- Python 3.x  
- [pandas](https://pypi.org/project/pandas/)  
- [customtkinter](https://pypi.org/project/customtkinter/)  
- [reportlab](https://pypi.org/project/reportlab/) (for PDF‑eksport)

## Installasjon

```bash
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate på Windows
pip install pandas customtkinter reportlab
```

## Bruk

1. Start programmet:
   ```bash
   python "Bilagskontroll v1.py"
   ```
2. Velg Excel-fil(er) for bilag og hovedbok.
3. Angi størrelse på utvalg og år, og trykk **🎲 Lag utvalg**.
4. Gå gjennom hvert bilag, marker status og legg inn eventuelle kommentarer.
5. Eksporter PDF-rapport når kontrollen er ferdig.

## Bidra

Bidrag og forslag til forbedringer er velkomne. Lag gjerne en pull request med en kort beskrivelse av endringen.

## Lisens

(Angi gjeldende lisens for prosjektet)
