from decimal import Decimal

import pandas as pd

from data_utils import calculate_net_amounts


def test_calculate_net_amounts_uses_fallback_only_when_needed():
    df = pd.DataFrame(
        {
            "Nettobeløp": ["1 234,50", "ugyldig", None, "0"],
            "Beløp": ["9", "20,25", "ugyldig", "99"],
            "Total": ["8", "88", "30", "77"],
        }
    )

    result = calculate_net_amounts(df, "Nettobeløp")

    assert result.tolist() == [
        Decimal("1234.50"),
        Decimal("20.25"),
        Decimal("30"),
        Decimal("0"),
    ]


def test_calculate_net_amounts_preserves_index_and_missing_values():
    df = pd.DataFrame({"Beskrivelse": ["A", "B"]}, index=[4, 9])

    result = calculate_net_amounts(df, None)

    assert result.index.tolist() == [4, 9]
    assert result.isna().all()
