"""
test_workflows.py

Tests the EdiProcessor workflow implementation
"""
from edi.models import (
    BaseMessageFormat,
    EdiMessageFormat,
    EdiProcessingMetrics,
)
from edi.workflows import EdiWorkflow
import pytest


def test_workflow_run_hl7(hl7_message):
    edi = EdiWorkflow(hl7_message)
    edi_result = edi.run()

    expected_meta_data = {
        "baseMessageFormat": BaseMessageFormat.TEXT,
        "ediMessageFormat": EdiMessageFormat.HL7,
        "checksum": "852a588f4aae297db99807b1f7d1888f4927624d411335a730b8a325347b9873",
        "implementationVersions": ["2.6"],
        "messageSize": 892,
        "recordCount": 8,
        "specificationVersion": "v2",
    }

    assert len(edi_result.errors) == 0
    assert edi_result.metadata == expected_meta_data
    assert edi_result.metrics.analyzeTime > 0.0
    assert edi_result.metrics.validateTime > 0.0


def test_workflow_run_x12(x12_message):
    edi = EdiWorkflow(x12_message)
    edi_result = edi.run()

    expected_meta_data = {
        "baseMessageFormat": BaseMessageFormat.TEXT,
        "ediMessageFormat": EdiMessageFormat.X12,
        "checksum": "578b8f172f2039cfcc1ec4b37eb8a3976e50577fb085823abbfead071e68d1d8",
        "implementationVersions": ["005010X279A1"],
        "messageSize": 494,
        "recordCount": 17,
        "specificationVersion": "005010",
    }

    assert len(edi_result.errors) == 0
    assert edi_result.metadata == expected_meta_data
    assert edi_result.metrics.analyzeTime > 0.0
    assert edi_result.metrics.validateTime > 0.0


def test_workflow_run_fhir_json(fhir_json_message):
    edi = EdiWorkflow(fhir_json_message)
    edi_result = edi.run()

    expected_meta_data = {
        "baseMessageFormat": BaseMessageFormat.JSON,
        "ediMessageFormat": EdiMessageFormat.FHIR,
        "checksum": "b35938e815b23a1aa64784ced03f133491277094449915142950df26bf016781",
        "implementationVersions": [
            "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"
        ],
        "messageSize": 5985,
        "recordCount": 1,
        "specificationVersion": "R4",
    }

    assert len(edi_result.errors) == 0
    assert edi_result.metadata == expected_meta_data
    assert edi_result.metrics.analyzeTime > 0.0
    assert edi_result.metrics.validateTime > 0.0


def test_workflow_error(x12_message):
    invalid_x12 = x12_message.replace("HL*1**20*1~", "HL*1**720*1~")
    edi = EdiWorkflow(invalid_x12)
    edi_result = edi.run()
    assert len(edi_result.errors) == 1
