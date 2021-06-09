"""
workflows.py

Defines EDI processing workflows.
"""
import time

import xworkflows
from xworkflows import transition
from typing import Any, Optional

from edi.core.analysis import EdiAnalyzer
from edi.core.models import EdiMessageMetadata, EdiProcessingMetrics, EdiOperations
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
        start = time.perf_counter()

        analyzer = EdiAnalyzer(self.input_message)
        self.meta_data = analyzer.analyze()

        end = time.perf_counter()
        elapsed_time = end - start
        self.metrics.analyzeTime = elapsed_time
        self.operations.append(EdiOperations.ANALYZE)

    @transition("enrich")
    def enrich(self):
        start = time.perf_counter()

        end = time.perf_counter()
        elapsed_time = end - start
        self.metrics.enrichTime = elapsed_time
        self.operations.append(EdiOperations.ENRICH)

    @transition("validate")
    def validate(self):
        start = time.perf_counter()

        end = time.perf_counter()
        elapsed_time = end - start
        self.metrics.validateTime = elapsed_time
        self.operations.append(EdiOperations.VALIDATE)

    @transition("translate")
    def translate(self):
        start = time.perf_counter()

        end = time.perf_counter()
        elapsed_time = end - start
        self.metrics.translateTime = elapsed_time
        self.operations.append(EdiOperations.TRANSLATE)

    @transition("complete")
    def complete(self):
        self.operations.append(EdiOperations.COMPLETE)

    @transition("cancel")
    def cancel(self):
        self.operations.append(EdiOperations.CANCEL)

    @transition("fail")
    def fail(self):
        self.operations.append(EdiOperations.FAIL)

    def run(self, *args: EdiOperations):
        """
        Convenience method used to run a workflow process.
        Run accepts an optional list of EdiOperations to perform, ignoring operations which are required (analyze) and additional
        operations used to terminate a workflow (cancel, complete, fail).
        If a list is not provided, the method will execute each available operations as noted above.
        If an exception occurs, the error is logged and the workflow is set to "fail"
        The EdiOperations are expected to be listed in dependency order.
        """
        excluded_operations = (
            EdiOperations.ANALYZE,
            EdiOperations.CANCEL,
            EdiOperations.COMPLETE,
            EdiOperations.FAIL,
        )

        if not args:
            args = list(EdiOperations)

        args = [a.lower() for a in args if a not in excluded_operations]

        try:
            self.analyze()
            for method_name in args:
                method = getattr(self, method_name)
                method()
            self.complete()
        except Exception as ex:
            logger.exception(f"Error executing workflow method {method_name}")
            self.fail()
