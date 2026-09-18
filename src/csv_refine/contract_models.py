from csv_refine.exceptions import YAMLContractError

VALID_DATE_FORMAT = {
    "DD-MM-YYYY": "%d-%m-%Y",
    "DD/MM/YYYY": "%d/%m/%Y",
    "YYYY-MM-DD": "%Y-%m-%d",
    "YYYY/MM/DD": "%Y/%m/%d",
}


class Columns_Contract:
    def __init__(
        self,
        column_name: str,
        column_type: str,
        date_format: str | None = None,
        nullable: bool = False,
        unique: bool = False,
        rules: dict = {},
        transformations: list = [],
    ) -> None:
        self.column_name = column_name
        self.column_type = column_type
        self.nullable = nullable
        self.unique = unique
        self.rules = rules
        self.transformations = transformations
        if column_type == "date":
            self.date_format = date_format

    def __repr__(self) -> str:
        if self.column_type != "date":
            return (
                f"\ncolumn_name: '{self.column_name}',\n"
                f"column_type: '{self.column_type}', \n"
                f"nullable: {self.nullable}, \n"
                f"unique: {self.unique}, \n"
                f"rules : {self.rules}\n"
                f"transformations: {self.transformations},\n"
                f"\n"
            )
        else:
            return (
                f"\ncolumn_name: '{self.column_name}',\n"
                f"column_type: '{self.column_type}', \n"
                f"date_format: '{self.date_format}', \n"
                f"nullable: {self.nullable}, \n"
                f"unique: {self.unique}, \n"
                f"rules : {self.rules}\n"
                f"transformations: {self.transformations},\n"
                f"\n"
            )

    def validate_date_format(self, VALID_DATE_FORMAT, raw_date_format):
        """Raise an error if the date format is not supported."""
        if raw_date_format not in VALID_DATE_FORMAT:
            raise YAMLContractError(
                f"date_format: {raw_date_format} isn't a valid format for date, please choices between '{VALID_DATE_FORMAT.keys()}'."
            )


class Contract:
    def __init__(
        self,
        columns: dict,
        headers: list,
        delimiter: str = ",",
        encoding: str = "utf-8",
    ) -> None:
        self.columns = columns
        self.headers = headers
        self.delimiter = delimiter
        self.encoding = encoding

    def __repr__(self) -> str:
        return (
            f"Delimiter: '{self.delimiter}',\n"
            f"Encoding: '{self.encoding}',\n"
            f"Headers: {self.headers},\n"
            f"Columns:\n{self.columns}"
        )
