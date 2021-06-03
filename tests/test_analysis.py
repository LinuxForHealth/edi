"""
test_analysis.py

Unit tests for EdiAnalyzer
"""
from edi.core.models import EdiMessageMetadata
from edi.core.analysis import EdiAnalyzer
from edi.core.models import EdiMessageType, BaseMessageType
import pytest


@pytest.mark.parametrize(
    "input_data",
    [None, "", "        ", "John, Doe, MD, 1400 Anyhoo Lane"],
)
def test_init_value_error(input_data):
    with pytest.raises(ValueError):
        EdiAnalyzer(input_message=input_data)


@pytest.mark.parametrize(
    "fixture_name, base_message_type, message_type",
    [
        ("hl7_message", BaseMessageType.TEXT, EdiMessageType.HL7),
        ("x12_message", BaseMessageType.TEXT, EdiMessageType.X12),
        ("fhir_json_message", BaseMessageType.JSON, EdiMessageType.FHIR),
        ("fhir_xml_message", BaseMessageType.XML, EdiMessageType.FHIR),
    ],
)
def test_init(fixture_name, base_message_type, message_type, request):
    message_fixture = request.getfixturevalue(fixture_name)
    analyzer = EdiAnalyzer(message_fixture, sample_length=100)
    assert analyzer.input_message == message_fixture
    assert analyzer.message_sample == message_fixture[0:100]
    assert analyzer.base_message_type == base_message_type
    assert analyzer.message_type == message_type


def test_analyze_hl7(hl7_message):
    expected_data = {
        "baseMessageType": "TEXT",
        "messageType": "HL7",
        "specificationVersion": "2.6",
        "checksum": "dce92fa2bb05ba55f975dcef9e9615d45e33981c36d46895f349886a87364d60",
        "messageSize": 884,
        "recordCount": 8,
    }
    analyzer = EdiAnalyzer(hl7_message, sample_length=100)
    actual_metadata = analyzer.analyze()

    expected_metadata = EdiMessageMetadata(**expected_data)
    assert actual_metadata.dict() == expected_metadata.dict()


def test_analyze_x12(x12_message):
    expected_data = {
        "baseMessageType": "TEXT",
        "messageType": "X12",
        "specificationVersion": "005010X279A1",
        "checksum": "d7a928f396efa0bb15277991bd8d4d9a2506d751f9de8b344c1a3e5f8c45a409",
        "messageSize": 509,
        "recordCount": 17,
    }
    analyzer = EdiAnalyzer(x12_message, sample_length=100)
    actual_metadata = analyzer.analyze()

    expected_metadata = EdiMessageMetadata(**expected_data)
    assert actual_metadata.dict() == expected_metadata.dict()


def test_analyze_fhir_xml(fhir_xml_message):
    expected_data = {
        "baseMessageType": "XML",
        "messageType": "FHIR",
        "specificationVersion": "http://hl7.org/fhir",
        "implementationVersions": [
            "http://hl7.org/fhir/us/someprofile",
            "http://hl7.org/fhir/us/otherprofile",
        ],
        "checksum": "c3331c97605865490503e779a697bdeeab5991517ce0655566e23e951b057dfe",
        "messageSize": 607,
        "recordCount": 1,
    }

    analyzer = EdiAnalyzer(fhir_xml_message, sample_length=100)
    actual_metadata = analyzer.analyze()

    expected_metadata = EdiMessageMetadata(**expected_data)
    assert actual_metadata.dict() == expected_metadata.dict()


def test_analyze_fhir_json(fhir_json_message):
    expected_data = {
        "baseMessageType": "JSON",
        "messageType": "FHIR",
        "specificationVersion": "http://hl7.org/fhir",
        "implementationVersions": [
            "http://hl7.org/fhir/us/someprofile",
            "http://hl7.org/fhir/us/otherprofile",
        ],
        "checksum": "abdfddcc98c5b57df07e778d2235d391ef5781f067eb84a8bd7413ca8b566002",
        "messageSize": 309,
        "recordCount": 1,
    }

    analyzer = EdiAnalyzer(fhir_json_message, sample_length=100)
    actual_metadata = analyzer.analyze()

    expected_metadata = EdiMessageMetadata(**expected_data)
    assert actual_metadata.dict() == expected_metadata.dict()
