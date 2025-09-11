import pandas as pd
from data_utils import calc_sum_net_all


def test_calc_sum_net_all_uten_summeringsrad():
    df = pd.DataFrame({
        'tekst': ['rad1', 'rad2', None],
        'netto': [100.0, 200.0, 0.0]
    })
    df['_netto_float'] = df['netto']
    assert calc_sum_net_all(df) == 300.0


def test_calc_sum_net_all_med_summeringsrader():
    df = pd.DataFrame({
        'tekst': ['rad1', 'Sum', 'rad2', 'SUM'],
        'netto': [100.0, 999.0, 200.0, 300.0]
    })
    df['_netto_float'] = df['netto']
    assert calc_sum_net_all(df) == 300.0


def test_calc_sum_net_all_kun_summeringsrad():
    df = pd.DataFrame({
        'tekst': ['Sum'],
        'netto': [123.0]
    })
    df['_netto_float'] = df['netto']
    assert calc_sum_net_all(df) == 0.0


def test_calc_sum_net_all_beholder_siste_rad_uten_sum():
    df = pd.DataFrame({
        'tekst': ['rad1', 'rad2', 'rad3'],
        'netto': [100.0, 200.0, 300.0]
    })
    df['_netto_float'] = df['netto']
    assert calc_sum_net_all(df) == 600.0


def test_calc_sum_net_all_med_sum_i_annen_kolonne():
    df = pd.DataFrame({
        'tekst': ['rad1', 'rad2'],
        'kommentar': ['ok', 'sum her'],
        'netto': [100.0, 200.0]
    })
    df['_netto_float'] = df['netto']
    assert calc_sum_net_all(df) == 100.0
