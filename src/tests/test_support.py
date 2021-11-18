"""
test_support.py

Tests EDI support functions.
"""
from edi.models import EdiProcessingMetrics
from edi.support import (
    create_checksum,
    load_xml,
    load_json,
    Timer,
    load_fhir_json,
    load_hl7,
    load_x12,
)

import pytest
from lxml.etree import ParseError
from json import JSONDecodeError
import time


@pytest.fixture
def workflow_fixture():
    class WorkflowFixture:
        def __init__(self):
            self.metrics: EdiProcessingMetrics = EdiProcessingMetrics(
                analyzeTime=0.0, enrichTime=0.0, validateTime=0.0, translateTime=0.0
            )

        def analyze(self):
            pass

    return WorkflowFixture


@pytest.mark.parametrize(
    "fixture_name, test_result",
    [
        (
            "x12_message",
            "578b8f172f2039cfcc1ec4b37eb8a3976e50577fb085823abbfead071e68d1d8",
        ),
        (
            "hl7_message",
            "852a588f4aae297db99807b1f7d1888f4927624d411335a730b8a325347b9873",
        ),
        (
            "fhir_json_message",
            "b35938e815b23a1aa64784ced03f133491277094449915142950df26bf016781",
        ),
        (
            "fhir_xml_message",
            "843b106243a70e4713e3cf9b9477ce0c7b1aef6840dee6a77dafeba972875dee",
        ),
    ],
)
def test_create_checksum(fixture_name, test_result, request):
    fixture_value = request.getfixturevalue(fixture_name)
    assert create_checksum(fixture_value) == test_result


def test_load_xml(fhir_xml_message):
    edi_xml = load_xml(fhir_xml_message)
    assert edi_xml is not None


def test_load_xml_failure(fhir_json_message):
    with pytest.raises(ParseError):
        load_xml(fhir_json_message)


def test_load_json(fhir_json_message):
    edi_json = load_json(fhir_json_message)
    assert edi_json is not None


def test_load_json_failure(fhir_xml_message):
    with pytest.raises(JSONDecodeError):
        load_json(fhir_xml_message)


def test_load_fhir_json(fhir_json_message):
    fhir_model = load_fhir_json(fhir_json_message)
    assert fhir_model is not None
    assert fhir_model.resource_type == "Patient"


def test_load_hl7(hl7_message):
    hl7_model = load_hl7(hl7_message)
    assert hl7_model is not None
    assert len(hl7_model) == 8


def test_load_x12(x12_message):
    x12_models = load_x12(x12_message)
    len(x12_models) == 1
    assert x12_models[0].header.st_segment.transaction_set_identifier_code == "270"


def test_timer():
    with Timer() as t:
        [x for x in range(1_0000)]
    assert t.elapsed_time >= 0
