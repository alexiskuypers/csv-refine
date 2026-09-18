import pytest, yaml
from typing import Any
from datetime import datetime, date

from csv_refine.exceptions import ApplicationError, YAMLContractError
from csv_refine.contract_models import (
    Contract,
    Columns_Contract,
    VALID_DATE_FORMAT,
)
from csv_refine.contract import (
    RULES,
    TRANSFORMATION,
    load_contract,
    validate_global_structure,
    validate_internal_structure,
    extract_columns,
    validate_type,
    validate_column_flags,
    resolve_encoding,
    resolve_delimiter,
    build_contract,
    build_column,
)


def test_load_contract(tmp_path):
    contract = tmp_path / "contract.yaml"
    contract.write_text(
        """
    columns:
      email:
        type: email
        """,
        encoding="utf-8",
    )
    result = load_contract(contract)

    assert result == {"columns": {"email": {"type": "email"}}}


def test_load_contract_suffix(tmp_path):
    contract = tmp_path / "contract.txt"
    contract.write_text("test")
    with pytest.raises(YAMLContractError):
        load_contract(contract)


def test_load_contract_size(tmp_path):
    contract = tmp_path / "contract.yaml"
    contract.write_text("")
    with pytest.raises(YAMLContractError):
        load_contract(contract)


def test_load_contract_with_dir(tmp_path):
    test_dir = tmp_path / "dir"
    test_dir.mkdir()
    with pytest.raises(YAMLContractError):
        load_contract(test_dir)


def test_validate_globale_structure():
    contract = {"test": 1}
    result = validate_global_structure(contract)
    assert result == contract


def test_validate_globale_structure_error():
    invalid_contract: Any = 1
    with pytest.raises(YAMLContractError):
        validate_global_structure(invalid_contract)


def test_extract_columns():
    contract = {"columns": {"columns_1": "metadata"}}

    assert extract_columns(contract) == {"columns_1": "metadata"}


@pytest.mark.parametrize(
    "column_name, metadata",
    [
        (None, {}),
        ("  ", {}),
        ("", {}),
        ("valid key", ["invalid value"]),
    ],
)
def test_validate_internal_structure_errors(column_name, metadata):
    with pytest.raises(YAMLContractError):
        validate_internal_structure(column_name, metadata)


def test_validate_internal_structure_valid_case():
    valid_dict = {
        "key": {"metadata": "value"},
    }
    for column_name, metadata in valid_dict.items():
        result = validate_internal_structure(column_name, metadata)
    assert result == None


@pytest.mark.parametrize(
    "invalid_type",
    [
        {"no_type": "str"},
        {"type": "invalid"},
        {"type": 0},
    ],
)
def test_validate_type_invalid_case(invalid_type):
    with pytest.raises(YAMLContractError):
        validate_type(invalid_type)


def test_validate_type_valid_case():
    valid_metadata = {"type": "Str "}
    result = validate_type(valid_metadata)
    assert result == "str"


def test_validate_column_flags_empty():
    empty_metadata = {"type": "str"}
    result = validate_column_flags(empty_metadata)
    assert result == {
        "type": "str",
        "unique": False,
        "nullable": False,
    }


def test_validate_column_flags_valid_case():
    metadata = {"type": "str", "unique": True, "nullable": False}
    result = validate_column_flags(metadata)
    assert result == {
        "type": "str",
        "unique": True,
        "nullable": False,
    }


def test_validate_column_flags_invalid_case():
    metadata = {"type": "str", "unique": 4, "nullable": False}
    with pytest.raises(YAMLContractError):
        validate_column_flags(metadata)


def test_resolve_delimiter_valid():
    delimiter = {"delimiter": ";"}
    result = resolve_delimiter(delimiter)
    assert result == ";"


def test_resolve_delimiter_invalid():
    delimiter = {"delimiter": "utf-8"}
    with pytest.raises(YAMLContractError):
        resolve_delimiter(delimiter)


def test_resolve_delimiter_default_value():
    delimiter = {}
    result = resolve_delimiter(delimiter)
    assert result == ","


def test_resolve_encoding_valid():
    encoding = {"encoding": "utf-8"}
    result = resolve_encoding(encoding)
    assert result == "utf-8"


def test_resolve_encoding_default_value():
    encoding = {}
    result = resolve_encoding(encoding)
    assert result == "utf-8"


def test_resolve_encoding_invalid():
    encoding = {"encoding": " "}
    with pytest.raises(YAMLContractError):
        resolve_encoding(encoding)


def test_build_contract_object():
    valid_contract = {
        "delimiter": ";",
        "encoding": "utf-8-sig",
        "invoice_id": {
            "type": "str",
            "nullable": False,
            "unique": True,
            "rules": {"starts_with": "INV-"},
            "transformations": ["strip", "upper"],
        },
        "customer_name": {
            "type": "str",
            "nullable": False,
            "unique": False,
            "rules": {},
            "transformations": ["strip", "collapse_spaces", "title"],
        },
    }
    result = build_contract(valid_contract)
    assert isinstance(result, Contract)
    assert result.encoding == "utf-8-sig"
    assert result.delimiter == ";"
    assert result.headers == ["invoice_id", "customer_name"]
    assert isinstance(result.columns, dict)
    assert isinstance(result.columns["invoice_id"], Columns_Contract)
    assert isinstance(result.columns["customer_name"], Columns_Contract)


def test_build_column():
    metadata = {
        "type": "str",
        "nullable": False,
        "unique": False,
        "rules": {"max": 5},
        "transformations": ["strip"],
    }
    column_name = "name"
    result = build_column(
        column_name=column_name, metadata=metadata, VALID_DATE_FORMAT=VALID_DATE_FORMAT
    )

    assert isinstance(result, Columns_Contract)
    assert result.column_name == "name"
    assert result.column_type == "str"
    assert result.unique is False
    assert result.nullable is False
    assert isinstance(result.rules, dict)
    assert result.rules == {"max": 5}
    assert isinstance(result.transformations, list)
    assert result.transformations == ["strip"]


def test_build_column_type_date():
    metadata = {
        "type": "date",
        "date_format": "DD-MM-YYYY",
        "nullable": False,
        "unique": False,
        "rules": {"allowed_values": ["05-01-2000", "06-01-2000"]},
        "transformations": [],
    }
    column_name = "invoice_date"
    result = build_column(
        column_name=column_name, metadata=metadata, VALID_DATE_FORMAT=VALID_DATE_FORMAT
    )

    assert result.column_type == "date"
    assert result.date_format == "%d-%m-%Y"
    assert result.rules == {"allowed_values": [date(2000, 1, 5), date(2000, 1, 6)]}


@pytest.mark.parametrize(
    "metadata, column_name",
    [
        ({"type": "date", "date_format": "YYY-mm-dd"}, "invoice_date"),
        ({"type": "date", "date_format": "yyyy-mm-dd"}, "invoice_date"),
        ({"type": "date", "date_format": "%Y-%m-%d"}, "invoice_date"),
    ],
)
def test_build_column_invalid_date(metadata, column_name):
    with pytest.raises(YAMLContractError):
        build_column(
            metadata=metadata,
            column_name=column_name,
            VALID_DATE_FORMAT=VALID_DATE_FORMAT,
        )
