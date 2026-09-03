from data_contract_cli.contract_models import (
    Contract,
    Columns_Contract,
    VALID_DATE_FORMAT,
)
import pytest


def test_contract_object_with_date():
    column = Columns_Contract(
        column_name="invoice_date",
        column_type="date",
        date_format="%Y-%m-%d",
        required=True,
        nullable=False,
        unique=False,
        rules={},
        transformations=["normalize_date"],
    )
    columns = {"invoice_date": column}

    contract = Contract(
        delimiter=",", encoding="utf-8", headers=["id"], columns=columns
    )
    assert contract.delimiter == ","
    assert isinstance(contract.columns, dict) == True
    assert isinstance(contract.columns["invoice_date"], Columns_Contract) == True
    assert contract.headers == ["id"]
    assert contract.encoding == "utf-8"
    for (
        key,
        value,
    ) in contract.columns.items():
        assert value.date_format == "%Y-%m-%d"


def test_contract_object():
    column = Columns_Contract(
        column_name="id",
        column_type="str",
        required=True,
        nullable=False,
        unique=False,
        rules={},
        transformations=["strip", "collapse_spaces", "title"],
    )
    columns = {"id": column}

    contract = Contract(
        delimiter=",", encoding="utf-8", headers=["id"], columns=columns
    )
    assert contract.delimiter == ","
    assert isinstance(contract.columns, dict) == True
    assert isinstance(contract.columns["id"], Columns_Contract) == True
    assert contract.headers == ["id"]
    assert contract.encoding == "utf-8"


def test_columns_contract_object():
    column = Columns_Contract(
        column_name="id",
        column_type="str",
        required=True,
        nullable=False,
        unique=False,
        rules={},
        transformations=["strip", "collapse_spaces", "title"],
    )
    assert column.column_name == "id"
    assert column.column_type == "str"
    assert column.required is True
    assert column.nullable is False
    assert column.unique is False
    assert column.rules == {}
    assert column.transformations == ["strip", "collapse_spaces", "title"]


def test_columns_contract_object_type_date():
    column = Columns_Contract(
        column_name="invoice_date",
        column_type="date",
        date_format="%Y-%m-%d",
        required=True,
        nullable=False,
        unique=False,
        rules={},
        transformations=["normalize_date"],
    )
    assert column.column_name == "invoice_date"
    assert column.column_type == "date"
    assert column.date_format == "%Y-%m-%d"
    assert column.required is True
    assert column.nullable is False
    assert column.unique is False
    assert column.rules == {}
    assert column.transformations == ["normalize_date"]


@pytest.mark.parametrize(
    "raw_date_format, date_format,  expected",
    [
        ("YYYY-MM-DD", "%Y-%m-%d", None),
        ("DD/MM/YYYY", "%d/%m/%Y", None),
        ("YYYY/MM/DD", "%Y/%m/%d", None),
        ("DD-MM-YYYY", "%d-%m-%Y", None),
    ],
)
def test_validate_date_format(
    raw_date_format,
    date_format,
    expected,
):
    column = Columns_Contract(
        column_name="invoice_date",
        column_type="date",
        date_format=date_format,
        required=True,
        nullable=False,
        unique=False,
        rules={},
        transformations=["normalize_date"],
    )

    result = column.validate_date_format(
        raw_date_format=raw_date_format, VALID_DATE_FORMAT=VALID_DATE_FORMAT
    )
    assert result == expected
