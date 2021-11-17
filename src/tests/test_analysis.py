"""
test_analysis.py

General test cases for the analysis package which tests message classification.
Tests for specific formats are implemented within separate modules named test_<format>_analysis.py.
For example: test_fhir_analysis.py, test_x12_analysis.py, etc
"""
import pytest
from edi.analysis import analyze
from edi.models import BaseMessageFormat, EdiMessageFormat


@pytest.mark.parametrize(
    "input_message",
    [None, "", "        ", "IS"],
)
def test_analyze_invalid_message(input_message):
    with pytest.raises(ValueError):
        analyze(input_message)


def test_analyze_fhir_json(fhir_json_message):
    edi_message_metadata = analyze(fhir_json_message)
    assert edi_message_metadata.baseMessageFormat == BaseMessageFormat.JSON
    assert edi_message_metadata.ediMessageFormat == EdiMessageFormat.FHIR
    assert edi_message_metadata.specificationVersion == "R4"
    assert edi_message_metadata.implementationVersions == [
        "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"
    ]
    assert edi_message_metadata.messageSize == 5985
    assert (
        edi_message_metadata.checksum
        == "b35938e815b23a1aa64784ced03f133491277094449915142950df26bf016781"
    )


def test_analyze_fhir_xml(fhir_xml_message):
    with pytest.raises(NotImplementedError):
        analyze(fhir_xml_message)


def test_analyze_hl7(hl7_message):
    edi_message_metadata = analyze(hl7_message)
    assert edi_message_metadata.baseMessageFormat == BaseMessageFormat.TEXT
    assert edi_message_metadata.ediMessageFormat == EdiMessageFormat.HL7
    assert edi_message_metadata.specificationVersion == "v2"
    assert edi_message_metadata.implementationVersions == ["2.6"]
    assert edi_message_metadata.messageSize == 892
    assert (
        edi_message_metadata.checksum
        == "852a588f4aae297db99807b1f7d1888f4927624d411335a730b8a325347b9873"
    )


def test_analyze_x12(x12_message):
    edi_message_metadata = analyze(x12_message)
    assert edi_message_metadata.baseMessageFormat == BaseMessageFormat.TEXT
    assert edi_message_metadata.ediMessageFormat == EdiMessageFormat.X12
    assert edi_message_metadata.specificationVersion == "005010"
    assert edi_message_metadata.implementationVersions == ["005010X279A1"]
    assert edi_message_metadata.messageSize == 494
    assert (
        edi_message_metadata.checksum
        == "578b8f172f2039cfcc1ec4b37eb8a3976e50577fb085823abbfead071e68d1d8"
    )
