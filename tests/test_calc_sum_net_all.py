import pandas as pd
from decimal import Decimal
from data_utils import calc_sum_net_all


def test_calc_sum_net_all_uten_summeringsrad():
    df = pd.DataFrame({
        'tekst': ['rad1', 'rad2', None],
        'netto': [Decimal('100'), Decimal('200'), Decimal('0')]
    })
    df['_netto_float'] = df['netto']
    assert calc_sum_net_all(df) == Decimal('300')


def test_calc_sum_net_all_med_summeringsrader():
    df = pd.DataFrame({
        'tekst': ['rad1', 'Sum', 'rad2', 'SUM'],
        'netto': [Decimal('100'), Decimal('999'), Decimal('200'), Decimal('300')]
    })
    df['_netto_float'] = df['netto']
    assert calc_sum_net_all(df) == Decimal('300')


def test_calc_sum_net_all_kun_summeringsrad():
    df = pd.DataFrame({
        'tekst': ['Sum'],
        'netto': [Decimal('123')]
    })
    df['_netto_float'] = df['netto']
    assert calc_sum_net_all(df) == Decimal('0')


def test_calc_sum_net_all_beholder_siste_rad_uten_sum():
    df = pd.DataFrame({
        'tekst': ['rad1', 'rad2', 'rad3'],
        'netto': [Decimal('100'), Decimal('200'), Decimal('300')]
    })
    df['_netto_float'] = df['netto']
    assert calc_sum_net_all(df) == Decimal('600')


def test_calc_sum_net_all_med_sum_i_annen_kolonne():
    df = pd.DataFrame({
        'tekst': ['rad1', 'rad2'],
        'kommentar': ['ok', 'sum her'],
        'netto': [Decimal('100'), Decimal('200')]
    })
    df['_netto_float'] = df['netto']
    assert calc_sum_net_all(df) == Decimal('100')
