class ApplicationError(Exception):
    pass


class YAMLContractError(ApplicationError):
    pass


class CSVError(ApplicationError):
    pass
