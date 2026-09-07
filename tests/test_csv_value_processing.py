import pytest
from decimal import Decimal
from data_contract_cli.contract_models import Columns_Contract
from data_contract_cli.csv_value_processing import apply_transformations, apply_rules


@pytest.mark.parametrize(
    "values, column_type, transformations, expected",
    [
        ("test ", "str", ["strip", "upper"], "TEST"),
        ("test ", "str", [], "test "),
        (Decimal("5.511"), "decimal", "format_decimal", Decimal("5.51")),
        ("05-03-2000", "date", ["normalize_date"], "2000-03-05"),
        ("tEst@gmail.com ", "email", ["strip", "lower"], "test@gmail.com"),
    ],
)
def test_apply_transformations(values, column_type, transformations, expected):
    date_format = None

    if column_type == "date":
        date_format = "%d-%m-%Y"

    column = Columns_Contract(
        column_name="column_test",
        column_type=column_type,
        transformations=transformations,
        date_format=date_format,
    )
    result = apply_transformations(column=column, validated_value=values)

    assert result == expected


@pytest.mark.parametrize(
    "values, column_type, rules, expected",
    [
        ("test ", "str", {"max_length": 10}, "test "),
        (
            "test ",
            "str",
            {"min_length": 10},
            ["length of value: (test ) is: '5', lenght min autorized is: 10"],
        ),
        ("test", "str", {"starts_with": "te", "ends_with": "st"}, "test"),
        (
            "test-1",
            "str",
            {"starts_with": "te", "ends_with": "st"},
            ["Value 'test-1' does not match endswith pattern 'st'."],
        ),
        (
            "1-test",
            "str",
            {"starts_with": "te", "ends_with": "st"},
            ["Value '1-test' does not match startwith pattern 'te'."],
        ),
        (
            "test-2",
            "str",
            {"allowed_values": ["test", "test-2"]},
            "test-2",
        ),
        (
            "test-3",
            "str",
            {"allowed_values": ["test", "test-2"]},
            ["the value  'test-3' not in allowed values: '['test', 'test-2']'"],
        ),
        (
            "15-06-2000",
            "str",
            {"allowed_values": ["15-06-2000", "18-06-2000"]},
            "15-06-2000",
        ),
        (
            "01-06-2000",
            "str",
            {"allowed_values": ["15-06-2000", "18-06-2000"]},
            [
                "the value  '01-06-2000' not in allowed values: '['15-06-2000', '18-06-2000']'"
            ],
        ),
        (
            "INV-001",
            "str",
            {"regex": r"^INV-\d{3}$"},
            "INV-001",
        ),
        (
            1,
            "int",
            {"min": 1},
            1,
        ),
        (
            4,
            "int",
            {"min": 1, "max": 3},
            ["Value: '4' exceeds the maximum autorized: '3'"],
        ),
    ],
)
def test_apply_rules(values, column_type, rules, expected):
    date_format = None

    if column_type == "date":
        date_format = "%d-%m-%Y"

    column = Columns_Contract(
        column_name="column_test",
        column_type=column_type,
        rules=rules,
        date_format=date_format,
    )
    result = apply_rules(column=column, validated_value=values, errors=[])

    assert result == expected
