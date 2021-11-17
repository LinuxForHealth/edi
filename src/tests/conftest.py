"""
conftest.py

Global PyTest fixtures
"""
import pytest
import json
import datetime
import os
from . import resources_directory


@pytest.fixture
def hl7_message():
    file_path = os.path.join(resources_directory, "adt_a01_26.hl7")
    with open(file_path) as f:
        return "\r".join(f.readlines())


@pytest.fixture
def x12_message():
    file_path = os.path.join(resources_directory, "270.x12")
    with open(file_path) as f:
        return "".join(f.readlines())


@pytest.fixture
def fhir_json_message():
    file_path = os.path.join(resources_directory, "fhir-us-core-patient.json")
    with open(file_path) as f:
        return "".join(f.readlines())


@pytest.fixture
def fhir_xml_message():
    file_path = os.path.join(resources_directory, "fhir-us-core-patient.xml")
    with open(file_path) as f:
        return "".join(f.readlines())
