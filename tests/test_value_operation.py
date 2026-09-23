import pytest
from email_validator import validate_email, EmailNotValidError
from datetime import date
from decimal import Decimal, DecimalException
from csv_refine.contract_models import Columns_Contract
from csv_refine.value_operation import (
    convert_str_to_int,
    convert_str_to_decimal,
    convert_str_to_bool,
    validate_str,
    validate_email_value,
    validate_date,
    normalize_date,
    format_decimal,
    remove_accents,
    apply_string_transformations,
    collapse_spaces,
    apply_max_length_rule,
    apply_min_length_rule,
    apply_regex_rule,
    apply_starts_with_rule,
    apply_ends_with_rule,
    apply_min_rule,
    apply_max_rule,
    apply_allowed_values_rule,
    process_value,
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
    with pytest.raises(TypeError):
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
        ("20/10/2010 ", "%d/%m/%Y", None),
        ("2010/10/20", "%Y/%m/%d", None),
        (" 20-10-2010", "%d-%m-%Y", None),
        ("2010-10-20", "%Y-%m-%d", None),
    ],
)
def test_validate_date_returns_None(valid_date, date_format, expected):
    result = validate_date(valid_date, date_format)
    assert result == expected


@pytest.mark.parametrize(
    "invalid_date, date_format, expected",
    [
        (
            "12/06",
            "%d/%m/%Y",
            "Date '12/06' is invalid or does not match the expected format '%d/%m/%Y'.",
        ),
        (
            "12_06/2020",
            "%d/%m/%Y",
            "Date '12_06/2020' is invalid or does not match the expected format '%d/%m/%Y'.",
        ),
        (
            "31/02/2005",
            "%d/%m/%Y",
            "Date '31/02/2005' is invalid or does not match the expected format '%d/%m/%Y'.",
        ),
    ],
)
def test_raises_validate_date(invalid_date, date_format, expected):
    result = validate_date(invalid_date, date_format)
    assert result == expected


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


@pytest.mark.parametrize(
    "value, expected",
    [
        ("5.5000", Decimal("5.50")),
        ("5.566", Decimal("5.57")),
        ("5.5550", Decimal("5.56")),
        ("5.1", Decimal("5.10")),
        ("5.544", Decimal("5.54")),
        ("-5.50", Decimal("-5.50")),
    ],
)
def test_format_decimal(value, expected):
    content = convert_str_to_decimal(value)
    result = format_decimal(content)
    assert result == expected


def test_remove_accents():
    content = "âàéèùôûäüöÉÈÇÊ€$"
    result = remove_accents(content)
    assert result == "aaeeuouauoEECE€$"


def test_collapse_spaces():
    content = "  test  ,  te st "
    result = collapse_spaces(content)
    assert result == " test , te st "


@pytest.mark.parametrize(
    "value, max_length, expected",
    [
        ("test", 5, None),
        (
            "test",
            3,
            f"Length of value: (test) is: '4', length max autorized is: 3",
        ),
        ("test", 4, None),
    ],
)
def test_apply_max_length_rule(value, max_length, expected):
    result = apply_max_length_rule(value, max_length)
    assert result == expected


@pytest.mark.parametrize(
    "value, min_length, expected",
    [
        ("test", 3, None),
        (
            "test",
            5,
            f"Length of value: (test) is: '4', length min autorized is: 5",
        ),
        ("test", 4, None),
    ],
)
def test_apply_min_length_rule(value, min_length, expected):
    result = apply_min_length_rule(value, min_length)
    assert result == expected


def test_apply_regex_rule():
    invoice_pattern = r"^INV-\d{3}$"
    content = "INV-001"
    result = apply_regex_rule(value=content, regex=invoice_pattern)
    assert result is None


def test_apply_regex_rule_invalid_case():
    invoice_pattern = r"^INV-\d{3}$"
    content = "invoice-001"
    result = apply_regex_rule(value=content, regex=invoice_pattern)
    assert isinstance(result, str)


@pytest.mark.parametrize(
    "value, start_whith, expected",
    [
        ("INV-001", "INV-0", None),
        (
            "INv -001",
            "INV-0",
            f"Value 'INv -001' does not match startwith pattern 'INV-0'.",
        ),
        ("INV", "INV-0", f"Value 'INV' does not match startwith pattern 'INV-0'."),
    ],
)
def test_apply_starts_with_rule(value, start_whith, expected):
    result = apply_starts_with_rule(value, start_whith)
    assert result == expected


@pytest.mark.parametrize(
    "value, ends_whith, expected",
    [
        ("test@gmail.com", "gmail.com", None),
        (
            "test@gmail.fr",
            "gmail.com",
            f"Value 'test@gmail.fr' does not match endswith pattern 'gmail.com'.",
        ),
        (
            "test@gmail.Com",
            "gmail.com",
            f"Value 'test@gmail.Com' does not match endswith pattern 'gmail.com'.",
        ),
    ],
)
def test_apply_ends_with_rule(value, ends_whith, expected):
    result = apply_ends_with_rule(value, ends_whith)
    assert result == expected


@pytest.mark.parametrize(
    "value,min_valid_value, expected",
    [
        (5, 5, None),
        (5, 6, f"Value: '5' is under the minimum autorized: '6'"),
        (5, 4, None),
        (-15, 4, f"Value: '-15' is under the minimum autorized: '4'"),
    ],
)
def test_apply_min_rules(value, min_valid_value, expected):
    result = apply_min_rule(value, min_valid_value)
    assert result == expected


@pytest.mark.parametrize(
    "value, max_valid_value, expected",
    [
        (5, 5, None),
        (6, 5, f"Value: '6' exceeds the maximum autorized: '5'"),
        (4, 5, None),
        (-6, 5, None),
    ],
)
def test_apply_max_rules(value, max_valid_value, expected):
    result = apply_max_rule(value, max_valid_value)
    assert result == expected


@pytest.mark.parametrize(
    "value, allowed_values, date_format, expected",
    [
        ("10/05/1995", [date(1995, 5, 10), date(1996, 5, 10)], "%d/%m/%Y", None),
        (
            "10/05/1994",
            [date(1995, 5, 10), date(1996, 5, 10)],
            "%d/%m/%Y",
            f"Value '10/05/1994' is not among the allowed values: ['10/05/1995', '10/05/1996'].",
        ),
        ("test", ["test", "Test1"], None, None),
        (
            "Test",
            ["test", "Test1"],
            None,
            f"The value  'Test' not in allowed values: '['test', 'Test1']'",
        ),
        (1, [1, 2], None, None),
        (-1, [1, 2], None, f"The value  '-1' not in allowed values: '[1, 2]'"),
    ],
)
def test_apply_allowed_values_rule(value, allowed_values, date_format, expected):
    result = apply_allowed_values_rule(value, allowed_values, date_format)
    assert result == expected


@pytest.mark.parametrize(
    "value, transformation, expected",
    [
        (" test ", "strip", "test"),
        ("TEsT", "lower", "test"),
        ("tesT", "upper", "TEST"),
        ("teST TeST", "title", "Test Test"),
        ("  test  tes t  ", "collapse_spaces", " test tes t "),
        ("élodie$", "remove_accents", "elodie$"),
        (" tES t ", "strip, lower, collapse_spaces", "tes t"),
    ],
)
def test_apply_string_transformations(value, transformation, expected):
    result = apply_string_transformations(value=value, transformations=transformation)
    assert result == expected


@pytest.mark.parametrize(
    "column_type, value, expected",
    [
        ("str", "test", "test"),
        ("int", "5", 5),
        ("decimal", "5.54", format_decimal(Decimal(5.54))),
        ("bool", "True", True),
        ("email", "test@gmail.com", "test@gmail.com"),
        ("date", "04-05-1996", "04-05-1996"),
    ],
)
def test_process_value_valid_case(column_type, value, expected):
    if column_type == "date":
        date_format = "%d-%m-%Y"
    else:
        date_format = None

    column = Columns_Contract(
        column_name="test",
        column_type=column_type,
        date_format=date_format,
    )

    result = process_value(column=column, value=value)
    assert result == expected


@pytest.mark.parametrize(
    "column_type, value",
    [
        ("str", True),
        ("int", "abc"),
        ("decimal", "5a"),
        ("bool", "t"),
        ("email", "test@@gmail"),
        ("date", "04:05:1996"),
    ],
)
def test_process_value_invalid_case(column_type, value):
    if column_type == "date":
        date_format = "%d-%m-%Y"
    else:
        date_format = None

    column = Columns_Contract(
        column_name="test",
        column_type=column_type,
        date_format=date_format,
    )
    with pytest.raises((TypeError, ValueError, DecimalException, EmailNotValidError)):
        process_value(column=column, value=value)
