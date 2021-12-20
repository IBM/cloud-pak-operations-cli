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

from typing import Any, Optional, Type

from cpo.lib.fyre.response_managers.json_response_manager import (
    AbstractJSONResponseManager,
)
from cpo.lib.fyre.types.ocp_request_get_response import OCPRequestGetResponse


class OCPRequestGetResponseManager(AbstractJSONResponseManager):
    """JSON response manager for ocp/request/{request_id} REST endpoint (GET)"""

    # override
    def get_error_message(self, json_error_response: Any) -> Optional[str]:
        return self.get_default_error_message(json_error_response)

    # override
    def get_error_response_schema(self) -> Optional[Any]:
        return self.get_default_error_response_schema()

    # override
    def get_response_schema(self) -> Any:
        return {
            "$defs": {
                "request": {
                    "additionalProperties": False,
                    "properties": {
                        "complete": {"type": "string"},
                        "completion_percent": {"type": "integer"},
                        "failed": {"type": "string"},
                        "in_progress": {"type": "string"},
                        "job_count": {"type": "string"},
                        "last_status_time": {"type": "string"},
                        "last_status": {"type": "string"},
                        "pending": {"type": "string"},
                        "request_id": {"type": "string"},
                        "task_count": {"type": "string"},
                    },
                    "required": [
                        "complete",
                        "completion_percent",
                        "failed",
                        "in_progress",
                        "job_count",
                        "last_status_time",
                        "last_status",
                        "pending",
                        "request_id",
                        "task_count",
                    ],
                    "type": "object",
                },
            },
            "additionalProperties": False,
            "properties": {
                "request": {"$ref": "#/$defs/request"},
                "status": {"type": "string"},
            },
            "required": [
                "request",
                "status",
            ],
            "type": "object",
        }

    # override
    def get_response_type(self) -> Type:
        return OCPRequestGetResponse
