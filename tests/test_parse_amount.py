from decimal import Decimal
from helpers import parse_amount


def test_parse_amount_parenteser():
    assert parse_amount("(123)") == Decimal("-123")
    assert parse_amount("(123,45)") == Decimal("-123.45")


def test_parse_amount_med_norsk_tusenskilletegn():
    assert parse_amount("1.234,56") == Decimal("1234.56")
    assert parse_amount("1.234.567,89") == Decimal("1234567.89")


def test_parse_amount_med_engelsk_tusenskilletegn():
    assert parse_amount("1,234.56") == Decimal("1234.56")


def test_parse_amount_avviser_ugyldig_gruppering():
    assert parse_amount("1.2,3") is None


def test_parse_amount_takler_kreditbelop_med_minustegn_bak():
    assert parse_amount("1 234,50-") == Decimal("-1234.50")
