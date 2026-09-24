import pytest
import datetime
from decimal import Decimal

from csv_refine.build_summary import (
    count_total_errors,
    collect_errors,
    count_rules_violations,
    count_errors_by_category,
    build_report,
)


def test_count_total_errors():
    content = {
        "valid_rows": [
            {
                "index": 1,
                "row": [
                    "test",
                ],
                "column_and_values": {
                    "test": "test",
                },
            }
        ],
        "invalid_rows": [
            {
                "index": 2,
                "row": [
                    "test",
                ],
                "errors": ["Value: 'INV-001' in column: 'invoice_id' isn't unique."],
            },
            {
                "index": 5,
                "row": [
                    "test",
                ],
                "errors": [
                    "Value at row 5, column 'invoice_id', cannot be null.",
                    "Value 'ok' cannot be converted or validated to type: 'bool'.",
                ],
            },
        ],
    }
    count_errors, rows_with_multiple_errors = count_total_errors(content)
    assert count_errors == 3
    assert rows_with_multiple_errors == 1


def test_collect_errors():
    content = {
        "valid_rows": [
            {
                "index": 1,
                "row": [
                    "test",
                ],
                "column_and_values": {
                    "test": "test",
                },
            }
        ],
        "invalid_rows": [
            {
                "index": 2,
                "row": [
                    "test",
                ],
                "errors": ["Value: 'INV-001' in column: 'invoice_id' isn't unique."],
            },
            {
                "index": 5,
                "row": [
                    "test",
                ],
                "errors": [
                    "Value at row 5, column 'invoice_id', cannot be null.",
                    "Value 'ok' cannot be converted or validated to type: 'bool'.",
                    "Value: 'ok' in column: 'status' isn't unique.",
                ],
            },
            {
                "index": 6,
                "row": [
                    "test",
                ],
                "errors": [
                    "Value at row 6, column 'invoice_id', cannot be null.",
                ],
            },
        ],
    }

    result = collect_errors(content)
    assert result == [
        "Value: 'INV-001' in column: 'invoice_id' isn't unique.",
        "Value at row 5, column 'invoice_id', cannot be null.",
        "Value 'ok' cannot be converted or validated to type: 'bool'.",
        "Value: 'ok' in column: 'status' isn't unique.",
        "Value at row 6, column 'invoice_id', cannot be null.",
    ]


def test_count_rules_violations():
    content = [
        "Value: 'INV-001' in column: 'invoice_id' isn't unique.",
        "The value  '5' not in allowed values: 'quantity'",
        "Length of value: ('Berlin') is: '6', length max autorized is: 2",
        "Length of value: ('BE') is: '2', length min autorized is: 3",
        r"Value 'ABC123' does not match regex pattern '^[A-Z]{3}-\d{3}$'.",
        "Value 'test@gmail.com' does not match endswith pattern '.be'.",
        "Value: '4' is under the minimum autorized: '5'.",
        "Value: '6' exceeds the maximum autorized: '5'.",
        "Value: '9' exceeds the maximum autorized: '4'.",
    ]
    result = count_rules_violations(content)
    assert result == [
        ("max", 2),
        ("max_length", 1),
        ("min_length", 1),
        ("min", 1),
        ("ends_with", 1),
        ("regex", 1),
        ("allowed_values", 1),
        ("starts_with", 0),
    ]


def test_count_errors_by_category():
    rules_violation = [
        ("max", 2),
        ("max_length", 1),
        ("min_length", 1),
        ("min", 1),
        ("ends_with", 1),
        ("regex", 1),
        ("allowed_values", 1),
        ("starts_with", 0),
    ]
    errors = [
        "Value: 'INV-001' in column: 'invoice_id' isn't unique.",
        "Value at row 5, column 'invoice_id', cannot be null.",
        "Value 'ok' cannot be converted or validated to type: 'bool'.",
        "Value: 'ok' in column: 'status' isn't unique.",
        "Value at row 6, column 'invoice_id', cannot be null.",
        "Value: '6' exceeds the maximum autorized: '5'.",
        "Value: '9' exceeds the maximum autorized: '4'.",
    ]
    result = count_errors_by_category(errors=errors, rules_violations=rules_violation)
    assert result == {
        "rules_violations": 8,
        "conversion_errors": 1,
        "unique_errors": 2,
        "nullable_errors": 2,
    }


def test_build_report(valid_contract):
    content = {
        "valid_rows": [
            {
                "index": 1,
                "row": [
                    1,
                    "test",
                ],
                "column_and_values": {
                    "invoice_id": 1,
                    "name": "test",
                },
            },
            {
                "index": 2,
                "row": [
                    2,
                    "test_2",
                ],
                "column_and_values": {
                    "invoice_id": 2,
                    "name": "test_2",
                },
            },
        ],
        "invalid_rows": [
            {
                "index": 3,
                "row": [
                    2,
                    "test_3",
                ],
                "errors": ["Value: '2' in column: 'invoice_id' isn't unique."],
            },
            {
                "index": 4,
                "row": [
                    "",
                    "Élodie laurent",
                    "elodie.laurent@gmail.com",
                ],
                "errors": [
                    "Value at row 5, column 'invoice_id', cannot be null.",
                    "Value 'ok' cannot be converted or validated to type: 'bool'.",
                ],
            },
            {
                "index": 5,
                "row": [
                    2,
                    "",
                ],
                "errors": [
                    "Value: '2' in column: 'invoice_id' isn't unique.",
                    "Value at row 5, column 'name', cannot be null.",
                ],
            },
        ],
    }

    result = build_report(
        validated_classified_rows=content,
        contract=valid_contract,
        mode="permissive",
        csv_name="tst.csv",
        duration=1250.78,
    )
    assert result == {
        "status": "completed_with_errors",
        "input_file": "tst.csv",
        "mode": "permissive",
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "columns_count": 2,
        "delimiter": ",",
        "encoding": "utf-8",
        "total_rows": 5,
        "valid_rows": 2,
        "invalid_rows": 3,
        "valid_rows_percentage": 40.0,
        "total_errors": 5,
        "rows_with_multiple_errors": 2,
        "average_errors_per_invalid_row": 1.67,
        "rules_violations": {
            "max_length": 0,
            "min_length": 0,
            "max": 0,
            "min": 0,
            "starts_with": 0,
            "ends_with": 0,
            "regex": 0,
            "allowed_values": 0,
        },
        "errors_by_category": {
            "rules_violations": 0,
            "conversion_errors": 1,
            "unique_errors": 2,
            "nullable_errors": 2,
        },
        "processing_duration_ms": 1250.78,
    }
