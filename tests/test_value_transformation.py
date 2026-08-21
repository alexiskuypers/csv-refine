import pytest
from email_validator import validate_email, EmailNotValidError
from decimal import Decimal, DecimalException
from data_contract_cli.value_transformations import (
    convert_str_to_int,
    convert_str_to_decimal,
    convert_str_to_bool,
    validate_str,
    validate_email_value,
    validate_date,
    normalize_date,
)


@pytest.mark.parametrize(
    "valid_values, expected",
    [
        ("5  ", 5),
        ("  -5", -5),
        (" 0 ", 0),
    ],
)
def test_convert_str_to_int_returns_int(valid_values, expected):
    result = convert_str_to_int(valid_values)
    assert result == expected


@pytest.mark.parametrize(
    "invalid_values",
    [
        "10.00",
        "1 0",
    ],
)
def test_raises_convert_str_to_int(invalid_values):
    with pytest.raises(ValueError):
        convert_str_to_int(invalid_values)


@pytest.mark.parametrize(
    "valid_values, expected",
    [
        ("5  ", Decimal("5")),
        ("  -5", Decimal("-5")),
        (" 0 ", Decimal("0")),
        ("0.24  ", Decimal("0.24")),
    ],
)
def test_convert_str_to_decimal_returns_decimal(valid_values, expected):
    result = convert_str_to_decimal(valid_values)
    assert result == expected


@pytest.mark.parametrize(
    "invalid_values",
    [
        "a-10.00",
        "1 0",
    ],
)
def test_raises_convert_str_to_decimal(invalid_values):
    with pytest.raises(DecimalException):
        convert_str_to_decimal(invalid_values)


@pytest.mark.parametrize(
    "valid_values, expected",
    [
        ("yEs", True),
        ("y", True),
        ("1", True),
        ("true", True),
        ("no ", False),
        ("n ", False),
        ("0", False),
        ("fAlse", False),
    ],
)
def test_convert_str_to_bool_returns_bool(valid_values, expected):
    result = convert_str_to_bool(valid_values)
    assert result == expected


@pytest.mark.parametrize(
    "invalid_values",
    [
        "tr ue",
        "2",
        " ",
        "",
    ],
)
def test_raises_convert_str_to_bool(invalid_values):
    with pytest.raises(ValueError):
        convert_str_to_bool(invalid_values)


def test_validate_str_accepts_str():
    validate_str("test")
    validate_str(" ")
    validate_str("1")
    validate_str("true")


@pytest.mark.parametrize("invalid_values", [1, True, 15.4, ["5"]])
def test_raises_validate_str(invalid_values):
    with pytest.raises(ValueError):
        validate_str(invalid_values)


def test_validate_email_value_returns_mail():
    content = "  test@gmail.com  "
    result = validate_email_value(content)
    assert result == "test@gmail.com"


@pytest.mark.parametrize(
    "invalid_mail",
    ["test@@gmail.com", "testgmail.com", "test @gmail.com", "test@gmailcom"],
)
def test_raises_validate_email_value(invalid_mail):
    with pytest.raises(EmailNotValidError):
        validate_email_value(invalid_mail)


@pytest.mark.parametrize(
    "valid_date, date_format, expected",
    [
        ("20/10/2010 ", "%d/%m/%Y", "20/10/2010"),
        ("2010/10/20", "%Y/%m/%d", "2010/10/20"),
        (" 20-10-2010", "%d-%m-%Y", "20-10-2010"),
        ("2010-10-20", "%Y-%m-%d", "2010-10-20"),
    ],
)
def test_validate_date_returns_string(valid_date, date_format, expected):
    result = validate_date(valid_date, date_format)
    assert result == expected


@pytest.mark.parametrize(
    "invalid_date, date_format",
    [
        ("12/06", "%d/%m/%Y"),
        ("12_06/2020", "%d/%m/%Y"),
        ("31/02/2005", "%d/%m/%Y"),
    ],
)
def test_raises_validate_date(invalid_date, date_format):
    with pytest.raises(ValueError):
        validate_date(invalid_date, date_format)


@pytest.mark.parametrize(
    "valid_date, date_format, expected",
    [
        ("20/10/2010 ", "%d/%m/%Y", "2010-10-20"),
        ("2010/10/20", "%Y/%m/%d", "2010-10-20"),
        (" 20-10-2010", "%d-%m-%Y", "2010-10-20"),
        ("2010-10-20", "%Y-%m-%d", "2010-10-20"),
    ],
)
def test_normalize_date_returns_isoformat(valid_date, date_format, expected):
    result = normalize_date(valid_date, date_format)
    assert result == expected
