"""
analysis.py

Classes and functions used to generate EDI message metadata.

Usage:
edi_metadata: EdiMessageMetadata = analyze(input_message)
"""
import abc
from enum import Enum
import json
from typing import Optional, Type, Dict, Union
import logging

from .models import EdiMessageMetadata, EdiMessageFormat, BaseMessageFormat
from .support import load_json, load_xml, create_checksum
from .exceptions import EdiDataValidationException

from lxml.etree import _Element
from fhir.resources import construct_fhir_element as construct_fhir_r4
from fhir.resources.DSTU2 import construct_fhir_element as construct_fhir_dstu2
from fhir.resources.STU3 import construct_fhir_element as construct_fhir_stu3

logger = logging.getLogger(__name__)

# the minimum message size required for analysis and classification
MESSAGE_SAMPLE_SIZE: int = 3


class EdiAnalyzer(metaclass=abc.ABCMeta):
    """
    Abstract base class for Edi Message Analysis.

    EdiAnalysis analyzes an input messages and determines:
    * the base message format (JSON, CSV, XML, etc)
    * edi message format (X12, FHIR, HL, etc)
    * message size
    * checksum

    Subclasses implement `analyze_message_data` to provide additional fields:
    * implementation version
    * specification version
    * record count
    """

    def __init__(
        self,
        input_message: str,
        base_message_format: BaseMessageFormat,
        edi_message_format: EdiMessageFormat,
    ):
        """ "
        :param input_message: The input EDI message
        :param base_message_format: The base message format (TEXT, JSON, XML, etc)
        :param edi_message_format: The edi message format (FHIR, XML, HL7, etc)
        """
        self.input_message = input_message
        self.base_message_format = base_message_format
        self.edi_message_format = edi_message_format

    def analyze(self) -> EdiMessageMetadata:
        """
        Returns EdiMessageMetadata for the associated message
        """
        metadata_fields = {
            "baseMessageFormat": self.base_message_format.value,
            "ediMessageFormat": self.edi_message_format.value,
            "checksum": create_checksum(self.input_message),
        }

        # handle str and bytes
        if isinstance(self.input_message, str):
            metadata_fields["messageSize"] = len(
                bytes(self.input_message.encode("utf-8"))
            )
        else:
            metadata_fields["messageSize"] = len(self.input_message)

        additional_fields = self.analyze_message_data()
        metadata_fields.update(additional_fields)
        message_metadata = EdiMessageMetadata(**metadata_fields)
        return message_metadata

    @abc.abstractmethod
    def analyze_message_data(self) -> Dict:
        """
        Parses the EDI message to provide edi format specific fields: such as specificationVersion and
        * implementationVersions
        * specificationVersion
        * recordCount
        """
        return


class FhirAnalyzer(EdiAnalyzer):
    """

    EdiAnalysis FHIR Implementation
    Currently only FHIR JSON is supported. FHIR XML support is included as a "starting point" for if/when FHIR XML
    is supported.
    """

    class FhirSpecificationVersion(str, Enum):
        R4 = "R4"
        STU3 = "STU3"
        DSTU2 = "DSTU2"

    # maps FHIR factory functions to a specification version
    version_map = {
        construct_fhir_r4: FhirSpecificationVersion.R4,
        construct_fhir_stu3: FhirSpecificationVersion.STU3,
        construct_fhir_dstu2: FhirSpecificationVersion.DSTU2,
    }

    def _parse_json_specification_version(self, fhir_json: Dict) -> str:
        """
        Parses the input message using multiple passes to determine the FHIR specification version.
        :param fhir_json: The FHIR JSON resource
        :raises: EdiDataValidationException if the specification version cannot be parsed
        :return: The specification version
        """
        resourceType = fhir_json.get("resourceType")
        specification_version = None

        for c in (construct_fhir_r4, construct_fhir_stu3, construct_fhir_dstu2):
            try:
                fhir_resource = c(resourceType, fhir_json)
                if fhir_resource:
                    specification_version = FhirAnalyzer.version_map[c]
                    break
            except Exception as ex:
                logger.debug(f"FHIR Resource is not compatible with {c.__name__}")

        if not specification_version:
            raise EdiDataValidationException(
                "Resource is not compatible with FHIR R4, STU3, DSTU2"
            )

        return specification_version

    def _analyze_fhir_json_data(self) -> Dict:
        """
        Parses additional data from a FHIR JSON message for the EDI Analysis.
        Sets the following fields:
        - specificationVersion
        - implementationVersions
        :returns: dictionary
        """
        fhir_json = load_json(self.input_message)

        data = {
            "specificationVersion": self._parse_json_specification_version(fhir_json),
            "implementationVersions": fhir_json.get("meta", {}).get("profile", []),
        }

        return data

    def _analyze_fhir_xml_data(self) -> Dict:
        """
        An initial implementation for when FHIR XML is supported.
        :returns: dictionary
        """

        def _get_namespace(xml_root: _Element) -> Optional[str]:
            """Returns the XML namespace for a root element"""
            namespace: str = ""

            if "}" in xml_root.tag:
                tag_value = xml_root.tag
                end_index = tag_value.find("}") + 1
                namespace = tag_value[0:end_index]

            return namespace

        data = {"specificationVersion": "http://hl7.org/fhir"}

        fhir_xml = load_xml(self.input_message)
        fhir_namespace = _get_namespace(fhir_xml)

        profile_elements = fhir_xml.findall(
            fhir_namespace + "meta/" + fhir_namespace + "profile/[@value]"
        )
        if profile_elements:
            data["implementationVersions"] = [
                e.attrib["value"] for e in profile_elements
            ]

        return data

    def analyze_message_data(self) -> Dict:
        """
        Analyzes FHIR message to parse edi format specific fields.
        :raises: NotImplementedError if the FHIR message is XML
        """
        if self.base_message_format == BaseMessageFormat.JSON:
            return self._analyze_fhir_json_data()
        else:
            raise NotImplementedError(
                f"FHIR {self.base_message_format} is not supported"
            )


class Hl7Analyzer(EdiAnalyzer):
    """
    Provides HL7 message analysis.
    """

    def analyze_message_data(self) -> Dict:
        """
        Parses additional data from an HL7 TEXT message for the EDI Analysis.
        Sets the following fields:
        - specificationVersion
        - implementationVersions
        :returns: dictionary
        """

        records = self.input_message.split("\r")
        data = {}

        # validate that the message as records and a delimiter character
        if records and records[0][3:4]:
            msh_record = records[0]
            delimiter = msh_record[3:4]

            implementation_version = msh_record.split(delimiter)[11]
            data["implementationVersions"] = [implementation_version]
            data["specificationVersion"] = f"V{implementation_version[0]}"

        return data


class X12Analyzer(EdiAnalyzer):
    """
    Provides X12 message analysis
    """

    def analyze_message_data(self) -> Dict:
        """
        Parses additional data from an X12 TEXT message for the EDI Analysis.
        Sets the following fields:
        - specificationVersion
        - implementationVersions
        :returns: dictionary
        """
        records = self.input_message.replace("\r", "").replace("\n", "").split("~")
        data = {}

        if records and len(records) >= 2:
            gs_segment = records[1].replace("~", "")
            delimiter = gs_segment[2:3]

            implementation_version = gs_segment.split(delimiter)[8]
            data["implementationVersions"] = [implementation_version]
            data["specificationVersion"] = implementation_version[
                0 : implementation_version.find("X")
            ]

        return data


class PassthroughAnalyzer(EdiAnalyzer):
    """
    Provides a "no-op" analysis for formats which do not support additional fields.
    """

    def analyze_message_data(self) -> Dict:
        return {}


def _get_base_message_format(input_message: Union[bytes, str]) -> BaseMessageFormat:
    """returns the base message format (BINARY, JSON, XML, TEXT, etc) for a message"""
    base_message_format: Union[BaseMessageFormat, None] = None
    first_char = input_message.lstrip()[0:1]

    if isinstance(input_message, bytes):
        base_message_format = BaseMessageFormat.BINARY
    elif first_char in ("{", "["):
        base_message_format = BaseMessageFormat.JSON
    elif first_char == "<":
        base_message_format = BaseMessageFormat.XML
    else:
        base_message_format = BaseMessageFormat.TEXT
    return base_message_format


def _get_edi_message_format(
    input_message: str, base_message_format: BaseMessageFormat
) -> EdiMessageFormat:
    """
    Returns the edi message format (HL7, X12, FHIR, etc) for an input message.

    :param input_message: The input message
    :param base_message_format: The base message format (JSON, XML, etc)
    :raises: EdiDataValidationException if the edi message format cannot be determined
    :raises: NotImplementedError if the edi message format is not supported
    """
    edi_message_format: Union[EdiMessageFormat, None] = None

    if base_message_format == BaseMessageFormat.TEXT:
        first_chars = input_message.lstrip()[0:3]
        if first_chars.upper() == "MSH":
            edi_message_format = EdiMessageFormat.HL7
        elif first_chars.upper() == "ISA":
            edi_message_format = EdiMessageFormat.X12
    elif base_message_format == BaseMessageFormat.JSON:
        json_message = json.loads(input_message)
        if json_message.get("resourceType") is not None:
            edi_message_format = EdiMessageFormat.FHIR
    elif base_message_format == BaseMessageFormat.XML:
        xml_message = load_xml(input_message)
        if "http://hl7.org/fhir" in xml_message.tag.lower():
            raise NotImplementedError("FHIR Xml Support Is Not Implemented")
    elif base_message_format == BaseMessageFormat.BINARY:
        # test for DICOM identifier
        if input_message[128:132] == "DICM".encode("utf-8"):
            edi_message_format = EdiMessageFormat.DICOM

    if edi_message_format is None:
        raise EdiDataValidationException(
            "Unable to determine edi message format for input message"
        )

    return edi_message_format


def analyze(input_message: Union[bytes, str]):
    """
    Returns an EdiMessageMetadata document for the given input message

    :param input_message: The cached input message
    :raises: EdiDataValidationException if the input message cannot be mapped to an analyzer
    :return: EdiMessageMetadata
    """
    if input_message is None or len(input_message) < MESSAGE_SAMPLE_SIZE:
        raise EdiDataValidationException("Invalid input message")

    base_message_format: BaseMessageFormat = _get_base_message_format(input_message)
    edi_message_format: EdiMessageFormat = _get_edi_message_format(
        input_message, base_message_format
    )

    metadata_fields = {
        "base_message_format": base_message_format,
        "edi_message_format": edi_message_format,
    }
    analyis_instance: Type[EdiAnalyzer] = None

    if edi_message_format == EdiMessageFormat.FHIR:
        analyis_instance = FhirAnalyzer(input_message, **metadata_fields)
    elif edi_message_format == EdiMessageFormat.HL7:
        analyis_instance = Hl7Analyzer(input_message, **metadata_fields)
    elif edi_message_format == EdiMessageFormat.X12:
        analyis_instance = X12Analyzer(input_message, **metadata_fields)
    elif edi_message_format == EdiMessageFormat.DICOM:
        analyis_instance = PassthroughAnalyzer(input_message, **metadata_fields)
    else:
        raise EdiDataValidationException("Unable to load analyzer for input message")

    return analyis_instance.analyze()
