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


def _col_key(name: str) -> str:
    """Normaliser kolonnenavn for enklare samanlikning."""
    return re.sub(r"[^0-9a-zæøå]", "", str(name).lower())


def _make_usecols_filter(cols: Optional[List[str]]):
    if not cols:
        return None
    keys = [_col_key(c) for c in cols]

    def _matcher(col: str) -> bool:
        ck = _col_key(col)
        return any(k in ck for k in keys)

    return _matcher


def load_invoice_df(
    path: str, header_idx: int = 4, usecols: Optional[List[str]] = None
) -> pd.DataFrame:
    """Leser fakturalisten fra Excel."""
    logger.info(f"Laster fakturaliste fra {path}")
    pd = _pd()
    usecols_filter = _make_usecols_filter(usecols)
    return pd.read_excel(path, engine="openpyxl", header=header_idx, usecols=usecols_filter)


def load_gl_df(path: str, usecols: Optional[List[str]] = None) -> pd.DataFrame:
    """Leser hovedboken fra Excel."""
    logger.info(f"Laster hovedbok fra {path}")
    pd = _pd()
    usecols_filter = _make_usecols_filter(usecols)
    gl = pd.read_excel(path, engine="openpyxl", header=0, usecols=usecols_filter)
    if sum(str(c).lower().startswith("unnamed") for c in gl.columns) > len(gl.columns) / 2:
        gl = pd.read_excel(path, engine="openpyxl", header=4, usecols=usecols_filter)
    return gl


def extract_customer_from_invoice_file(path: str) -> Optional[str]:
    """
    Leser rad 2 i fakturalista og prøver å hente ut kundenavn.

    Strategi:
      - Søk etter mønster "Kunde: <navn>" eller "Customer: <navn>" i rad 2
      - Hvis ikke funn, velg lengste ikke-numeriske tekstcelle i rad 2
    """
    logger.info(f"Henter kundenavn fra {path}")
    try:
        pd = _pd()
        raw = pd.read_excel(path, engine="openpyxl", header=None, nrows=2)
    except Exception:
        return None
    if raw is None or len(raw) < 2:
        return None
    row2 = raw.iloc[1].fillna("")
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


def calc_sum_kontrollert(sample_df: Optional[pd.DataFrame], decisions: list, net_amount_col: Optional[str]) -> float:
    if sample_df is None:
        return 0.0
    total = 0.0
    for i, d in enumerate(decisions):
        if d is None:
            continue
        row = sample_df.iloc[i]
        val = _net_amount_from_row(row, net_amount_col)
        if val is not None:
            total += val
    return total


def calc_sum_net_all(
    df: Optional[pd.DataFrame],
    net_amount_col: Optional[str],
    skip_last: bool = True,
) -> float:
    if (
        df is None
        or df.dropna(how="all").empty
        or not net_amount_col
        or net_amount_col not in df.columns
    ):
        return 0.0
    df_eff = df.dropna(how="all").copy()
    if skip_last and len(df_eff) > 0:
        last_row = df_eff.iloc[-1].astype(str)
        if last_row.str.contains(r"\bsum\b", case=False).any():
            df_eff = df_eff.iloc[:-1]
    mask = ~df_eff.astype(str).apply(
        lambda c: c.str.contains(r"\bsum\b", case=False, na=False)
    ).any(axis=1)
    ser = df_eff.loc[mask, net_amount_col].apply(parse_amount)
    return ser.sum(skipna=True)

