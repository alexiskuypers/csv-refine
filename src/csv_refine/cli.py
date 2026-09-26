import argparse
import logging
import webbrowser
from pathlib import Path

from csv_refine.exceptions import YAMLContractError, CSVError
from csv_refine.logging_config import configure_logging
from csv_refine.orchestration import orchestration

logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="A Python CLI for validating and normalizing CSV files using YAML data contracts.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--contract", type=Path, required=True, help="Path to the YAML contract."
    )

    parser.add_argument(
        "--csv", type=Path, required=True, help="Path to the CSV file to process."
    )

    parser.add_argument(
        "--output",
        help="Output directory.",
        default="output",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["strict", "permissive"],
        help="Validation mode.",
        default="permissive",
    )
    return parser


def run_csv_refine() -> int:
    """Run the CSV Refine CLI and return the appropriate exit code."""
    configure_logging()
    parser = create_parser()
    args = parser.parse_args()

    try:
        report, html_output = orchestration(
            yaml_contract_path=args.contract,
            csv_path=args.csv,
            mode=args.mode,
            output=args.output,
        )

    except YAMLContractError as error:
        logger.error(f"Error(s) caused by contract, error(s): '{error}'.")
        return 1

    except CSVError as error:
        logger.error(f"Error(s) caused by csv, error(s): '{error}'.")
        return 2

    webbrowser.open(html_output.resolve().as_uri())
    print_summary(report=report)
    return 0


def print_summary(report: dict) -> None:
    """Print a concise processing summary for the user."""
    print(
        f"Columns counted: {report['columns_count']}\n"
        f"Total rows: {report['total_rows']}\n"
        f"Total valid rows: {report['valid_rows']}\n"
        f"Errors: {report['total_errors']}."
    )


if __name__ == "__main__":
    raise SystemExit(run_csv_refine())
