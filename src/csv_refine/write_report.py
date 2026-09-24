import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def write_json_report(report: dict, output: Path, file_stem: str) -> None:
    logger.info("Start writing json report.")
    file_name = file_stem + ".json"
    output = Path(output)
    output.mkdir(exist_ok=True, parents=True)
    output = output / file_name

    with output.open("x", encoding="utf-8") as json_file:
        json.dump(
            obj=report,
            fp=json_file,
            indent=4,
            ensure_ascii=False,
        )
    logger.info(f"Json file write successfully. Path: {output}")


def write_html_report(report: dict, output: Path, file_stem: str) -> Path:
    logger.info("Start writing html report.")
    status_class = "status-passed" if report["status"] == "passed" else "status-errors"
    status_text = (
        "Validation passed" if report["status"] == "passed" else "Completed with errors"
    )

    html_content = f"""
        <!DOCTYPE html>
    <html>
    <head>
        <title>CSV Refine Report</title>
        <style>
            body {{
                font-family: Arial, Helvetica, sans-serif;
                margin: 40px;
                max-width: 1000px;
                }}
                h2 {{
                    margin-top: 32px;
                    margin-bottom: 18px;
                    padding-bottom: 6px;

                    border-bottom: 1px solid #1F4E78;
                    width: 75%;
                }}
                p {{
                    margin-left: 32px;
                }}
            table {{
                border-collapse: collapse;
                margin-left: 32px;
                }}
                th,
                td {{
                    border: 1px solid;
                    padding: 8px;
                    text-align: left;
                }}

                th {{
                    background-color: #1F4E78;
                    color: white;
                }}
                .status {{
                    font-weight: bold;
                }}

                .status-passed {{
                    color: #15803D;
                }}

                .status-errors {{
                    color: #B45309;
                }}
        </style>
    </head>

    <body>
        <h1>CSV Refine Report</h1>
        <h2>Status</h2>

                <p class="status {status_class}">
                    {status_text}</p>
                <p>Mode: {report["mode"]}</p>
                <p>Generated at: {report["generated_at"]}</p>
                <p>Processing duration in ms: {report["processing_duration_ms"]}</p>

            <h2>File</h2>
                <p>Input file: {report["input_file"]}</p>
                <p>Columns count: {report["columns_count"]}</p>
                <p>Delimiter: '{report["delimiter"]}'</p>
                <p>Encoding: {report["encoding"]}</p>

            <h2>Summary</h2>

                <p>Total rows: <strong>{report["total_rows"]}</strong></p>
                <p>Valid rows: <strong>{report["valid_rows"]}</strong></p>
                <p>Invalid rows: <strong>{report[ "invalid_rows"]}</strong></p>
                <p>Valid rows percentage: {report["valid_rows_percentage"]}%</p>


            <h2>Errors</h2>

                <p>Total errors: {report["total_errors"]}</p>
                <p>Rows with multiple errors: {report["rows_with_multiple_errors"]}</p>
                <p>Average errors per invalid row: {report["average_errors_per_invalid_row"]}</p>


            <h2>Errors by category</h2>
                <table>
                    <tr>
                        <th>Category</th>
                        <th>Count</th>
                    </tr>
                    <tr>
                        <td>Conversion errors</td>
                        <td>{report["errors_by_category"]["conversion_errors"]}</td>
                    </tr>
                    <tr>
                        <td>Rule violations</td>
                        <td>{report["errors_by_category"]["rules_violations"]}</td>
                    </tr>
                    <tr>
                        <td>Unique errors</td>
                        <td>{report["errors_by_category"]["unique_errors"]}</td>
                    </tr>
                    <tr>
                        <td>Nullable errors</td>
                        <td>{report["errors_by_category"]["nullable_errors"]}</td>
                    </tr>
                </table>

                <h2>Rule violations</h2>
                <table>
                    <tr>
                        <th>Category</th>
                        <th>Count</th>
                    </tr>
                    <tr>
                        <td>Max length</td>
                        <td>{report["rules_violations"]["max_length"]}</td>
                    </tr>
                    <tr>
                        <td>Min length</td>
                        <td>{report["rules_violations"]["min_length"]}</td>
                    </tr>
                    <tr>
                        <td>Max</td>
                        <td>{report["rules_violations"]["max"]}</td>
                    </tr>
                    <tr>
                        <td>Min</td>
                        <td>{report["rules_violations"]["min"]}</td>
                    </tr>
                    <tr>
                        <td>Allowed values</td>
                        <td>{report["rules_violations"]["allowed_values"]}</td>
                    </tr>
                    <tr>
                        <td>Starts with</td>
                        <td>{report["rules_violations"]["starts_with"]}</td>
                    </tr>
                    <tr>
                        <td>Ends with</td>
                        <td>{report["rules_violations"]["ends_with"]}</td>
                    </tr>
                    <tr>
                        <td>Regex</td>
                        <td>{report["rules_violations"]["regex"]}</td>
                    </tr>
                </table>

    </body>
    </html>
    """
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    file_name = file_stem + ".html"
    output = output / file_name
    with output.open("x", encoding="utf-8") as export_html:
        export_html.write(html_content)

    logger.info(f"Html file write successfully. Path: {output}")
    return output
