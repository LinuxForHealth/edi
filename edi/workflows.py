"""
workflows.py

Defines EDI processing workflows.
"""

from typing import Any, List, Optional

from edi.analysis import EdiAnalyzer
from edi.models import (
    EdiMessageMetadata,
    EdiProcessingMetrics,
    EdiOperations,
    EdiResult,
)
from edi.support import perf_counter_ms
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
        - meta_data: EdiMessageMetadata object
        - metrics: EdiProcessingMetrics object
        - operations: List of EdiOperations completed for this instance
        """

        self.input_message = input_message
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
        start = perf_counter_ms()

        analyzer = EdiAnalyzer(self.input_message)
        self.meta_data = analyzer.analyze()

        end = perf_counter_ms()
        elapsed_time = end - start
        self.metrics.analyzeTime = elapsed_time
        self.operations.append(EdiOperations.ANALYZE)

    def enrich(self):
        """
        Adds additional data to the input message.
        """
        start = perf_counter_ms()
        # TODO: enrichment implementation
        end = perf_counter_ms()
        elapsed_time = end - start
        self.metrics.enrichTime = elapsed_time
        self.operations.append(EdiOperations.ENRICH)

    def validate(self):
        """
        Validates the input message.
        """
        start = perf_counter_ms()
        # TODO: validation implementation
        end = perf_counter_ms()
        elapsed_time = end - start
        self.metrics.validateTime = elapsed_time
        self.operations.append(EdiOperations.VALIDATE)

    def translate(self):
        """
        Translates the input message to a different, supported format.
        """
        start = perf_counter_ms()
        # TODO: translate implementation
        end = perf_counter_ms()
        elapsed_time = end - start
        self.metrics.translateTime = elapsed_time
        self.operations.append(EdiOperations.TRANSLATE)

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
        By default the workflow process includes: analyze, enrich, validate, and translate, and is marked as completed.
        The method paramee
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
            msg = "An error occurred executing the EdiProcessor workflow"
            logger.exception(msg)
            return self.fail(msg, ex)
