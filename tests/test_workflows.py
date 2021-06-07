"""
test_workflows.py

Tests the EdiProcessor workflow implementation
"""
from xworkflows.base import InvalidTransitionError

from edi.core.models import BaseMessageType, EdiMessageType
from edi.core.workflows import EdiProcessor
import pytest


def test_workflow_state_progression(hl7_message):
    """Tests linear workflow state transitions"""
    edi = EdiProcessor(hl7_message)
    assert edi.state == "init"

    edi.analyze()
    assert edi.state == "analyzed"
    assert edi.meta_data is not None

    edi.enrich()
    assert edi.state == "enriched"

    edi.validate()
    assert edi.state == "validated"

    edi.translate()
    assert edi.state == "translated"

    edi.complete()
    assert edi.state == "completed"

    edi = EdiProcessor(hl7_message)
    edi.cancel()
    assert edi.state == "cancelled"

    edi = EdiProcessor(hl7_message)
    edi.fail()
    assert edi.state == "failed"


def test_workflow_transition_errors(hl7_message):
    """Simple tests for workflow transition errors"""
    edi = EdiProcessor(hl7_message)

    with pytest.raises(InvalidTransitionError):
        edi.enrich()

    with pytest.raises(InvalidTransitionError):
        edi.validate()

    with pytest.raises(InvalidTransitionError):
        edi.translate()

    with pytest.raises(InvalidTransitionError):
        edi.complete()


def test_workflow_enrich(hl7_message):
    """Validates enrich transition invocation"""
    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.enrich()


def test_workflow_validate(hl7_message):
    """Validates validate transition invocation"""
    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.validate()

    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.enrich()
    edi.validate()


def test_workflow_translate(hl7_message):
    """Validates translate transition invocation"""
    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.translate()

    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.enrich()
    edi.translate()

    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.enrich()
    edi.validate()
    edi.translate()


def test_workflow_complete(hl7_message):
    """Validates complete transition invocation"""
    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.complete()

    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.enrich()
    edi.complete()

    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.enrich()
    edi.validate()
    edi.complete()

    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.enrich()
    edi.validate()
    edi.translate()
    edi.complete()


def test_workflow_cancel(hl7_message):
    """Validates cancel transition invocation"""
    edi = EdiProcessor(hl7_message)
    edi.cancel()

    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.cancel()

    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.enrich()
    edi.cancel()

    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.enrich()
    edi.validate()
    edi.cancel()

    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.enrich()
    edi.validate()
    edi.translate()
    edi.cancel()


def test_workflow_fail(hl7_message):
    """Validates fail transition invocation"""
    edi = EdiProcessor(hl7_message)
    edi.fail()

    edi = EdiProcessor(hl7_message)
    edi.fail()

    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.enrich()
    edi.fail()

    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.enrich()
    edi.validate()
    edi.fail()

    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.enrich()
    edi.validate()
    edi.translate()
    edi.fail()


def test_workflow_analyze_hl7(hl7_message):
    edi = EdiProcessor(hl7_message)
    assert edi.state == "init"

    edi.analyze()
    assert edi.state == "analyzed"

    expected_meta_data = {
        "baseMessageType": BaseMessageType.TEXT,
        "checksum": "dce92fa2bb05ba55f975dcef9e9615d45e33981c36d46895f349886a87364d60",
        "implementationVersions": None,
        "messageSize": 884,
        "messageType": EdiMessageType.HL7,
        "recordCount": 8,
        "specificationVersion": "2.6",
    }
    assert edi.meta_data.dict() == expected_meta_data


def test_workflow_analyze_x12(x12_message):
    edi = EdiProcessor(x12_message)
    assert edi.state == "init"

    edi.analyze()
    assert edi.state == "analyzed"

    expected_meta_data = {
        "baseMessageType": BaseMessageType.TEXT,
        "checksum": "d7a928f396efa0bb15277991bd8d4d9a2506d751f9de8b344c1a3e5f8c45a409",
        "implementationVersions": None,
        "messageSize": 509,
        "messageType": EdiMessageType.X12,
        "recordCount": 17,
        "specificationVersion": "005010X279A1",
    }
    assert edi.meta_data.dict() == expected_meta_data


def test_workflow_analyze_fhir_json(fhir_json_message):
    edi = EdiProcessor(fhir_json_message)
    assert edi.state == "init"

    edi.analyze()
    assert edi.state == "analyzed"

    expected_meta_data = {
        "baseMessageType": BaseMessageType.JSON,
        "checksum": "abdfddcc98c5b57df07e778d2235d391ef5781f067eb84a8bd7413ca8b566002",
        "implementationVersions": [
            "http://hl7.org/fhir/us/someprofile",
            "http://hl7.org/fhir/us/otherprofile",
        ],
        "messageSize": 309,
        "messageType": EdiMessageType.FHIR,
        "recordCount": 1,
        "specificationVersion": "http://hl7.org/fhir",
    }
    assert edi.meta_data.dict() == expected_meta_data


def test_workflow_analyze_fhir_xml(fhir_xml_message):
    edi = EdiProcessor(fhir_xml_message)
    assert edi.state == "init"

    edi.analyze()
    assert edi.state == "analyzed"

    expected_meta_data = {
        "baseMessageType": BaseMessageType.XML,
        "checksum": "c3331c97605865490503e779a697bdeeab5991517ce0655566e23e951b057dfe",
        "implementationVersions": [
            "http://hl7.org/fhir/us/someprofile",
            "http://hl7.org/fhir/us/otherprofile",
        ],
        "messageSize": 607,
        "messageType": EdiMessageType.FHIR,
        "recordCount": 1,
        "specificationVersion": "http://hl7.org/fhir",
    }
    assert edi.meta_data.dict() == expected_meta_data
