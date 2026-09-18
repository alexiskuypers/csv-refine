from data_contract_cli.contract_models import Contract, Columns_Contract
from data_contract_cli.contract import load_and_validate_contract
from data_contract_cli.validate_csv import load_and_validate_csv
from data_contract_cli.row_processing import validate_and_transform_csv_values
from data_contract_cli.validate_unique import validate_unique
from pathlib import Path


def orchestration(yaml_contract_path: Path, csv_path: Path, mode: str):
    yaml_contract = load_and_validate_contract(yaml_contract_path)
    classified_rows = load_and_validate_csv(path=csv_path, contract=yaml_contract)
    cleaned_classified_rows = validate_and_transform_csv_values(
        classified_rows=classified_rows, contract=yaml_contract, mode=mode
    )
    validated_unique = validate_unique(
        contrat=yaml_contract,
        cleaned_classified_rows=cleaned_classified_rows,
        mode=mode,
    )

    return validated_unique


csv = Path("examples") / "example-4.csv"
yaml_contract = Path("examples") / "valid-contract.yaml"
print(orchestration(yaml_contract_path=yaml_contract, csv_path=csv, mode="permissive"))
