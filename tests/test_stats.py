from edi.core.stats import parse_statistics
from edi.core.models import EdiStatistics


def test_parse_statistics_hl7(hl7_message):
    expected_data = {
        "message_type": "HL7",
        "specification_version": "2.6",
        "checksum": "dce92fa2bb05ba55f975dcef9e9615d45e33981c36d46895f349886a87364d60",
        "message_size": 884,
        "record_count": 8,
    }
    expected_stats = EdiStatistics(**expected_data)
    actual_stats = parse_statistics(hl7_message)
    assert actual_stats.dict() == expected_stats.dict()


def test_parse_statistics_x12(x12_message):
    expected_data = {
        "message_type": "X12",
        "specification_version": "005010X279A1",
        "checksum": "d7a928f396efa0bb15277991bd8d4d9a2506d751f9de8b344c1a3e5f8c45a409",
        "message_size": 509,
        "record_count": 17,
    }
    expected_stats = EdiStatistics(**expected_data)
    actual_stats = parse_statistics(x12_message)
    assert actual_stats.dict() == expected_stats.dict()


def test_parse_statistics_fhir_xml(fhir_xml_message):
    expected_data = {
        "message_type": "FHIR",
        "specification_version": "http://hl7.org/fhir",
        "implementation_versions": [
            "http://hl7.org/fhir/us/someprofile",
            "http://hl7.org/fhir/us/otherprofile",
        ],
        "checksum": "c3331c97605865490503e779a697bdeeab5991517ce0655566e23e951b057dfe",
        "message_size": 607,
        "record_count": 1,
    }
    expected_stats = EdiStatistics(**expected_data)
    actual_stats = parse_statistics(fhir_xml_message)
    assert actual_stats.dict() == expected_stats.dict()


def test_parse_statistics_fhir_json(fhir_json_message):
    expected_data = {
        "message_type": "FHIR",
        "specification_version": "http://hl7.org/fhir",
        "implementation_versions": [
            "http://hl7.org/fhir/us/someprofile",
            "http://hl7.org/fhir/us/otherprofile",
        ],
        "checksum": "abdfddcc98c5b57df07e778d2235d391ef5781f067eb84a8bd7413ca8b566002",
        "message_size": 309,
        "record_count": 1,
    }
    expected_stats = EdiStatistics(**expected_data)
    actual_stats = parse_statistics(fhir_json_message)
    assert actual_stats.dict() == expected_stats.dict()
