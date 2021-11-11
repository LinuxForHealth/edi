"""
analysis.py

Classes and functions used to parse and process EDI message metadata.
"""
from .models import EdiMessageMetadata, EdiMessageFormat, BaseMessageFormat
from .support import load_json, load_xml, create_checksum
from lxml.etree import _Element
from typing import Optional


class EdiAnalyzer:
    """
    Generates EdiMessageMetadata from an EDI Message.
    """

    def __init__(self, input_message: str):
        """
        Validates the input message
        :param input_message: The input message to be analyzed.
        """

        if not input_message or input_message.isspace():
            raise ValueError("Input message is empty, blank, or None")

        self.input_message: str = input_message
        self.base_message_format = None
        self.message_format = None

    def _is_hl7(self) -> bool:
        """
        Returns True if the associated message is a HL7 message
        """
        return self.input_message[0:3] == "MSH"

    def _is_x12(self) -> bool:
        """
        Returns True if the associated message is a X12 message
        """
        return self.input_message[0:3] == "ISA"

    def _is_fhir(self) -> bool:
        """
        Returns True if the associated message is a FHIR message
        """
        edi_first_char = self.input_message.lstrip()[0:1]

        if edi_first_char == "{":
            edi_json = load_json(self.input_message)
            return bool(edi_json.get("resourceType"))
        elif edi_first_char == "<":
            edi_xml = load_xml(self.input_message)
            return "http://hl7.org/fhir" in edi_xml.tag.lower()
        else:
            return False

    def _parse_message_format(self) -> EdiMessageFormat:
        """
        Returns the associated message's EDI Message Type
        Raises a ValueError if the format cannot be determined
        """
        if self._is_hl7():
            return EdiMessageFormat.HL7
        elif self._is_x12():
            return EdiMessageFormat.X12
        elif self._is_fhir():
            return EdiMessageFormat.FHIR
        else:
            raise ValueError("Unable to determine EDI format")

    def _parse_base_message_format(self) -> BaseMessageFormat:
        """
        Returns the associated message's base message format
        """
        first_char = self.input_message.lstrip()[0:1]
        if first_char in ("{", "["):
            return BaseMessageFormat.JSON
        elif first_char == "<":
            return BaseMessageFormat.XML
        else:
            return BaseMessageFormat.TEXT

    def _analyze_fhir_json_data(self) -> dict:
        """
        Parses additional data from a FHIR JSON message for the EDI Analysis.
        Sets the following fields:
        - specificationVersion
        - implementationVersion
        - recordCount
        :returns: dictionary
        """
        data = {"recordCount": 1, "specificationVersion": "http://hl7.org/fhir"}

        fhir_json = load_json(self.input_message)
        data["implementationVersions"] = profiles = fhir_json.get("meta", {}).get(
            "profile", []
        )

        if fhir_json.get("resourceType", "").lower() == "bundle":
            record_count = len(fhir_json.get("entry", []))
            data["recordCount"] = record_count

        return data

    def _analyze_fhir_xml_data(self) -> dict:
        """
        Parses additional data from a FHIR XML message for the EDI Analysis.
        Sets the following fields:
        - specificationVersion
        - implementationVersion
        - recordCount
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

        data = {"recordCount": 1, "specificationVersion": "http://hl7.org/fhir"}

        fhir_xml = load_xml(self.input_message)
        fhir_namespace = _get_namespace(fhir_xml)

        profile_elements = fhir_xml.findall(
            fhir_namespace + "meta/" + fhir_namespace + "profile/[@value]"
        )
        if profile_elements:
            data["implementationVersions"] = [
                e.attrib["value"] for e in profile_elements
            ]

        if "bundle" in fhir_xml.tag.lower():
            data["record_count"] = len(fhir_xml.findall(fhir_namespace + "entry"))

        return data

    def _analyze_hl7_data(self) -> dict:
        """
        Parses additional data from an HL7 message for the EDI Analysis.
        Sets the following fields:
        - specificationVersion
        - recordCount
        :returns: dictionary
        """

        records = self.input_message.split("\r")
        data = {"recordCount": 0}

        if records or not records[0][3:4]:
            msh_record = records[0]
            delimiter = msh_record[3:4]

            data["specificationVersion"] = msh_record.split(delimiter)[11]
            data["recordCount"] = len([r for r in records if r])

        return data

    def _analyze_x12_data(self) -> dict:
        """
        Parses additional data from a X12 message for the EDI Analysis.
        Sets the following fields:
        - specificationVersion
        - recordCount
        :returns: dictionary
        """

        records = self.input_message.replace("\r", "").replace("\n", "").split("~")
        data = {"recordCount": 0}

        if records and len(records) >= 2:
            gs_segment = records[1].replace("~", "")
            delimiter = gs_segment[2:3]

            data["specificationVersion"] = gs_segment.split(delimiter)[8]
            data["recordCount"] = len([r for r in records if r])

        return data

    def analyze(self) -> EdiMessageMetadata:
        """
        Returns EdiMessageMetadata for the associated message
        """
        self.base_message_format = self._parse_base_message_format()
        self.message_format = self._parse_message_format()

        metadata_fields = {
            "baseMessageFormat": self.base_message_format.value,
            "messageFormat": self.message_format.value,
            "messageSize": len(bytes(self.input_message.encode("utf-8"))),
            "checksum": create_checksum(self.input_message),
        }

        additional_fields = {}
        if self.message_format == EdiMessageFormat.HL7:
            additional_fields = self._analyze_hl7_data()
        elif (
                self.message_format == EdiMessageFormat.FHIR
                and self.base_message_format == BaseMessageFormat.JSON
        ):
            additional_fields = self._analyze_fhir_json_data()
        elif (
                self.message_format == EdiMessageFormat.FHIR
                and self.base_message_format == BaseMessageFormat.XML
        ):
            additional_fields = self._analyze_fhir_xml_data()
        elif self.message_format == EdiMessageFormat.X12:
            additional_fields = self._analyze_x12_data()
        else:
            raise ValueError("Unsupported format")

        metadata_fields.update(additional_fields)
        message_metadata = EdiMessageMetadata(**metadata_fields)
        return message_metadata
