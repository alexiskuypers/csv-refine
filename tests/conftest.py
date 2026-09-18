import pytest
import csv
from pathlib import Path
from data_contract_cli.contract_models import Columns_Contract, Contract


@pytest.fixture
def valid_contract() -> Contract:
    invoice_id = Columns_Contract(
        column_name="invoice_id",
        column_type="int",
        unique=True,
    )
    name = Columns_Contract(
        column_name="name",
        column_type="str",
        unique=True,
    )

    return Contract(
        encoding="utf-8",
        delimiter=",",
        headers=["invoice_id", "name"],
        columns={"invoice_id": invoice_id, "name": name},
    )


@pytest.fixture
def csv_factory(tmp_path: Path, valid_contract: Contract):
    def create_csv(filename: str, content: str) -> Path:
        csv_path = tmp_path / filename

        csv_path.write_text(
            content,
            encoding=valid_contract.encoding,
        )

        return csv_path

    return create_csv


@pytest.fixture
def valid_csv(csv_factory) -> Path:
    return csv_factory(
        content=("invoice_id,name\n" "1,test\n" "2,test2\n"),
        filename="valid.csv",
    )


@pytest.fixture
def invalid_csv(csv_factory) -> Path:
    return csv_factory(
        content=("invoice_id," "1,test\n" "2,test2,extra_value\n" "3,test3\n"),
        filename="invalid.csv",
    )
