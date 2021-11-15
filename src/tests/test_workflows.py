"""
test_workflows.py

Tests the EdiProcessor workflow implementation
"""
from edi.models import (
    BaseMessageFormat,
    EdiMessageFormat,
    EdiProcessingMetrics,
    EdiOperations,
)
from edi.workflows import EdiWorkflow, WorkflowNotActive
import pytest


def test_linear_workflow_progression(hl7_message):
    edi = EdiWorkflow(hl7_message)
    assert edi.input_message == hl7_message
    assert edi.meta_data is None
    assert edi.metrics == EdiProcessingMetrics(
        analyzeTime=0.0, enrichTime=0.0, validateTime=0.0, translateTime=0.0
    )
    assert edi.current_state is None
    assert edi.operations == []

    edi.analyze()
    assert edi.input_message == hl7_message
    assert edi.current_state == EdiOperations.ANALYZE
    assert edi.operations == [EdiOperations.ANALYZE]
    assert edi.meta_data.ediMessageFormat == "HL7"
    assert edi.meta_data.baseMessageFormat == "TEXT"

    edi.enrich()
    assert edi.current_state == EdiOperations.ENRICH
    assert edi.operations == [EdiOperations.ANALYZE, EdiOperations.ENRICH]

    edi.validate()
    assert edi.current_state == EdiOperations.VALIDATE
    assert edi.operations == [
        EdiOperations.ANALYZE,
        EdiOperations.ENRICH,
        EdiOperations.VALIDATE,
    ]
    assert edi.data_model is not None
    assert len(edi.data_model) == 8

    edi.translate()
    assert edi.current_state == EdiOperations.TRANSLATE
    assert edi.operations == [
        EdiOperations.ANALYZE,
        EdiOperations.ENRICH,
        EdiOperations.VALIDATE,
        EdiOperations.TRANSLATE,
    ]

    actual_result = edi.complete()
    assert actual_result.metadata is not None
    assert actual_result.metrics.analyzeTime > 0.0
    assert actual_result.inputMessage == hl7_message
    assert edi.current_state == EdiOperations.COMPLETE
    assert edi.operations == [
        EdiOperations.ANALYZE,
        EdiOperations.ENRICH,
        EdiOperations.VALIDATE,
        EdiOperations.TRANSLATE,
        EdiOperations.COMPLETE,
    ]


def test_workflow_complete(hl7_message):
    """Validates complete transition invocation"""
    edi = EdiWorkflow(hl7_message)
    edi.analyze()
    edi.enrich()
    edi.validate()
    edi.translate()
    edi.complete()

    assert edi.current_state == EdiOperations.COMPLETE
    assert edi.operations == [
        EdiOperations.ANALYZE,
        EdiOperations.ENRICH,
        EdiOperations.VALIDATE,
        EdiOperations.TRANSLATE,
        EdiOperations.COMPLETE,
    ]

    with pytest.raises(WorkflowNotActive):
        edi.analyze()


def test_workflow_cancel(hl7_message):
    """Validates cancel transition invocation"""
    edi = EdiWorkflow(hl7_message)
    actual_result = edi.cancel()
    assert actual_result.metadata is None
    assert actual_result.metrics.analyzeTime == 0.0
    assert actual_result.inputMessage == hl7_message
    assert actual_result.operations == [EdiOperations.CANCEL]
    assert len(actual_result.errors) == 0

    edi = EdiWorkflow(hl7_message)
    edi.analyze()
    edi.enrich()
    edi.validate()
    edi.cancel()
    assert edi.current_state == EdiOperations.CANCEL
    assert edi.operations == [
        EdiOperations.ANALYZE,
        EdiOperations.ENRICH,
        EdiOperations.VALIDATE,
        EdiOperations.CANCEL,
    ]


def test_workflow_fail(hl7_message):
    """Validates fail transition invocation"""
    edi = EdiWorkflow(hl7_message)
    actual_result = edi.fail("oops", ValueError("something happened"))
    assert actual_result.metadata is None
    assert actual_result.metrics.analyzeTime == 0.0
    assert actual_result.inputMessage == hl7_message
    assert actual_result.operations == [EdiOperations.FAIL]
    assert actual_result.errors == [{"msg": "oops"}, {"msg": "something happened"}]

    assert edi.current_state == EdiOperations.FAIL
    assert edi.operations == [EdiOperations.FAIL]

    edi = EdiWorkflow(hl7_message)
    edi.analyze()
    edi.enrich()
    actual_result = edi.fail("oops")
    assert actual_result.errors == [{"msg": "oops"}]
    assert edi.current_state == EdiOperations.FAIL
    assert edi.operations == [
        EdiOperations.ANALYZE,
        EdiOperations.ENRICH,
        EdiOperations.FAIL,
    ]


def test_workflow_run(hl7_message):
    edi = EdiWorkflow(hl7_message)
    edi.run()
    assert edi.current_state == EdiOperations.COMPLETE
    assert edi.operations == [
        EdiOperations.ANALYZE,
        EdiOperations.ENRICH,
        EdiOperations.VALIDATE,
        EdiOperations.TRANSLATE,
        EdiOperations.COMPLETE,
    ]

    edi = EdiWorkflow(hl7_message)
    edi.run(enrich=False, translate=False)
    assert edi.current_state == EdiOperations.COMPLETE
    assert edi.operations == [
        EdiOperations.ANALYZE,
        EdiOperations.VALIDATE,
        EdiOperations.COMPLETE,
    ]


def test_workflow_is_active(hl7_message):
    edi = EdiWorkflow(hl7_message)
    edi.analyze()

    assert edi.is_active() is True

    edi.fail("foo", ValueError("bar"))

    assert edi.is_active() is False
    with pytest.raises(WorkflowNotActive):
        edi.analyze()

    assert edi.is_active() is False
    with pytest.raises(WorkflowNotActive):
        edi.enrich()

    assert edi.is_active() is False
    with pytest.raises(WorkflowNotActive):
        edi.validate()

    assert edi.is_active() is False
    with pytest.raises(WorkflowNotActive):
        edi.translate()


def test_workflow_analyze_hl7(hl7_message):
    edi = EdiWorkflow(hl7_message)
    edi.analyze()

    expected_meta_data = {
        "baseMessageFormat": BaseMessageFormat.TEXT,
        "ediMessageFormat": EdiMessageFormat.HL7,
        "checksum": "dce92fa2bb05ba55f975dcef9e9615d45e33981c36d46895f349886a87364d60",
        "implementationVersions": ["2.6"],
        "messageSize": 884,
        "recordCount": 8,
        "specificationVersion": "v2",
    }
    assert edi.meta_data.dict() == expected_meta_data

    assert edi.current_state == EdiOperations.ANALYZE
    assert edi.operations == [EdiOperations.ANALYZE]
    assert edi.metrics.analyzeTime > 0.0


def test_workflow_analyze_x12(x12_message):
    edi = EdiWorkflow(x12_message)
    edi.analyze()

    expected_meta_data = {
        "baseMessageFormat": BaseMessageFormat.TEXT,
        "ediMessageFormat": EdiMessageFormat.X12,
        "checksum": "d7a928f396efa0bb15277991bd8d4d9a2506d751f9de8b344c1a3e5f8c45a409",
        "implementationVersions": ["005010X279A1"],
        "messageSize": 509,
        "recordCount": 17,
        "specificationVersion": "005010",
    }
    assert edi.meta_data.dict() == expected_meta_data

    assert edi.current_state == EdiOperations.ANALYZE
    assert edi.operations == [EdiOperations.ANALYZE]
    assert edi.metrics.analyzeTime > 0.0


def test_workflow_analyze_fhir_json(fhir_json_message):
    edi = EdiWorkflow(fhir_json_message)
    edi.analyze()

    expected_meta_data = {
        "baseMessageFormat": BaseMessageFormat.JSON,
        "ediMessageFormat": EdiMessageFormat.FHIR,
        "checksum": "abdfddcc98c5b57df07e778d2235d391ef5781f067eb84a8bd7413ca8b566002",
        "implementationVersions": [
            "http://hl7.org/fhir/us/someprofile",
            "http://hl7.org/fhir/us/otherprofile",
        ],
        "messageSize": 309,
        "recordCount": 1,
        "specificationVersion": "R4",
    }
    assert edi.meta_data.dict() == expected_meta_data

    assert edi.current_state == EdiOperations.ANALYZE
    assert edi.operations == [EdiOperations.ANALYZE]
    assert edi.metrics.analyzeTime > 0.0


def test_workflow_analyze_fhir_xml(fhir_xml_message):
    edi = EdiWorkflow(fhir_xml_message)
    edi.analyze()
    assert edi.is_active() is False
