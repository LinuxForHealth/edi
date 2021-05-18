from edi.core.message_metadata import parse_message
from edi.core.models import EdiMessageMetadata


def test_parse_message_hl7(hl7_message):
    expected_data = {
        "messageType": "HL7",
        "specificationVersion": "2.6",
        "checksum": "dce92fa2bb05ba55f975dcef9e9615d45e33981c36d46895f349886a87364d60",
        "messageSize": 884,
        "recordCount": 8,
    }
    expected_stats = EdiMessageMetadata(**expected_data)
    actual_stats = parse_message(hl7_message)
    assert actual_stats.dict() == expected_stats.dict()


def test_parse_message_x12(x12_message):
    expected_data = {
        "messageType": "X12",
        "specificationVersion": "005010X279A1",
        "checksum": "d7a928f396efa0bb15277991bd8d4d9a2506d751f9de8b344c1a3e5f8c45a409",
        "messageSize": 509,
        "recordCount": 17,
    }
    expected_stats = EdiMessageMetadata(**expected_data)
    actual_stats = parse_message(x12_message)
    assert actual_stats.dict() == expected_stats.dict()


def test_parse_message_fhir_xml(fhir_xml_message):
    expected_data = {
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
    expected_stats = EdiMessageMetadata(**expected_data)
    actual_stats = parse_message(fhir_xml_message)
    assert actual_stats.dict() == expected_stats.dict()


def test_parse_message_fhir_json(fhir_json_message):
    expected_data = {
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
    expected_stats = EdiMessageMetadata(**expected_data)
    actual_stats = parse_message(fhir_json_message)
    assert actual_stats.dict() == expected_stats.dict()
