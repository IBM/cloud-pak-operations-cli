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
from cpo.lib.fyre.types.ocp_quick_burn_sizes_response import (
    OCPQuickBurnSizesResponse,
)


class OCPQuickBurnSizesResponseManager(AbstractJSONResponseManager):
    """JSON response manager for ocp/quick_burn_sizes REST endpoint (GET)"""

    # override
    def get_error_message(self, json_error_response: Any) -> Optional[str]:
        return None

    # override
    def get_error_response_schema(self) -> Optional[Any]:
        return None

    # override
    def get_response_schema(self) -> Any:
        node_size_specification_ref = "#/$defs/nodeSizeSpecification"

        return {
            "$defs": {
                "nodeSizeSpecification": {
                    "additionalProperties": False,
                    "properties": {
                        "additional_disk": {
                            "type": "string",
                        },
                        "additional_disk_size": {
                            "type": "string",
                        },
                        "count": {
                            "type": "string",
                        },
                        "cpu": {
                            "type": "string",
                        },
                        "disk_size": {
                            "type": "string",
                        },
                        "memory": {
                            "type": "string",
                        },
                    },
                    "required": [
                        "additional_disk",
                        "count",
                        "cpu",
                        "disk_size",
                        "memory",
                    ],
                },
                "nodeSizeSpecificationData": {
                    "additionalProperties": False,
                    "properties": {
                        "inf": {
                            "$ref": node_size_specification_ref,
                        },
                        "master": {
                            "$ref": node_size_specification_ref,
                        },
                        "worker": {
                            "$ref": node_size_specification_ref,
                        },
                    },
                    "required": [
                        "inf",
                        "master",
                        "worker",
                    ],
                },
                "platformQuickBurnSizeSpecificationData": {
                    "additionalProperties": False,
                    "properties": {
                        "large": {
                            "$ref": "#/$defs/nodeSizeSpecificationData",
                        },
                        "medium": {
                            "$ref": "#/$defs/nodeSizeSpecificationData",
                        },
                    },
                    "required": [
                        "large",
                        "medium",
                    ],
                },
            },
            "additionalProperties": False,
            "properties": {
                "p": {
                    "$ref": "#/$defs/platformQuickBurnSizeSpecificationData",
                },
                "x": {
                    "$ref": "#/$defs/platformQuickBurnSizeSpecificationData",
                },
                "z": {
                    "$ref": "#/$defs/platformQuickBurnSizeSpecificationData",
                },
            },
            "required": ["p", "x", "z"],
            "type": "object",
        }

    # override
    def get_response_type(self) -> Type:
        return OCPQuickBurnSizesResponse
