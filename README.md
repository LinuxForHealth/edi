# LinuxForHealth EDI

![GitHub License](https://img.shields.io/github/license/linuxforhealth/edi)
![Supported Versions](https://img.shields.io/badge/python%20version-3.8%2C%203.9-blue)
<br>
![Template CI](https://github.com/linuxforhealth/edi/actions/workflows/continuous-integration.yml/badge.svg)
<br>
![GitHub Issues](https://img.shields.io/github/issues/linuxforhealth/edi)
![GitHub Forks](https://img.shields.io/github/forks/linuxforhealth/edi)
![GitHub Stars](https://img.shields.io/github/stars/linuxforhealth/edi)

## Overview

LinuxForHealth EDI provides a standard workflow for processing health care data regardless of format. 

![LinuxForHealth EDI Overview](lfh-edi-overview.png)

LinuxForHealth EDI supports multiple integration modes. Integration options include REST endpoints, CLI (command line), or direct access using the Python SDK. The EdiWorkflow delegates message operations to external libraries.

EdiWorkflow Transitions Include:

| Transition Name | Description                                                                                                           | Required |
| --------------- | --------------------------------------------------------------------------------------------------------------------- | -------- |
| Analyze         | Generates an EdiMessageMetadata object for the EDI Message                                                            | Yes      |
| Enrich          | Enriches the input message with additional data using custom transformations.                                         | No       |
| Validate        | Validates the input message.                                                                                          | No       |
| Translate       | Translates the input message in a supported format to a different supported format. Example: translate HL7v2 to FHIR. | No       |
| Cancel          | Cancels the current workflow process.                                                                                 | No       |
| Fail            | Reached when the workflow encounters an unrecoverable error and fails.                                                | No       |


Supported formats include: 
* ASC X12 5010
* C-CDA
* DICOM  
* HL7v2
* FHIR-R4

This project is currently under construction. Please refer to the [LinuxForHealth EDI Issue Board](https://github.com/LinuxForHealth/edi/issues) to review the current "to-dos" and "to-dones".

## Quickstart

### Pre-requisites
The LinuxForHealth EDI development environment relies on the following software packages:

- [git](https://git-scm.com) for project version control
- [Python 3.8 or higher](https://www.python.org/downloads/) for runtime/coding support
- [Pipenv](https://pipenv.pypa.io) for Python dependency management  

### Project Setup and Validation
```shell
pip install --upgrade pip setuptools

git clone https://github.com/LinuxForHealth/edi
cd edi

python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip setuptools 
pip install -e .[dev]
pytest
```

### CLI
```shell
# run within project root directory
pipenv run cli -p demo-files/270.x12
```
EdiResult Output:
```json
{
    "errors": [],
    "inputMessage": "ISA*00*          *00*          *ZZ*890069730      *ZZ*154663145      *200929*1705*|*00501*000000001*0*T*:~GS*HS*890069730*154663145*20200929*1705*0001*X*005010X279A1~ST*270*0001*005010X279A1~BHT*0022*13*10001234*20200929*1319~HL*1**20*1~NM1*PR*2*UNIFIED INSURANCE CO*****PI*842610001~HL*2*1*21*1~NM1*1P*2*DOWNTOWN MEDICAL CENTER*****XX*2868383243~HL*3*2*22*0~TRN*1*1*1453915417~NM1*IL*1*DOE*JOHN****MI*11122333301~DMG*D8*19800519~DTP*291*D8*20200101~EQ*30~SE*13*0001~GE*1*0001~IEA*1*000010216~\n",
    "metadata": {
        "baseMessageType": "TEXT",
        "checksum": "578b8f172f2039cfcc1ec4b37eb8a3976e50577fb085823abbfead071e68d1d8",
        "implementationVersions": null,
        "messageSize": 494,
        "messageType": "X12",
        "recordCount": 17,
        "specificationVersion": "005010X279A1"
    },
    "metrics": {
        "analyzeTime": 0.05738999999996963,
        "enrichTime": 0.0,
        "totalTime": 0.05738999999996963,
        "translateTime": 0.0,
        "validateTime": 0.0
    },
    "operations": [
        "ANALYZE",
        "COMPLETE"
    ]
}
```

### REST API
Under Development

### SDK
```shell
# run within project root directory
pipenv run python3
```

Open a Python interpreter

```python
import pprint
from src.edi.workflows import EdiWorkflow

with open("./samples/270.x12") as f:
    edi_message = ",".join(f.readlines())
    edi = EdiWorkflow(edi_message)
    edi.analyze()
    edi_result = edi.complete()
    pprint.pprint(edi_result.dict())
```

EdiResult
```json
{
    "errors": [],
    "inputMessage": "ISA*00*          *00*          *ZZ*890069730      *ZZ*154663145      *200929*1705*|*00501*000000001*0*T*:~GS*HS*890069730*154663145*20200929*1705*0001*X*005010X279A1~ST*270*0001*005010X279A1~BHT*0022*13*10001234*20200929*1319~HL*1**20*1~NM1*PR*2*UNIFIED INSURANCE CO*****PI*842610001~HL*2*1*21*1~NM1*1P*2*DOWNTOWN MEDICAL CENTER*****XX*2868383243~HL*3*2*22*0~TRN*1*1*1453915417~NM1*IL*1*DOE*JOHN****MI*11122333301~DMG*D8*19800519~DTP*291*D8*20200101~EQ*30~SE*13*0001~GE*1*0001~IEA*1*000010216~\n",
    "metadata": {
        "baseMessageType": "TEXT",
        "checksum": "578b8f172f2039cfcc1ec4b37eb8a3976e50577fb085823abbfead071e68d1d8",
        "implementationVersions": null,
        "messageSize": 494,
        "messageType": "X12",
        "recordCount": 17,
        "specificationVersion": "005010X279A1"
    },
    "metrics": {
        "analyzeTime": 0.1178989999999942,
        "enrichTime": 0.0,
        "totalTime": 0.1178989999999942,
        "translateTime": 0.0,
        "validateTime": 0.0
    },
    "operations": [
        "ANALYZE",
        "COMPLETE"
    ]
}
```
