import pytest, yaml
from textwrap import dedent
from decimal import Decimal


from data_contract_cli.exceptions import ApplicationError, YAMLContractError
from data_contract_cli.contract_models import Columns_Contract, Contract
from data_contract_cli.contract import (
    RULES,
    TRANSFORMATION,
    rules_orchestration,
    transformations_orchestration,
    load_and_validate_contract,
)


@pytest.mark.parametrize(
    "column_name, valid_metadata, expected_result",
    [
        (
            "invoice",
            {
                "type": "int",
                "rules": None,
            },
            {},
        ),
        (
            "invoice",
            {
                "type": "int",
                "rules": {},
            },
            {},
        ),
        (
            "invoice",
            {
                "type": "int",
                "rules": {"max": 5, "min": 2},
            },
            {"max": 5, "min": 2},
        ),
    ],
)
def test_rules_orchestration_valid_case(column_name, valid_metadata, expected_result):
    content = rules_orchestration(column_name, valid_metadata)
    assert content == expected_result


def test_rules_orchestration_decimal():
    column_name = "invoice"
    metadata = {"type": "decimal", "rules": {"max": 5.50}}
    content = rules_orchestration(column_name, metadata)
    assert content == {"max": Decimal("5.5")}


def test_rules_orchestration_invalid_case():
    column_name = "invoice"
    metadata = {"type": "decimal", "rules": {"regex": 5.50}}
    with pytest.raises(YAMLContractError):
        rules_orchestration(column_name, metadata)


@pytest.mark.parametrize(
    "valid_case, expected",
    [
        (
            {
                "type": "int",
                "transformations": None,
            },
            [],
        ),
        (
            {
                "type": "int",
                "transformations": [],
            },
            [],
        ),
        (
            {
                "type": "str",
                "transformations": ["STrip", "lOWER  "],
            },
            ["strip", "lower"],
        ),
    ],
)
def test_transformations_orchestration_valid_case(valid_case, expected):
    result = transformations_orchestration(valid_case)
    assert result == expected


@pytest.mark.parametrize(
    "invalid_transformation",
    [
        ({"transformations": {}}),
        ({"transformations": {1}}),
    ],
)
def test_transformations_orchestration_invalid_case(invalid_transformation):
    with pytest.raises(YAMLContractError):
        transformations_orchestration(invalid_transformation)


def test_load_and_validate_contract(tmp_path):
    content = dedent("""\
            delimiter: ";"
            encoding: utf-8-sig

            columns:
                invoice_id:
                    type: str
                    nullable: false
                    unique: true
                    rules: {starts_with: "INV-"}
                    transformations: [strip, upper]

                customer_name:
                    type: str
                    nullable: false
                    unique: false
                    rules: {}
                    transformations: [strip, collapse_spaces, title]
                        """)

    contract_yaml = tmp_path / "contract.yaml"
    contract_yaml.write_text(content)
    result = load_and_validate_contract(contract_yaml)
    flag = False
    assert result.headers == ["invoice_id", "customer_name"]
    assert result.delimiter == ";"
    assert result.encoding == "utf-8-sig"
    assert vars(result.columns["invoice_id"]) == {
        "column_name": "invoice_id",
        "column_type": "str",
        "nullable": False,
        "unique": True,
        "rules": {"starts_with": "INV-"},
        "transformations": ["strip", "upper"],
    }
    assert vars(result.columns["customer_name"]) == {
        "column_name": "customer_name",
        "column_type": "str",
        "nullable": False,
        "unique": False,
        "rules": {},
        "transformations": ["strip", "collapse_spaces", "title"],
    }


def test_load_and_validate_contract_invalid_case(tmp_path):
    content = dedent("""\
    customer_name:
      type: int
      nullable: false
      unique: false
      rules:
        regex: '^[^@]+@[^@]+[.][^@]+$'
      transformations:
    """)
    contract_yaml = tmp_path / "contract.yaml"
    contract_yaml.write_text(content)
    with pytest.raises(YAMLContractError):
        load_and_validate_contract(contract_yaml)
