from datetime import date, datetime
from decimal import Decimal
from email_validator import EmailNotValidError, validate_email


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


def validate_str(values) -> None:
    """Raise ValueError if the value is not a string."""
    if isinstance(values, str):
        return
    else:
        raise ValueError(f"value: '{values}' is not str.")


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


def normalize_date(row_date, date_format: str) -> str:
    """Convert a date string to ISO format."""
    date = datetime.strptime(row_date.strip(), date_format).date()
    return date.isoformat()


print(validate_email_value("  kuypers.a@gmail.com  "))
