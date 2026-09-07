from data_contract_cli.contract_models import Contract, Columns_Contract
from data_contract_cli.validate_csv import get_invalid_rows, get_valid_rows
from data_contract_cli.structure_example import structure, contrate
from data_contract_cli.orchestration import orchestration
from data_contract_cli.exceptions import CSVError
from datetime import date
import datetime
from data_contract_cli.value_transformations import (
    validate_str,
    convert_str_to_int,
    convert_str_to_decimal,
    convert_str_to_bool,
    validate_email_value,
    validate_date,
    remove_accents,
    normalize_date,
    format_decimal,
    apply_allowed_values_rule,
    apply_string_transformations,
    apply_ends_with_rule,
    apply_max_length_rule,
    apply_max_rule,
    apply_min_length_rule,
    apply_min_rule,
    apply_regex_rule,
    apply_starts_with_rule,
    process_value,
)
from pathlib import Path
from decimal import Decimal, DecimalException
from email_validator import EmailNotValidError
import re


def obtains_column_contract(
    contract: Contract, column_name: str, errors: list
) -> Columns_Contract | None:
    for key, column_contract in contract.columns.items():
        if key == column_name:
            return column_contract
    errors.append(
        f"CSV column and values is deconnected from columns in contract :{column_name}"
    )


ProcessedValue = int | Decimal | str | bool


def process_value_and_collect_errors(
    column, value, errors: list
) -> ProcessedValue | list:
    try:
        validated_value = process_value(column=column, value=value)
        if validated_value is None:
            return value
        else:
            return validated_value

    except (
        ValueError,
        DecimalException,
        EmailNotValidError,
    ) as error:
        errors.append(
            f"Value '{value}' cannot be converted to type "
            f"'{column.column_type}': {error}"
        )
    return errors


def is_nullable(value: str, errors: list, index: int, column_name: str) -> None:
    if value.strip() == "":
        errors.append(
            f"Value in row index: '{index}' and column: '{column_name}' is nullable'."
        )


Validated_Value = int | Decimal | str | bool


def apply_transformations(
    column: Columns_Contract, validated_value: Validated_Value
) -> Validated_Value:
    """Apply the configured transformations to a value."""
    if (
        column.column_type in ("str", "email")
        and column.transformations
        and isinstance(validated_value, str)
    ):
        return apply_string_transformations(
            transformations=column.transformations,
            value=validated_value,
        )

    elif (
        column.column_type == "decimal"
        and column.transformations
        and isinstance(validated_value, Decimal)
    ):
        return format_decimal(validated_value)

    elif (
        column.column_type == "date"
        and column.transformations
        and column.date_format
        and isinstance(validated_value, str)
    ):
        return normalize_date(validated_value, column.date_format)

    return validated_value


def apply_rules(
    column: Columns_Contract,
    validated_value: Validated_Value,
    errors: list,
) -> Validated_Value | list[str]:
    """Apply the configured rules to a value."""
    if (
        column.column_type == "str"
        and column.rules
        and isinstance(validated_value, str)
    ):
        if "max_length" in column.rules:
            is_value_valid = apply_max_length_rule(
                value=validated_value,
                max_length_rules=column.rules["max_length"],
            )
            if is_value_valid is not None:
                errors.append(is_value_valid)

        if "min_length" in column.rules:
            is_value_valid = apply_min_length_rule(
                value=validated_value,
                min_length_rules=column.rules["min_length"],
            )
            if is_value_valid is not None:
                errors.append(is_value_valid)

        if "regex" in column.rules:
            is_value_valid = apply_regex_rule(
                value=validated_value, regex=column.rules["regex"]
            )
            if is_value_valid is not None:
                errors.append(is_value_valid)

        if "starts_with" in column.rules:
            is_value_valid = apply_starts_with_rule(
                value=validated_value, startwith=column.rules["starts_with"]
            )
            if is_value_valid is not None:
                errors.append(is_value_valid)

        if "ends_with" in column.rules:
            is_value_valid = apply_ends_with_rule(
                value=validated_value, ends_with=column.rules["ends_with"]
            )
            if is_value_valid is not None:
                errors.append(is_value_valid)

        if errors:
            return errors

    elif (
        column.column_type == "int"
        and column.rules
        and isinstance(validated_value, int)
    ):
        if "min" in column.rules:
            is_value_valid = apply_min_rule(
                value=validated_value, min_valid_value=column.rules["min"]
            )
            if is_value_valid is not None:
                errors.append(is_value_valid)

        if "max" in column.rules:
            is_value_valid = apply_max_rule(
                value=validated_value, max_valid_value=column.rules["max"]
            )
            if is_value_valid is not None:
                errors.append(is_value_valid)

        if errors:
            return errors

    try:
        date_format = column.date_format
    except AttributeError:
        date_format = None
    if "allowed_values" in column.rules:
        is_value_valid = apply_allowed_values_rule(
            value=validated_value,
            allowed_values=column.rules["allowed_values"],
            date_format=date_format,
        )
        if is_value_valid is not None:
            errors.append(is_value_valid)

        if errors:
            return errors

    return validated_value


def validate_and_transform_csv_values(classified_rows: dict, contract: Contract):
    cleaned_valid_rows = []
    cleaned_invalid_rows = []

    valid_rows = classified_rows["valid_rows"]
    invalid_rows = classified_rows["invalid_rows"]

    for valid_row in valid_rows:
        errors = []

        for column_name, value in valid_row["column_and_values"].items():
            validated_value = value
            # obtention Columns contract
            column = obtains_column_contract(
                contract=contract, column_name=column_name, errors=errors
            )
            if column == None:
                continue

            # gestion nullable
            if column.nullable is False:
                is_nullable(
                    value=value,
                    errors=errors,
                    index=valid_row.get("index"),
                    column_name=column_name,
                )

            # conversion dans le type réel de la valeur
            processed_value = process_value_and_collect_errors(
                column=column, value=value, errors=errors
            )
            if errors:
                continue

            if not isinstance(processed_value, list):
                validated_value = processed_value

            validated_value = apply_transformations(
                validated_value=validated_value,
                column=column,
            )

            valid_row["column_and_values"][column_name] = validated_value

            apply_rules(
                column=column,
                validated_value=valid_row["column_and_values"][column_name],
                errors=errors,
            )

        if errors:
            invalid_row = get_invalid_rows(
                index=valid_row["index"], row=valid_row["row"], errors=errors
            )
            cleaned_invalid_rows.append(invalid_row)

        else:
            valid_row = {
                "index": valid_row["index"],
                "row": valid_row["row"],
                "column_and_values": valid_row["column_and_values"],
            }

            cleaned_valid_rows.append(valid_row)
    return cleaned_valid_rows, cleaned_invalid_rows


csv = Path("examples") / "example-4.csv"
yaml_contract = Path("examples") / "valid-contract.yaml"

contrat, csv_validate = orchestration(yaml_contract_path=yaml_contract, csv_path=csv)

print(validate_and_transform_csv_values(classified_rows=csv_validate, contract=contrat))
