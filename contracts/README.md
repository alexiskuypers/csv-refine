# YAML Contract Documentation

The YAML contract defines how a CSV file should be read, validated, and cleaned.

## Contract structure

```yaml
delimiter: ";"
encoding: "utf-8"

columns:
  email:
    type: email
    required: true
    nullable: false
    unique: true

    rules:
      max_length: 255

    transformations:
      - strip
      - lower
```

A contract contains global CSV reading options and a `columns` section. Each column may define a type, options, validation rules, and transformations.

### CSV reading options

| Option      | Supported values         | Default   | Description                           |
| ----------- | ------------------------ | --------- | ------------------------------------- |
| `delimiter` | `","`, `";"`             | `","`     | Character separating CSV fields       |
| `encoding`  | `"utf-8"`, `"utf-8-sig"` | `"utf-8"` | Character encoding of the source file |

Both options are optional. Unsupported values make the contract invalid.

## Supported types

CSV values are initially read as text and temporarily converted when required for validation.

| Type      | Description                      | Example                |
| --------- | -------------------------------- | ---------------------- |
| `str`     | Character string                 | `"Alice"`              |
| `int`     | Integer                          | `"42"` → `42`          |
| `decimal` | Precise decimal number           | `"1200.50"`            |
| `bool`    | Boolean value                    | `"true"` → `True`      |
| `date`    | Valid calendar date              | `"14/06/2026"`         |
| `email`   | String with a valid email format | `"client@example.com"` |

### Date columns

The `date` type validates that each non-empty value represents a real calendar date and matches the format declared in the contract.

Every date column must define a `date_format`. This format must match the representation used in the source CSV and in the column's `allowed_values`, when this rule is configured.

```yaml
invoice_date:
  type: date
  date_format: "DD/MM/YYYY"
  required: true
  nullable: false
  unique: false

  rules:
    allowed_values:
      - "14/06/2026"
      - "15/06/2026"

  transformations:
    - normalize_date
```

Supported date formats:

```text
YYYY-MM-DD
DD/MM/YYYY
YYYY/MM/DD
DD-MM-YYYY
```

By default, a valid date keeps its original representation. When the `normalize_date` transformation is configured, the value is converted to the ISO `YYYY-MM-DD` format.

If date validation is not required, declare the column as `str`. Its values will then be treated as ordinary text without calendar or date-format validation.


## Column options

Options are declared directly under each column name.

| Option     | Description                                              | Example           |
| ---------- | -------------------------------------------------------- | ----------------- |
| `required` | The column must be present in the CSV                    | `required: true`  |
| `nullable` | Cells may be empty                                       | `nullable: false` |
| `unique`   | Duplicate values are rejected from the second occurrence | `unique: true`    |

Example:

```yaml
email:
  type: email
  required: true
  nullable: false
  unique: true
```

## Validation rules

Rules are declared under the `rules` key.

| Rule             | Description                         | Example              |
| ---------------- | ----------------------------------- | -------------------- |
| `min`            | Minimum numeric value               | `min: 18`            |
| `max`            | Maximum numeric value               | `max: 120`           |
| `min_length`     | Minimum number of characters        | `min_length: 3`      |
| `max_length`     | Maximum number of characters        | `max_length: 10`     |
| `allowed_values` | List of accepted values             | `[pending, paid]`    |
| `regex`          | Required regular-expression pattern | `^[A-Z]{2}[0-9]{3}$` |
| `starts_with`    | Required prefix                     | `"INV-"`             |
| `ends_with`      | Required suffix                     | `".py"`              |

Example:

```yaml
rules:
  min: 18
  max: 120
  allowed_values:
    - pending
    - paid
    - cancelled
```

When a rule fails, the row is invalid and the error is added to the CSV error report.

## Transformations

Transformations are applied in their declared order.

| Transformation    | Description                              | Example                              |
| ----------------- | ---------------------------------------- | ------------------------------------ |
| `strip`           | Removes outer whitespace                 | `"  Alice  "` → `"Alice"`            |
| `lower`           | Converts to lowercase                    | `"ALICE"` → `"alice"`                |
| `upper`           | Converts to uppercase                    | `"alice"` → `"ALICE"`                |
| `title`           | Capitalizes each word                    | `"jean dupont"` → `"Jean Dupont"`    |
| `collapse_spaces` | Replaces repeated spaces                 | `"Jean    Dupont"` → `"Jean Dupont"` |
| `remove_accents`  | Removes accents                          | `"Élodie"` → `"Elodie"`              |
| `format_decimal`  | Rounds and formats to two decimal places | `"14.75416"` → `"14.75"`             |
| `normalize_date`  | Converts a date to ISO format            | `"14/06/2026"` → `"2026-06-14"`      |

Example:

```yaml
transformations:
  - strip
  - lower
```

`"  CLIENT@EXAMPLE.COM  "` becomes `"client@example.com"`.

Transformations are applied before type and rule validation. Some transformations temporarily convert values to their corresponding Python type before writing them back as text.
