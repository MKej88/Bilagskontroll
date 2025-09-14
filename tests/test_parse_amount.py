from decimal import Decimal
from helpers import parse_amount


def test_parse_amount_parenteser():
    assert parse_amount("(123)") == Decimal("-123")
    assert parse_amount("(123,45)") == Decimal("-123.45")
