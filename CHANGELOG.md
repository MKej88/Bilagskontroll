# CHANGELOG

## 1.0.3

### Endringer
- Programmet heter nå "Bilagskontroll" (tidligere "Bilagskontroll v1").
- Vindustittel oppdatert til det nye navnet.

### Dokumentasjon
- README oppdatert med nytt programnavn.

## 1.0.2

### Dokumentasjon
- Lagt til seksjon om versjonsnotater i README som viser til `CHANGELOG.md`.

## 1.0.1

### Dokumentasjon
- Oppdatert README med lisensinformasjon og oversikt over `data_utils.py` og `report_utils.py`.

## 1.0

### Viktige endringer
- Programmet er tatt ut av beta og har nå navnet "Bilagskontroll v1"
- Startfilen har fått nytt navn og importene er delt opp for tydeligere oppstart
- Koden er strukturert i modulene `gui.py`, `helpers.py` og `report.py` for bedre oversikt og gjenbruk
- README er utvidet med modulstruktur, prosjektbeskrivelse og avhengigheter, noe som gjør det enklere å forstå prosjektet og komme i gang

### Funksjoner
- Moderne GUI basert på CustomTkinter og Tkinter
- Vindustittel "Bilagskontroll v1" for enkel identifikasjon
- Trekker et tilfeldig utvalg av bilag og registrerer antall bilag i datakilden
- Hurtiglenke som åpner faktura i PowerOffice direkte fra appen
- Eksport av PDF-rapport med status og detaljer per bilag

### Avhengigheter
- Python 3.x, pandas, customtkinter og reportlab kreves for å kjøre applikasjonen

