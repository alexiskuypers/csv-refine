import csv
from pathlib import Path
import logging
from csv_refine.contract_models import Contract

logger = logging.getLogger(__name__)


def convert_to_str(validated_classified_rows: dict) -> dict:
    """Return classified rows with all values converted to strings."""
    valid_rows = validated_classified_rows["valid_rows"]
    invalid_rows = validated_classified_rows["invalid_rows"]

    for valid_row in valid_rows:
        for column_name, value in valid_row["column_and_values"].items():
            if not isinstance(value, str):
                valid_row["column_and_values"][column_name] = str(value)

    return validated_classified_rows


def prepare_csv_rows(validated_classified_rows: dict) -> list:
    """Return rows ready to be written to a CSV file."""
    normalized_data = []
    valid_rows = validated_classified_rows["valid_rows"]

    for valid_row in valid_rows:
        normalized_data.append(valid_row["column_and_values"])

    return normalized_data


def write_csv(
    validated_classified_rows: dict, contract: Contract, csv_output: Path
) -> None:
    """Write validated rows to the output CSV file."""
    logger.info(f"Starting validated CSV export.")
    validated_classified_rows = convert_to_str(validated_classified_rows)
    csv_ready_data = prepare_csv_rows(
        validated_classified_rows=validated_classified_rows
    )

    csv_output.parent.mkdir(parents=True, exist_ok=True)

    headers = contract.headers

    with csv_output.open("x", encoding=contract.encoding, newline="") as csv_file:
        csv_writer = csv.DictWriter(
            csv_file, fieldnames=headers, delimiter=contract.delimiter
        )
        csv_writer.writeheader()
        csv_writer.writerows(csv_ready_data)
    logger.info(f"Validated CSV successfully written to '{csv_output}'.")
