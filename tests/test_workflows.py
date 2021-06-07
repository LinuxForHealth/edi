"""
test_workflows.py

Tests the EdiProcessor workflow implementation
"""
from edi.core.workflows import EdiProcessor


def test_workflow_states(hl7_message):
    edi = EdiProcessor(hl7_message)
    assert edi.state == "init"

    edi.analyze()
    assert edi.state == "analyzed"
