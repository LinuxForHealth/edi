"""
workflows.py

Defines EDI processing workflows.
"""
import time

import xworkflows
from xworkflows import transition
from typing import Any, List, Optional

from edi.core.analysis import EdiAnalyzer
from edi.core.models import (
    EdiMessageMetadata,
    EdiProcessingMetrics,
    EdiOperations,
    EdiResult,
)
import logging

logger = logging.getLogger(__name__)


class EdiWorkflow(xworkflows.Workflow):
    """
    Defines the states and transitions used in an EDI workflow.

    States are used to specify the current state of processing, while transitions are methods which perform a task and
    then update the state. The EdiWorkflow is used within an EdiProcess to process an EDI message.

    Transitions in the EDI workflow include:
    <ul>
        <li>analyze - Generates an EdiMessageMetadata object for the EDI Message.</li>
        <li>enrich - Enriches the input message with additional data using custom transformations.</li>
        <li>validate - Validates the input message.</li>
        <li>translate- Translates the input message in a supported format to a different supported format. Example: translate HL7v2 to FHIR.</li>
        <li>complete - Marks the EDI workflow as complete, returning an EDI result.</li>
        <li>cancel - Cancels the current workflow process, returning an EDI result.</li>
        <li>fail - Reached if the workflow encounters an unrecoverable error. Returns an EDI result.</li>
    </ul>
    """

    states = (
        ("init", "Initial State"),
        ("analyzed", "Analyze Message"),
        ("enriched", "Enrich Message"),
        ("validated", "Validate Message"),
        ("translated", "Translate Message"),
        ("completed", "Complete Processing"),
        ("cancelled", "Cancel Processing"),
        ("failed", "Fail Processing"),
    )

    transitions = (
        ("analyze", "init", "analyzed"),
        ("enrich", "analyzed", "enriched"),
        ("validate", ("analyzed", "enriched"), "validated"),
        ("translate", ("analyzed", "enriched", "validated"), "translated"),
        ("complete", ("analyzed", "enriched", "validated", "translated"), "completed"),
        (
            "cancel",
            ("init", "analyzed", "enriched", "validated", "translated"),
            "cancelled",
        ),
        ("fail", ("init", "analyzed", "enriched", "validated", "translated"), "failed"),
    )

    initial_state = "init"


class EdiProcessor(xworkflows.WorkflowEnabled):
    """
    Processes EDI Messages.
    """

    state = EdiWorkflow()

    supported_run_operations: List[EdiOperations] = [
        EdiOperations.ENRICH,
        EdiOperations.VALIDATE,
        EdiOperations.TRANSLATE,
    ]

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

    @transition("analyze")
    def analyze(self):
        """
        Generates EdiMessageMetadata for the input message.
        """
        start = time.perf_counter()

        analyzer = EdiAnalyzer(self.input_message)
        self.meta_data = analyzer.analyze()

        end = time.perf_counter()
        elapsed_time = end - start
        self.metrics.analyzeTime = elapsed_time
        self.operations.append(EdiOperations.ANALYZE)

    @transition("enrich")
    def enrich(self):
        """
        Adds additional data to the input message.
        """
        start = time.perf_counter()
        # TODO: enrichment implementation
        end = time.perf_counter()
        elapsed_time = end - start
        self.metrics.enrichTime = elapsed_time
        self.operations.append(EdiOperations.ENRICH)

    @transition("validate")
    def validate(self):
        """
        Validates the input message.
        """
        start = time.perf_counter()
        # TODO: validation implementation
        end = time.perf_counter()
        elapsed_time = end - start
        self.metrics.validateTime = elapsed_time
        self.operations.append(EdiOperations.VALIDATE)

    @transition("translate")
    def translate(self):
        """
        Translates the input message to a different, supported format.
        """
        start = time.perf_counter()
        # TODO: translate implementation
        end = time.perf_counter()
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

    @transition("complete")
    def complete(self) -> EdiResult:
        """
        Marks the workflow as completed and generates an EDI Result.
        :return: EdiResult
        """
        self.operations.append(EdiOperations.COMPLETE)
        return self._create_edi_result()

    @transition("cancel")
    def cancel(self) -> EdiResult:
        """
        Marks the workflow as cancelled and generates an EDI Result.
        :return: EdiResult
        """
        self.operations.append(EdiOperations.CANCEL)
        return self._create_edi_result()

    @transition("fail")
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
