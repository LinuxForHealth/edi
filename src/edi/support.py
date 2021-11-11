import time
from json import JSONDecodeError
import json
import logging
from lxml import etree
from lxml.etree import ParseError
import hashlib

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


class Timer:
    """
    Context manager which mesasures elapsed time
    """
    def __enter__(self):
        self.start = time.perf_counter() * 1_000
        return self

    def __exit__(self, *args):
        self.end = time.perf_counter() * 1_000
        self.elapsed_time = self.end - self.start
