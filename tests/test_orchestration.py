from textwrap import dedent
from pathlib import Path
import json
from csv_refine.orchestration import orchestration


def test_orchestration_permissive(tmp_path):
    csv_content = """invoice_id,customer_name,email,quantity,amount,invoice_date,paid,status
INV-001,  alice   martin  ,alice.martin@gmail.com,3,1200.5045,05-01-2004,false,paid
INV-002,Bernard   Louis,bernard.louis@outlook.com,2,450.00,05-01-2000,false,pending
,Élodie Laurent,elodie.laurent@gmail.com,0,2500.756,07-01-2000,true,pending
INV-003,chloé   dubois,chloe.dubois@yahoo.com,12,89.9045,05-01-2000,true,paid
INV-004,David Leroy,david.leroy@proton.me,1,240.00,06-01-2000,false,cancelled
INV-002,Marc Dupont,marc.dupont@gmail.com,4,310.499,08-01-2000,true,paid
INV-005,  félix   noël  ,felix.noel@outlook.com,7,315.75,09-01-2000,true,paid
INV-006,,sophie.bernard@gmail.com,5,780.126,10-01-2000,false,pending
INV-007,Lucas Moreau,,6,640.00,11-01-2000,true,paid
INV-008,Emma Petit,emma.petit@yahoo.com ,8,999.995,12-01-2000,false,pending
INV-009,Nicolas Simon,nicolas.simon@Gmail.com,10,1500.40,13-01-2000,true,paid
INV-009,Julie Robert,david.leroy@proton.me,3,525.555,14-01-2000,false,cancelled
INV-011,Thomas Richard,thomas.richard@outlook.com,9,870.49,15-01-2000,true,paid
INv-012,  camille   durand  ,camille.durand@gmail.com,11,1111.111,16-01-2000,false,pending
BAD-015,Hugo Lefevre,hugo.lefevre@yahoo.com,4,430.875,17-01-2000,true,paid
    """

    yaml_content = dedent("""
    delimiter: ","
    encoding: utf-8

    columns:
        invoice_id:
            type: str
            nullable: false
            unique: true
            rules: {starts_with: INV-}
            transformations: [upper, strip]

        customer_name:
            type: str
            nullable: true
            unique: true
            rules: {}
            transformations: [strip, collapse_spaces, title]

        email:
            type: email
            nullable: false
            unique: true
            rules: {}
            transformations: [strip, lower]

        quantity:
            type: int
            nullable: true
            unique: false
            rules: {max: 50}
            transformations: []

        amount:
            type: decimal
            nullable: true
            unique: false
            rules: {max: 2000}
            transformations: [format_decimal]

        invoice_date:
            type: date
            date_format: "DD-MM-YYYY"
            nullable: true
            unique: false
            rules: {}
            transformations: [normalize_date]

        paid:
            type: bool
            nullable: true
            unique: false
            rules: {}
            transformations: []

        status:
            type: str
            nullable: true
            unique: false
            rules: {}
            transformations: [strip, lower]
    """)
    csv_path = tmp_path / "test.csv"
    csv_path.write_text(csv_content, encoding="utf-8")

    yaml_path = tmp_path / "yaml_contract.yaml"
    yaml_path.write_text(yaml_content, encoding="utf-8")

    output = Path(tmp_path) / "output"

    report, html_output = orchestration(
        yaml_contract_path=yaml_path,
        csv_path=csv_path,
        output=output,
        mode="permissive",
    )
    valid_csv = output / "validated_test.csv"
    valid_csv = valid_csv.read_text(encoding="utf-8")
    errors = output / "errors_test.csv"
    errors_csv = errors.read_text(encoding="utf-8")
    json_report = output / "test.json"
    json_report = json.loads(json_report.read_text(encoding="utf-8"))
    html_report = output / "test.html"
    html_report = html_report.read_text(encoding="utf-8")

    assert (
        valid_csv
        == "invoice_id,customer_name,email,quantity,amount,invoice_date,paid,status\n"
        "INV-001,Alice Martin,alice.martin@gmail.com,3,1200.50,2004-01-05,False,paid\n"
        "INV-002,Bernard Louis,bernard.louis@outlook.com,2,450.00,2000-01-05,False,pending\n"
        "INV-003,Chlo\xe9 Dubois,chloe.dubois@yahoo.com,12,89.90,2000-01-05,True,paid\n"
        "INV-004,David Leroy,david.leroy@proton.me,1,240.00,2000-01-06,False,cancelled\n"
        "INV-005,F\xe9lix No\xebl,felix.noel@outlook.com,7,315.75,2000-01-09,True,paid\n"
        "INV-006,,sophie.bernard@gmail.com,5,780.13,2000-01-10,False,pending\n"
        "INV-008,Emma Petit,emma.petit@yahoo.com,8,1000.00,2000-01-12,False,pending\n"
        "INV-009,Nicolas Simon,nicolas.simon@gmail.com,10,1500.40,2000-01-13,True,paid\n"
        "INV-011,Thomas Richard,thomas.richard@outlook.com,9,870.49,2000-01-15,True,paid\n"
        "INV-012,Camille Durand,camille.durand@gmail.com,11,1111.11,2000-01-16,False,pending\n"
    )
    assert (
        errors_csv
        == "invoice_id,customer_name,email,quantity,amount,invoice_date,paid,status,errors\n"
        ",\xc9lodie Laurent,elodie.laurent@gmail.com,0,2500.756,07-01-2000,true,pending,\"Value at row 3, column 'invoice_id', cannot be null.\""
        "\nINV-002,Marc Dupont,marc.dupont@gmail.com,4,310.50,2000-01-08,True,paid,Value: 'INV-002' in column: 'invoice_id' isn't unique.\n"
        "INV-007,Lucas Moreau,,6,640.00,11-01-2000,true,paid,\"Value at row 9, column 'email', cannot be null. | Value '' cannot be converted or validated to type: 'email'.\""
        "\nINV-009,Julie Robert,david.leroy@proton.me,3,525.56,2000-01-14,False,cancelled,Value: 'INV-009' in column: 'invoice_id' isn't unique. | Value: 'david.leroy@proton.me' in column: 'email' isn't unique."
        "\nBAD-015,Hugo Lefevre,hugo.lefevre@yahoo.com,4,430.875,17-01-2000,true,paid,Value 'BAD-015' does not match startwith pattern 'INV-'.\n"
    )
    assert json_report["status"] == "completed_with_errors"
    assert json_report["valid_rows"] == 10
    assert json_report["invalid_rows"] == 5
    assert json_report["total_errors"] == 7
    assert "CSV Refine Report" in html_report
    assert "Completed with errors" in html_report
    assert "Mode: permissive" in html_report
    assert "Valid rows: <strong>10</strong>" in html_report
    assert "Invalid rows: <strong>5</strong>" in html_report
    assert "Total errors: 7" in html_report
    assert isinstance(report, dict)
    assert isinstance(html_output, Path)
