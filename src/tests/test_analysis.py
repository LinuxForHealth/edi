"""
test_analysis.py

General test cases for the analysis package which tests message classification.
Tests for specific formats are implemented within separate modules named test_<format>_analysis.py.
For example: test_fhir_analysis.py, test_x12_analysis.py, etc
"""
import pytest
from edi.analysis import get_analyzer, FhirAnalyzer, Hl7Analyzer, X12Analyzer
from edi.models import BaseMessageFormat, EdiMessageFormat


@pytest.mark.parametrize(
    "input_message",
    [None, "", "        ", "IS"],
)
def test_analyze_invalid_message(input_message):
    with pytest.raises(ValueError):
        get_analyzer(input_message)

def test_analyze_fhir_json(fhir_json_message):
    analyzer = get_analyzer(fhir_json_message)
    assert isinstance(analyzer, FhirAnalyzer)

    edi_message_metadata = analyzer.analyze()
    assert edi_message_metadata.baseMessageFormat == BaseMessageFormat.JSON
    assert edi_message_metadata.ediMessageFormat == EdiMessageFormat.FHIR
    assert edi_message_metadata.specificationVersion == "R4"
    assert edi_message_metadata.implementationVersions == ["http://hl7.org/fhir/us/someprofile", "http://hl7.org/fhir/us/otherprofile"]
    assert edi_message_metadata.messageSize == 309
    assert edi_message_metadata.recordCount == 1
    assert edi_message_metadata.checksum == "abdfddcc98c5b57df07e778d2235d391ef5781f067eb84a8bd7413ca8b566002"


def test_analyze_fhir_xml(fhir_xml_message):
    with pytest.raises(NotImplementedError):
        get_analyzer(fhir_xml_message)

def test_analyze_hl7(hl7_message):
    analyzer = get_analyzer(hl7_message)
    assert isinstance(analyzer, Hl7Analyzer)

    edi_message_metadata = analyzer.analyze()
    assert edi_message_metadata.baseMessageFormat == BaseMessageFormat.TEXT
    assert edi_message_metadata.ediMessageFormat == EdiMessageFormat.HL7
    assert edi_message_metadata.specificationVersion == "v2"
    assert edi_message_metadata.implementationVersions == ["2.6"]
    assert edi_message_metadata.messageSize == 884
    assert edi_message_metadata.recordCount == 8
    assert edi_message_metadata.checksum == "dce92fa2bb05ba55f975dcef9e9615d45e33981c36d46895f349886a87364d60"


def test_analyze_x12(x12_message):
    analyzer = get_analyzer(x12_message)
    assert isinstance(analyzer, X12Analyzer)

    edi_message_metadata = analyzer.analyze()
    assert edi_message_metadata.baseMessageFormat == BaseMessageFormat.TEXT
    assert edi_message_metadata.ediMessageFormat == EdiMessageFormat.X12
    assert edi_message_metadata.specificationVersion == "005010"
    assert edi_message_metadata.implementationVersions == ["005010X279A1"]
    assert edi_message_metadata.messageSize == 509
    assert edi_message_metadata.recordCount == 17
    assert edi_message_metadata.checksum == "d7a928f396efa0bb15277991bd8d4d9a2506d751f9de8b344c1a3e5f8c45a409"
