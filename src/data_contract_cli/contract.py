from data_contract_cli.exceptions import ApplicationError, YAMLContractError
from data_contract_cli.contract_models import (
    Contract,
    Columns_Contract,
    VALID_DATE_FORMAT,
)
from datetime import date, datetime
from pathlib import Path
from decimal import Decimal, InvalidOperation
import logging, re, yaml

VALID_TYPE = [
    "str",
    "int",
    "decimal",
    "bool",
    "date",
    "email",
]
TRANSFORMATION = [
    "strip",
    "lower",
    "upper",
    "title",
    "collapse_spaces",
    "remove_accent",
    "format_decimal",
    "normalize_date",
]
RULES = [
    "min",
    "max",
    "min_length",
    "max_length",
    "allowed_values",
    "regex",
    "starts_with",
    "ends_with",
]


logger = logging.getLogger(__name__)


def load_contract(path: Path) -> dict:
    """Load and parse a YAML contract file."""
    if not path.is_file():
        raise YAMLContractError(f"file: {path}, isn't file")

    if path.suffix != ".yaml":
        raise YAMLContractError(f"file: {path} arn't yaml contract")

    if path.stat().st_size == 0:
        raise YAMLContractError(f"file: {path} is empty")

    with path.open("r", encoding="utf-8") as contract_file:
        raw_contract = yaml.safe_load(contract_file)
        logger.info("Contract loaded successfully")
        return raw_contract


def validate_global_structure(raw_contract: dict) -> dict:
    """Validate that the YAML contract is a dictionary."""
    if isinstance(raw_contract, dict):
        return raw_contract

    else:
        raise YAMLContractError(
            f"file: {raw_contract} have an invalid structure, need a dict"
        )


def resolve_delimiter(raw_contract: dict) -> str:
    for key, value in raw_contract.items():
        if key == "delimiter":
            if value not in (",", ";"):
                raise YAMLContractError(f"Key '{key}' has an invalid value.")
            return value
    return ","


def resolve_encoding(raw_contract: dict) -> str:
    for key, value in raw_contract.items():
        if key == "encoding":
            if value not in ("utf-8", "utf-8-sig"):
                raise YAMLContractError(f"Key '{key}' has an invalid value.")
            return value
    return "utf-8"


def extract_columns(raw_contract: dict) -> dict:
    """Remove the top-level columns wrapper from the YAML contract."""
    structured_yaml_contract = {}

    if "columns" in raw_contract:
        if not isinstance(raw_contract["columns"], dict):
            raise YAMLContractError(f"invalid yaml contract, key: 'columns' isn't dict")
    else:
        raise YAMLContractError(f"invalid yaml contract, key: 'columns' missing")

    columns = raw_contract["columns"]

    for column_name, metadata in columns.items():
        structured_yaml_contract[column_name] = metadata

    return structured_yaml_contract


def validate_internal_structure(column_names: str, metadata: dict) -> None:
    """Validate the columns names, structure and the metadata structure."""
    if not isinstance(column_names, str):
        raise YAMLContractError(
            f"Column name must be a string, got {type(column_names).__name__}."
        )

    if column_names is not None:
        column_names = column_names.strip()

    if column_names == "":
        raise YAMLContractError(f"'{column_names}' Column name is invalid")

    elif not isinstance(column_names, str):
        raise YAMLContractError(f"{column_names} the column structure isn't a dict")

    elif not isinstance(metadata, dict):
        raise YAMLContractError(f"{metadata} isn't dict")


def validate_type(metadata: dict) -> str:
    """Validate and normalize the declared column type."""
    if "type" not in metadata:
        raise YAMLContractError(f"Column metadata must include a 'type' field.")

    raw_type = metadata["type"]

    if not isinstance(raw_type, str):
        raise YAMLContractError(
            f"Column type must be a string, got {type(raw_type).__name__}"
        )

    raw_type = raw_type.strip().lower()

    if not raw_type:
        raise YAMLContractError(f"Column type must be a string, got")

    if raw_type not in VALID_TYPE:
        raise YAMLContractError(
            f"Unsupported column type '{raw_type}'. "
            f"Please enter a valid type: {sorted(VALID_TYPE)}"
        )

    metadata["type"] = raw_type

    return metadata["type"]


def validate_column_flags(metadata: dict) -> dict:
    """Validate and add default values for column flags."""
    if "required" not in metadata:
        metadata["required"] = False

    else:
        if not isinstance(metadata["required"], bool):
            raise YAMLContractError("The 'required' flag must be a boolean.")

    if "nullable" not in metadata:
        metadata["nullable"] = False

    else:
        if not isinstance(metadata["nullable"], bool):
            raise YAMLContractError("The 'nullable' flag must be a boolean.")

    if "unique" not in metadata:
        metadata["unique"] = False

    else:
        if not isinstance(metadata["unique"], bool):
            raise YAMLContractError("The 'unique' flag must be a boolean.")

    return metadata


def validate_rules_structure(column: str, metadata: dict) -> dict:
    """Validate the rules structure and return an empty dictionary when absent."""
    rules = metadata.get("rules")

    if rules is None:
        rules = {}

    if not isinstance(rules, dict):
        raise YAMLContractError(f"Rules for column '{column}' must be a dictionary.")

    return rules


def normalize_rule_names(rules: dict) -> dict:
    """Validate and normalize rule names by stripping whitespace and converting them to lowercase."""
    normalized_rules = {}

    for rule_name, value in rules.items():
        if not isinstance(rule_name, str):
            raise YAMLContractError(
                f"Rule name must be a string, got {type(rule_name).__name__}."
            )

        rule_name = rule_name.strip().lower()
        normalized_rules[rule_name] = value

    return normalized_rules


def validate_rules(normalized_rules) -> None:
    """Validate rule names and their expected value types."""
    errors = []
    for key, value in normalized_rules.items():
        if key not in RULES:
            errors.append(f"Unsupported rule '{key}'.")

        if key in ("min", "max"):
            if not isinstance(value, (int, Decimal)):
                errors.append(f"Rule '{key}' must have a numeric value.")

        elif key in ("min_length", "max_length"):
            if not isinstance(value, int):
                errors.append(f"Rule '{key}' must have an integer value.")

        elif key == "allowed_values":
            if not isinstance(value, list):
                errors.append(f"Rule '{key}' must have a list value.")

        else:
            if not isinstance(value, str):
                errors.append(f"Rule '{key}' must have a string value.")

    if errors:
        raise YAMLContractError(errors)


def convert_rules_to_decimal(rules: dict) -> dict:
    """Convert numeric rule values to Decimal instances."""
    for rule_name, rule_value in rules.items():
        if rule_name not in ("min", "max", "allowed_values"):
            continue

        if isinstance(rule_value, list):
            converted_values = []

            for raw_value in rule_value:
                try:
                    decimal_value = Decimal(str(raw_value))
                except InvalidOperation:
                    raise YAMLContractError(
                        f"rules value '{raw_value} can't be converted in decimal"
                    )
                converted_values.append(decimal_value)

            if rule_name == "allowed_values":
                rules["allowed_values"] = converted_values

        else:
            try:
                decimal_value = Decimal(str(rule_value))
            except InvalidOperation:
                raise YAMLContractError(
                    f"rules value '{rule_value}' can't be converted in decimal"
                )
            rules[rule_name] = decimal_value

    return rules


def validate_regex(rules: dict) -> None:
    """Validate that the regex rule is non-empty and syntactically valid."""
    for rule_name, rule_value in rules.items():
        if not rule_name == "regex":
            continue

        if rule_value.strip() == "":
            raise YAMLContractError("Regex rule cannot be empty.")

        try:
            re.compile(rule_value)

        except re.error:
            raise YAMLContractError(f"invalid regex: {rule_value}")


def validate_allowed_values(
    rules: dict,
    column_type: str,
) -> None:
    """Validate that allowed values match the declared column type."""
    for rule_name, allowed_values in rules.items():
        if not rule_name == "allowed_values":
            continue

        if len(allowed_values) == 0:
            raise YAMLContractError("The 'allowed_values' rule cannot be empty.")

        for item in allowed_values:

            if column_type in ("str", "email"):
                if not isinstance(item, str):
                    raise YAMLContractError(
                        f"column type: {column_type} and type in allowed values need to be same."
                    )

            if column_type == "int":
                if not isinstance(item, int) or isinstance(item, bool):
                    raise YAMLContractError(
                        f"column type: {column_type} and type in allowed values need to be same."
                    )

            if column_type == "decimal":
                if not isinstance(item, Decimal):
                    raise YAMLContractError(
                        f"column type: {column_type} and type in allowed values need to be same."
                    )

            if column_type == "bool":
                if not isinstance(item, bool):
                    raise YAMLContractError(
                        f"column type: {column_type} and type in allowed values need to be same."
                    )


def convert_dates_in_allowed_values(allowed_values: list, date_format: str) -> list:
    """Convert date strings in allowed values to date objects."""
    cleaned_allowed_values = []
    for date_value in allowed_values:
        if isinstance(date_value, date):
            cleaned_allowed_values.append(date_value)
            continue

        try:
            date_value = datetime.strptime(date_value, date_format).date()
        except (TypeError, ValueError):
            raise YAMLContractError(
                f"Values in 'allowed_values' must be valid dates matching the format '{date_format}'."
            )
        cleaned_allowed_values.append(date_value)
    return cleaned_allowed_values


def verify_rules_type(normalized_rules: dict, column_type: str) -> None:
    """Validate that each rule is compatible with the declared column type."""
    errors = []

    for rule_name in normalized_rules:
        if column_type in ("int", "decimal") and rule_name not in (
            "min",
            "max",
            "allowed_values",
        ):
            errors.append(
                f"Column type '{column_type}' only supports "
                "'min', 'max', and 'allowed_values' rules."
            )

        elif column_type in ("str", "email") and rule_name not in (
            "min_length",
            "max_length",
            "allowed_values",
            "regex",
            "starts_with",
            "ends_with",
        ):
            errors.append(
                f"Column type '{column_type}' only supports "
                "'min_length', 'max_length', 'allowed_values', "
                "'regex', 'starts_with', and 'ends_with' rules."
            )

        elif column_type in ("bool", "date") and rule_name != "allowed_values":
            errors.append(
                f"Column type '{column_type}' only supports "
                "the 'allowed_values' rule."
            )

    if errors:
        raise YAMLContractError(errors)


def validate_contract_transformation(metadata: dict) -> list:
    """Validate the transformations structure and return an empty list when absent."""
    transformations = metadata.get("transformations")

    if transformations is None:
        return []

    if not isinstance(transformations, list):
        raise YAMLContractError("The 'transformations' field must be a list.")

    for transformation in transformations:
        if not isinstance(transformation, str):
            raise YAMLContractError("Every transformation must be a string.")

    return transformations


def normalize_transformations(transformations: list) -> list:
    """Normalize transformation names by trimming whitespace and using lowercase."""
    normalized_transformations = []

    for transformation in transformations:
        normalized_transformations.append(transformation.strip().lower())

    return normalized_transformations


def validate_transformation(
    normalized_transformations: list,
    column_type: str,
) -> None:
    """Validate that each transformation is compatible with the column type."""
    for transformation in normalized_transformations:
        if transformation not in TRANSFORMATION:
            raise YAMLContractError(f"Unsupported transformation '{transformation}'.")

        if transformation in ("strip", "lower"):
            if column_type not in ("str", "email"):
                raise YAMLContractError(
                    f"Transformation '{transformation}' is not supported "
                    f"for column type '{column_type}'."
                )

        elif transformation in (
            "upper",
            "title",
            "collapse_spaces",
            "remove_accent",
        ):
            if column_type != "str":
                raise YAMLContractError(
                    f"Transformation '{transformation}' requires " "column type 'str'."
                )

        elif transformation == "format_decimal":
            if column_type != "decimal":
                raise YAMLContractError(
                    "Transformation 'format_decimal' requires " "column type 'decimal'."
                )

        elif transformation == "normalize_date":
            if column_type != "date":
                raise YAMLContractError(
                    "Transformation 'normalize_date' requires " "column type 'date'."
                )


def rules_orchestration(column_name: str, metadata: dict) -> dict:
    """Validate and normalize the rules declared for one column."""
    raw_rules = validate_rules_structure(column_name, metadata)

    if not raw_rules:
        return {}

    normalized_rules = normalize_rule_names(raw_rules)
    if metadata["type"] == "decimal":
        normalized_rules = convert_rules_to_decimal(normalized_rules)

    validate_rules(normalized_rules)
    verify_rules_type(normalized_rules, metadata["type"])

    validate_regex(normalized_rules)
    validate_allowed_values(normalized_rules, metadata["type"])

    return normalized_rules


def transformations_orchestration(metadata: dict) -> list:
    """Validate and normalize the transformations declared for one column."""
    raw_transformations = validate_contract_transformation(metadata)
    normalized_transformations = normalize_transformations(raw_transformations)

    validate_transformation(
        normalized_transformations,
        metadata["type"],
    )

    return normalized_transformations


def build_contract(contract: dict) -> Contract:
    """Build a Contract object from validated contract data."""
    columns = {}
    headers = []
    for key, metadata in contract.items():
        if key == "delimiter":
            delimiter = metadata

        elif key == "encoding":
            encoding = metadata

        else:
            column_object = build_column(
                key, metadata, VALID_DATE_FORMAT=VALID_DATE_FORMAT
            )
            headers.append(column_object.column_name)
            columns[key] = column_object

    contract_object = Contract(
        delimiter=delimiter,
        encoding=encoding,
        columns=columns,
        headers=headers,
    )
    return contract_object


def build_column(
    column_name: str, metadata: dict, VALID_DATE_FORMAT: dict
) -> Columns_Contract:
    """Build a Columns_Contract object from validated column metadata."""
    date_format = None
    column_name = column_name
    column_type = metadata["type"]

    if column_type == "date":
        try:
            date_format = VALID_DATE_FORMAT[metadata["date_format"]]
        except KeyError:
            raise YAMLContractError(
                f"date_format: '{metadata.get('date_format')}' is not supported. "
                f"Choose one of: {list(VALID_DATE_FORMAT.keys())}."
            )
        if metadata["rules"].get("allowed_values") is not None:

            allowed_values = metadata["rules"]["allowed_values"]
            normalize_allowed_values = convert_dates_in_allowed_values(
                allowed_values=allowed_values, date_format=date_format
            )
            metadata["rules"]["allowed_values"] = normalize_allowed_values

    required = metadata["required"]
    nullable = metadata["nullable"]
    unique = metadata["unique"]
    rules = metadata["rules"]
    transformations = metadata["transformations"]

    column = Columns_Contract(
        column_name=column_name,
        column_type=column_type,
        date_format=date_format,
        required=required,
        nullable=nullable,
        unique=unique,
        rules=rules,
        transformations=transformations,
    )
    if column_type == "date":
        column.validate_date_format(
            VALID_DATE_FORMAT=VALID_DATE_FORMAT,
            raw_date_format=metadata["date_format"],
        )
    return column


def load_and_validate_contract(path: Path) -> Contract:
    """Load, validate, and normalize the complete YAML contract."""

    validated_contract = {}
    logger.info(f"start validation of yaml")

    raw_contract = load_contract(path)
    validated_structure = validate_global_structure(raw_contract)

    validated_contract["delimiter"] = resolve_delimiter(raw_contract)
    validated_contract["encoding"] = resolve_encoding(raw_contract)

    normalized_contract = extract_columns(validated_structure)

    for column_name, metadata in normalized_contract.items():
        validate_internal_structure(column_name, metadata)

        metadata["type"] = validate_type(metadata)
        metadata = validate_column_flags(metadata)
        metadata["rules"] = rules_orchestration(column_name, metadata)
        metadata["transformations"] = transformations_orchestration(metadata)

        validated_contract[column_name] = metadata

    logger.info("Contract validated successfully")
    contract = build_contract(validated_contract)

    return contract
