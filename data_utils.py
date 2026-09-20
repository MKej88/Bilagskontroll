from __future__ import annotations

import re
from typing import Optional, List
from decimal import Decimal

from helpers import parse_amount, logger


FALLBACK_NET_COLUMNS: List[str] = [
    "Beløp",
    "Belop",
    "Total",
    "Sum",
    "Nettobeløp",
    "Netto beløp",
    "Beløp eks mva",
]


def _pd():
    import pandas as pd
    return pd


def load_invoice_df(path: str, header_idx: int = 4) -> tuple[pd.DataFrame, Optional[str]]:
    """Leser fakturalisten fra Excel og henter også kundenavn.

    Returnerer en tupel med ``DataFrame`` og eventuelt kundenavn hvis dette
    finnes i de øverste radene av filen. ``openpyxl``-radene bygges direkte
    om til en dataramme. Det unngår den ekstra konverteringen i
    ``pandas.read_excel``, som er merkbar for store fakturalister.
    """
    logger.info(f"Laster fakturaliste fra {path}")
    pd = _pd()
    from openpyxl import load_workbook

    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        raw = pd.DataFrame(workbook.active.values, dtype=str)
    finally:
        workbook.close()

    kunde = extract_customer_from_invoice_file(df=raw)
    df = raw.iloc[header_idx + 1 :].reset_index(drop=True)
    df.columns = raw.iloc[header_idx]
    return df, kunde


def load_gl_df(path: str, nrows: int = 10) -> pd.DataFrame:
    """Leser hovedboken fra Excel.

    Leser arbeidsarket én gang og finner riktig header blant de første radene.

    Tidligere åpnet vi samme arbeidsbok først med ``openpyxl`` for å finne
    headeren og deretter på nytt med ``pandas``. Åpning og tolking av en stor
    Excel-fil er en vesentlig del av ventetiden, så headeren oppdages nå i den
    allerede innleste datarammen.
    """
    logger.info(f"Laster hovedbok fra {path}")
    pd = _pd()
    raw = pd.read_excel(
        path,
        engine="openpyxl",
        header=None,
        dtype=str,
        engine_kwargs={"read_only": True},
    )

    header_idx = 0
    for i in range(min(nrows, len(raw))):
        row = raw.iloc[i]
        if row.notna().sum() > len(row) / 2:
            header_idx = i
            break

    columns = _excel_column_names(raw.iloc[header_idx].tolist())
    df = raw.iloc[header_idx + 1 :].reset_index(drop=True)
    df.columns = columns
    return df


def _excel_column_names(values: list) -> list[str]:
    """Lag samme type unike kolonnenavn som ``read_excel(header=...)``."""
    pd = _pd()
    names = [
        f"Unnamed: {index}" if pd.isna(value) else str(value)
        for index, value in enumerate(values)
    ]
    reserved = set(names)
    result: list[str] = []
    occurrences: dict[str, int] = {}
    for name in names:
        occurrence = occurrences.get(name, 0)
        candidate = name
        while candidate in result:
            occurrence += 1
            candidate = f"{name}.{occurrence}"
            while candidate in reserved:
                occurrence += 1
                candidate = f"{name}.{occurrence}"
        occurrences[name] = occurrence
        result.append(candidate)
    return result


def extract_customer_from_invoice_file(
    path: Optional[str] = None, df: Optional[pd.DataFrame] = None
) -> Optional[str]:
    """
    Leser rad 2 i fakturalista og prøver å hente ut kundenavn.

    Strategi:
      - Søk etter mønster "Kunde: <navn>" eller "Customer: <navn>" i rad 2
      - Hvis ikke funn, velg lengste ikke-numeriske tekstcelle i rad 2

    Parameter ``df`` kan oppgis for å unngå ny fillesing.
    """
    logger.info(
        f"Henter kundenavn fra {path}" if path else "Henter kundenavn fra DataFrame"
    )
    try:
        pd = _pd()
        if df is None:
            if path is None:
                return None
            df = pd.read_excel(path, engine="openpyxl", header=None, nrows=2)
        else:
            df = df.head(2)
    except (OSError, ValueError):
        logger.exception("Kunne ikke lese kundedata")
        return None
    if df is None or len(df) < 2:
        return None
    row2 = df.iloc[1].fillna("")
    # Direkte mønster "Kunde: X"
    for v in row2.values:
        s = str(v).strip()
        m = re.match(r"^\s*(Kunde|Customer)\s*[:\-]\s*(.+)$", s, flags=re.IGNORECASE)
        if m:
            return m.group(2).strip()
    # Velg den lengste tekstcellen som ikke ser ut som tall/dato
    candidates = []
    for v in row2.values:
        s = str(v).strip()
        if not s:
            continue
        if re.fullmatch(r"[\d\s\.,:/-]+", s):
            continue
        # unngå typiske etiketter
        if re.search(r"faktura|liste|dato|org|orgnr|organisasjonsnummer|periode|rapport|utvalg", s, re.IGNORECASE):
            continue
        candidates.append(s)
    if candidates:
        return max(candidates, key=len)
    return None




def _net_amount_from_row(row: pd.Series, net_amount_col: Optional[str]) -> Optional[Decimal]:
    """Hent netto beløp fra raden ved å sjekke prioriterte kolonner."""
    cols = []
    if net_amount_col:
        cols.append(net_amount_col)
    cols.extend(c for c in FALLBACK_NET_COLUMNS if c != net_amount_col)
    for col in cols:
        if col in row:
            val = parse_amount(row.get(col))
            if val is not None:
                return val
    return None


def calculate_net_amounts(
    df: pd.DataFrame, net_amount_col: Optional[str]
) -> pd.Series:
    """Beregn nettobeløp kolonnevis, med samme reservekolonner som før.

    Bare rader som ikke ga et gyldig beløp i en prioritert kolonne sendes
    videre til neste reservekolonne. Det unngår kostnaden ved å opprette en
    komplett ``Series`` for hver rad i store fakturalister.
    """
    pd = _pd()
    prioritized_columns = []
    if net_amount_col:
        prioritized_columns.append(net_amount_col)
    prioritized_columns.extend(
        column
        for column in FALLBACK_NET_COLUMNS
        if column not in prioritized_columns
    )

    amounts = pd.Series(None, index=df.index, dtype=object)
    for column in prioritized_columns:
        if column not in df.columns:
            continue
        missing = amounts.isna()
        if not missing.any():
            break
        amounts.loc[missing] = df.loc[missing, column].map(parse_amount)
    return amounts


def calc_sum_kontrollert(sample_df: Optional[pd.DataFrame], decisions: list) -> Decimal:
    """Summer netto-beløp for rader som er kontrollert."""
    if sample_df is None or "_netto_float" not in sample_df.columns:
        return Decimal("0")
    import pandas as pd

    dec_ser = pd.Series(decisions).reindex(sample_df.index)
    mask = dec_ser.notna()
    vals = sample_df.loc[mask, "_netto_float"].dropna().tolist()
    return sum(vals, Decimal("0"))


def calc_sum_net_all(df: Optional[pd.DataFrame], skip_last: bool = True) -> Decimal:
    """Summer netto-beløp for alle rader i ``df``."""
    if df is None or "_netto_float" not in df.columns:
        return Decimal("0")
    pd = _pd()
    df_eff = df.dropna(how="all")
    if df_eff.empty:
        return Decimal("0")
    sum_pattern = re.compile(r"\bsum\b", re.IGNORECASE)
    if skip_last and len(df_eff) > 0:
        last_row = df_eff.iloc[-1].astype(str)
        if last_row.str.contains(sum_pattern).any():
            df_eff = df_eff.iloc[:-1]

    # Sjekk kolonnene fortløpende. Den tidligere stack-operasjonen laget en
    # stor, midlertidig serie med alle cellene og forsinket visning av innlest
    # innhold merkbart for store fakturalister.
    has_sum = pd.Series(False, index=df_eff.index)
    for column in df_eff.columns:
        has_sum |= (
            df_eff[column]
            .fillna("")
            .astype(str)
            .str.contains(sum_pattern, na=False)
        )

    values = df_eff.loc[~has_sum, "_netto_float"].dropna()
    return sum(values, Decimal("0"))
