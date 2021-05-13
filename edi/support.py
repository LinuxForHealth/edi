"""
support.py

EDI utility functions for detecting formats and creating metadata statistics.
"""
import json
from json.decoder import JSONDecodeError
from lxml import etree
from lxml.etree import ParseError
import logging
from edi.models import EdiStatistics, EdiMessageType
import hashlib
from typing import Optional

logger = logging.getLogger(__name__)


def is_hl7(edi_message: str) -> bool:
    """
    Returns True if the EDI message is a HL7 message.
    A True result does not indicate that the edi message is valid, rather that it appears to be a HL7 message and may
    be parsed.
    """
    return isinstance(edi_message, str) and edi_message[0:3] == "MSH"


def is_x12(edi_message: str) -> bool:
    """
    Returns True if the EDI message is a X12 message.
    A True result does not indicate that the edi message is valid, rather that it appears to be a X12 message and may
    be parsed.
    """
    return isinstance(edi_message, str) and edi_message[0:3] == "ISA"


def _load_json(edi_message: str) -> dict:
    """
    Attempts to load the EDI message as a JSON object.
    Returns the JSON object if successful, otherwise None.
    :param edi_message: the input edi message
    :returns: The JSON object (dictionary) or None
    """
    edi_json = None
    try:
        edi_json = json.loads(edi_message)
    except JSONDecodeError:
        logger.exception("Error loading JSON message")

    return edi_json


def _load_xml(edi_message: str):
    """
    Attempts to load the EDI message as a XML object.
    Returns the XML object if successful, otherwise None.
    :param edi_message: the input edi message
    :returns: The XML object  or None
    """
    edi_xml = None
    try:
        edi_xml = etree.fromstring(edi_message.encode("utf-8"))
    except ParseError:
        logger.exception("Error loading XML message")
    return edi_xml


def is_fhir(edi_message: str) -> bool:
    """
    Returns True if the EDI message is a FHIR message either XML or JSON.
    A True result does not indicate that the edi message is valid, rather that it appears to be a FHIR message and may
    be parsed.
    """
    if not edi_message:
        return False

    edi_first_char = edi_message.lstrip()[0:1]

    if edi_first_char == "{":
        edi_json = _load_json(edi_message)
        return bool(edi_json.get("resourceType"))
    elif edi_first_char == "<":
        edi_xml = _load_xml(edi_message)
        return "http://hl7.org/fhir" in edi_xml.tag.lower()
    else:
        return False


def create_checksum(edi_message: str) -> str:
    """
    Creates a SHA-256 checksum for an EDI message.
    :param edi_message: The input EDI message
    :returns: The SHA-256 checksum as a hex digest
    """
    return hashlib.sha256(edi_message.encode("utf-8")).hexdigest()


def _parse_hl7_version(edi_message: str) -> Optional[str]:
    """
    Parses HL7 version information from a MSH record.
    :param edi_message: The input edi message
    :returns: The version identifier
    """
    records = edi_message.split("\r")

    if not records or not records[0][3:4]:
        return None

    msh_record = records[0]
    delimiter = msh_record[3:4]
    version = msh_record.split(delimiter)[11]
    return version


def _parse_x12_version(edi_message: str) -> Optional[str]:
    """
    Parses X12 version information from a X12 record.
    :param edi_message: The input edi message
    :returns: The version identifier
    """
    records = edi_message.split("\n")

    if not records or len(records) < 2:
        return None

    gs_segment = records[1].replace("~", "")
    delimiter = gs_segment[2:3]
    version = gs_segment.split(delimiter)[8]
    return version


def _parse_fhir_json_stats(edi_message: str) -> EdiStatistics:
    """
    Parses a FHIR JSON message to generate EDI Statistics.
    :param edi_message: The input EDI message
    :returns: EdiStatistics
    """
    fhir_data = _load_json(edi_message)

    stats = {
        "message_type": EdiMessageType.FHIR,
        "checksum": create_checksum(edi_message),
        "message_size": len(bytes(edi_message.encode("utf-8"))),
        "record_count": 1,
        "specification_version": "http://hl7.org/fhir",
    }

    if fhir_data.get("resourceType", "").lower() == "bundle":
        record_count = len(fhir_data.get("entry", []))
        stats["record_count"] = record_count

    stats["implementation_versions"] = fhir_data.get("meta", {}).get("profile")
    return EdiStatistics(**stats)


def _parse_fhir_xml_stats(edi_message: str) -> EdiStatistics:
    """
    Parses a FHIR XML message to generate EDI Statistics.
    :param edi_message: The input EDI message
    :returns: EdiStatistics
    """
    root_element = _load_xml(edi_message)
    namespace = ""

    if "}" in root_element.tag:
        tag_value = root_element.tag
        end_index = tag_value.find("}") + 1
        namespace = tag_value[0:end_index]

    stats = {
        "message_type": EdiMessageType.FHIR,
        "checksum": create_checksum(edi_message),
        "message_size": len(bytes(edi_message.encode("utf-8"))),
        "record_count": 1,
        "specification_version": "http://hl7.org/fhir",
    }

    profile_elements = root_element.findall(
        namespace + "meta/" + namespace + "profile/[@value]"
    )
    if profile_elements:
        stats["implementation_versions"] = [e.attrib["value"] for e in profile_elements]

    if "bundle" in root_element.tag.lower():
        stats["record_count"] = len(root_element.findall(namespace + "entry"))

    return EdiStatistics(**stats)


def _parse_delimited_edi_stats(edi_message: str) -> EdiStatistics:
    """
    Parses a delimited EDI message to generate EDI statistics
    :param edi_message: The input EDI message
    :returns: EdiStatistics
    """
    stats = {
        "message_type": EdiMessageType.HL7
        if is_hl7(edi_message)
        else EdiMessageType.X12,
        "checksum": create_checksum(edi_message),
        "message_size": len(bytes(edi_message.encode("utf-8"))),
        "record_count": len(edi_message.split("\r" if is_hl7(edi_message) else "\n")),
    }

    if is_hl7(edi_message):
        version = _parse_hl7_version(edi_message)
    else:
        version = _parse_x12_version(edi_message)

    stats["specification_version"] = version

    return EdiStatistics(**stats)


def parse_statistics(edi_message: str) -> EdiStatistics:
    """
    Parses EDI statistics from an input message.
    :param edi_message: The input edi message
    :returns: EdiStatistics
    """
    if is_hl7(edi_message) or is_x12(edi_message):
        return _parse_delimited_edi_stats(edi_message)
    elif is_fhir(edi_message) and edi_message.lstrip().startswith("<"):
        return _parse_fhir_xml_stats(edi_message)
    elif is_fhir(edi_message) and edi_message.lstrip().startswith("{"):
        return _parse_fhir_json_stats(edi_message)
    else:
        raise ValueError("Unable to determine EDI message type")
