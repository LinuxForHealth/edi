import time
from json import JSONDecodeError
import json
import logging
from typing import Union, List, Tuple
from lxml import etree
from lxml.etree import ParseError
import hashlib
from fhir.resources import construct_fhir_element as construct_fhir_r4
from fhir.resources import FHIRAbstractModel as FHIRAbstractModelR4
from fhir.resources.STU3 import construct_fhir_element as construct_fhir_stu3
from fhir.resources.STU3 import FHIRAbstractModel as FHIRAbstractModelSTU3
from fhir.resources.DSTU2 import construct_fhir_element as construct_fhir_dstu2
from fhir.resources.DSTU2 import FHIRAbstractModel as FHIRAbstractModelDSTU2
import hl7
from hl7 import Message
from x12.io import X12ModelReader, X12SegmentGroup

logger = logging.getLogger(__name__)


def create_checksum(edi_message: str) -> str:
    """
    Creates a SHA-256 checksum for an EDI message.
    :param edi_message: The input EDI message
    :returns: The SHA-256 checksum as a hex digest
    """
    return hashlib.sha256(edi_message.encode("utf-8")).hexdigest()


def load_json(message: str) -> dict:
    """
    Attempts to load the message as a JSON object.
    Returns the JSON object if successful, otherwise None.
    :param message: the input message
    :returns: The JSON object (dictionary) or None
    """
    try:
        json_message = json.loads(message)
    except JSONDecodeError:
        logger.exception("Error loading JSON message")
        raise

    return json_message


def load_xml(message: str):
    """
    Attempts to load the message as a XML object.
    Returns the XML object if successful, otherwise None.
    :param message: the input message
    :returns: The XML object  or None
    """
    try:
        xml_message = etree.fromstring(message.encode("utf-8"))
    except ParseError:
        logger.exception("Error loading XML message")
        raise
    return xml_message


def load_fhir_json(
    input_message: str,
) -> Union[FHIRAbstractModelR4, FHIRAbstractModelSTU3, FHIRAbstractModelDSTU2]:
    """
    Loads a FHIR Json Resource into a domain model
    :param input_message: The message to load.
    :returns: FHIR Resource Model
    """
    parsed_data = json.loads(input_message)
    resource_type: str = parsed_data.get("resourceType")
    for c in (construct_fhir_r4, construct_fhir_stu3, construct_fhir_dstu2):
        try:
            fhir_resource = c(resource_type, parsed_data)
            if fhir_resource:
                return fhir_resource
        except Exception as ex:
            logger.debug(f"FHIR Resource is not compatible with {c.__name__}")
            raise


def load_x12(input_message: str) -> List[X12SegmentGroup]:
    """
    Loads an X12 input into a model list
    """
    models: List[X12SegmentGroup] = []

    with X12ModelReader(input_message) as r:
        for m in r.models():
            models.append(m)
    return models


def load_hl7(input_message: str) -> Message:
    """
    Loads a HL7 input into a model
    """
    return hl7.parse(input_message)


class Timer:
    """
    Context manager which mesasures elapsed time
    """

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.elapsed_time = self.end - self.start
