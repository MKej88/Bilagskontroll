from decimal import Decimal

import pandas as pd

from data_utils import calc_sum_kontrollert


def test_calc_sum_kontrollert_utelater_bilag_som_gjenstar():
    sample_df = pd.DataFrame(
        {
            "_netto_float": [
                Decimal("100.50"),
                Decimal("900.00"),
                Decimal("25.25"),
            ]
        }
    )
    decisions = ["Godkjent", None, "Ikke godkjent"]

    assert calc_sum_kontrollert(sample_df, decisions) == Decimal("125.75")
