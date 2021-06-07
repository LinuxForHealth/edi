"""
workflows.py

Defines EDI processing workflows.
"""
import xworkflows
from xworkflows import transition
from typing import Any, Optional

from edi.core.analysis import EdiAnalyzer
from edi.core.models import EdiMessageMetadata, EdiProcessingMetrics
from edi.core.support import workflow_timer


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
        self.input_message = input_message
        self.meta_data: Optional[EdiMessageMetadata] = None
        self.metrics: EdiProcessingMetrics = EdiProcessingMetrics(
            analyzeTime=0.0, enrichTime=0.0, validateTime=0.0, translateTime=0.0
        )

    @transition("analyze")
    @workflow_timer
    def analyze(self):
        analyzer = EdiAnalyzer(self.input_message)
        self.meta_data = analyzer.analyze()

    @transition("enrich")
    @workflow_timer
    def enrich(self):
        pass

    @transition("validate")
    @workflow_timer
    def validate(self):
        pass

    @transition("translate")
    @workflow_timer
    def translate(self):
        pass

    @transition("complete")
    def complete(self):
        pass

    @transition("cancel")
    def cancel(self):
        pass

    @transition("fail")
    def fail(self):
        pass
