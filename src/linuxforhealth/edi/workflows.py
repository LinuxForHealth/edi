"""
workflows.py

Defines EDI processing workflows.
"""

from typing import Union, Optional

from .models import (
    EdiMessageMetadata,
    EdiProcessingMetrics,
    EdiResult,
    EdiMessageFormat,
)
from .support import Timer, load_fhir_json, load_hl7, load_x12, load_dicom
from .analysis import analyze
import logging
import os

logger = logging.getLogger(__name__)


class EdiWorkflow:
    """
    Defines the steps and transitions used in an EDI workflow.

    The EdiWorkflow is used within an EdiProcess to process an EDI message.

    Transitions in the EDI workflow include:
        * analyze - Generates an EdiMessageMetadata object for the EDI Message.
        * enrich - Enriches the input message with additional data using custom transformations.
        * validate - Validates the input message.
        * translate- Translates the input message in a supported format to a different supported format. Example: translate HL7v2 to FHIR
        * complete - Marks the EDI workflow as complete, returning an EDI result.
        * cancel - Cancels the current workflow process, returning an EDI result.
        * fail - Reached if the workflow encounters an unrecoverable error. Returns an EDI result
    """

    def __init__(self, input_message: Union[bytes, str]):
        """
        Configures the EdiProcess instance.
        Attributes include:
        - input_message: cached source message
        - errors: error messages encountered during processing
        - data_model: edi domain model (FHIR, HL7, X12, etc)
        - meta_data: EdiMessageMetadata object
        - metrics: EdiProcessingMetrics object
        - operations: List of EdiOperations completed for this instance
        """

        self.input_message = input_message
        self.errors: List[str] = []
        self.data_model = None
        self.meta_data: Optional[EdiMessageMetadata] = None
        self.metrics: EdiProcessingMetrics = EdiProcessingMetrics(
            analyzeTime=0.0, enrichTime=0.0, validateTime=0.0, translateTime=0.0
        )
        self.operations: Optional[EdiOperations] = []

    def _analyze(self):
        """
        Generates EdiMessageMetadata for the input message.
        """
        try:
            with Timer() as t:
                self.meta_data = analyze(self.input_message)

            self.metrics.analyzeTime = t.elapsed_time
        except Exception as ex:
            self._fail(f"An error occurred analyzing EDI {ex}")

    def _enrich(self):
        """
        Adds additional data to the input message.
        """
        pass

    def _validate(self):
        """
        Validates the input message and populates the data_model instance attribute.
        """
        try:
            with Timer() as t:
                edi_message_format = self.meta_data.ediMessageFormat

                if edi_message_format == EdiMessageFormat.FHIR:
                    self.data_model = load_fhir_json(self.input_message)
                elif edi_message_format == EdiMessageFormat.HL7:
                    self.data_model = load_hl7(self.input_message)
                elif edi_message_format == EdiMessageFormat.X12:
                    self.data_model = load_x12(self.input_message)
                elif edi_message_format == EdiMessageFormat.DICOM:
                    self.data_model = load_dicom(self.input_message)

                if self.data_model is None:
                    raise ValueError("Unable to load model")

            self.metrics.validateTime = t.elapsed_time
        except Exception as ex:
            self._fail(f"An error occurred validating EDI {ex}")

    def _translate(self):
        """
        Translates the input message to a different, supported format.
        """
        pass

    def _create_edi_result(self) -> EdiResult:
        """
        Creates an EdiResult
        """
        result_data = {
            "metadata": self.meta_data.dict() if self.meta_data else None,
            "metrics": self.metrics.dict(),
            "errors": self.errors,
        }

        return EdiResult(**result_data)

    def _fail(self, *errors):
        """
        Records errors which occurred during processing
        :param errors: error messages encountered during processing
        """
        self.errors.extend(errors)

    def run(self, enrich=True, validate=True, translate=True):
        """
        Runs an EDI workflow process.

        :param enrich: Indicates if the enrich step is executed. Defaults to True.
        :param validate: Indicates if the validation step is executed. Defaults to True.
        :param translate: Indicates if the translate step is executed. Defaults to True.
        """

        try:
            self._analyze()

            if enrich:
                self._enrich()

            if validate:
                self._validate()

            if translate:
                self._translate()

        except Exception as ex:
            msg = f"An error occurred executing the EdiWorkflow {ex}"
            logger.exception(msg, ex)
            self._fail(msg)
        finally:
            return self._create_edi_result()


def load_workflow_from_file(file_path: str) -> EdiWorkflow:
    """
    Loads an EDI workflow from an EDI file
    :param file_path: The path to the EDI file
    :returns: EdiWorkflow
    """
    with open(file_path, "rb") as f:
        contents: bytes = f.read()

    try:
        buffer = contents[0:1024]
        buffer.decode("utf-8")
        is_unicode = True
    except UnicodeDecodeError:
        is_unicode = False

    input_message = contents.decode("utf-8") if is_unicode else contents
    return EdiWorkflow(input_message)
