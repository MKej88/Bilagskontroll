import re
from typing import Optional, List

import pandas as pd

from helpers import parse_amount


FALLBACK_NET_COLUMNS: List[str] = [
    "Beløp",
    "Belop",
    "Total",
    "Sum",
    "Nettobeløp",
    "Netto beløp",
    "Beløp eks mva",
]


def load_invoice_df(path: str, header_idx: int = 4) -> pd.DataFrame:
    """Leser fakturalisten fra Excel."""
    return pd.read_excel(path, engine="openpyxl", header=header_idx)


def load_gl_df(path: str) -> pd.DataFrame:
    """Leser hovedboken fra Excel."""
    gl = pd.read_excel(path, engine="openpyxl", header=0)
    if sum(str(c).lower().startswith("unnamed") for c in gl.columns) > len(gl.columns) / 2:
        gl = pd.read_excel(path, engine="openpyxl", header=4)
    return gl


def extract_customer_from_invoice_file(path: str) -> Optional[str]:
    """
    Leser rad 2 i fakturalista og prøver å hente ut kundenavn.

    Strategi:
      - Søk etter mønster "Kunde: <navn>" eller "Customer: <navn>" i rad 2
      - Hvis ikke funn, velg lengste ikke-numeriske tekstcelle i rad 2
    """
    try:
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


def row_has_sum_word(row: pd.Series) -> bool:
    for v in row.values:
        if isinstance(v, str) and re.search(r"\bsum\b", v, re.IGNORECASE):
            return True
    return False


def calc_sum_kontrollert(sample_df: Optional[pd.DataFrame], decisions: list, net_amount_col: Optional[str]) -> float:
    if sample_df is None:
        return 0.0
    total = 0.0
    for i, d in enumerate(decisions):
        if d is None:
            continue
        row = sample_df.iloc[i]
        val = None
        if net_amount_col and net_amount_col in sample_df.columns:
            val = parse_amount(row.get(net_amount_col))
        if val is None:
            for fb in FALLBACK_NET_COLUMNS:
                if fb in sample_df.columns:
                    val = parse_amount(row.get(fb))
                    if val is not None:
                        break
        if val is not None:
            total += val
    return total


def calc_sum_net_all(df: Optional[pd.DataFrame], net_amount_col: Optional[str]) -> float:
    if df is None or df.dropna(how="all").empty:
        return 0.0
    df_eff = df.dropna(how="all").copy()
    if len(df_eff) > 0:
        df_eff = df_eff.iloc[:-1]
    df_eff = df_eff.loc[~df_eff.apply(row_has_sum_word, axis=1)]
    col = net_amount_col if (net_amount_col in df_eff.columns) else None
    total = 0.0
    for _, r in df_eff.iterrows():
        v = parse_amount(r.get(col)) if col else None
        if v is None:
            for fb in FALLBACK_NET_COLUMNS:
                if fb in df_eff.columns:
                    v = parse_amount(r.get(fb))
                    if v is not None:
                        break
        if v is not None:
            total += v
    return total

