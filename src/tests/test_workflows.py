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
        "checksum": "dce92fa2bb05ba55f975dcef9e9615d45e33981c36d46895f349886a87364d60",
        "implementationVersions": ["2.6"],
        "messageSize": 884,
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
        "checksum": "d7a928f396efa0bb15277991bd8d4d9a2506d751f9de8b344c1a3e5f8c45a409",
        "implementationVersions": ["005010X279A1"],
        "messageSize": 509,
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
        "checksum": "abdfddcc98c5b57df07e778d2235d391ef5781f067eb84a8bd7413ca8b566002",
        "implementationVersions": [
            "http://hl7.org/fhir/us/someprofile",
            "http://hl7.org/fhir/us/otherprofile",
        ],
        "messageSize": 309,
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
