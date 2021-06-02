from edi.core.workflows import EdiProcessor


def test_workflow_states(hl7_message):
    edi = EdiProcessor(hl7_message)
    assert edi.state == "init"

    edi.analyze()
    assert edi.state == "analyzed"

    edi.transform()
    assert edi.state == "transformed"

    edi.validate()
    assert edi.state == "validated"

    edi.complete()
    assert edi.state == "completed"


def test_workflow_cancel(hl7_message):
    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.cancel()
    assert edi.state == "cancelled"
