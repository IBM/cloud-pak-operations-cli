#  Copyright 2021 IBM Corporation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import re as regex

from typing import Optional

import colorama


class DataGateCLIException(Exception):
    def __init__(self, error_message: str, stderr: Optional[str] = None, stdout: Optional[str] = None):
        super().__init__(error_message)
        self._error_message = error_message[7:] if error_message.startswith("Error: ") else error_message
        self._stderr = stderr
        self._stdout = stdout

    def __str__(self):
        output = f"{colorama.Style.BRIGHT}{self._error_message}{colorama.Style.RESET_ALL}"

        if self._stderr is not None:
            output += f" – error details:\n{self._stderr}"

        if self._stdout is not None:
            if not output.endswith("\n"):
                output += "\n"

            output += f"Standard output:\n{self._stdout}"

        return output

    def get_error_message(self):
        return self._error_message

    @property
    def stderr(self) -> Optional[str]:
        return self._stderr

    @property
    def stdout(self) -> Optional[str]:
        return self._stdout


class IBMCloudException(DataGateCLIException):
    @classmethod
    def get_parsed_error_message(cls, error_message: str) -> str:
        # use regex.DOTALL to match newline characters
        search_result = regex.search("FAILED\\n(.*)\\n\\n(Incident ID: .*)\\n", error_message, regex.DOTALL)

        if search_result is not None:
            output = f"{search_result.group(1)} [{search_result.group(2)}]"
        else:
            output = error_message

        return output

    @classmethod
    def get_parsed_error_message_without_incident_id(cls, error_message: str) -> str:
        # use regex.DOTALL to match newline characters
        search_result = regex.search("FAILED\\n(.*)\\n\\n(Incident ID: .*)\\n", error_message, regex.DOTALL)

        if search_result is not None:
            output = search_result.group(1)
        else:
            output = error_message

        return output

    def __init__(self, error_message, stderr: Optional[str] = None, stdout: Optional[str] = None):
        super().__init__(error_message, stderr, stdout)

    def __str__(self):
        output: Optional[str] = None

        if self._stderr is None:
            output = self._get_highlighted_str(IBMCloudException.get_parsed_error_message(self._error_message))
        else:
            output = (
                f"{self._get_highlighted_str(self._error_message)} – error details:\n"
                f"{IBMCloudException.get_parsed_error_message(self._stderr)}"
            )

        if self._stdout is not None:
            if not output.endswith("\n"):
                output += "\n"

            output += f"Standard output:\n{self._stdout}"

        return output

    def _get_highlighted_str(self, str: str) -> str:
        return f"{colorama.Style.BRIGHT}{str}{colorama.Style.RESET_ALL}"


class JmespathPathExpressionNotFoundException(DataGateCLIException):
    def __init__(self, expresion):
        super().__init__(f"Jmespath expression not found ({expresion})")


class UnexpectedTypeException(DataGateCLIException):
    def __init__(self, value):
        super().__init__(f"Unexpected type ({type(value)})")
