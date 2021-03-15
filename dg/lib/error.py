import re as regex

from typing import Union

import colorama


class DataGateCLIException(Exception):
    def __init__(
        self,
        error_message: str,
        stderr: Union[str, None] = None,
        stdout: Union[str, None] = None,
    ):
        super().__init__(error_message)
        self._error_message = error_message
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


class IBMCloudException(DataGateCLIException):
    @classmethod
    def get_parsed_error_message(cls, error_message: str) -> str:
        search_result = regex.search("FAILED\\n(.*)\\n\\n(Incident ID: .*)\\n", error_message, regex.DOTALL)

        if search_result is not None:
            output = f"{search_result.group(1)} [{search_result.group(2)}]"
        else:
            output = error_message

        return output

    def __init__(
        self,
        error_message,
        stderr: Union[str, None] = None,
        stdout: Union[str, None] = None,
    ):
        super().__init__(error_message, stderr, stdout)

    def __str__(self):
        output: Union[str, None] = None

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
