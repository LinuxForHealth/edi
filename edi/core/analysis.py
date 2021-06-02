from edi.core.models import EdiMessageMetadata


class EdiAnalyzer:
    """
    Parses an EDI Message
    """

    def __init__(self, input_message: str, sample_length: int = 100):
        if not input_message or input_message.isspace():
            raise ValueError("Input message is empty, blank, or None")

        self.input_message = input_message
        self.message_sample = input_message[0:sample_length]

    def analyze(self) -> EdiMessageMetadata:
        pass
