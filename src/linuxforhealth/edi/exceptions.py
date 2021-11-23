class EdiException(Exception):
    """
    Base class for EDI Exceptions
    """

    pass


class EdiAnalysisException(EdiException):
    """
    Raised when an exception occurs during the analysis phase.
    """

    pass


class EdiValidationException(EdiException):
    """
    Raised when an exception occurs during the validation phase.
    """

    pass


class EdiDataValidationException(EdiException):
    """
    Raised when EDI data is invalid. This exception is not specifically tied to the validation phase.
    """

    pass
