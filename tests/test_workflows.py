from edi.core.workflows import EdiProcessor


def test_workflow_states(hl7_message):
    edi = EdiProcessor(hl7_message)
    assert edi.state == "init"

    edi.classify()
    assert edi.state == "classified"

    edi.transform()
    assert edi.state == "transformed"

    edi.validate()
    assert edi.state == "validated"

    edi.transmit()
    assert edi.state == "transmitted"

    edi.complete()
    assert edi.state == "completed"


def test_workflow_cancel(hl7_message):
    edi = EdiProcessor(hl7_message)
    edi.classify()
    edi.cancel()
    assert edi.state == "cancelled"
