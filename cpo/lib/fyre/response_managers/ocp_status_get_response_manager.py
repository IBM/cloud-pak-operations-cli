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
from cpo.lib.fyre.types.ocp_status_get_response import OCPStatusGetResponse


class OCPStatusGetResponseManager(AbstractJSONResponseManager):
    """JSON response manager for ocp/{cluster name}/status REST endpoint
    (GET)"""

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
                "vm": {
                    "additionalProperties": False,
                    "properties": {
                        "job_status": {
                            "anyOf": [
                                {
                                    "additionalProperties": False,
                                    "properties": {
                                        "completion_percent": {"type": "integer"},
                                        "status": {"type": "string"},
                                    },
                                    "required": [
                                        "completion_percent",
                                        "status",
                                    ],
                                    "type": "object",
                                },
                                {"type": "string"},
                            ]
                        },
                        "kvm_state": {"type": "string"},
                        "name": {"type": "string"},
                        "pingable_last_checked": {"type": ["string", "null"]},
                        "pingable": {"type": "string"},
                        "platform": {"type": "string"},
                        "sshable_last_checked": {"type": "string"},
                        "sshable": {"type": "string"},
                        "state_last_checked": {"type": "string"},
                        "state": {"type": "string"},
                        "vm_id": {"type": "string"},
                    },
                    "required": [
                        "kvm_state",
                        "name",
                        "pingable_last_checked",
                        "pingable",
                        "platform",
                        "state_last_checked",
                        "state",
                        "vm_id",
                    ],
                    "type": "object",
                },
                "request": {
                    "additionalProperties": False,
                    "properties": {
                        "complete": {"type": "string"},
                        "completion_percent": {"type": "integer"},
                        "failed": {"type": "string"},
                        "in_progress": {"type": "string"},
                        "job_count": {"type": "string"},
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
                        "pending",
                        "request_id",
                        "task_count",
                    ],
                    "type": "object",
                },
            },
            "additionalProperties": False,
            "properties": {
                "cluster_id": {"type": "string"},
                "cluster_name": {"type": "string"},
                "deployed_status": {"type": "string"},
                "expiration": {"type": "string"},
                "location_name": {"type": "string"},
                "product_group_id": {"type": "string"},
                "product_group": {"type": "string"},
                "status": {
                    "anyOf": [
                        {
                            "additionalProperties": False,
                            "properties": {
                                "active_requests": {"type": "integer"},
                                "request": {
                                    "anyOf": [
                                        {"$ref": "#/$defs/request"},
                                        {
                                            "items": {"$ref": "#/$defs/request"},
                                            "type": "array",
                                        },
                                    ]
                                },
                            },
                            "required": [
                                "active_requests",
                                "request",
                            ],
                            "type": "object",
                        },
                        {"type": "string"},
                    ]
                },
                "type": {"type": "string"},
                "vm_count": {"type": "integer"},
                "vm": {
                    "items": {"$ref": "#/$defs/vm"},
                    "type": "array",
                },
            },
            "required": [
                "cluster_id",
                "cluster_name",
                "deployed_status",
                "expiration",
                "location_name",
                "product_group_id",
                "product_group",
                "status",
                "type",
                "vm_count",
                "vm",
            ],
            "type": "object",
        }

    # override
    def get_response_type(self) -> Type:
        return OCPStatusGetResponse
