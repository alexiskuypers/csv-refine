import pytest
from pathlib import Path

from csv_refine.cli import create_parser


def test_create_parser():

    parser = create_parser()

    args = parser.parse_args(
        [
            "--contract",
            "contract.yaml",
            "--csv",
            "data.csv",
            "--mode",
            "strict",
        ]
    )

    assert args.contract == Path("contract.yaml")
    assert args.csv == Path("data.csv")
    assert args.mode == "strict"
    assert args.output == "output"

    import pytest


def test_invalid_mode():

    parser = create_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(
            [
                "--contract",
                "contract.yaml",
                "--csv",
                "data.csv",
                "--mode",
                "false_value",
            ]
        )
