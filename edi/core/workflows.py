"""
workflows.py

Defines EDI processing workflows.
"""
import xworkflows
from xworkflows import transition
from typing import Any, Optional
from edi.core.models import EdiMessageMetadata


class EdiWorkflow(xworkflows.Workflow):
    """
    Defines the states and transitions used in an EDI workflow.

    States are used to specify the current state of processing, while transitions are methods which perform a task and
    then update the state. The EdiWorkflow is used within an EdiProcess to process an EDI message.

    Transitions in the EDI workflow include:
    <ul>
        <li>analyze - generates EDI Message metadata.</li>
        <li>transform- used to enrich the input message in its current format, or transform the message to a different format.</li>
        <li>validate - validates the message.</li>
        <li>complete - marks the EDI workflow as complete, returning an EDI result.</li>
        <li>cancel - terminates the EDI workflow. May be used at any state prior to transmit.</li>
    </ul>
    """

    states = (
        ("init", "Initial State"),
        ("analyzed", "Analyze Message"),
    )

    transitions = (("analyze", "init", "analyzed"),)

    initial_state = "init"


class EdiProcessor(xworkflows.WorkflowEnabled):
    """
    Processes EDI Messages.
    """

    state = EdiWorkflow()

    def __init__(self, input_message: Any):
        self.input_message = input_message
        self.meta_data: Optional[EdiMessageMetadata] = None

    @transition("analyze")
    def analyze(self):
        pass
