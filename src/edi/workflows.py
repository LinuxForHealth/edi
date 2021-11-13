"""
workflows.py

Defines EDI processing workflows.
"""

from typing import Any, Optional

from .models import (
    EdiMessageMetadata,
    EdiProcessingMetrics,
    EdiOperations,
    EdiResult,
    EdiMessageFormat
)
from .support import Timer, load_fhir_json, load_hl7, load_x12
from .analysis import get_analyzer
import logging

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

    def __init__(self, input_message: Any):
        """
        Configures the EdiProcess instance.
        Attributes include:
        - input_message: cached source message
        - data_model: edi domain model (FHIR, HL7, X12, etc)
        - meta_data: EdiMessageMetadata object
        - metrics: EdiProcessingMetrics object
        - operations: List of EdiOperations completed for this instance
        """

        self.input_message = input_message
        self.data_model = None
        self.meta_data: Optional[EdiMessageMetadata] = None
        self.metrics: EdiProcessingMetrics = EdiProcessingMetrics(
            analyzeTime=0.0, enrichTime=0.0, validateTime=0.0, translateTime=0.0
        )
        self.operations: Optional[EdiOperations] = []

    @property
    def current_state(self) -> EdiOperations:
        """Returns the current operation state"""
        return self.operations[-1] if self.operations else None

    def analyze(self):
        """
        Generates EdiMessageMetadata for the input message.
        """
        with Timer() as t:
            analyzer = get_analyzer(self.input_message)
            self.meta_data = analyzer.analyze()
            self.operations.append(EdiOperations.ANALYZE)

        self.metrics.analyzeTime = t.elapsed_time

    def enrich(self):
        """
        Adds additional data to the input message.
        """
        with Timer() as t:
            # TODO: enrichment implementation
            self.operations.append(EdiOperations.ENRICH)
        self.metrics.enrichTime = t.elapsed_time

    def validate(self):
        """
        Validates the input message and populates the data_model instance attribute.
        """
        with Timer() as t:
            edi_message_format = self.meta_data.ediMessageFormat

            if edi_message_format == EdiMessageFormat.FHIR:
                self.data_model = load_fhir_json(self.input_message)
            elif edi_message_format == EdiMessageFormat.HL7:
                self.data_model = load_hl7(self.input_message)
            elif edi_message_format == EdiMessageFormat.X12:
                self.data_model = load_x12(self.input_message)

            if self.data_model is None:
                raise ValueError("Unable to load model")

            self.operations.append(EdiOperations.VALIDATE)
        self.metrics.validateTime = t.elapsed_time

    def translate(self):
        """
        Translates the input message to a different, supported format.
        """
        with Timer() as t:
            # TODO: validation implementation
            self.operations.append(EdiOperations.TRANSLATE)
        self.metrics.translateTime = t.elapsed_time

    def _create_edi_result(self) -> EdiResult:
        """
        Creates an EdiResult
        """
        result_data = {
            "metadata": self.meta_data.dict() if self.meta_data else None,
            "metrics": self.metrics.dict(),
            "inputMessage": self.input_message,
            "operations": self.operations,
            "errors": [],
        }

        return EdiResult(**result_data)

    def complete(self) -> EdiResult:
        """
        Marks the workflow as completed and generates an EDI Result.
        :return: EdiResult
        """
        self.operations.append(EdiOperations.COMPLETE)
        return self._create_edi_result()

    def cancel(self) -> EdiResult:
        """
        Marks the workflow as cancelled and generates an EDI Result.
        :return: EdiResult
        """
        self.operations.append(EdiOperations.CANCEL)
        return self._create_edi_result()

    def fail(self, reason: str, exception: Exception = None):
        """
        Marks the workflow as cancelled and generates an EDI Result.
        :param reason: The reason the workflow failed
        :param exception: The associated exception object if available. Defaults to None
        :return: EdiResult
        """
        self.operations.append(EdiOperations.FAIL)

        edi_result = self._create_edi_result()
        edi_result.errors.append({"msg": reason})

        if exception:
            edi_result.errors.append({"msg": str(exception)})
        return edi_result

    def run(self, enrich=True, validate=True, translate=True):
        """
        Convenience method used to run a workflow process.
        The analyze step is included by default.
        The reamining steps: enrich, validate, and translate are optional.

        :param enrich: Indicates if the enrich step is executed. Defaults to True.
        :param validate: Indicates if the validation step is executed. Defaults to True.
        :param translate: Indicates if the translate step is executed. Defaults to True.
        """

        try:
            self.analyze()

            if enrich:
                self.enrich()

            if validate:
                self.validate()

            if translate:
                self.translate()

            return self.complete()
        except Exception as ex:
            msg = "An error occurred executing the EdiWorkflow"
            logger.exception(msg)
            return self.fail(msg, ex)
