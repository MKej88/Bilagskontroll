from __future__ import annotations

import re
from typing import Optional, List

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
    finnes i de øverste radene av filen.
    """
    logger.info(f"Laster fakturaliste fra {path}")
    pd = _pd()
    raw = pd.read_excel(
        path,
        engine="openpyxl",
        header=None,
        dtype=str,
        engine_kwargs={"read_only": True},
    )
    kunde = extract_customer_from_invoice_file(df=raw)
    df = raw.iloc[header_idx + 1 :].reset_index(drop=True)
    df.columns = raw.iloc[header_idx]
    return df, kunde


def load_gl_df(path: str, nrows: int = 10) -> pd.DataFrame:
    """Leser hovedboken fra Excel.

    Leser et lite antall rader med ``openpyxl`` for å finne riktig header og
    leser deretter hele filen én gang med ``pandas``.
    """
    logger.info(f"Laster hovedbok fra {path}")
    import openpyxl

    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb.active
    header_idx = 0
    for i, row in enumerate(ws.iter_rows(min_row=1, max_row=nrows, values_only=True)):
        if not row:
            continue
        non_empty = sum(1 for c in row if c not in (None, ""))
        if non_empty > len(row) / 2:
            header_idx = i
            break
    wb.close()

    pd = _pd()
    return pd.read_excel(
        path,
        engine="openpyxl",
        header=header_idx,
        dtype=str,
        engine_kwargs={"read_only": True},
    )


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
    except Exception:
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




def _net_amount_from_row(row: pd.Series, net_amount_col: Optional[str]) -> Optional[float]:
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


def calc_sum_kontrollert(sample_df: Optional[pd.DataFrame], decisions: list) -> float:
    """Summer netto-beløp for rader som er kontrollert."""
    if sample_df is None or "_netto_float" not in sample_df.columns:
        return 0.0
    import pandas as pd

    dec_ser = pd.Series(decisions).reindex(sample_df.index)
    mask = dec_ser.notna()
    return float(sample_df.loc[mask, "_netto_float"].sum())


def calc_sum_net_all(df: Optional[pd.DataFrame], skip_last: bool = True) -> float:
    """Summer netto-beløp for alle rader i ``df``."""
    if df is None or df.dropna(how="all").empty or "_netto_float" not in df.columns:
        return 0.0
    df_eff = df.dropna(how="all").copy()
    if skip_last and len(df_eff) > 0:
        last_row = df_eff.iloc[-1].astype(str)
        if last_row.str.contains(r"\bsum\b", case=False).any():
            df_eff = df_eff.iloc[:-1]
    mask = ~df_eff.astype(str).apply(
        lambda c: c.str.contains(r"\bsum\b", case=False, na=False)
    ).any(axis=1)
    return float(df_eff.loc[mask, "_netto_float"].sum())

