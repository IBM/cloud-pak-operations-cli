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

from typing import Any, List, Optional, Type

from jsonschema import validate

from cpo.lib.fyre.response_managers.json_response_manager import (
    AbstractJSONResponseManager,
)
from cpo.lib.fyre.types.ocp_post_response import (
    OCPPostErrorResponse,
    OCPPostResponse,
)


class OCPPostResponseManager(AbstractJSONResponseManager):
    """JSON response manager for ocp REST endpoint (GET)"""

    # override
    def get_error_message(self, json_error_response: Any) -> Optional[str]:
        validate(json_error_response, self.get_error_response_schema())

        error_messages: List[str] = []
        error_response: OCPPostErrorResponse = json_error_response
        details = error_response["details"]

        if isinstance(details, str):
            if "build_errors" in error_response:
                build_errors = "', '".join(error_response["build_errors"])

                error_messages.append(f"'{details}' ('{build_errors}')")
            else:
                error_messages.append(f"'{details}'")
        else:
            for error in details["errors"]:
                if isinstance(error, str):
                    error_messages.append(f"'{error}'")
                else:
                    internal_error = error["error"]

                    error_messages.append(f"'{internal_error}'")

        return ", ".join(error_messages)

    # override
    def get_error_response_schema(self) -> Optional[Any]:
        return {
            "additionalProperties": False,
            "properties": {
                "build_errors": {
                    "items": {
                        "type": "string",
                    },
                    "type": "array",
                },
                "details": {
                    "anyOf": [
                        {
                            "properties": {
                                "errors": {
                                    "items": {
                                        "anyOf": [
                                            {
                                                "properties": {
                                                    "error": {
                                                        "type": "string",
                                                    },
                                                    "issued": {
                                                        "type": "string",
                                                    },
                                                },
                                                "required": [
                                                    "error",
                                                    "issued",
                                                ],
                                                "type": "object",
                                            },
                                            {
                                                "type": "string",
                                            },
                                        ]
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
                "status": {"type": "string"},
            },
            "required": ["details", "status"],
            "type": "object",
        }

    # override
    def get_response_schema(self) -> Any:
        return {
            "properties": {
                "cluster_name": {"type": "string"},
                "details": {"type": "string"},
                "request_id": {"type": "string"},
                "status": {"type": "string"},
            },
            "required": [
                "cluster_name",
                "details",
                "request_id",
                "status",
            ],
            "type": "object",
        }

    # override
    def get_response_type(self) -> Type:
        return OCPPostResponse
