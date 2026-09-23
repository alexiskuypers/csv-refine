import pytest
import csv
from decimal import Decimal
from pathlib import Path

from csv_refine.write_csv import convert_to_str, prepare_csv_rows, write_csv
from csv_refine.contract_models import Contract, Columns_Contract


def test_convert_to_str():
    content = {
        "valid_rows": [
            {"column_and_values": {"test_str": "INV-001", "test_int": 2}},
            {
                "column_and_values": {
                    "test_bool": False,
                    "test_decimal": Decimal("315.75"),
                    "test_none": None,
                }
            },
        ],
        "invalid_rows": [{"test": "test"}],
    }
    result = convert_to_str(content)
    assert result == {
        "valid_rows": [
            {"column_and_values": {"test_str": "INV-001", "test_int": "2"}},
            {
                "column_and_values": {
                    "test_bool": "False",
                    "test_decimal": "315.75",
                    "test_none": "None",
                }
            },
        ],
        "invalid_rows": [{"test": "test"}],
    }


def test_prepare_data():
    content = {
        "valid_rows": [
            {"column_and_values": {"test_str": "INV-001", "test_int": "2"}},
            {
                "column_and_values": {
                    "test_bool": "False",
                    "test_decimal": "315.75",
                    "test_none": "None",
                }
            },
        ],
        "invalid_rows": [{"test": "test"}],
    }
    result = prepare_csv_rows(content)

    assert result == [
        {"test_str": "INV-001", "test_int": "2"},
        {
            "test_bool": "False",
            "test_decimal": "315.75",
            "test_none": "None",
        },
    ]


def test_write_csv(tmp_path):

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

    contract = Contract(
        delimiter=",", encoding="utf-8", headers=["test_1", "test_2"], columns=column
    )

    content = {
        "valid_rows": [
            {"column_and_values": {"test_1": "INV-001", "test_2": 2}},
        ],
        "invalid_rows": [{"test": "test"}],
    }
    file_name = "test.csv"
    output = tmp_path

    write_csv(
        contract=contract,
        output=output,
        output_filename=file_name,
        validated_classified_rows=content,
    )
    file_name = "validated_" + file_name + ".csv"
    output = output / file_name

    with output.open("r", encoding=contract.encoding, newline="") as csv_file:
        csv_file = csv.DictReader(csv_file, delimiter=contract.delimiter)

        assert csv_file.fieldnames == ["test_1", "test_2"]
        assert list(csv_file) == [{"test_1": "INV-001", "test_2": "2"}]
