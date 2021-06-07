"""
models.py

EDI Pydantic Domain Models.
"""
from pydantic import BaseModel
from enum import Enum
from typing import List


class BaseMessageType(str, Enum):
    """
    The base message type used for an EDI message
    """

    JSON = "JSON"
    TEXT = "TEXT"
    XML = "XML"


class EdiMessageType(str, Enum):
    """
    Supported EDI Message Types
    """

    FHIR = "FHIR"
    HL7 = "HL7"
    X12 = "X12"


class EdiOperations(str, Enum):
    """
    Supported EDI Operations
    """

    ANALYZE = "ANALYZE"
    ENRICH = "ENRICH"
    VALIDATE = "VALIDATE"
    TRANSLATE = "TRANSLATE"
    COMPLETE = "COMPLETE"
    CANCEL = "CANCEL"
    FAIL = "FAIL"


class EdiMessageMetadata(BaseModel):
    """
    EDI message metadata including the message type, version, record count, etc.
    """

    baseMessageType: BaseMessageType
    messageType: EdiMessageType
    specificationVersion: str
    implementationVersions: List[str] = None
    messageSize: int
    recordCount: int
    checksum: str

    class Config:
        schema_extra = {
            "example": {
                "baseMessageType": "TEXT",
                "messageType": "X12",
                "specificationVersion": "005010X279A1",
                "implementationVersions": ["Supplemental Payer Guide"],
                "messageSize": 509,
                "recordCount": 17,
                "checksum": "d7a928f396efa0bb15277991bd8d4d9a2506d751f9de8b344c1a3e5f8c45a409",
            }
        }


class EdiProcessingMetrics(BaseModel):
    """
    Captures processing metrics for EDI operations
    """

    operations: List[EdiOperations] = []
    analyzeTime: float = 0.0
    enrichTime: float = 0.0
    validateTime: float = 0.0
    translateTime: float = 0.0
    totalTime: float = 0.0

    @property
    def total_time(self) -> float:
        """Returns the total processing time"""
        return (
            self.analyzeTime + self.enrichTime + self.validateTime + self.translateTime
        )

    class Config:
        schema_extra = {
            "example": {
                "operations": [
                    "ANALYZE",
                    "ENRICH",
                    "VALIDATE",
                    "TRANSLATE",
                    "COMPLETE",
                ],
                "analyzeTime": 0.142347273,
                "enrichTime": 0.013415911,
                "validationTime": 0.013415911,
                "translateTime": 2.625179046,
                "totalTime": 2.794358141,
            }
        }


class EdiResult(BaseModel):
    """
    EDI Processing Result
    """

    metadata: EdiMessageMetadata
    metrics: EdiProcessingMetrics
    errors: List[dict] = []

    class Config:
        schema_extra = {
            "example": {
                "metadata": {
                    "baseMessageType": "TEXT",
                    "messageType": "HL7",
                    "specificationVersion": "2.6",
                    "messageSize": 509,
                    "recordCount": 17,
                    "checksum": "d7a928f396efa0bb15277991bd8d4d9a2506d751f9de8b344c1a3e5f8c45a409",
                },
                "metrics": {
                    "operations": ["ANALYZE", "VALIDATE", "TRANSLATE", "COMPLETE"],
                    "analyzeTime": 0.142347273,
                    "validationTime": 0.013415911,
                    "translateTime": 2.625179046,
                },
                "errors": [],
            }
        }


class StatusResponse(BaseModel):
    """
    Status check response model.
    Provides component specific and overall status information
    """

    application: str
    applicationVersion: str
    isReloadEnabled: bool

    class Config:
        allow_mutation = False
        schema_extra = {
            "example": {
                "application": "edi.main:app",
                "applicationVersion": "0.25.0",
                "isReloadEnabled": False,
            }
        }
