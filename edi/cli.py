"""
cli.py

Implements a command line interface for the EDI service/application.
"""
import argparse

CLI_DESCRIPTION = """
Analyze, Enrich, Validate and Translate EDI Messages using the LinuxForHealth CLI!
The LinuxForHealth EDI CLI accepts an input EDI message and returns an EdiResult object (JSON).
The CLI's options are used to specify which EDI operations are included.
If no options are provided, the CLI will execute all available operations.
The "analyze" operation is a default operation and is included with each CLI invocation.
"""


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        prog="LinuxForHealth EDI",
        description=CLI_DESCRIPTION,
        epilog="All messages are analyzed by default",
    )
    arg_parser.add_argument(
        "-e",
        "--enrich",
        help="supplements the EDI message with additional data",
        action="store_const",
        const="enrich",
    )
    arg_parser.add_argument(
        "-v",
        "--validate",
        help="validates the EDI message",
        action="store_const",
        const="validate",
    )
    arg_parser.add_argument(
        "-t",
        "--translate",
        help="validates the EDI message",
        action="store_const",
        const="translate",
    )

    arg_parser.add_argument(
        "-p",
        "--pretty",
        help="pretty print the EDI Result",
        action="store_const",
        const="pretty",
    )

    arg_parser.add_argument("edi_file", help="the path to the EDI message")

    args = arg_parser.parse_args()
    print(args)
