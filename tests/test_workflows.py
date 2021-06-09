"""
test_workflows.py

Tests the EdiProcessor workflow implementation
"""
from xworkflows.base import InvalidTransitionError

from edi.core.models import (
    BaseMessageType,
    EdiMessageType,
    EdiProcessingMetrics,
    EdiOperations,
)
from edi.core.workflows import EdiProcessor
import pytest


def test_linear_workflow_progression(hl7_message):
    edi = EdiProcessor(hl7_message)
    assert edi.state == "init"
    assert edi.input_message == hl7_message
    assert edi.meta_data is None
    assert edi.metrics == EdiProcessingMetrics(
        analyzeTime=0.0, enrichTime=0.0, validateTime=0.0, translateTime=0.0
    )
    assert edi.operations == []

    edi.analyze()
    assert edi.state == "analyzed"
    assert edi.input_message == hl7_message
    assert edi.operations == ["ANALYZE"]
    assert edi.meta_data is not None

    edi.enrich()
    assert edi.state == "enriched"
    assert edi.operations == ["ANALYZE", "ENRICH"]

    edi.validate()
    assert edi.state == "validated"
    assert edi.operations == ["ANALYZE", "ENRICH", "VALIDATE"]

    edi.translate()
    assert edi.state == "translated"
    assert edi.operations == ["ANALYZE", "ENRICH", "VALIDATE", "TRANSLATE"]

    actual_result = edi.complete()
    assert actual_result.metadata is not None
    assert actual_result.metrics.analyzeTime > 0.0
    assert actual_result.inputMessage == hl7_message
    assert actual_result.operations == [
        "ANALYZE",
        "ENRICH",
        "VALIDATE",
        "TRANSLATE",
        "COMPLETE",
    ]

    assert edi.state == "completed"
    assert edi.operations == [
        "ANALYZE",
        "ENRICH",
        "VALIDATE",
        "TRANSLATE",
        "COMPLETE",
    ]


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
    assert edi.operations == ["ANALYZE", "ENRICH"]


def test_workflow_validate(hl7_message):
    """Validates validate transition invocation"""
    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.validate()
    assert edi.operations == ["ANALYZE", "VALIDATE"]

    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.enrich()
    edi.validate()
    assert edi.operations == ["ANALYZE", "ENRICH", "VALIDATE"]


def test_workflow_translate(hl7_message):
    """Validates translate transition invocation"""
    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.translate()
    assert edi.operations == ["ANALYZE", "TRANSLATE"]

    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.enrich()
    edi.translate()
    assert edi.operations == ["ANALYZE", "ENRICH", "TRANSLATE"]

    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.enrich()
    edi.validate()
    edi.translate()
    assert edi.operations == ["ANALYZE", "ENRICH", "VALIDATE", "TRANSLATE"]


def test_workflow_complete(hl7_message):
    """Validates complete transition invocation"""
    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.complete()
    assert edi.operations == ["ANALYZE", "COMPLETE"]

    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.enrich()
    edi.complete()
    assert edi.operations == ["ANALYZE", "ENRICH", "COMPLETE"]

    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.enrich()
    edi.validate()
    edi.complete()
    assert edi.operations == ["ANALYZE", "ENRICH", "VALIDATE", "COMPLETE"]

    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.enrich()
    edi.validate()
    edi.translate()
    edi.complete()
    assert edi.operations == [
        "ANALYZE",
        "ENRICH",
        "VALIDATE",
        "TRANSLATE",
        "COMPLETE",
    ]


def test_workflow_cancel(hl7_message):
    """Validates cancel transition invocation"""
    edi = EdiProcessor(hl7_message)
    actual_result = edi.cancel()
    assert actual_result.metadata is None
    assert actual_result.metrics.analyzeTime == 0.0
    assert actual_result.inputMessage == hl7_message
    assert actual_result.operations == ["CANCEL"]
    assert len(actual_result.errors) == 0

    assert edi.operations == ["CANCEL"]

    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.cancel()
    assert edi.operations == ["ANALYZE", "CANCEL"]

    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.enrich()
    edi.cancel()
    assert edi.operations == ["ANALYZE", "ENRICH", "CANCEL"]

    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.enrich()
    edi.validate()
    edi.cancel()
    assert edi.operations == ["ANALYZE", "ENRICH", "VALIDATE", "CANCEL"]

    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.enrich()
    edi.validate()
    edi.translate()
    edi.cancel()
    assert edi.operations == [
        "ANALYZE",
        "ENRICH",
        "VALIDATE",
        "TRANSLATE",
        "CANCEL",
    ]


def test_workflow_fail(hl7_message):
    """Validates fail transition invocation"""
    edi = EdiProcessor(hl7_message)
    actual_result = edi.fail("oops", ValueError("something happened"))
    assert actual_result.metadata is None
    assert actual_result.metrics.analyzeTime == 0.0
    assert actual_result.inputMessage == hl7_message
    assert actual_result.operations == ["FAIL"]
    assert actual_result.errors == [{"msg": "oops"}, {"msg": "something happened"}]

    assert edi.operations == ["FAIL"]

    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.enrich()
    actual_result = edi.fail("oops")
    assert actual_result.errors == [{"msg": "oops"}]
    assert edi.operations == ["ANALYZE", "ENRICH", "FAIL"]

    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.enrich()
    edi.validate()
    edi.fail("oops")
    assert edi.operations == ["ANALYZE", "ENRICH", "VALIDATE", "FAIL"]

    edi = EdiProcessor(hl7_message)
    edi.analyze()
    edi.enrich()
    edi.validate()
    edi.translate()
    edi.fail("oops")
    assert edi.operations == [
        "ANALYZE",
        "ENRICH",
        "VALIDATE",
        "TRANSLATE",
        "FAIL",
    ]


def test_workflow_run(hl7_message):
    edi = EdiProcessor(hl7_message)
    edi.run()
    assert edi.operations == [
        EdiOperations.ANALYZE,
        EdiOperations.ENRICH,
        EdiOperations.VALIDATE,
        EdiOperations.TRANSLATE,
        EdiOperations.COMPLETE,
    ]

    edi = EdiProcessor(hl7_message)
    edi.run(enrich=False, translate=False)
    assert edi.operations == [
        EdiOperations.ANALYZE,
        EdiOperations.VALIDATE,
        EdiOperations.COMPLETE,
    ]


def test_workflow_analyze_hl7(hl7_message):
    edi = EdiProcessor(hl7_message)
    edi.analyze()

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

    assert edi.operations == ["ANALYZE"]
    assert edi.metrics.analyzeTime > 0.0


def test_workflow_analyze_x12(x12_message):
    edi = EdiProcessor(x12_message)
    edi.analyze()

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

    assert edi.operations == ["ANALYZE"]
    assert edi.metrics.analyzeTime > 0.0


def test_workflow_analyze_fhir_json(fhir_json_message):
    edi = EdiProcessor(fhir_json_message)
    edi.analyze()

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

    assert edi.operations == ["ANALYZE"]
    assert edi.metrics.analyzeTime > 0.0


def test_workflow_analyze_fhir_xml(fhir_xml_message):
    edi = EdiProcessor(fhir_xml_message)
    edi.analyze()

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

    assert edi.operations == ["ANALYZE"]
    assert edi.metrics.analyzeTime > 0.0
