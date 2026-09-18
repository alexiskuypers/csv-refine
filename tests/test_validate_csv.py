import pytest
import csv

from pathlib import Path
from csv_refine.exceptions import CSVError
from csv_refine.contract import load_and_validate_contract
from csv_refine.contract_models import Contract, Columns_Contract
from csv_refine.validate_csv import (
    load_csv,
    validate_headers,
    is_rows_empty,
    get_valid_rows,
    get_invalid_rows,
    separate_csv_rows,
    load_and_validate_csv,
)


def test_load_csv(valid_csv: Path, valid_contract: Contract):
    result = load_csv(path=valid_csv, contract=valid_contract)
    assert result == {
        "headers": ["invoice_id", "name"],
        "csv_rows": [["1", "test"], ["2", "test2"]],
    }


def test_load_csv_invalid_case(tmp_path: Path, valid_contract: Contract):
    path = tmp_path / "csv_file.csv"
    with pytest.raises(CSVError):
        load_csv(path=path, contract=valid_contract)


def test_load_csv_empty_file(tmp_path: Path, valid_contract: Contract):
    path = tmp_path / "csv_file.csv"
    path.write_text("")
    with pytest.raises(CSVError):
        load_csv(path=path, contract=valid_contract)


def test_validate_headers_valid_case(valid_contract: Contract):
    headers = {"headers": ["invoice_id", "name"]}
    result = validate_headers(headers, valid_contract)
    assert result == None


@pytest.mark.parametrize(
    "invalid_case",
    [
        {"headers": "invoice_id"},
        {"headers": ["invoice_id", "invoice_id"]},
        {"headers": ["invoice_id", "invalid"]},
    ],
)
def test_validate_headers_invalid_case(invalid_case, valid_contract: Contract):
    with pytest.raises(CSVError):
        validate_headers(invalid_case, valid_contract)


@pytest.mark.parametrize(
    "valid_case",
    [
        [[["", "test"], ["", "test"], ["test", "", "test"], ["test", ""]]],
        [
            [["test", ""], ["test"]],
        ],
        [[["test", ""], ["test"], []]],
        [
            [
                ["test", ""],
                [],
                ["test"],
            ]
        ],
    ],
)
def test_is_rows_empty(valid_case: list):
    for item in valid_case:
        is_rows_empty(item)


def test_is_rows_empty_invalid_case():
    empty_row = [[], []]
    with pytest.raises(CSVError):
        is_rows_empty(empty_row)


def test_get_valid_rows(valid_contract: Contract):
    rows = [["1", "test"], ["2", "test2"]]
    index = 0
    valid_rows = []
    for row in rows:
        index += 1
        valid_rows.append(get_valid_rows(index=index, row=row, contract=valid_contract))
    assert valid_rows == [
        {
            "index": 1,
            "row": ["1", "test"],
            "column_and_values": {"invoice_id": "1", "name": "test"},
        },
        {
            "index": 2,
            "row": ["2", "test2"],
            "column_and_values": {"invoice_id": "2", "name": "test2"},
        },
    ]


def test_get_invalid_rows():
    rows = [["1", "test"]]
    errors = ["error"]
    index = 0
    invalid_rows = []
    for row in rows:
        index += 1
        invalid_rows.append(get_invalid_rows(index=index, row=row, errors=errors))
    assert invalid_rows == [{"index": 1, "row": ["1", "test"], "errors": ["error"]}]


def test_separate_rows(valid_contract: Contract):
    row = [["1", "test"], ["2", "test2", "13/08"], ["3", "continue?"]]
    result = separate_csv_rows(raw_csv_rows=row, contract=valid_contract)
    assert result == {
        "valid_rows": [
            {
                "index": 1,
                "row": ["1", "test"],
                "column_and_values": {"invoice_id": "1", "name": "test"},
            },
            {
                "index": 3,
                "row": ["3", "continue?"],
                "column_and_values": {"invoice_id": "3", "name": "continue?"},
            },
        ],
        "invalid_rows": [
            {
                "index": 2,
                "row": ["2", "test2", "13/08"],
                "errors": ["Row contains more columns than expected."],
            },
        ],
    }


@pytest.mark.parametrize(
    "error, expected",
    [
        (
            [[]],
            [
                {
                    "index": 1,
                    "row": [],
                    "errors": [
                        "Row contains fewer columns than expected.",
                        "Row is empty.",
                    ],
                }
            ],
        ),
        (
            [["name"]],
            [
                {
                    "index": 1,
                    "row": ["name"],
                    "errors": ["Row contains fewer columns than expected."],
                }
            ],
        ),
        (
            [["1", "test", "18/08"]],
            [
                {
                    "index": 1,
                    "row": ["1", "test", "18/08"],
                    "errors": ["Row contains more columns than expected."],
                }
            ],
        ),
    ],
)
def test_separate_rows_invalid_rows(
    error: list, expected: list, valid_contract: Contract
):
    result = separate_csv_rows(raw_csv_rows=error, contract=valid_contract)
    assert result["invalid_rows"] == expected


def test_load_and_validate_csv(valid_csv, valid_contract):
    result = load_and_validate_csv(path=valid_csv, contract=valid_contract)
    assert result == {
        "valid_rows": [
            {
                "index": 1,
                "row": ["1", "test"],
                "column_and_values": {"invoice_id": "1", "name": "test"},
            },
            {
                "index": 2,
                "row": ["2", "test2"],
                "column_and_values": {"invoice_id": "2", "name": "test2"},
            },
        ],
        "invalid_rows": [],
    }


def test_load_and_validate_csv_invalid_csv(invalid_csv, valid_contract):
    with pytest.raises(CSVError):
        load_and_validate_csv(invalid_csv, valid_contract)
