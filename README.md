# LinuxForHealth EDI

![GitHub License](https://img.shields.io/github/license/linuxforhealth/edi)
![Supported Versions](https://img.shields.io/badge/python%20version-3.8%2C%203.9-blue)
<br>
![Template CI](https://github.com/linuxforhealth/edi/actions/workflows/continuous-integration.yml/badge.svg)
![Image Build](https://github.com/linuxforhealth/edi/actions/workflows/image-build.yml/badge.svg)
<br>
![GitHub Issues](https://img.shields.io/github/issues/dixonwhitmire/fastapi-template)
![GitHub Forks](https://img.shields.io/github/forks/dixonwhitmire/fastapi-template)
![GitHub Stars](https://img.shields.io/github/stars/dixonwhitmire/fastapi-template)

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
* HL7v2
* FHIR R4

This project is currently under construction. Please refer to the [LinuxForHealth EDI Issue Board](https://github.com/LinuxForHealth/edi/issues) to review the current "to-dos" and "to-dones".

## Quickstart

TBD