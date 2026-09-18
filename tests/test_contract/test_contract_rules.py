import pytest
from decimal import Decimal
from datetime import datetime, date


from data_contract_cli.exceptions import ApplicationError, YAMLContractError
from data_contract_cli.contract import (
    RULES,
    TRANSFORMATION,
    validate_rules_structure,
    normalize_rule_names,
    validate_rules,
    validate_regex,
    verify_rules_type,
    validate_allowed_values,
    convert_rules_to_decimal,
    convert_dates_in_allowed_values,
)


def test_validate_rules_structure_empty():
    column = "amount"
    metadata = {"type": "int"}
    result = validate_rules_structure(column, metadata)
    assert result == {}


def test_validate_rules_structure_valid_case():
    column = "amount"
    metadata = {
        "type": "int",
        "rules": {"max": 5, "min": 2},
    }
    result = validate_rules_structure(column, metadata)
    assert result == {"max": 5, "min": 2}


def test_validate_rules_structure_invalid_case():
    column = "amount"
    metadata = {"type": "int", "rules": "str"}
    with pytest.raises(YAMLContractError):
        validate_rules_structure(column, metadata)


def test_normalize_rule_names_valid_case():
    rules = {"maX": 5, "Min": 2, "allowed_values": [1, 5]}
    result = normalize_rule_names(rules)
    assert result == {"max": 5, "min": 2, "allowed_values": [1, 5]}


def test_normalize_rule_names_invalid_case():
    rules = {7: None}
    with pytest.raises(YAMLContractError):
        normalize_rule_names(rules)


def test_validate_rules_valid_case():
    rules = {
        "max": 5,
        "min": Decimal(2.5),
        "allowed_values": [4, 3],
        "regex": "str",
        "starts_with": "str",
        "ends_with": "str",
        "min_length": 6,
    }
    result = validate_rules(rules)
    assert result == None


@pytest.mark.parametrize(
    "invalid_rules",
    [
        {5: 5},
        {"max": "5"},
        {"min": None},
        {"allowed_values": 5},
        {"starts_with": True},
        {"ends_with": 9},
        {"regex": ()},
        {"unknow_rules": 5},
    ],
)
def test_validate_rules_invalid_case(invalid_rules):
    with pytest.raises(YAMLContractError):
        validate_rules(invalid_rules)


def test_validate_regex_valid_case():
    rules = {"regex": "^[A-Z]+([0-9]+)"}
    result = validate_regex(rules)
    assert result is None


def test_validate_regex_invalid_case():
    rules = {"regex": "^[A-Z]+([0-9]+"}
    with pytest.raises(YAMLContractError):
        validate_regex(rules)


def test_validate_regex_empty_case():
    rules = {"regex": "   "}

    with pytest.raises(YAMLContractError):
        validate_regex(rules)


@pytest.mark.parametrize(
    "normalized_rules, column_type",
    [
        ({"min": 0, "max": 15, "allowed_values": [14]}, "int"),
        (
            {
                "min_length": 1,
                "max_length": 10,
                "allowed_values": ["test"],
                "regex": "test",
                "starts_with": "test",
                "ends_with": "test",
            },
            "str",
        ),
        ({"allowed_values": [False]}, "bool"),
    ],
)
def test_verify_rules_type_valid_case(normalized_rules, column_type):
    result = verify_rules_type(normalized_rules, column_type)
    assert result is None


@pytest.mark.parametrize(
    "normalized_rules, invalid_type",
    [
        ({"min": 0, "max": 15, "allowed_values": [14]}, "str"),
        (
            {
                "min_length": 1,
                "max_length": 10,
                "allowed_values": ["test"],
                "regex": "test",
                "starts_with": "test",
                "ends_with": "test",
            },
            "bool",
        ),
    ],
)
def test_verify_rules_type_invalid_case(normalized_rules, invalid_type):
    with pytest.raises(YAMLContractError):
        verify_rules_type(normalized_rules, invalid_type)


@pytest.mark.parametrize(
    "valid_rules, column_type",
    [
        ({"allowed_values": [1, 5, 9]}, "int"),
        ({"allowed_values": ["str", "test"]}, "str"),
        ({"allowed_values": [True, False]}, "bool"),
        ({"allowed_values": [Decimal(0.5)]}, "decimal"),
        ({"other_key": 1}, "decimal"),
    ],
)
def test_validate_allowed_values_valid_case(valid_rules, column_type):
    result = validate_allowed_values(valid_rules, column_type)
    assert result is None


@pytest.mark.parametrize(
    "invalid_rules, column_type",
    [
        ({"allowed_values": [True, False]}, "int"),
        ({"allowed_values": [1, 2]}, "str"),
        ({"allowed_values": [1, 2]}, "bool"),
        ({"allowed_values": [1, 2]}, "decimal"),
        ({"allowed_values": []}, "decimal"),
    ],
)
def test_validate_allowed_values_invalid_case(invalid_rules, column_type):
    with pytest.raises(YAMLContractError):
        validate_allowed_values(invalid_rules, column_type)


@pytest.mark.parametrize(
    "raw_rules, expected_rules",
    [
        (
            {"max": 5, "min": 2, "allowed_values": [1, 2]},
            {
                "max": Decimal("5"),
                "min": Decimal("2"),
                "allowed_values": [Decimal("1"), Decimal("2")],
            },
        ),
        (
            {"max": 5.5, "min": 2.5, "allowed_values": [1.5, 2.5]},
            {
                "max": Decimal("5.5"),
                "min": Decimal("2.5"),
                "allowed_values": [Decimal("1.5"), Decimal("2.5")],
            },
        ),
        (
            {
                "max": "5",
                "min": "2",
                "allowed_values": ["1", "2"],
            },
            {
                "max": Decimal("5"),
                "min": Decimal("2"),
                "allowed_values": [Decimal("1"), Decimal("2")],
            },
        ),
    ],
)
def test_convert_rules_to_decimal_valid_case(raw_rules, expected_rules):
    result = convert_rules_to_decimal(raw_rules)

    assert result == expected_rules


@pytest.mark.parametrize(
    "date, date_format",
    [
        (["20/12/2000"], "%Y-%m-%d"),
        (["20-12-2000"], "%Y/%m/%d"),
        (["20/12/2000"], "%d-%m-%Y"),
        (["20-12-2000", "20/12/2000"], "%d-%m-%Y"),
    ],
)
def test_convert_date_in_allowed_values_invalid_case(date, date_format):
    with pytest.raises(YAMLContractError):
        convert_dates_in_allowed_values(date, date_format)


def test_convert_date_in_allowed_values():
    valid_date = ["20/12/2000", "20/12/2001"]
    date_format = "%d/%m/%Y"
    result = convert_dates_in_allowed_values(valid_date, date_format)
    assert result == [date(2000, 12, 20), date(2001, 12, 20)]
