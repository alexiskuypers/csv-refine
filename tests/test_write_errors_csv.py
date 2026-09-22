import pytest
import csv
from decimal import Decimal
from pathlib import Path

from csv_refine.write_errors_csv import (
    convert_invalid_row_values_to_str,
    prepare_errors,
    prepare_csv_rows,
    write_errors_csv,
)

from csv_refine.contract_models import Contract, Columns_Contract


def test_convert_invalid_row_values_to_str():
    content = {
        "valid_rows": [
            [{"test": "test"}],
        ],
        "invalid_rows": [
            {
                "row": [1, False],
            },
            {
                "row": ["str", Decimal("5.40")],
            },
        ],
    }

    result = convert_invalid_row_values_to_str(content)

    for invalid_row in result:
        for value in invalid_row["row"]:
            assert isinstance(value, str)


def test_prepare_errors():
    content = [
        {"errors": ["Value at row 5, column 'invoice_id', cannot be null."]},
        {
            "errors": [
                "Value at row 5, column 'invoice_id', cannot be null.",
                "Value 'ok' cannot be converted or validated to type: 'bool'.",
            ]
        },
        {
            "errors": [
                "Value at row 5, column 'invoice_id', cannot be null.",
                "Value 'ok' cannot be converted or validated to type: 'bool'.",
                "Value at row 5, column 'customer_name', cannot be null.",
            ]
        },
    ]
    result = prepare_errors(content)

    assert result == [
        {"errors": ["Value at row 5, column 'invoice_id', cannot be null."]},
        {
            "errors": [
                "Value at row 5, column 'invoice_id', cannot be null. | Value 'ok' cannot be converted or validated to type: 'bool'."
            ]
        },
        {
            "errors": [
                "Value at row 5, column 'invoice_id', cannot be null. | Value 'ok' cannot be converted or validated to type: 'bool'. | Value at row 5, column 'customer_name', cannot be null."
            ]
        },
    ]


def test_prepare_csv_rows():
    content = [
        {
            "row": ["1", "False"],
            "errors": ["Value at row 5, column 'invoice_id', cannot be null."],
        },
        {
            "row": ["2", "True"],
            "errors": [
                "Value at row 5, column 'invoice_id', cannot be null. | Value 'ok' cannot be converted or validated to type: 'bool'."
            ],
        },
        {
            "row": ["4", "False"],
            "errors": [
                "Value at row 5, column 'invoice_id', cannot be null. | Value 'ok' cannot be converted or validated to type: 'bool'. | Value at row 5, column 'customer_name', cannot be null."
            ],
        },
    ]
    result = prepare_csv_rows(content)
    assert result == [
        ["1", "False", "Value at row 5, column 'invoice_id', cannot be null."],
        [
            "2",
            "True",
            "Value at row 5, column 'invoice_id', cannot be null. | Value 'ok' cannot be converted or validated to type: 'bool'.",
        ],
        [
            "4",
            "False",
            "Value at row 5, column 'invoice_id', cannot be null. | Value 'ok' cannot be converted or validated to type: 'bool'. | Value at row 5, column 'customer_name', cannot be null.",
        ],
    ]


def test_write_errors_csv(tmp_path):
    column = {
        "columns": [
            Columns_Contract(
                column_name="test_1",
                column_type="str",
            ),
            Columns_Contract(
                column_name="test_2",
                column_type="int",
            ),
        ]
    }

    classified_rows = {
        "valid_rows": [
            {
                "index": 1,
                "row": ["test"],
                "column_and_values": {"column": "test"},
            },
        ],
        "invalid_rows": [
            {
                "index": 2,
                "row": [
                    "INV-001",
                    "False",
                ],
                "errors": ["Value: 'INV-001' in column: 'invoice_id' isn't unique."],
            },
            {
                "index": 5,
                "row": [
                    "",
                    "ok",
                ],
                "errors": [
                    "Value at row 5, column 'invoice_id', cannot be null.",
                    "Value 'ok' cannot be converted or validated to type: 'bool'.",
                ],
            },
        ],
    }
    contract = Contract(
        delimiter=",", encoding="utf-8", headers=["invoice", "paid"], columns=column
    )

    field_name = "test"
    output = tmp_path

    write_errors_csv(
        validated_classified_rows=classified_rows,
        output=output,
        output_filename=field_name,
        contract=contract,
    )

    path = output / "errors_test.csv"

    with path.open("r", encoding=contract.encoding, newline="") as test_file:
        csv_file = csv.reader(test_file, delimiter=contract.delimiter)
        header = next(csv_file)
        assert header == ["invoice", "paid", "errors"]
