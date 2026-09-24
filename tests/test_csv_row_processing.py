import pytest
from decimal import Decimal
from csv_refine.exceptions import CSVError
from csv_refine.contract_models import Columns_Contract, Contract
from csv_refine.row_processing import (
    apply_transformations,
    apply_rules,
    get_column_contract,
    is_nullable,
    process_value_and_collect_errors,
    rebuild_row_from_column_values,
    validate_and_transform_csv_values,
)
from conftest import valid_contract


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
            ["Length of value: (test ) is: '5', length min autorized is: 10"],
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
            ["The value  'test-3' not in allowed values: '['test', 'test-2']'"],
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
                "The value  '01-06-2000' not in allowed values: '['15-06-2000', '18-06-2000']'"
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


def test_get_column_contract(valid_contract):
    result = get_column_contract(contract=valid_contract, column_name="name")
    assert result.column_name == "name"
    assert result.column_type == "str"
    assert result.rules == {}


@pytest.mark.parametrize(
    "value, test_index, errors",
    [
        ("test", "1", []),
        ("  ", "3", ["Value at row 3, column 'test', cannot be null."]),
        ("", "5", ["Value at row 5, column 'test', cannot be null."]),
    ],
)
def test_is_nullable(value, test_index, errors) -> None:
    test_error = []
    strict_errors = []
    result = is_nullable(
        value=value,
        errors=test_error,
        index=test_index,
        column_name="test",
        strict_errors=strict_errors,
    )
    assert result is None
    assert test_error == errors
    assert strict_errors == errors


@pytest.mark.parametrize(
    "value, column_type, expected, expected_strict_errors",
    [
        ("test", "str", "test", []),
        ("1", "int", 1, []),
        (
            "abc",
            "int",
            [f"Value 'abc' cannot be converted or validated to type: 'int'."],
            [f"Value 'abc' cannot be converted or validated to type: 'int'."],
        ),
        (
            "abc",
            "decimal",
            [f"Value 'abc' cannot be converted or validated to type: 'decimal'."],
            [f"Value 'abc' cannot be converted or validated to type: 'decimal'."],
        ),
        (
            "abc",
            "email",
            [f"Value 'abc' cannot be converted or validated to type: 'email'."],
            [f"Value 'abc' cannot be converted or validated to type: 'email'."],
        ),
        (
            "abc",
            "bool",
            [f"Value 'abc' cannot be converted or validated to type: 'bool'."],
            [f"Value 'abc' cannot be converted or validated to type: 'bool'."],
        ),
        (
            "05-11-2000",
            "date",
            [
                "Date '05-11-2000' is invalid or does not match the expected format '%Y-%m-%d'.",
                "Value '05-11-2000' cannot be converted or validated to type: 'date'.",
            ],
            [
                "Date '05-11-2000' is invalid or does not match the expected format '%Y-%m-%d'.",
                "Value '05-11-2000' cannot be converted or validated to type: 'date'.",
            ],
        ),
    ],
)
def test_process_value_and_collect_errors(
    value, column_type, expected, expected_strict_errors
):
    strict_errors = []
    date_format = None
    if column_type == "date":
        date_format = "%Y-%m-%d"
    column = Columns_Contract(
        column_name="test", column_type=column_type, date_format=date_format
    )
    result = process_value_and_collect_errors(
        value=value, errors=[], column=column, strict_errors=strict_errors
    )
    assert result == expected
    assert strict_errors == expected_strict_errors


def test_rebuild_row_from_column_values():
    classified_rows = {
        "valid_rows": [
            {
                "index": 7,
                "row": [
                    "valid",
                    "INV-006 ",
                    "Félix  Noël ",
                ],
                "column_and_values": {
                    "valid": "valid",
                    "invoice_id": "INV-006",
                    "customer_name": "Felix Noel",
                },
            },
        ]
    }
    valid_rows = classified_rows["valid_rows"]

    for valid_row in valid_rows:
        for column_name, value in valid_row["column_and_values"].items():
            result = rebuild_row_from_column_values(valid_row=valid_row)

    assert result == [
        "valid",
        "INV-006",
        "Felix Noel",
    ]


@pytest.fixture
def classified_rows() -> dict:
    return {
        "valid_rows": [
            {
                "index": 1,
                "row": [" test ", "4 ", Decimal("1200.5004"), " 05/01/2002"],
                "column_and_values": {
                    "name": " test ",
                    "quantity": "4 ",
                    "price": Decimal("1200.50"),
                    "invoice_date": " 05/01/2002",
                },
            },
            {
                "index": 2,
                "row": ["  ", "4 ", Decimal("1200.5004"), " 05/01/2002"],
                "column_and_values": {
                    "name": "  ",
                    "quantity": "4 ",
                    "price": Decimal("1200.50"),
                    "invoice_date": " 05/01/2002",
                },
            },
            {
                "index": 3,
                "row": [" test ", "4b ", Decimal("1200.5004"), " 05/01/2002b"],
                "column_and_values": {
                    "name": " test ",
                    "quantity": "4b ",
                    "price": Decimal("1200.50"),
                    "invoice_date": " 05/01/2002b",
                },
            },
        ],
        "invalid_rows": [],
    }


@pytest.fixture
def test_contract() -> Contract:
    return Contract(
        headers=["name", "quantity", "price", "invoice_date"],
        columns={
            "name": Columns_Contract(
                column_name="name",
                column_type="str",
                nullable=False,
                rules={},
                transformations=["strip", "title"],
            ),
            "quantity": Columns_Contract(
                column_name="quantity",
                column_type="int",
                nullable=True,
                rules={"min": 1},
                transformations=[],
            ),
            "price": Columns_Contract(
                column_name="price",
                column_type="decimal",
                nullable=True,
                rules={},
                transformations=["format_decimal"],
            ),
            "invoice_date": Columns_Contract(
                column_name="invoice_date",
                column_type="date",
                date_format="%d/%m/%Y",
                nullable=True,
                rules={},
                transformations=["normalize_date"],
            ),
        },
        encoding="utf-8",
        delimiter=",",
    )


def test_value_processing(classified_rows, test_contract):
    result = validate_and_transform_csv_values(
        classified_rows=classified_rows, contract=test_contract, mode="permissive"
    )
    assert result == {
        "valid_rows": [
            {
                "index": 1,
                "row": ["Test", 4, Decimal("1200.50"), "2002-01-05"],
                "column_and_values": {
                    "name": "Test",
                    "quantity": 4,
                    "price": Decimal("1200.50"),
                    "invoice_date": "2002-01-05",
                },
            }
        ],
        "invalid_rows": [
            {
                "index": 2,
                "row": ["  ", "4 ", Decimal("1200.5004"), " 05/01/2002"],
                "errors": ["Value at row 2, column 'name', cannot be null."],
            },
            {
                "index": 3,
                "row": [" test ", "4b ", Decimal("1200.5004"), " 05/01/2002b"],
                "errors": [
                    "Value '4b ' cannot be converted or validated to type: 'int'.",
                    "Date ' 05/01/2002b' is invalid or does not match the expected format '%d/%m/%Y'.",
                    "Value ' 05/01/2002b' cannot be converted or validated to type: 'date'.",
                ],
            },
        ],
    }


def test_value_processing_strict_mode(test_contract, classified_rows):
    with pytest.raises(CSVError):
        validate_and_transform_csv_values(
            classified_rows=classified_rows, contract=test_contract, mode="strict"
        )
