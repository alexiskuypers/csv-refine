import logging

from data_contract_cli.contract_models import Contract, Columns_Contract
from data_contract_cli.exceptions import CSVError
from data_contract_cli.validate_csv import get_invalid_rows
from data_contract_cli.row_processing import get_column_contract

logger = logging.getLogger(__name__)


def apply_unique_constraints(
    cleaned_classified_rows: dict, column_name: str
) -> list | None:
    """Enforce unique column constraints according to the processing mode."""
    seen_values = set({})
    collected_values = []
    errors = []

    for valid_row in cleaned_classified_rows["valid_rows"]:
        duplicate_errors = []
        for current_column_name, value in valid_row["column_and_values"].items():
            if isinstance(value, str):
                if value.strip() == "":
                    continue
            if current_column_name == column_name:
                seen_values.add(value)
                collected_values.append(value)

                if len(seen_values) != len(collected_values):
                    duplicate_errors.append(
                        f"Value: '{value}' in column: '{column_name}' isn't unique."
                    )
                    errors.append(
                        get_invalid_rows(
                            index=valid_row["index"],
                            row=valid_row["row"],
                            errors=duplicate_errors,
                        )
                    )
                    collected_values.pop()
    if not errors:
        return None

    return errors


def normalized_errors_structure(errors: list[list]) -> list[dict]:
    """Flatten grouped errors into a single list."""
    normalized_errors = []

    for index, error_group in enumerate(errors, start=0):
        if len(error_group) > 1:
            for error in error_group:
                normalized_errors.append(error)

        else:
            normalized_errors.append(errors[index][0])

    return normalized_errors


def group_errors_by_index(errors: list) -> list:
    """Group errors by row index."""
    seen_indices = set({})
    cleaned_errors = []

    for error in errors:
        if error["index"] not in seen_indices:
            cleaned_errors.append(error)
            seen_indices.add(error["index"])

        else:
            for pooled_error in cleaned_errors:
                if pooled_error["index"] == error["index"]:
                    pooled_error["errors"].append(error["errors"][0])

    return cleaned_errors


def rebuild_classified_rows(cleaned_classified_rows: dict, errors: list) -> dict:
    """Build the final structure with valid and invalid rows."""
    invalid_indices = [error["index"] for error in errors]

    validated_classified_rows = {
        "valid_rows": [],
        "invalid_rows": cleaned_classified_rows["invalid_rows"],
    }

    for row in cleaned_classified_rows["valid_rows"]:
        if row["index"] in invalid_indices:

            error = [
                error["errors"] for error in errors if error["index"] == row["index"]
            ]

            normalized_row = get_invalid_rows(
                row=row["row"], index=row["index"], errors=error[0]
            )
            validated_classified_rows["invalid_rows"].append(normalized_row)

        else:
            validated_classified_rows["valid_rows"].append(row)

    return validated_classified_rows


def sort_invalid_rows_by_index(validated_classified_rows: dict) -> dict:
    """Sort invalid rows by index in place and return the updated dictionary."""
    invalid_rows = validated_classified_rows["invalid_rows"]
    invalid_rows = sorted(invalid_rows, key=lambda row: row["index"])
    validated_classified_rows["invalid_rows"] = invalid_rows
    return validated_classified_rows


def validate_unique(
    contrat: Contract, cleaned_classified_rows: dict, mode: str
) -> dict:
    """Orchestrate uniqueness validation."""
    logger.info(f"Starting uniqueness validation.")
    duplicate_errors_by_column = []

    for column_name in contrat.headers:
        column = get_column_contract(column_name=column_name, contract=contrat)

        if column.unique is True:
            error = apply_unique_constraints(
                cleaned_classified_rows=cleaned_classified_rows,
                column_name=column.column_name,
            )

            if error is not None:
                duplicate_errors_by_column.append(error)

    if mode == "strict" and duplicate_errors_by_column:
        raise CSVError(
            f"Duplicate values detected in strict mode. Errors: {duplicate_errors_by_column}"
        )

    if not duplicate_errors_by_column:
        logger.info("Uniqueness validation completed. No duplicates found.")
        return cleaned_classified_rows

    normalized_errors = normalized_errors_structure(duplicate_errors_by_column)
    cleaned_errors = group_errors_by_index(normalized_errors)
    validated_classified_rows = rebuild_classified_rows(
        cleaned_classified_rows=cleaned_classified_rows,
        errors=cleaned_errors,
    )
    validated_classified_rows = sort_invalid_rows_by_index(validated_classified_rows)
    logger.warning(
        f"Uniqueness validation completed with duplicates. "
        f"Errors: {duplicate_errors_by_column}. "
        f"Rows invalidated by duplicates: {len(cleaned_errors)}. "
    )
    return validated_classified_rows
