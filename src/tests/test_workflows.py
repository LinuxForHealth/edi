"""
test_workflows.py

Tests the EdiProcessor workflow implementation
"""
from linuxforhealth.edi.models import (
    BaseMessageFormat,
    EdiMessageFormat,
    EdiProcessingMetrics,
)
from linuxforhealth.edi.workflows import EdiWorkflow
from linuxforhealth.edi.exceptions import (
    EdiValidationException,
    EdiAnalysisException,
    EdiDataValidationException,
)
import pytest
import json


def test_workflow_run_hl7(hl7_message):
    edi = EdiWorkflow(hl7_message)
    edi_result = edi.run()

    expected_meta_data = {
        "baseMessageFormat": BaseMessageFormat.TEXT,
        "ediMessageFormat": EdiMessageFormat.HL7,
        "checksum": "852a588f4aae297db99807b1f7d1888f4927624d411335a730b8a325347b9873",
        "implementationVersions": ["2.6"],
        "messageSize": 892,
        "specificationVersion": "V2",
    }

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
        "specificationVersion": "005010",
    }

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
        "specificationVersion": "R4",
    }

    assert edi_result.metadata == expected_meta_data
    assert edi_result.metrics.analyzeTime > 0.0
    assert edi_result.metrics.validateTime > 0.0


def test_workflow_run_dicom(dicom_message):
    edi = EdiWorkflow(dicom_message)
    edi_result = edi.run()

    expected_meta_data = {
        "baseMessageFormat": BaseMessageFormat.BINARY,
        "ediMessageFormat": EdiMessageFormat.DICOM,
        "checksum": "2a242a24c176abb27506e541659822b1132236656efa5d133dd7d5c745ed56ef",
        "implementationVersions": [],
        "messageSize": 14399514,
        "specificationVersion": None,
    }

    assert edi_result.metadata == expected_meta_data
    assert edi_result.metrics.analyzeTime > 0.0
    assert edi_result.metrics.validateTime > 0.0


def test_x12_workflow_exception(x12_message):
    with pytest.raises(EdiDataValidationException):
        EdiWorkflow("IS").run()

    invalid_x12 = x12_message.replace("HL*1**20*1~", "HL*1**720*1~")
    with pytest.raises(EdiDataValidationException):
        EdiWorkflow(invalid_x12).run()


def test_fhir_workflow_exception(fhir_json_message):

    fhir_dict = json.loads(fhir_json_message)
    fhir_dict["resourceType"] = "NotARealResource"
    with pytest.raises(EdiDataValidationException):
        EdiWorkflow(json.dumps(fhir_dict)).run()


def test_hl7_workflow_exception(hl7_message):
    invalid_hl7 = hl7_message.replace("MSH|", "FISH|")
    with pytest.raises(EdiDataValidationException):
        EdiWorkflow(invalid_hl7).run()
