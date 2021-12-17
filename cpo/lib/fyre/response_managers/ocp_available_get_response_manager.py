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
from cpo.lib.fyre.types.ocp_available_get_response import (
    OCPAvailableGetResponse,
)


class OCPAvailableGetResponseManager(AbstractJSONResponseManager):
    """JSON response manager for ocp_available/{platform} REST endpoint
    (GET)"""

    # override
    def get_error_message(self, json_error_response: Any) -> Optional[str]:
        return self.get_default_error_message(json_error_response)

    # override
    def get_error_response_schema(self) -> Optional[Any]:
        return self.get_default_error_response_schema()

    # override
    def get_response_schema(self) -> Any:
        node_size_ref = "#/$defs/nodeSize"

        return {
            "$defs": {
                "defaultClusterSizeData": {
                    "additionalProperties": False,
                    "properties": {
                        "inf": {"$ref": node_size_ref},
                        "master": {"$ref": node_size_ref},
                        "worker": {"$ref": node_size_ref},
                    },
                    "required": [
                        "inf",
                        "master",
                        "worker",
                    ],
                    "type": "object",
                },
                "nodeSize": {
                    "additionalProperties": False,
                    "properties": {
                        "additional_disk_size": {"type": "string"},
                        "additional_disk": {"type": "string"},
                        "base_disk_size": {"type": "string"},
                        "count": {"type": "string"},
                        "cpu": {"type": "string"},
                        "max_cpu": {"type": "string"},
                        "max_disk_size": {"type": "string"},
                        "max_disk": {"type": "string"},
                        "max_memory": {"type": "string"},
                        "memory": {"type": "string"},
                    },
                    "required": [
                        "base_disk_size",
                        "cpu",
                        "memory",
                    ],
                    "type": "object",
                },
            },
            "additionalProperties": False,
            "properties": {
                "default_size": {
                    "$ref": "#/$defs/defaultClusterSizeData",
                },
                "ocp_versions": {
                    "items": {
                        "type": "string",
                    },
                    "type": "array",
                },
            },
            "required": [
                "default_size",
                "ocp_versions",
            ],
            "type": "object",
        }

    # override
    def get_response_type(self) -> Type:
        return OCPAvailableGetResponse
