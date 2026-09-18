import csv
from pathlib import Path
import logging

from data_contract_cli.exceptions import CSVError
from data_contract_cli.contract_models import Contract

logger = logging.getLogger(__name__)


def load_csv(path: Path, contract: Contract) -> dict:
    """Load a CSV file and return its raw headers and rows."""
    raw_csv_rows = []
    if not path.is_file():
        raise CSVError(f"'{path}' isn't a valid file")

    if path.stat().st_size == 0:
        raise CSVError(f"'{path}' is empty")

    with open(
        path,
        "r",
        encoding=contract.encoding,
    ) as csv_file:
        content = csv.reader(csv_file, delimiter=contract.delimiter)

        for row in content:
            raw_csv_rows.append(row)

        headers = raw_csv_rows[0]
        raw_csv_rows.remove(headers)

        return {"headers": headers, "csv_rows": raw_csv_rows}


def validate_headers(raw_structure: dict, contract: Contract) -> None:
    """ "Validate CSV headers against the contract headers."""
    errors = []
    headers = raw_structure["headers"]

    if not isinstance(headers, list):
        raise CSVError(f"CSV headers must be a list, received: {headers}.")

    if len(headers) != len(set(headers)):
        raise CSVError("CSV header names must be unique.")

    if headers == contract.headers:
        return

    for column_name in contract.headers:
        if column_name not in headers:
            errors.append(column_name)
            raise CSVError(f"CSV headers do not match the contract. ")


def is_rows_empty(raw_csv_rows: list) -> None:
    """Raise CSVError if the CSV contains no non-empty data rows."""
    flag = False
    for row in raw_csv_rows:
        for item in row:
            if item.strip() != "":
                flag = True
                return
    if flag is False:
        raise CSVError(f"Csv rows is empty.")


def get_valid_rows(row: list, index: int, contract: Contract) -> dict:
    """Build the structured representation of a valid CSV row."""
    column_and_values = {}

    for second_index, column in enumerate(contract.headers, start=0):
        column_and_values[column] = row[second_index]

    return {"index": index, "row": row, "column_and_values": column_and_values}


def get_invalid_rows(row: list, index: int, errors: list) -> dict:
    """Build the structured representation of an invalid CSV row."""

    return {"index": index, "row": row, "errors": errors}


def separate_csv_rows(contract: Contract, raw_csv_rows: list) -> dict:
    """Validate and separate CSV rows into valid and invalid lists."""
    data_structure = {"valid_rows": [], "invalid_rows": []}
    for index, row in enumerate(raw_csv_rows, start=1):

        errors = []
        if len(row) > len(contract.headers):
            errors.append("Row contains more columns than expected.")

        if len(row) < len(contract.headers):
            errors.append("Row contains fewer columns than expected.")

        if not row:
            errors.append("Row is empty.")

        if errors:
            data_structure["invalid_rows"].append(
                get_invalid_rows(row=row, index=index, errors=errors)
            )

        else:
            data_structure["valid_rows"].append(
                get_valid_rows(row=row, index=index, contract=contract)
            )
    return data_structure


def load_and_validate_csv(
    path: Path,
    contract: Contract,
) -> dict:
    """Load a CSV file, validate its structure, and classify its rows."""
    logger.info(f"Started CSV structural validation: {path}")
    raw_structure = load_csv(path=path, contract=contract)
    validate_headers(raw_structure=raw_structure, contract=contract)
    raw_csv_rows = raw_structure["csv_rows"]
    is_rows_empty(raw_csv_rows)
    classified_rows = separate_csv_rows(raw_csv_rows=raw_csv_rows, contract=contract)

    if len(classified_rows["invalid_rows"]):
        logger.warning(
            "CSV structural validation completed with invalid rows: "
            f"file: {path}, "
            f"total rows: {len(raw_csv_rows)}, "
            f"valid rows: {len(classified_rows['valid_rows'])}, "
            f"invalid rows: {len(classified_rows['invalid_rows'])} "
        )

    else:
        logger.info(
            "CSV structural validation completed successfully: "
            f"file: {path}, "
            f"total rows: {len(raw_csv_rows)}, "
            f"valid rows: {len(classified_rows['valid_rows'])}, "
            f"invalid rows: {len(classified_rows['invalid_rows'])} "
        )

    return classified_rows
