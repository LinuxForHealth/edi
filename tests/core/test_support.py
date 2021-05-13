import pytest
from edi.core.support import is_hl7, is_x12, is_fhir, parse_statistics, create_checksum
from edi.core.models import EdiStatistics
import datetime
import json

# sample data messages
hl7_message = "\r".join(
    [
        "MSH|^~\\&|SE050|050|PACS|050|20120912011230||ADT^A01|102|T|2.6|||AL|NE|764|||||||^4086::132:2A57:3C28^IPv6",
        "EVN||201209122222",
        "PID|0010||PID1234^5^M11^A^MR^HOSP~1234568965^^^USA^SS||DOE^JOHN^A^||19800202|F||W|111 TEST_STREET_NAME^"
        + "^TEST_CITY^NY^111-1111^USA||(905)111-1111|||S|ZZ|12^^^124|34-13-312||||TEST_BIRTH_PLACE",
        "PV1|1|ff|yyy|EL|ABC||200^ATTEND_DOC_FAMILY_TEST^ATTEND_DOC_GIVEN_TEST|201^REFER_DOC_FAMILY_TEST^"
        + "REFER_DOC_GIVEN_TEST|202^CONSULTING_DOC_FAMILY_TEST^CONSULTING_DOC_GIVEN_TEST|MED|||||B6|E|272^"
        + "ADMITTING_DOC_FAMILY_TEST^ADMITTING_DOC_GIVEN_TEST||48390|||||||||||||||||||||||||201409122200|",
        "OBX|1|TX|1234||ECHOCARDIOGRAPHIC REPORT||||||F|||||2740^TRDSE^Janetary~2913^MRTTE^Darren^F~3065^MGHOBT"
        + "^Paul^J~4723^LOTHDEW^Robert^L|",
        "AL1|1|DRUG|00000741^OXYCODONE||HYPOTENSION",
        "AL1|2|DRUG|00001433^TRAMADOL||SEIZURES~VOMITING",
        "PRB|AD|200603150625|aortic stenosis|53692||2||200603150625",
    ]
)


x12_message = "\n".join(
    [
        "ISA*00*          *00*          *ZZ*890069730      *ZZ*154663145      *200929*1705*|*00501*000000001*0*T*:~",
        "GS*HS*890069730*154663145*20200929*1705*0001*X*005010X279A1~",
        "ST*270*0001*005010X279A1~",
        "BHT*0022*13*10001234*20200929*1319~",
        "HL*1**20*1~",
        "NM1*PR*2*UNIFIED INSURANCE CO*****PI*842610001~",
        "HL*2*1*21*1~",
        "NM1*1P*2*DOWNTOWN MEDICAL CENTER*****XX*2868383243~",
        "HL*3*2*22*0~",
        "TRN*1*1*1453915417~",
        "NM1*IL*1*DOE*JOHN****MI*11122333301~",
        "DMG*D8*19800519~",
        "DTP*291*D8*20200101~",
        "EQ*30~",
        "SE*13*0001~",
        "GE*1*0001~",
        "IEA*1*000010216~",
    ]
)

fhir_json_message = json.dumps(
    {
        "resourceType": "Patient",
        "meta": {
            "profile": [
                "http://hl7.org/fhir/us/someprofile",
                "http://hl7.org/fhir/us/otherprofile",
            ]
        },
        "identifier": [{"system": "urn:oid:1.2.36.146.595.217.0.1", "value": "12345"}],
        "name": [{"family": "Duck", "given": ["Donald", "D."]}],
        "gender": "male",
        "birthDate": datetime.date(1974, 12, 25).isoformat(),
    }
)

fhir_xml_message = "".join(
    [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<Patient xmlns="http://hl7.org/fhir">',
        "<meta>",
        '<profile value="http://hl7.org/fhir/us/someprofile"/>',
        '<profile value="http://hl7.org/fhir/us/otherprofile"/>',
        "</meta>",
        "<identifier>",
        '<system value="urn:oid:1.2.36.146.595.217.0.1"/>',
        '<value value="12345"/>',
        "</identifier>" "<name>",
        '<use value="official"/>',
        '<family value="Chalmers"/>',
        '<given value="Peter"/>',
        '<given value="James"/>',
        "</name>",
        '<gender value="male"/>',
        '<birthDate value="1974-12-25">',
        '<extension url="http://hl7.org/fhir/StructureDefinition/patient-birthTime">',
        '<valueDateTime value="1974-12-25T14:35:45-05:00"/>',
        "</extension>",
        "</birthDate>",
        "</Patient>",
    ]
)


@pytest.mark.parametrize(
    "edi_message, test_result",
    [
        (x12_message, False),
        (hl7_message, True),
        ("", False),
        (None, False),
        (fhir_json_message, False),
        (fhir_xml_message, False),
    ],
)
def test_is_hl7(edi_message, test_result):
    assert is_hl7(edi_message) is test_result


@pytest.mark.parametrize(
    "edi_message, test_result",
    [
        (x12_message, True),
        (hl7_message, False),
        ("", False),
        (None, False),
        (fhir_json_message, False),
        (fhir_xml_message, False),
    ],
)
def test_is_x12(edi_message, test_result):
    assert is_x12(edi_message) is test_result


@pytest.mark.parametrize(
    "edi_message, test_result",
    [
        (x12_message, False),
        (hl7_message, False),
        ("", False),
        (None, False),
        (fhir_json_message, True),
        (fhir_xml_message, True),
    ],
)
def test_is_fhir(edi_message, test_result):
    assert is_fhir(edi_message) is test_result


@pytest.mark.parametrize(
    "edi_message, test_result",
    [
        (
            x12_message,
            "d7a928f396efa0bb15277991bd8d4d9a2506d751f9de8b344c1a3e5f8c45a409",
        ),
        (
            hl7_message,
            "dce92fa2bb05ba55f975dcef9e9615d45e33981c36d46895f349886a87364d60",
        ),
        (
            fhir_json_message,
            "abdfddcc98c5b57df07e778d2235d391ef5781f067eb84a8bd7413ca8b566002",
        ),
        (
            fhir_xml_message,
            "c3331c97605865490503e779a697bdeeab5991517ce0655566e23e951b057dfe",
        ),
    ],
)
def test_create_checksum(edi_message, test_result):
    assert create_checksum(edi_message) == test_result


def test_parse_statistics_hl7():
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


def test_parse_statistics_x12():
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


def test_parse_statistics_fhir_xml():
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


def test_parse_statistics_fhir_json():
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
