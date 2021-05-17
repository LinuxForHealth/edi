"""
support.py
"""
import hashlib
import json
from json import JSONDecodeError
from typing import Union, Optional, Tuple
from lxml import etree
from lxml.etree import ParseError, _Element
import logging


logger = logging.getLogger(__name__)

FHIR_SPECIFICATION_URL = "http://hl7.org/fhir"


def load_json(edi_message: str) -> dict:
    """
    Attempts to load the EDI message as a JSON object.
    Returns the JSON object if successful, otherwise None.
    :param edi_message: the input edi message
    :returns: The JSON object (dictionary) or None
    """
    try:
        edi_json = json.loads(edi_message)
    except JSONDecodeError:
        logger.exception("Error loading JSON message")
        raise

    return edi_json


def load_xml(edi_message: str):
    """
    Attempts to load the EDI message as a XML object.
    Returns the XML object if successful, otherwise None.
    :param edi_message: the input edi message
    :returns: The XML object  or None
    """
    try:
        edi_xml = etree.fromstring(edi_message.encode("utf-8"))
    except ParseError:
        logger.exception("Error loading XML message")
        raise
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
        edi_json = load_json(edi_message)
        return bool(edi_json.get("resourceType"))
    elif edi_first_char == "<":
        edi_xml = load_xml(edi_message)
        return "http://hl7.org/fhir" in edi_xml.tag.lower()
    else:
        return False


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


def create_checksum(edi_message: str) -> str:
    """
    Creates a SHA-256 checksum for an EDI message.
    :param edi_message: The input EDI message
    :returns: The SHA-256 checksum as a hex digest
    """
    return hashlib.sha256(edi_message.encode("utf-8")).hexdigest()


def load_fhir(edi_message: str) -> Union[dict, _Element]:
    """
    Loads a FHIR Message from a string.
    FHIR supports XML and JSON formats. The format used is dictated by the input string.
    :param edi_message: The input edi message
    :returns: FHIR as a XML or JSON resource
    """
    if not is_fhir(edi_message) or not any(
        (edi_message.startswith("<"), edi_message.startswith("{"))
    ):
        raise ValueError("Invalid FHIR Message")

    if edi_message.lstrip().startswith("<"):
        return load_xml(edi_message)
    else:
        return load_json(edi_message)


def parse_version(edi_message: str) -> Optional[Tuple[str]]:
    """
    Parses version information from an EDI message.
    Version information is returned as a tuple. The first entry is the specification version. Additional entries, if
    found, are the implementation versions.

    :param edi_message: The input edi message
    :returns: Tuple of version info.
    """
    parsed_version = None

    if is_hl7(edi_message):
        parsed_version = (_parse_hl7_version(edi_message),)
    elif is_x12(edi_message):
        parsed_version = (_parse_x12_version(edi_message),)
    elif is_fhir(edi_message):
        fhir_data = load_fhir(edi_message)
        parsed_version = _parse_fhir_version(fhir_data)

    return parsed_version


def get_namespace(xml_root: _Element) -> Optional[str]:
    """Returns the XML namespace for a root element"""
    namespace = None

    if "}" in xml_root.tag:
        tag_value = xml_root.tag
        end_index = tag_value.find("}") + 1
        namespace = tag_value[0:end_index]

    return namespace


def _parse_fhir_version(edi_message: Union[dict, _Element]) -> Tuple[str]:
    """
    Parses FHIR Version Information from a resource.
    "Version" information includes URL/URIs which point to the core specification and optional profiles.
    :param edi_message: The input edi message
    :returns: tuple(core version, profile, profile, profile, etc)
    """
    profiles = [FHIR_SPECIFICATION_URL]

    if isinstance(edi_message, dict):
        profiles += edi_message.get("meta", {}).get("profile", [])
    else:
        namespace = get_namespace(edi_message)
        if not namespace:
            namespace = ""

        profile_elements = edi_message.findall(
            namespace + "meta/" + namespace + "profile/[@value]"
        )

        if profile_elements:
            profiles += [e.attrib["value"] for e in profile_elements]

    return tuple(profiles)


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
