import pytest
from data_contract_cli.validate_unique import (
    apply_unique_constraints,
    normalized_errors_structure,
    group_errors_by_index,
    rebuild_classified_rows,
    validate_unique,
    sort_invalid_rows_by_index,
)
from data_contract_cli.contract_models import Contract, Columns_Contract
from data_contract_cli.validate_csv import get_invalid_rows
from data_contract_cli.exceptions import CSVError


@pytest.fixture
def cleaned_classified_rows() -> dict:
    return {
        "valid_rows": [
            {
                "index": 1,
                "row": [
                    "  INV-002  ",
                    "Bernard Louis",
                    "bernard.louis@outlook.com",
                    2,
                ],
                "column_and_values": {
                    "invoice_id": "  INV-002  ",
                    "customer_name": "Bernard Louis",
                    "email": "bernard.louis@outlook.com",
                    "quantity": 2,
                },
            },
            {
                "index": 2,
                "row": [
                    "INV-004",
                    "David Leroy",
                    "david.leroy@proton.me",
                    2,
                ],
                "column_and_values": {
                    "invoice_id": "INV-004",
                    "customer_name": "David Leroy",
                    "email": "david.leroy@proton.me",
                    "quantity": 2,
                },
            },
            {
                "index": 3,
                "row": [
                    "INV-005",
                    "David Leroy",
                    "david.leroy@proton.me",
                    2,
                ],
                "column_and_values": {
                    "invoice_id": "INV-005",
                    "customer_name": "David Leroy",
                    "email": "david.leroy@proton.me",
                    "quantity": 2,
                },
            },
        ],
        "invalid_rows": [],
    }


@pytest.fixture
def unique_contract() -> Contract:
    return Contract(
        encoding="utf-8",
        delimiter=",",
        headers=["invoice_id", "customer_name", "email", "quantity"],
        columns={
            "invoice_id": Columns_Contract(
                column_name="invoice_id",
                column_type="str",
                unique=True,
            ),
            "customer_name": Columns_Contract(
                column_name="customer_name",
                column_type="str",
                unique=False,
            ),
            "email": Columns_Contract(
                column_name="email",
                column_type="email",
                unique=True,
            ),
            "quantity": Columns_Contract(
                column_name="quantity",
                column_type="int",
                unique=False,
            ),
        },
    )


@pytest.mark.parametrize(
    "column_name, expected",
    [
        (
            "email",
            [
                {
                    "index": 3,
                    "row": [
                        "INV-005",
                        "David Leroy",
                        "david.leroy@proton.me",
                        2,
                    ],
                    "errors": [
                        "Value: 'david.leroy@proton.me' in column: 'email' isn't unique.",
                    ],
                }
            ],
        ),
        (
            "quantity",
            [
                {
                    "index": 2,
                    "row": ["INV-004", "David Leroy", "david.leroy@proton.me", 2],
                    "errors": ["Value: '2' in column: 'quantity' isn't unique."],
                },
                {
                    "index": 3,
                    "row": ["INV-005", "David Leroy", "david.leroy@proton.me", 2],
                    "errors": ["Value: '2' in column: 'quantity' isn't unique."],
                },
            ],
        ),
        ("invoice_id", None),
    ],
)
def test_apply_unique_constraints(cleaned_classified_rows, column_name, expected):
    result = apply_unique_constraints(
        cleaned_classified_rows=cleaned_classified_rows, column_name=column_name
    )

    assert result == expected


def test_apply_unique_constraints_with_empty_value():
    cleaned_classified_rows = {
        "valid_rows": [
            {
                "index": 1,
                "row": [
                    "",
                ],
                "column_and_values": {
                    "invoice_id": "",
                },
            },
            {
                "index": 2,
                "row": [
                    "",
                ],
                "column_and_values": {
                    "invoice_id": "",
                },
            },
        ]
    }
    result = apply_unique_constraints(
        cleaned_classified_rows=cleaned_classified_rows, column_name="invoice_id"
    )
    assert result == None


def test_normalized_errors_structure():
    content = [
        [
            {
                "index": 2,
                "row": [
                    "  INV-002  ",
                    "Bernard Louis",
                    "bernard.louis@outlook.com",
                    2,
                ],
                "errors": [
                    "Value: 'bernard.louis@outlook.com' in column: 'email' isn't unique."
                ],
            },
            {
                "index": 4,
                "row": [
                    "INV-004",
                    "David Leroy",
                    "bernard.louis@outlook.com",
                    2,
                ],
                "errors": [
                    "Value: 'bernard.louis@outlook.com' in column: 'email' isn't unique."
                ],
            },
        ],
        [
            {
                "index": 2,
                "row": [
                    "  INV-002  ",
                    "Bernard Louis",
                    "bernard.louis@outlook.com",
                    2,
                ],
                "errors": ["Value: '1' in column: 'quantity' isn't unique."],
            }
        ],
    ]
    result = normalized_errors_structure(errors=content)
    assert result == [
        {
            "index": 2,
            "row": ["  INV-002  ", "Bernard Louis", "bernard.louis@outlook.com", 2],
            "errors": [
                "Value: 'bernard.louis@outlook.com' in column: 'email' isn't unique."
            ],
        },
        {
            "index": 4,
            "row": ["INV-004", "David Leroy", "bernard.louis@outlook.com", 2],
            "errors": [
                "Value: 'bernard.louis@outlook.com' in column: 'email' isn't unique."
            ],
        },
        {
            "index": 2,
            "row": ["  INV-002  ", "Bernard Louis", "bernard.louis@outlook.com", 2],
            "errors": ["Value: '1' in column: 'quantity' isn't unique."],
        },
    ]


def test_group_error_by_index():
    content = [
        {
            "index": 2,
            "row": ["  INV-002  ", "Bernard Louis", "bernard.louis@outlook.com", 2],
            "errors": [
                "Value: 'bernard.louis@outlook.com' in column: 'email' isn't unique."
            ],
        },
        {
            "index": 4,
            "row": ["INV-004", "David Leroy", "bernard.louis@outlook.com", 2],
            "errors": [
                "Value: 'bernard.louis@outlook.com' in column: 'email' isn't unique."
            ],
        },
        {
            "index": 2,
            "row": ["  INV-002  ", "Bernard Louis", "bernard.louis@outlook.com", 2],
            "errors": ["Value: '1' in column: 'quantity' isn't unique."],
        },
    ]
    result = group_errors_by_index(content)

    assert result == [
        {
            "index": 2,
            "row": [
                "  INV-002  ",
                "Bernard Louis",
                "bernard.louis@outlook.com",
                2,
            ],
            "errors": [
                "Value: 'bernard.louis@outlook.com' in column: 'email' isn't unique.",
                "Value: '1' in column: 'quantity' isn't unique.",
            ],
        },
        {
            "index": 4,
            "row": [
                "INV-004",
                "David Leroy",
                "bernard.louis@outlook.com",
                2,
            ],
            "errors": [
                "Value: 'bernard.louis@outlook.com' in column: 'email' isn't unique."
            ],
        },
    ]


def test_rebuild_classified_rows():
    classified_rows = {
        "valid_rows": [
            {
                "index": 2,
                "row": ["Alice"],
                "column_and_values": {"name": "Alice"},
            },
            {
                "index": 8,
                "row": ["Bob"],
                "column_and_values": {"name": "Bob"},
            },
        ],
        "invalid_rows": [
            {
                "index": 1,
                "row": [""],
                "errors": ["Empty value"],
            },
        ],
    }

    errors = [
        {
            "index": 2,
            "row": ["Alice"],
            "errors": ["Duplicate name", "Another error"],
        },
    ]

    result = rebuild_classified_rows(
        cleaned_classified_rows=classified_rows,
        errors=errors,
    )

    assert result == {
        "valid_rows": [
            {
                "index": 8,
                "row": ["Bob"],
                "column_and_values": {"name": "Bob"},
            },
        ],
        "invalid_rows": [
            {
                "index": 1,
                "row": [""],
                "errors": ["Empty value"],
            },
            {
                "index": 2,
                "row": ["Alice"],
                "errors": ["Duplicate name", "Another error"],
            },
        ],
    }


def test_validate_unique_permissive_mode(cleaned_classified_rows, unique_contract):
    result = validate_unique(
        cleaned_classified_rows=cleaned_classified_rows,
        contrat=unique_contract,
        mode="permissive",
    )
    assert result == {
        "valid_rows": [
            {
                "index": 1,
                "row": ["  INV-002  ", "Bernard Louis", "bernard.louis@outlook.com", 2],
                "column_and_values": {
                    "invoice_id": "  INV-002  ",
                    "customer_name": "Bernard Louis",
                    "email": "bernard.louis@outlook.com",
                    "quantity": 2,
                },
            },
            {
                "index": 2,
                "row": ["INV-004", "David Leroy", "david.leroy@proton.me", 2],
                "column_and_values": {
                    "invoice_id": "INV-004",
                    "customer_name": "David Leroy",
                    "email": "david.leroy@proton.me",
                    "quantity": 2,
                },
            },
        ],
        "invalid_rows": [
            {
                "index": 3,
                "row": ["INV-005", "David Leroy", "david.leroy@proton.me", 2],
                "errors": [
                    "Value: 'david.leroy@proton.me' in column: 'email' isn't unique."
                ],
            }
        ],
    }


def test_validate_unique_strict_mode(cleaned_classified_rows, unique_contract):
    with pytest.raises(CSVError):
        validate_unique(
            cleaned_classified_rows=cleaned_classified_rows,
            contrat=unique_contract,
            mode="strict",
        )


def test_sort_invalid_rows_by_index():
    data = {
        "valid_rows": [
            {
                "index": 1,
                "row": [
                    "INV-001",
                    "Clement Defre",
                ],
                "column_and_values": {
                    "invoice_id": "INV-001",
                    "customer_name": "Clement Defre",
                },
            },
            {
                "index": 3,
                "row": [
                    "INV-003",
                    "Chloe Dubois",
                ],
                "column_and_values": {
                    "invoice_id": "INV-003",
                    "customer_name": "Chloe Dubois",
                },
            },
        ],
        "invalid_rows": [
            {
                "index": 5,
                "row": [
                    "",
                    "Élodie laurent",
                ],
                "errors": ["Value at row 5, column 'invoice_id', cannot be null."],
            },
            {
                "index": 3,
                "row": [
                    "INV-001",
                    "Bernard Louis",
                ],
                "errors": ["Value: 'INV-001' in column: 'invoice_id' isn't unique."],
            },
            {
                "index": 2,
                "row": [
                    "",
                    "Jean Dupont",
                ],
                "errors": ["Value at row 5, column 'invoice_id', cannot be null."],
            },
        ],
    }
    result = sort_invalid_rows_by_index(data)
    assert result == {
        "valid_rows": [
            {
                "index": 1,
                "row": ["INV-001", "Clement Defre"],
                "column_and_values": {
                    "invoice_id": "INV-001",
                    "customer_name": "Clement Defre",
                },
            },
            {
                "index": 3,
                "row": ["INV-003", "Chloe Dubois"],
                "column_and_values": {
                    "invoice_id": "INV-003",
                    "customer_name": "Chloe Dubois",
                },
            },
        ],
        "invalid_rows": [
            {
                "index": 2,
                "row": ["", "Jean Dupont"],
                "errors": ["Value at row 5, column 'invoice_id', cannot be null."],
            },
            {
                "index": 3,
                "row": ["INV-001", "Bernard Louis"],
                "errors": ["Value: 'INV-001' in column: 'invoice_id' isn't unique."],
            },
            {
                "index": 5,
                "row": ["", "\xc9lodie laurent"],
                "errors": ["Value at row 5, column 'invoice_id', cannot be null."],
            },
        ],
    }
