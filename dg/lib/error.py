import re

from typing import Union

import colorama


class DataGateCLIException(Exception):
    def __init__(self, error_message: str, error_details: Union[str, None] = None):
        super().__init__(error_message)
        self._error_details = error_details
        self._error_message = error_message

    def __str__(self):
        output = (
            f"{colorama.Style.BRIGHT}{self._error_message}{colorama.Style.RESET_ALL}"
        )

        if self._error_details is not None:
            output += f" – error details:\n{self._error_details}"

        return output


class IBMCloudException(DataGateCLIException):
    @classmethod
    def get_parsed_error_message(cls, error_message: str) -> str:
        search_result = re.search(
            "FAILED\\n(.*)\\n\\n(Incident ID: .*)\\n", error_message, re.DOTALL
        )

        if search_result is not None:
            output = f"{search_result.group(1)} [{search_result.group(2)}]"
        else:
            output = error_message

        return output

    def __init__(self, error_message, error_details: Union[str, None] = None):
        super().__init__(error_message, error_details)

    def __str__(self):
        output: Union[str, None] = None

        if self._error_details is None:
            output = self._get_highlighted_str(
                IBMCloudException.get_parsed_error_message(self._error_message)
            )
        else:
            output = (
                f"{self._get_highlighted_str(self._error_message)} – error details:\n"
                f"{IBMCloudException.get_parsed_error_message(self._error_details)}"
            )

        return output

    def _get_highlighted_str(self, str: str) -> str:
        return f"{colorama.Style.BRIGHT}{str}{colorama.Style.RESET_ALL}"
