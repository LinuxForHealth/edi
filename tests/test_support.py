import pytest
from edi.core.support import (
    is_hl7,
    is_x12,
    is_fhir,
    load_json,
    load_xml,
    load_fhir,
    create_checksum,
    parse_version,
    get_namespace,
)
from lxml.etree import ParseError, _Element
from json import JSONDecodeError


@pytest.mark.parametrize(
    "fixture_name, test_result",
    [
        ("hl7_message", True),
        ("x12_message", False),
        ("fhir_xml_message", False),
        ("fhir_json_message", False),
    ],
)
def test_is_hl7(fixture_name, test_result, request):
    fixture_value = request.getfixturevalue(fixture_name)
    assert is_hl7(fixture_value) is test_result


@pytest.mark.parametrize(
    "fixture_name, test_result",
    [
        ("hl7_message", False),
        ("x12_message", True),
        ("fhir_xml_message", False),
        ("fhir_json_message", False),
    ],
)
def test_is_x12(fixture_name, test_result, request):
    fixture_value = request.getfixturevalue(fixture_name)
    assert is_x12(fixture_value) is test_result


@pytest.mark.parametrize(
    "fixture_name, test_result",
    [
        ("x12_message", False),
        ("hl7_message", False),
        ("fhir_json_message", True),
        ("fhir_xml_message", True),
    ],
)
def test_is_fhir(fixture_name, test_result, request):
    fixture_value = request.getfixturevalue(fixture_name)
    assert is_fhir(fixture_value) is test_result
    assert is_fhir(fixture_value) is test_result


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


@pytest.mark.parametrize(
    "fixture_name, expected_type",
    [("fhir_xml_message", _Element), ("fhir_json_message", dict)],
)
def test_load_fhir(fixture_name, expected_type, request):
    fixture_value = request.getfixturevalue(fixture_name)
    fhir_data = load_fhir(fixture_value)
    assert isinstance(fhir_data, expected_type)


@pytest.mark.parametrize(
    "fixture_name, expected_version",
    [
        ("hl7_message", ("2.6",)),
        ("x12_message", ("005010X279A1",)),
        (
            "fhir_xml_message",
            (
                "http://hl7.org/fhir",
                "http://hl7.org/fhir/us/someprofile",
                "http://hl7.org/fhir/us/otherprofile",
            ),
        ),
        (
            "fhir_json_message",
            (
                "http://hl7.org/fhir",
                "http://hl7.org/fhir/us/someprofile",
                "http://hl7.org/fhir/us/otherprofile",
            ),
        ),
    ],
)
def test_parse_version(fixture_name, expected_version, request):
    fixture_value = request.getfixturevalue(fixture_name)
    actual_version = parse_version(fixture_value)
    assert actual_version == expected_version


def test_get_namespace():
    xml = '<?xml version="1.0" encoding="UTF-8"?><Name>John Doe</Name>'
    root_element = load_xml(xml)
    assert get_namespace(root_element) is None

    xml = '<?xml version="1.0" encoding="UTF-8"?><Name xmlns="http://hl7.org/fhir">John Doe</Name>'
    root_element = load_xml(xml)
    assert get_namespace(root_element) == "{http://hl7.org/fhir}"
