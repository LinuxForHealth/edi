from pydantic import BaseModel
from enum import Enum


class EdiMessageType(str, Enum):
    CCDA = "CCDA"
    FHIR = "FHIR"
    HL7 = "HL7"
    X12 = "X12"


class EdiStatistics(BaseModel):
    """EDI Statistics"""

    message_type: EdiMessageType
    specification_version: str
    implementation_version: str
    message_size: int
    record_count: int
    checksum: str

    class Config:
        allow_mutation = False
        schema_extra = {
            "example": {
                "message_type": "X12_270",
                "specification_version": "005010X279A1",
                "implementation_version": "005010X279A1",
                "message_size": 509,
                "record_count": 17,
                "checksum": "d7a928f396efa0bb15277991bd8d4d9a2506d751f9de8b344c1a3e5f8c45a409",
            }
        }


class StatusResponse(BaseModel):
    """
    Status check response model.
    Provides component specific and overall status information
    """

    application: str
    application_version: str
    is_reload_enabled: bool

    class Config:
        allow_mutation = False
        schema_extra = {
            "example": {
                "application": "edi.main:app",
                "application_version": "0.25.0",
                "is_reload_enabled": False,
            }
        }
