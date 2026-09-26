import time
import logging
from pathlib import Path

from csv_refine.contract import load_and_validate_contract
from csv_refine.validate_csv import load_and_validate_csv
from csv_refine.row_processing import validate_and_transform_csv_values
from csv_refine.validate_unique import validate_unique
from csv_refine.write_csv import write_csv
from csv_refine.write_errors_csv import write_errors_csv
from csv_refine.build_summary import build_report
from csv_refine.write_report import write_json_report, write_html_report

logger = logging.getLogger(__name__)


def orchestration(
    yaml_contract_path: Path, csv_path: Path, mode: str, output: Path
) -> tuple:
    """Orchestrate the entire pipeline."""
    logger.info("Start CSV Refine processing.")
    start_time = time.perf_counter()
    yaml_contract = load_and_validate_contract(yaml_contract_path)
    classified_rows = load_and_validate_csv(path=csv_path, contract=yaml_contract)

    cleaned_classified_rows = validate_and_transform_csv_values(
        classified_rows=classified_rows, contract=yaml_contract, mode=mode
    )

    validated_classified_rows = validate_unique(
        contrat=yaml_contract,
        cleaned_classified_rows=cleaned_classified_rows,
        mode=mode,
    )

    end_time = time.perf_counter()

    report = build_report(
        validated_classified_rows=validated_classified_rows,
        mode=mode,
        contract=yaml_contract,
        csv_name=csv_path.stem,
        duration=(end_time - start_time) * 1000,
    )

    write_csv(
        validated_classified_rows=validated_classified_rows,
        contract=yaml_contract,
        output=output,
        output_filename=csv_path.stem,
    )

    write_errors_csv(
        validated_classified_rows=validated_classified_rows,
        contract=yaml_contract,
        output=output,
        output_filename=csv_path.stem,
    )

    write_json_report(report=report, file_stem=csv_path.stem, output=output)

    html_output = write_html_report(
        report=report, file_stem=csv_path.stem, output=output
    )

    logger.info("CSV Refine processing completed successfully.")
    return report, html_output
