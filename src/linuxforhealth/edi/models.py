"""
models.py

EDI Pydantic Domain Models.
"""
from pydantic import BaseModel
from enum import Enum
from typing import List, Optional


class BaseMessageFormat(str, Enum):
    """
    The base message format used for an EDI message
    """

    BINARY = "BINARY"
    JSON = "JSON"
    TEXT = "TEXT"
    XML = "XML"


class EdiMessageFormat(str, Enum):
    """
    Supported EDI Message Formats
    """

    CCDA = "C-CDA"
    DICOM = "DICOM"
    FHIR = "FHIR"
    HL7 = "HL7"
    X12 = "X12"


class EdiMessageMetadata(BaseModel):
    """
    EDI message metadata including the message type, version, record count, etc.
    """

    baseMessageFormat: BaseMessageFormat
    ediMessageFormat: EdiMessageFormat
    specificationVersion: Optional[str]
    implementationVersions: List[str] = []
    messageSize: int
    checksum: str

    class Config:
        extra = "forbid"
        schema_extra = {
            "example": {
                "baseMessageFormat": "TEXT",
                "ediMessageFormat": "X12",
                "specificationVersion": "005010X279A1",
                "implementationVersions": ["Supplemental Payer Guide"],
                "messageSize": 509,
                "checksum": "d7a928f396efa0bb15277991bd8d4d9a2506d751f9de8b344c1a3e5f8c45a409",
            }
        }


class EdiProcessingMetrics(BaseModel):
    """
    Captures processing metrics for EDI operations
    """

    analyzeTime: float = 0.0
    enrichTime: float = 0.0
    validateTime: float = 0.0
    translateTime: float = 0.0
    totalTime: float = 0.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.totalTime = (
            self.analyzeTime + self.enrichTime + self.validateTime + self.translateTime
        )

    class Config:
        extra = "forbid"
        schema_extra = {
            "example": {
                "analyzeTime": 0.142347273,
                "enrichTime": 0.013415911,
                "validateTime": 0.013415911,
                "translateTime": 2.625179046,
                "totalTime": 2.794358141,
            }
        }


class EdiResult(BaseModel):
    """
    EDI Processing Result
    """

    metadata: Optional[EdiMessageMetadata]
    metrics: Optional[EdiProcessingMetrics]
    errors: List[str] = []

    class Config:
        extra = "forbid"
        schema_extra = {
            "example": {
                "metadata": {
                    "baseMessageFormat": "TEXT",
                    "ediMessageFormat": "HL7",
                    "specificationVersion": "v2",
                    "implementationVersions": ["2.6"],
                    "messageSize": 509,
                    "checksum": "d7a928f396efa0bb15277991bd8d4d9a2506d751f9de8b344c1a3e5f8c45a409",
                },
                "metrics": {
                    "analyzeTime": 0.142347273,
                    "enrichTime": 0.0,
                    "validateTime": 0.013415911,
                    "translateTime": 2.625179046,
                },
                "errors": [],
            }
        }
