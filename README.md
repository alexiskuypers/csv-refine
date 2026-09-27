# CSV Refine

CSV Refine is a Python CLI for cleaning, filtering, and normalizing CSV files.

It lets you define exactly how each column should be validated, cleaned, and normalized through a YAML contract. CSV Refine then separates valid and invalid rows and generates reports to assess the overall health of the dataset.

## Features

- Clean and normalize messy CSV data
- Filter out invalid rows while preserving valid data
- Detect missing values, duplicates, invalid formats, and rule violations
- Separate valid and invalid rows into dedicated CSV files
- Generate JSON and HTML reports to assess CSV data quality

## Installation

Install CSV Refine from PyPI:

```bash
pip install csv-refine
```

Check the CLI:

```bash
csv-refine --help
```

## Quick start

```bash
csv-refine \
  --contract examples/01-input/example-contract.yaml \
  --csv examples/01-input/example.csv \
  --mode permissive
```

By default, generated files are written to `output/`.

A custom output directory can be provided with `--output`.

## YAML contract

CSV Refine is configured through a YAML contract that defines exactly how each column should be validated and normalized.

A contract can define data types, nullability, uniqueness, validation rules, transformations, delimiter, and encoding.

Example:

```yaml
columns:
  Transaction ID:
    type: str
    nullable: false
    unique: true
    rules:
      starts_with: "TXN_"
```

For the complete contract syntax and all supported options, see the [contract README](contracts/README.md).

## Validation modes

### Permissive

Invalid rows are collected while processing continues.

### Strict

Structural, type conversion, nullability, and uniqueness failures can stop processing.

Validation-rule violations still act as row filters.

## Outputs

CSV Refine generates:

```text
output/
├── validated_example.csv
├── errors_example.csv
├── example.json
└── example.html
```

- **Validated CSV** — valid rows with transformations applied
- **Error CSV** — invalid rows with their detected errors
- **JSON report** — machine-readable summary
- **HTML report** — human-readable overview of CSV health

The original CSV is never modified.

## Real-world example

The repository includes a 200-row retail dataset containing missing values, invalid categories, malformed identifiers, duplicate values, invalid dates, and conversion errors.

```text
examples/
├── 01-input/
│   ├── example.csv
│   └── example-contract.yaml
└── 02-expected-output/
    ├── validated_example.csv
    ├── errors_example.csv
    ├── example.json
    └── example.html
```

Run the example with:

```bash
csv-refine \
  --contract examples/01-input/example-contract.yaml \
  --csv examples/01-input/example.csv \
  --mode permissive
```

Example result:

```text
Total rows:    200
Valid rows:    133
Invalid rows:   67
Total errors:  117
```

## Preview

### Raw CSV

The original dataset contains missing values, invalid formats, duplicates, and values that do not comply with the configured data contract.

![Raw CSV input](https://raw.githubusercontent.com/alexiskuypers/csv-refine/main/docs/images/raw-csv.png)

### Validated rows

Rows that successfully pass the contract validation are cleaned, normalized, and written to a dedicated CSV file.

![Validated CSV output](https://raw.githubusercontent.com/alexiskuypers/csv-refine/main/docs/images/validated-csv.png)

### Invalid rows and detected errors

Invalid rows are separated from the validated dataset and include the errors detected during processing.

![CSV errors output](https://raw.githubusercontent.com/alexiskuypers/csv-refine/main/docs/images/errors-csv.png)

### Data quality report

CSV Refine generates an HTML report summarizing the overall quality of the dataset and the errors detected during processing.

![CSV Refine HTML report](https://raw.githubusercontent.com/alexiskuypers/csv-refine/main/docs/images/html-report.png)

## Development

Clone the repository:

```bash
git clone https://github.com/alexiskuypers/csv-refine.git
cd csv-refine

python3 -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
```

## Tests

Run the test suite with:

```bash
python3 -m pytest
```

## Stack

Python 3.12+, PyYAML, email-validator, pytest, argparse, pathlib, logging.

## Status

**Version 0.1.3 is available on [PyPI](https://pypi.org/project/csv-refine/).**
