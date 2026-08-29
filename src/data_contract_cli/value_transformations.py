from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from email_validator import EmailNotValidError, validate_email
import unicodedata


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


def validate_date(row_date: str, date_format: str) -> str:
    """Validate that a date string matches the expected format."""
    datetime.strptime(row_date.strip(), date_format)
    return row_date.strip()


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
    date = datetime.strptime(row_date.strip(), date_format).date()
    return date.isoformat()


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


# Functions apply rules.
