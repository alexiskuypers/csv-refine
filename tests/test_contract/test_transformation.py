import pytest, yaml


from csv_refine.exceptions import ApplicationError, YAMLContractError
from csv_refine.contract import (
    TRANSFORMATION,
    validate_contract_transformation,
    normalize_transformations,
    validate_transformation,
)


@pytest.mark.parametrize(
    "valid_transformation, expected_transformations",
    [
        ({"transformations": []}, []),
        ({"type": "str"}, []),
        ({"transformations": ["strip", "upper"]}, ["strip", "upper"]),
    ],
)
def test_validate_contract_transformation(
    valid_transformation, expected_transformations
):
    result = validate_contract_transformation(valid_transformation)
    assert result == expected_transformations


@pytest.mark.parametrize(
    "invalid_transformations",
    [
        {"transformations": [None]},
        {"transformations": [1]},
        {"transformations": ["str", True]},
        {"transformations": {}},
    ],
)
def test_validate_contract_transformation_invalid_case(invalid_transformations):
    with pytest.raises(YAMLContractError):
        validate_contract_transformation(invalid_transformations)


def test_normalize_transformation():
    transformation = ["Strip  ", "  lowER  "]
    result = normalize_transformations(transformation)
    assert result == ["strip", "lower"]


@pytest.mark.parametrize(
    "valid_transformation, valid_type",
    [
        (["upper", "title", "collapse_spaces", "remove_accents"], "str"),
        (["strip", "lower"], "str"),
        (["strip", "lower"], "email"),
        (["format_decimal"], ("decimal")),
        (["normalize_date"], ("date")),
    ],
)
def test_validate_transformation_valid_case(valid_transformation, valid_type):
    result = validate_transformation(valid_transformation, valid_type)
    assert result == None


@pytest.mark.parametrize(
    "invalid_transformation, column_type",
    [
        (["unknow_transformation"], "str"),
        (["strip", "lower"], "int"),
        (["strip", "lower"], "decimal"),
        (["strip", "lower"], "date"),
        (["format_decimal"], "date"),
        (["normalize_date"], "str"),
        (["upper", "title", "collapse_spaces", "remove_accent"], "bool"),
    ],
)
def test_validate_transformation_invalid_case(invalid_transformation, column_type):
    with pytest.raises(YAMLContractError):
        validate_transformation(invalid_transformation, column_type)
