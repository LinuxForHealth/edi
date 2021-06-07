from json import JSONDecodeError
import json
import logging
from lxml import etree
from lxml.etree import ParseError
import hashlib
import time
import functools

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


def workflow_timer(fn):
    """
    Used to annotate a workflow method (decorator) to generate metrics.
    """

    @functools.wraps(fn)
    def wrapped_fn(self, *args, **kwargs):
        start = time.perf_counter()
        fn(self, *args, **kwargs)
        stop = time.perf_counter()
        elapsed_time = stop - start

        metric_name = f"{fn.__name__}Time"
        setattr(self.metrics, metric_name, elapsed_time)

    return wrapped_fn
