#  Copyright 2022 IBM Corporation
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


class CloudPakOperationsCLIException(Exception):
    def __init__(self, error_message: str, stderr: Optional[str] = None, stdout: Optional[str] = None):
        super().__init__(error_message)
        self._error_message = error_message[7:] if error_message.startswith("Error: ") else error_message
        self._stderr = stderr
        self._stdout = stdout

    def __str__(self):
        output = self._get_highlighted_str(self._error_message)

        if (self._stderr is not None) and (self._stderr != ""):
            if not output.endswith("\n"):
                output += "\n"

            output += f"Error output:\n{self._stderr.rstrip()}"

        if (self._stdout is not None) and (self._stdout != ""):
            if not output.endswith("\n"):
                output += "\n"

            output += f"Standard output:\n{self._stdout.rstrip()}"

        return output

    @property
    def error_message(self) -> str:
        return self._error_message

    @property
    def stderr(self) -> Optional[str]:
        return self._stderr

    @property
    def stdout(self) -> Optional[str]:
        return self._stdout

    def _get_highlighted_str(self, str: str) -> str:
        return f"{colorama.Style.BRIGHT}{str}{colorama.Style.RESET_ALL}"


class IBMCloudException(CloudPakOperationsCLIException):
    @classmethod
    def create_exception(cls, exception: CloudPakOperationsCLIException):
        return IBMCloudException(exception.error_message, exception.stderr, exception.stdout)

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


class JmespathPathExpressionNotFoundException(CloudPakOperationsCLIException):
    def __init__(self, expresion):
        super().__init__(f"Jmespath expression not found ({expresion})")


class UnexpectedTypeException(CloudPakOperationsCLIException):
    def __init__(self, value):
        super().__init__(f"Unexpected type ({type(value)})")
