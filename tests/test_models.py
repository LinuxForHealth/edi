"""
test_models.py

Tests model features such as properties, custom validations, and processing methods.
Each model is tested with it's Open API "example"
"""
from edi.core.models import (
    EdiProcessingMetrics,
    EdiMessageMetadata,
    EdiResult,
)


def test_edi_processing_metrics():
    data = EdiProcessingMetrics.Config.schema_extra["example"]
    metrics = EdiProcessingMetrics(**data)
    assert metrics.totalTime == 2.78094223


def test_edi_message_metadata():
    data = EdiMessageMetadata.Config.schema_extra["example"]
    edi_message_metadata = EdiMessageMetadata(**data)
    assert edi_message_metadata


def test_edi_result():
    data = EdiResult.Config.schema_extra["example"]
    edi_result = EdiResult(**data)
    assert edi_result
