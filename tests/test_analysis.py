from edi.core.analysis import EdiAnalyzer
import pytest


@pytest.mark.parametrize(
    "input_data",
    [
        None,
        "",
        "        ",
    ],
)
def test_init_value_error(input_data):
    with pytest.raises(ValueError):
        EdiAnalyzer(input_message=input_data)


def test_init(hl7_message):
    analyzer = EdiAnalyzer(hl7_message, sample_length=100)
    assert analyzer.input_message == hl7_message
    assert analyzer.message_sample == hl7_message[0:100]
