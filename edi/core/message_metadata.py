"""
message_metadata.py

Functions used to generate EDI message metadata.
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
from edi.core.models import EdiMessageMetadata, EdiMessageType


def _parse_fhir_xml(edi_message: str) -> EdiMessageMetadata:
    """
    Parses a FHIR XML message to generate EdiMessageMetadata
    :param edi_message: The input EDI message
    :returns: EdiMessageMetadata
    """
    root_element = load_xml(edi_message)
    namespace = get_namespace(root_element)

    if not namespace:
        namespace = ""

    stats = {
        "messageType": EdiMessageType.FHIR,
        "checksum": create_checksum(edi_message),
        "messageSize": len(bytes(edi_message.encode("utf-8"))),
        "recordCount": 1,
        "specificationVersion": "http://hl7.org/fhir",
    }

    profile_elements = root_element.findall(
        namespace + "meta/" + namespace + "profile/[@value]"
    )
    if profile_elements:
        stats["implementationVersions"] = [e.attrib["value"] for e in profile_elements]

    if "bundle" in root_element.tag.lower():
        stats["record_count"] = len(root_element.findall(namespace + "entry"))

    return EdiMessageMetadata(**stats)


def _parse_delimited_edi(edi_message: str) -> EdiMessageMetadata:
    """
    Parses a delimited EDI message to generate EdiMessageMetadata
    :param edi_message: The input EDI message
    :returns: EdiMessageMetadata
    """
    stats = {
        "checksum": create_checksum(edi_message),
        "messageSize": len(bytes(edi_message.encode("utf-8"))),
        "recordCount": len(edi_message.split("\r" if is_hl7(edi_message) else "\n")),
    }

    version = parse_version(edi_message)
    stats["specificationVersion"] = version[0] if version else None
    stats["implementationVersion"] = version[1:] if len(version) > 1 else None

    if is_hl7(edi_message):
        message_type = EdiMessageType.HL7
    else:
        message_type = EdiMessageType.X12

    stats["messageType"] = message_type

    return EdiMessageMetadata(**stats)


def _parse_fhir_json(edi_message: str) -> EdiMessageMetadata:
    """
    Parses a FHIR JSON message to generate EdiMessageMetadata
    :param edi_message: The input EDI message
    :returns: EdiMessageMetadata
    """
    fhir_data = load_json(edi_message)

    stats = {
        "messageType": EdiMessageType.FHIR,
        "checksum": create_checksum(edi_message),
        "messageSize": len(bytes(edi_message.encode("utf-8"))),
        "recordCount": 1,
        "specificationVersion": "http://hl7.org/fhir",
    }

    if fhir_data.get("resourceType", "").lower() == "bundle":
        record_count = len(fhir_data.get("entry", []))
        stats["recordCount"] = record_count

    stats["implementationVersions"] = fhir_data.get("meta", {}).get("profile")
    return EdiMessageMetadata(**stats)


def parse_message(edi_message: str) -> EdiMessageMetadata:
    """
    Parses an EDI message to generate EdiMessageMetadata
    :param edi_message: The input edi message
    :returns: EdiMessageMetadata
    """
    if is_hl7(edi_message) or is_x12(edi_message):
        return _parse_delimited_edi(edi_message)
    elif is_fhir(edi_message) and edi_message.lstrip().startswith("<"):
        return _parse_fhir_xml(edi_message)
    elif is_fhir(edi_message) and edi_message.lstrip().startswith("{"):
        return _parse_fhir_json(edi_message)
    else:
        raise ValueError("Unable to determine EDI message type")
