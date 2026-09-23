from csv_refine.contract_models import Contract
import datetime


def count_total_errors(validated_classified_rows: dict) -> tuple:
    """Return the total error count and the number of rows with multiple errors."""
    count_errors = 0
    rows_with_multiple_errors = 0

    invalid_rows = validated_classified_rows["invalid_rows"]

    for invalid_row in invalid_rows:
        count_errors += len(invalid_row["errors"])
        if len(invalid_row["errors"]) > 1:
            rows_with_multiple_errors += 1

    return count_errors, rows_with_multiple_errors


def collect_errors(validated_classified_rows: dict):
    """Return the errors collected from all invalid rows."""
    errors = []
    invalid_rows = validated_classified_rows["invalid_rows"]
    for invalid_row in invalid_rows:
        errors.extend(invalid_row["errors"])
    return errors


def count_rules_violations(errors) -> list[tuple]:
    """Count rule violations and return them sorted by frequency."""
    rules_violations = {
        "max_length": 0,
        "min_length": 0,
        "max": 0,
        "min": 0,
        "starts_with": 0,
        "ends_with": 0,
        "regex": 0,
        "allowed_values": 0,
    }
    for error in errors:
        if "length max" in error:
            rules_violations["max_length"] = rules_violations["max_length"] + 1
        if "length min" in error:
            rules_violations["min_length"] = rules_violations["min_length"] + 1
        if "minimum autorized" in error:
            rules_violations["min"] = rules_violations["min"] + 1
        if "maximum autorized" in error:
            rules_violations["max"] = rules_violations["max"] + 1
        if "regex" in error:
            rules_violations["regex"] = rules_violations["regex"] + 1
        if "startwith" in error:
            rules_violations["starts_with"] = rules_violations["starts_with"] + 1
        if "endswith" in error:
            rules_violations["ends_with"] = rules_violations["ends_with"] + 1
        if "allowed values" in error:
            rules_violations["allowed_values"] = rules_violations["allowed_values"] + 1

    return sorted(rules_violations.items(), key=lambda item: item[1], reverse=True)


def count_errors_by_category(errors: list, rules_violations: list[tuple]):
    """Return error counts grouped by category."""
    count_errors_by_category = {
        "rules_violations": sum(values[1] for values in rules_violations),
        "conversion_errors": 0,
        "unique_errors": 0,
        "nullable_errors": 0,
    }
    for error in errors:
        if "cannot be null" in error:
            count_errors_by_category["nullable_errors"] = (
                count_errors_by_category["nullable_errors"] + 1
            )
        if "converted or validated" in error:
            count_errors_by_category["conversion_errors"] = (
                count_errors_by_category["conversion_errors"] + 1
            )
        if "unique" in error:
            count_errors_by_category["unique_errors"] = (
                count_errors_by_category["unique_errors"] + 1
            )

    return count_errors_by_category


def build_report(
    validated_classified_rows: dict,
    mode: str,
    contract: Contract,
    csv_name: str,
    duration: float,
):
    """Build the validation summary report."""
    valid_rows = len(validated_classified_rows["valid_rows"])
    invalid_rows = len(validated_classified_rows["invalid_rows"])

    total_rows = valid_rows + invalid_rows

    count_errors, rows_with_multiple_errors = count_total_errors(
        validated_classified_rows
    )
    collected_errors = collect_errors(validated_classified_rows)
    rule_violations = count_rules_violations(collected_errors)
    errors_by_category = count_errors_by_category(collected_errors, rule_violations)

    if total_rows == 0:
        valid_rows_percentage = 0
    else:
        valid_rows_percentage = valid_rows / total_rows * 100

    if invalid_rows == 0:
        average_errors_per_invalid_row = 0
        status = "passed"
    else:
        average_errors_per_invalid_row = count_errors / invalid_rows
        status = "completed_with_errors"

    report = {
        "status": status,
        "input_file": csv_name,
        "mode": mode,
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "columns_count": len(contract.headers),
        "delimiter": contract.delimiter,
        "encoding": contract.encoding,
        "total_rows": valid_rows + invalid_rows,
        "valid_rows": valid_rows,
        "invalid_rows": invalid_rows,
        "valid_rows_percentage": str(round(valid_rows_percentage, 2)) + " %",
        "total_errors": count_errors,
        "rows_with_multiple_errors": rows_with_multiple_errors,
        "average_errors_per_invalid_row": round(average_errors_per_invalid_row, 2),
        "rules_violations": rule_violations,
        "errors_by_category": errors_by_category,
        "processing_duration_ms": duration,
    }
    return report
