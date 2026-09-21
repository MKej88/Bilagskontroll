# Bilagskontroll

Bilagskontroll er et skrivebordverktøy skrevet i ren Python for å kontrollere leverandørbilag. Applikasjonen tilbyr et moderne CustomTkinter-grensesnitt som hjelper deg å trekke tilfeldige bilagsutvalg, kontrollere hvert enkelt bilag og dokumentere funnene i en rapport.

## Oversikt

- Last inn fakturalister og hovedbok fra Excel.
- Trekk et tilfeldig utvalg av bilag og få oversikt over hvor mange bilag som finnes i datagrunnlaget.
- Gå gjennom hvert bilag, registrer status, legg inn kommentarer og åpne den originale fakturaen direkte fra appen.
- Se bilagslinjer fra hovedboken for valgt faktura og summer netto-beløp både for utvalget og for hele datagrunnlaget.
- Eksporter en PDF-rapport som dokumenterer resultatet av kontrollen og logg hendelser til disk.

## Viktige funksjoner

- Moderne og responsivt brukergrensesnitt bygget med CustomTkinter.
- Automatisk gjenkjenning av kolonner for fakturanummer og nettobeløp.
- Fremhever statuskortet med tydelige farger for godkjent og ikke godkjent.
- Hurtiglenke som åpner fakturaen i PowerOffice direkte fra appen.
- Drag-og-slipp av filer med tilhørende ventedialog ved lasting.
- Kolonnebredder i hovedboken tilpasser seg vindusstørrelsen og støtter mørk modus.
- PDF-rapport med tidsstempel og detaljerte summer for hvert bilag.
- Logger hendelser i `logs/` og oppretter loggkatalogen automatisk.

## Teknologier og avhengigheter

- Python 3.10 eller nyere
- [pandas](https://pypi.org/project/pandas/) – lesing og filtrering av Excel-data
- [openpyxl](https://pypi.org/project/openpyxl/) – effektiv filsupport for Excel
- [customtkinter](https://pypi.org/project/customtkinter/) – moderne GUI-komponenter
- [tkinterdnd2](https://pypi.org/project/tkinterdnd2/) – valgfri dra-og-slipp støtte
- [reportlab](https://pypi.org/project/reportlab/) – generering av PDF-rapporter
- [pytest](https://pypi.org/project/pytest/) – kjøres for å teste prosjektet under utvikling

## Kom i gang

### Oppsett av miljø

1. Sørg for at Python er installert (`python --version`).
2. Lag et virtuelt miljø og installer avhengigheter:

   ```bash
   python -m venv venv
   source venv/bin/activate  # venv\Scripts\activate på Windows
   pip install -U pip
   pip install pandas openpyxl customtkinter tkinterdnd2 reportlab pytest
   ```

### Starte applikasjonen

1. Aktiver det virtuelle miljøet hvis det ikke allerede er aktivt.
2. Start programmet:

   ```bash
   python bilagskontroll.py
   ```
3. Velg Excel-fil(er) for bilag og hovedbok.
4. Angi størrelse på utvalg og år, og trykk **🎲 Lag utvalg**.
5. Gå gjennom hvert bilag, marker status og legg inn eventuelle kommentarer.
6. Eksporter PDF-rapport når kontrollen er ferdig.

### Bygge Windows-program

GitHub Actions kan bygge en ferdig `Bilagskontroll.exe` uten at Python må være
installert på Windows-maskinen som skal bruke programmet:

1. Åpne fanen **Actions** i GitHub.
2. Velg arbeidsflyten **Build Windows EXE**.
3. Trykk **Run workflow** og vent til byggingen er ferdig.
4. Last ned `Bilagskontroll-Windows` under **Artifacts** på den fullførte
   kjøringen. ZIP-filen inneholder `Bilagskontroll.exe` og støttemappen `_internal`.
5. Velg **Pakk ut alle** og legg hele innholdet i en fast mappe på PC-en.
6. Start `Bilagskontroll.exe` fra den utpakkede mappen. Du kan opprette en
   snarvei til EXE-filen på skrivebordet.

**Behold `_internal` ved siden av EXE-filen.** Ikke flytt bare EXE-filen eller
start den direkte fra ZIP-filen. Ved oppdatering pakkes hele den nye ZIP-filen
ut i en ny mappe, og eventuell snarvei oppdateres.

Programmet bygges som en programmappe (`--onedir`) for raskere oppstart.
Tidligere ble det bygget som én selvutpakkende fil (`--onefile`), som måtte
pakke ut støttefilene til en midlertidig mappe ved hver start. Denne utpakkingen
unngås nå. Faktisk oppstartstid avhenger fortsatt av PC, lagringssted og antivirus.
Se [PyInstallers beskrivelse av pakkemetodene](https://pyinstaller.org/en/stable/operating-mode.html#how-the-one-file-program-works).

Byggingen kontrollerer at EXE-filen viser et vindu og fortsetter å kjøre.
Tid til første vindu vises i kjøringens oppsummering i GitHub Actions; dette er
en måling på byggemaskinen, ikke en garanti for oppstartstiden på din PC.

Arbeidsflyten kjører også automatisk når det opprettes en Git-tag som begynner
med `v`, for eksempel `v1.0.0`. Byggeresultatet er tilgjengelig i 14 dager.

### Konfigurasjon

- **`settings.py`** kan brukes til å overstyre standardinnstillinger, f.eks. `UI_SCALING` for å endre skalering på høyoppløselige skjermer.
- **`helpers_path.resource_path`** hjelper applikasjonen å finne ressurser (for eksempel ikoner) både i utvikling og når programmet pakkes til et kjørbart format.

### Loggfiler

Loggeren er konfigurert i `helpers.py` og skriver til `logs/bilagskontroll.log`. Katalogen opprettes automatisk hvis den ikke finnes.

## Prosjektstruktur

```
.
├── bilagskontroll.py        # Inngangspunkt som starter GUI-applikasjonen
├── data_utils.py            # Laster Excel-data og utfører beregninger
├── helpers.py               # Tekstformatering, logikk for tall og logging
├── helpers_path.py          # Håndtering av ressursstier ved pakking
├── report.py                # Sammensetting av PDF-rapport
├── report_utils.py          # Hjelpefunksjoner for rapportgenerering
├── settings.py              # Valgfrie brukerinnstillinger
├── gui/
│   ├── __init__.py          # App-klassen og hovedkomponentene i GUI-et
│   ├── sidebar.py           # Sidepanel for filvalg og utvalg
│   ├── mainview.py          # Hovedvisningen med statuskort og detaljer
│   ├── ledger.py            # Viser hovedbokslinjer for valgt bilag
│   ├── dropzone.py          # Dra-og-slipp logikk for filer
│   ├── busy.py              # Ventedialog når data lastes
│   └── style.py             # Felles farger, fonter og spacing-konstanter
├── icons/                   # Ikoner brukt i applikasjonen
├── logs/                    # Loggfiler genereres her
├── tests/                   # Pytest-baserte enhetstester
└── README.md
```

## Utvikling og testing

Kjør enhetstestene før du leverer endringer:

```bash
pytest
```

Testene dekker blant annet lasting av hovedbok, summering av netto-beløp, statuskort-logikk og logging.

GitHub Actions kjører automatisk de samme testene med Python 3.10 og 3.13 ved
hver endring og pull request. Dermed oppdages testfeil og problemer med støttede
Python-versjoner før en endring blir slått sammen.

## Versjonsnotater

Se `CHANGELOG.md` for en detaljert oversikt over endringer mellom versjoner.

## Bidra

Forslag til forbedringer og feilrapporter er velkomne. Opprett gjerne en issue eller send inn en pull request med en kort beskrivelse av endringen.

## Lisens

Prosjektet er lisensiert under MIT-lisensen.
