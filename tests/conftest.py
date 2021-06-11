"""
conftest.py

Global PyTest fixtures
"""
import pytest
import json
import datetime


@pytest.fixture
def hl7_message():
    return "\r".join(
        [
            "MSH|^~\\&|SE050|050|PACS|050|20120912011230||ADT^A01|102|T|2.6|||AL|NE|764|||||||"
            + "^4086::132:2A57:3C28^IPv6",
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


@pytest.fixture
def x12_message():
    return "\n".join(
        [
            "ISA*00*          *00*          *ZZ*890069730      *ZZ*154663145      *200929*1705*|"
            + "*00501*000000001*0*T*:~",
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


@pytest.fixture
def fhir_json_message():
    return json.dumps(
        {
            "resourceType": "Patient",
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/us/someprofile",
                    "http://hl7.org/fhir/us/otherprofile",
                ]
            },
            "identifier": [
                {"system": "urn:oid:1.2.36.146.595.217.0.1", "value": "12345"}
            ],
            "name": [{"family": "Duck", "given": ["Donald", "D."]}],
            "gender": "male",
            "birthDate": datetime.date(1974, 12, 25).isoformat(),
        }
    )


@pytest.fixture
def fhir_xml_message():
    return "".join(
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
