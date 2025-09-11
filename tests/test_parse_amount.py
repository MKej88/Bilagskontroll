from helpers import parse_amount


def test_parse_amount_parenteser():
    assert parse_amount("(123)") == -123.0
    assert parse_amount("(123,45)") == -123.45
