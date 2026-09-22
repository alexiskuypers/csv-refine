import csv
import logging
from decimal import Decimal
from pathlib import Path

from csv_refine.contract_models import Contract

logger = logging.getLogger(__name__)


def convert_invalid_row_values_to_str(validated_classified_rows: dict) -> list:
    """Return invalid_rows with all values converted to strings."""
    invalid_rows = validated_classified_rows["invalid_rows"]

    for invalid_row in invalid_rows:
        normalized_row = []
        for value in invalid_row["row"]:
            if not isinstance(value, str):
                normalized_value = str(value)
                normalized_row.append(normalized_value)
            else:
                normalized_row.append(value)
        invalid_row["row"] = normalized_row

    return invalid_rows


def prepare_errors(invalid_rows: list) -> list:
    """Join multiple error messages into a single string."""

    for invalid_row in invalid_rows:
        if len(invalid_row["errors"]) > 1:
            invalid_row["errors"] = [" | ".join(invalid_row["errors"])]

    return invalid_rows


def prepare_csv_rows(invalid_rows: list):
    """Return rows ready to be written to a CSV file."""
    csv_rows = []

    for invalid_row in invalid_rows:
        normalized_row = invalid_row["row"] + invalid_row["errors"]
        csv_rows.append(normalized_row)

    return csv_rows


def write_errors_csv(
    validated_classified_rows: dict,
    contract: Contract,
    output: Path,
    output_filename: str,
):
    """Write invalid rows to the error CSV file."""
    logger.info(f"Starting errors CSV export.")

    invalid_rows = convert_invalid_row_values_to_str(
        validated_classified_rows=validated_classified_rows
    )
    prepared_invalid_rows = prepare_errors(invalid_rows)
    errors_csv_rows = prepare_csv_rows(prepared_invalid_rows)

    headers = contract.headers
    headers.append("errors")

    file_stem = "errors_" + output_filename + ".csv"

    output.mkdir(parents=True, exist_ok=True)
    output = Path(output) / file_stem

    with output.open("x", encoding=contract.encoding, newline="") as errors_csv:
        csv_writer = csv.writer(errors_csv, delimiter=contract.delimiter)
        csv_writer.writerow(headers)
        csv_writer.writerows(errors_csv_rows)

    logger.info(f"Errors CSV successfully written to '{output}'.")
