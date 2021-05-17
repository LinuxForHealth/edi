"""
stats.py

EDI utility functions for detecting formats and creating metadata statistics.
"""
from edi.core.support import (
    is_fhir,
    is_hl7,
    is_x12,
    load_json,
    create_checksum,
    load_xml,
    get_namespace,
    parse_version,
)
from edi.core.models import EdiStatistics, EdiMessageType


def _parse_fhir_xml_stats(edi_message: str) -> EdiStatistics:
    """
    Parses a FHIR XML message to generate EDI Statistics.
    :param edi_message: The input EDI message
    :returns: EdiStatistics
    """
    root_element = load_xml(edi_message)
    namespace = get_namespace(root_element)

    if not namespace:
        namespace = ""

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
        "checksum": create_checksum(edi_message),
        "message_size": len(bytes(edi_message.encode("utf-8"))),
        "record_count": len(edi_message.split("\r" if is_hl7(edi_message) else "\n")),
    }

    version = parse_version(edi_message)
    stats["specification_version"] = version[0] if version else None
    stats["implementation_version"] = version[1:] if len(version) > 1 else None

    if is_hl7(edi_message):
        message_type = EdiMessageType.HL7
    else:
        message_type = EdiMessageType.X12

    stats["message_type"] = message_type

    return EdiStatistics(**stats)


def _parse_fhir_json_stats(edi_message: str) -> EdiStatistics:
    """
    Parses a FHIR JSON message to generate EDI Statistics.
    :param edi_message: The input EDI message
    :returns: EdiStatistics
    """
    fhir_data = load_json(edi_message)

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
