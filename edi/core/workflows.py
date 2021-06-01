import xworkflows
from xworkflows import transition


class EdiWorkflow(xworkflows.Workflow):
    """
    Defines the states and transitions used in an EDI workflow.

    States are used to specify the current state of processing, while transitions are methods which perform a task and
    then update the state. The EdiWorkflow is used within an EdiProcess to process an EDI message.

    The transitions in the EDI workflow include:
    <ul>
        <li>classify - generates EDI Message metadata.</li>
        <li>transform- used to enrich the input message in its current format, or transform the message to a different format.</li>
        <li>validate - validates the message.</li>
        <li>transmit - transmits the EDI message to an external system.</li>
        <li>complete - marks the EDI workflow as complete, returning an EDI result.</li>
        <li>cancel - terminates the EDI workflow. May be used at any state prior to transmit.</li>
    </ul>
    """
    states = (
        ("init", "Initial State"),
        ("classified", "Classify Message"),
        ("transformed", "Transform Message"),
        ("validated", "Validate Message"),
        ("transmitted", "Transmit Message"),
        ("completed", "Processing Complete"),
        ("cancelled", "Processing Cancelled")
    )

    transitions = (
        ("classify", "init", "classified"),
        ("transform", "classified", "transformed"),
        ("validate", "transformed", "validated"),
        ("transmit", "validated", "transmitted"),
        ("complete", "transmitted", "completed"),
        ("cancel", ("classified", "transformed", "validated"), "cancelled")
    )

    initial_state = "init"


class EdiProcessor(xworkflows.WorkflowEnabled):
    """
    Provides a base implementation for processing EDI messages.
    This class is extended to support specific EDI implementations and formats such as HL7v2, FHIR R4, X12 5010, etc.
    The EdiProcessor and its subclasses use the transition methods defined in the EdiWorkflow to support workflow
    processing.
    """
    state = EdiWorkflow()

    def __init__(self, message):
        self.message = message
        self.result = {}

    @transition("classify")
    def classify(self):
        pass

    @transition("transform")
    def transform(self):
        pass

    @transition("validate")
    def validate(self):
        pass

    @transition("transmit")
    def transmit(self):
        pass

    @transition("complete")
    def complete(self):
        pass

    @transition("cancel")
    def cancel(self):
        pass
