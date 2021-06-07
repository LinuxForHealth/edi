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

LinuxForHealth EDI provides a common processing model for standard health care messaging formats. Supported formats include: 
* ASC X12 5010
* HL7v2
* FHIR R4

The common processing model is implemented using [xWorkflows](https://xworkflows.readthedocs.io/en/latest/). The xWorkflows API supports workflow declaration, introspection, and event handling during state transitions. A workflow definition includes states and transitions, which are used to direct the workflow to a new state. LinuxForHealth defines a single workflow, EDIWorkflow, for message processing.

The LinuxForHealth EDI workflow processor, EdiProcessor, includes the following transitions:

| Transition Name | Description                                                                                                           | Required |
| --------------- | --------------------------------------------------------------------------------------------------------------------- | -------- |
| Analyze         | Generates an EdiMessageMetadata object for the EDI Message.                                                           | Yes      |
| Enrich          | Enriches the input message with additional data using custom transformations.                                         | No       |
| Validate        | Validates the input message.                                                                                          | No       |
| Translate       | Translates the input message in a supported format to a different supported format. Example: translate HL7v2 to FHIR. | No       |
| Cancel          | Cancels the current workflow process.                                                                                 | No       |
| Fail            | Reached when the workflow encounters an unrecoverable error and fails.                                                | No       |

LinuxForHealth EDI supports several integration modes:
* REST API
* CLI
* Direct invocation as an external library

## Quickstart

TBD