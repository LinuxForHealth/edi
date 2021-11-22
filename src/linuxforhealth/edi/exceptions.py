class EdiException(Exception):
    """
    Base class for EDI Exceptions
    """

    pass


class EdiAnalysisException(Exception):
    """
    Raised when an exception occurs during the analysis phase.
    """

    pass


class EdiValidationException(Exception):
    """
    Raised when an exception occurs during the validation phase.
    """

    pass
