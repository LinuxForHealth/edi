"""
test_support.py

Tests EDI support functions.
"""
from edi.core.models import EdiProcessingMetrics
from edi.core.support import create_checksum, load_xml, load_json, workflow_timer
import pytest
from lxml.etree import ParseError
from json import JSONDecodeError


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
            "d7a928f396efa0bb15277991bd8d4d9a2506d751f9de8b344c1a3e5f8c45a409",
        ),
        (
            "hl7_message",
            "dce92fa2bb05ba55f975dcef9e9615d45e33981c36d46895f349886a87364d60",
        ),
        (
            "fhir_json_message",
            "abdfddcc98c5b57df07e778d2235d391ef5781f067eb84a8bd7413ca8b566002",
        ),
        (
            "fhir_xml_message",
            "c3331c97605865490503e779a697bdeeab5991517ce0655566e23e951b057dfe",
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


def test_workflow_timer(workflow_fixture):
    """Tests the workflow_timer decorator"""
    # manually wire up the "decorator"
    workflow_fixture.analyze = workflow_timer(workflow_fixture.analyze)
    # create new instance
    wf = workflow_fixture()
    wf.analyze()
    assert wf.metrics.analyzeTime > 0.0
