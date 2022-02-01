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

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Type

import jsonschema

from jsonschema import validate

from cpo.lib.error import DataGateCLIException
from cpo.lib.fyre.types.default_error_response import DefaulErrorResponse


class AbstractJSONResponseManager(ABC):
    """Base class of all JSON response manager classes"""

    def check_response(self, json_response: Any, error_message: str):
        """Checks the given JSON response

        This method ensures that the given JSON response is not an error
        response and its schema is as expected.

        Parameters
        ----------
        json_response
            JSON response to be checked
        error_message
            error message to be used when raising an exception if the given JSON
            response is an error response
        """

        self.raise_error_if_error_response(json_response, error_message)

        jsonschema.Draft7Validator(self.get_response_schema()).validate(json_response)

    def get_default_error_message(self, json_error_response: Any) -> str:
        """Returns the error messages extracted from the given JSON error
        response based on the default error message type

        Parameters
        ----------
        json_error_response
            JSON error response

        Returns
        -------
        str
            error messages extracted from the given JSON error response
            based on the default error message type
        """

        validate(json_error_response, self.get_default_error_response_schema())

        error_messages: List[str] = []
        error_response: DefaulErrorResponse = json_error_response
        details = error_response["details"]

        if isinstance(details, str):
            error_messages.append(f"'{details}'")
        else:
            for error in details["errors"]:
                error_messages.append(f"'{error}'")

        return ", ".join(error_messages)

    def get_default_error_response_schema(self) -> Any:
        """Returns the default error response schema

        Returns
        -------
        Any
            default error response schema
        """

        return {
            "additionalProperties": False,
            "properties": {
                "details": {
                    "anyOf": [
                        {
                            "additionalProperties": False,
                            "properties": {
                                "errors": {
                                    "items": {
                                        "type": "string",
                                    },
                                    "type": "array",
                                }
                            },
                            "required": ["errors"],
                            "type": "object",
                        },
                        {
                            "type": "string",
                        },
                    ]
                },
                "status": {"const": "error"},
            },
            "required": ["details", "status"],
            "type": "object",
        }

    def get_default_success_response_schema(self) -> Any:
        """Returns the default success response schema

        Returns
        -------
        Any
            default success response schema
        """

        return {
            "properties": {
                "details": {"type": "string"},
                "request_id": {"type": "string"},
                "status": {"type": "string"},
            },
            "required": [
                "details",
                "request_id",
                "status",
            ],
            "type": "object",
        }

    @abstractmethod
    def get_error_message(self, json_error_response: Any) -> Optional[str]:
        """Returns the error message extracted from the given JSON error
        response

        Parameters
        ----------
        json_error_response
            JSON error response

        Returns
        -------
        str
            error message extracted from the given JSON error response
        """

        pass

    @abstractmethod
    def get_error_response_schema(self) -> Optional[Any]:
        """Returns the error response schema

        Returns
        -------
        Optional[Any]
            error response schema
        """

        pass

    @abstractmethod
    def get_response_schema(self) -> Any:
        """Returns the response schema

        Returns
        -------
        Any
            response schema
        """

        pass

    @abstractmethod
    def get_response_type(self) -> Type:
        """Returns the response type

        Returns
        -------
        Type
            response type
        """

        pass

    def raise_error_if_error_response(self, json_response: Any, error_message: str):
        """Raises an error if the given JSON response is an error response

        Parameters
        ----------
        json_response
            JSON response to be checked
        error_message
            error message to be used when raising an exception if the given JSON
            response is an error response
        """

        error_response_schema = self.get_error_response_schema()

        if error_response_schema is not None and jsonschema.Draft7Validator(error_response_schema).is_valid(
            json_response
        ):
            raise DataGateCLIException(f"{error_message} [{self.get_error_message(json_response)}]")
