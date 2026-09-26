from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from email_validator import EmailNotValidError, validate_email
from csv_refine.contract_models import Contract, Columns_Contract
import unicodedata
import re


def convert_str_to_int(value: str) -> int:
    """Convert a string value to an integer."""
    return int(value.strip())


def convert_str_to_decimal(value: str) -> Decimal:
    """Convert a string value to a Decimal."""
    return Decimal(str(value).strip())


def convert_str_to_bool(value: str) -> bool:
    """Convert a supported string value to a boolean."""
    if value.strip().lower() in ("true", "1", "y", "yes"):
        return True
    elif value.strip().lower() in ("false", "0", "n", "no"):
        return False
    else:
        raise ValueError


def validate_str(value) -> None:
    """Raise ValueError if the value is not a string."""
    if isinstance(value, str):
        return
    else:
        raise TypeError(f"value: '{value}' is not a string.")


def validate_email_value(mail: str) -> str:
    """Validate and normalize an email address."""
    content = mail.strip()
    result = validate_email(
        content,
        check_deliverability=False,
    )
    return result.normalized


def validate_date(row_date: str, date_format: str) -> None | str:
    """Validate that a date string matches the expected format."""
    try:
        parsed_date = datetime.strptime(row_date.strip(), date_format).date()
    except (ValueError, TypeError):
        return (
            f"Value '{row_date}' cannot be converted or validated to type: 'date'. "
            f"Expected format: '{date_format}'."
        )


def remove_accents(value: str) -> str:
    """Remove accents from a string value."""
    split_value = unicodedata.normalize("NFD", value)
    value_without_accent = "".join(
        char for char in split_value if not unicodedata.combining(char)
    )

    return unicodedata.normalize("NFC", value_without_accent)


def format_decimal(value: Decimal) -> Decimal:
    """Round a decimal value to two decimal places."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def collapse_spaces(value: str) -> str:
    """Collapse consecutive spaces into a single space."""
    cleaned_value = ""

    for index, i in enumerate(value, start=0):
        if i != " ":
            cleaned_value += i
        else:
            if index != 0:
                if value[index - 1] == " ":
                    continue
                else:
                    cleaned_value += i
            else:
                cleaned_value += i
    return cleaned_value


def normalize_date(row_date: str, date_format: str) -> str:
    """Convert a date string to ISO format."""
    parsed_date = datetime.strptime(row_date.strip(), date_format).date()
    return str(parsed_date.isoformat())


def apply_max_length_rule(value: str, max_length_rules: int) -> str | None:
    """Return an error message if the value exceeds the maximum length."""
    if len(value) > max_length_rules:
        return f"Length of value: ({value}) is: '{len(value)}', length max autorized is: {max_length_rules}"
    return None


def apply_min_length_rule(value: str, min_length_rules: int) -> str | None:
    """Return an error message if the value is under the minimum length."""
    if len(value) < min_length_rules:
        return f"Length of value: ({value}) is: '{len(value)}', length min autorized is: {min_length_rules}"
    return None


def apply_regex_rule(value: str, regex: str) -> str | None:
    """Return an error message if the value unmatch with regex pattern."""
    if re.fullmatch(regex, value) is None:
        return f"Value '{value}' does not match regex pattern '{regex}'."
    return None


def apply_starts_with_rule(value: str, startwith: str) -> str | None:
    """Return an error message if the value unmatch with startwith pattern."""
    if not value.startswith(startwith):
        return f"Value '{value}' does not match startwith pattern '{startwith}'."
    return None


def apply_ends_with_rule(value: str, ends_with: str) -> str | None:
    """Return an error message if the value unmatch with endswith pattern."""
    if not value.endswith(ends_with):
        return f"Value '{value}' does not match endswith pattern '{ends_with}'."
    return None


def apply_min_rule(value: int, min_valid_value: int) -> str | None:
    """Return an error message if the value is under the minimal valid value."""
    if value < min_valid_value:
        return f"Value: '{value}' is under the minimum autorized: '{min_valid_value}'"
    return None


def apply_max_rule(value: int, max_valid_value: int) -> str | None:
    """Return an error message if the value is exceeds the maximal valid value."""
    if value > max_valid_value:
        return f"Value: '{value}' exceeds the maximum autorized: '{max_valid_value}'"
    return None


type value = str | int | Decimal | bool


def apply_allowed_values_rule(
    value: value, allowed_values: list, date_format: str | None = None
) -> str | None:
    """Return an error message if the value is not among the allowed values."""
    formatted_date_values = []

    for item in allowed_values:
        if isinstance(item, date) and date_format is not None:
            date_parsed = date.strftime(item, date_format)
            formatted_date_values.append(date_parsed)

    if formatted_date_values:
        if value not in formatted_date_values:
            return f"Value '{value}' is not among the allowed values: {formatted_date_values}."

    elif value not in allowed_values:
        return f"The value  '{value}' not in allowed values: '{allowed_values}'"

    return None


def apply_string_transformations(transformations: list, value: str) -> str:
    """Apply the configured transformations to a string value."""
    if "strip" in transformations:
        value = value.strip()

    if "lower" in transformations:
        value = value.lower()

    if "upper" in transformations:
        value = value.upper()

    if "title" in transformations:
        value = value.title()

    if "collapse_spaces" in transformations:
        value = collapse_spaces(value)

    if "remove_accents" in transformations:
        value = remove_accents(value)

    return value


def process_value(column: Columns_Contract, value: str) -> value:
    """Convert or validate a value according to the column type."""
    converted_value = None
    if column.column_type == "str":
        validate_str(value)

    elif column.column_type == "int":
        converted_value = convert_str_to_int(value)

    elif column.column_type == "decimal":
        converted_value = convert_str_to_decimal(value)

    elif column.column_type == "bool":
        converted_value = convert_str_to_bool(value)

    elif column.column_type == "email":
        validate_email_value(value)

    elif column.column_type == "date" and column.date_format:
        validated_date = validate_date(row_date=value, date_format=column.date_format)
        if isinstance(validated_date, str):
            raise ValueError(validated_date)

    if converted_value is not None:
        return converted_value

    else:
        return value
