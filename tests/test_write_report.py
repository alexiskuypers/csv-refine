import pytest
import json
from datetime import datetime
from pathlib import Path

from csv_refine.write_report import write_html_report, write_json_report


def test_write_json_report(tmp_path):
    file_stem = "test"
    output = Path(tmp_path)
    report = {"test": 1}

    write_json_report(file_stem=file_stem, output=output, report=report)
    name = file_stem + ".json"
    file_test = output / name
    with open(file_test, "r", encoding="utf-8") as f:
        file_test = json.load(f)
        assert file_test["test"] == 1


def test_write_html_report(tmp_path):
    content = {
        "status": "completed_with_errors",
        "input_file": "tst.csv",
        "mode": "permissive",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "columns_count": 2,
        "delimiter": ",",
        "encoding": "utf-8",
        "total_rows": 5,
        "valid_rows": 2,
        "invalid_rows": 3,
        "valid_rows_percentage": 40.0,
        "total_errors": 5,
        "rows_with_multiple_errors": 2,
        "average_errors_per_invalid_row": 1.67,
        "rules_violations": {
            "max_length": 0,
            "min_length": 0,
            "max": 0,
            "min": 0,
            "starts_with": 0,
            "ends_with": 0,
            "regex": 0,
            "allowed_values": 0,
        },
        "errors_by_category": {
            "rules_violations": 0,
            "conversion_errors": 1,
            "unique_errors": 2,
            "nullable_errors": 2,
        },
        "processing_duration_ms": 1250.78,
    }

    output = tmp_path
    write_html_report(report=content, file_stem="test", output=output)
    file_test = output / "test.html"

    with open(file_test, "r", encoding="utf-8") as f:
        html_content = f.read()
        assert "CSV Refine Report" in html_content
        assert "Completed with errors" in html_content
        assert "Mode: permissive" in html_content
        assert "Encoding: utf-8" in html_content
        assert "Conversion errors" in html_content
        assert "1250.78" in html_content


def test_raise_write_html_report(tmp_path):
    content = {
        "status": "completed_with_errors",
        "input_file": "tst.csv",
        "mode": "permissive",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "columns_count": 2,
        "delimiter": ",",
        "encoding": "utf-8",
        "total_rows": 5,
        "valid_rows": 2,
        "invalid_rows": 3,
        "valid_rows_percentage": 40.0,
        "total_errors": 5,
        "rows_with_multiple_errors": 2,
        "average_errors_per_invalid_row": 1.67,
        "rules_violations": {
            "max_length": 0,
            "min_length": 0,
            "max": 0,
            "min": 0,
            "starts_with": 0,
            "ends_with": 0,
            "regex": 0,
            "allowed_values": 0,
        },
        "errors_by_category": {
            "rules_violations": 0,
            "conversion_errors": 1,
            "unique_errors": 2,
            "nullable_errors": 2,
        },
        "processing_duration_ms": 1250.78,
    }

    output = Path(tmp_path)
    file_stem = "test"
    write_html_report(report=content, output=output, file_stem=file_stem)

    with pytest.raises(FileExistsError):
        write_html_report(report=content, output=output, file_stem=file_stem)


def test_raise_write_json(tmp_path):
    file_stem = "test"
    output = Path(tmp_path)
    report = {"test": 1}

    write_json_report(file_stem=file_stem, output=output, report=report)

    with pytest.raises(FileExistsError):
        write_json_report(file_stem=file_stem, output=output, report=report)
