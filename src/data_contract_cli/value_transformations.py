from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from email_validator import EmailNotValidError, validate_email
import unicodedata
import re


# Value conversion and validation functions.
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
        raise ValueError(f"Cannot convert '{value}' to boolean.")


def validate_str(value) -> None:
    """Raise ValueError if the value is not a string."""
    if isinstance(value, str):
        return
    else:
        raise ValueError(f"value: '{value}' is not a string.")


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
    except ValueError as e:
        return (
            f"Date '{row_date}' is invalid or does not match "
            f"the expected format '{date_format}'."
        )
    return


# Functions apply transformations.
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
        return f"the value  '{value}' not in allowed values: '{allowed_values}'"

    return None
