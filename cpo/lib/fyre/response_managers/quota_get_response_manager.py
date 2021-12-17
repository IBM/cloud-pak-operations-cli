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
from cpo.lib.fyre.types.quota_get_response import QuotaGetResponse


class QuotaGetResponseManager(AbstractJSONResponseManager):
    """JSON response manager for quota REST endpoint (GET)"""

    # override
    def get_error_message(self, json_error_response: Any) -> Optional[str]:
        return self.get_default_error_message(json_error_response)

    # override
    def get_error_response_schema(self) -> Optional[Any]:
        return self.get_default_error_response_schema()

    # override
    def get_response_schema(self) -> Any:
        platform_quota_ref = "#/$defs/platformQuota"

        return {
            "$defs": {
                "platformQuota": {
                    "additionalProperties": False,
                    "properties": {
                        "cpu_percent": {"type": "integer"},
                        "cpu_used": {"type": "integer"},
                        "cpu": {"type": "string"},
                        "disk_percent": {"type": "integer"},
                        "disk_used": {"type": "integer"},
                        "disk": {"type": "string"},
                        "memory_percent": {"type": "integer"},
                        "memory_used": {"type": "integer"},
                        "memory": {"type": "string"},
                    },
                    "required": [
                        "cpu_percent",
                        "disk_percent",
                        "memory_percent",
                    ],
                    "type": "object",
                },
                "productGroupQuota": {
                    "additionalProperties": False,
                    "properties": {
                        "ip": {
                            "properties": {
                                "floating": {
                                    "properties": {
                                        "quota": {"type": "string"},
                                        "used": {"type": "string"},
                                    },
                                    "required": [
                                        "quota",
                                        "used",
                                    ],
                                    "type": "object",
                                }
                            },
                            "required": [
                                "floating",
                            ],
                            "type": "object",
                        },
                        "p": {
                            "$ref": platform_quota_ref,
                        },
                        "product_group_id": {"type": "string"},
                        "product_group_name": {"type": "string"},
                        "x": {
                            "$ref": platform_quota_ref,
                        },
                        "z": {
                            "$ref": platform_quota_ref,
                        },
                    },
                    "required": [
                        "product_group_id",
                        "product_group_name",
                    ],
                    "type": "object",
                },
            },
            "additionalProperties": False,
            "properties": {
                "details": {
                    "items": {"$ref": "#/$defs/productGroupQuota"},
                    "type": "array",
                },
                "status": {"type": "string"},
            },
            "required": [
                "details",
                "status",
            ],
            "type": "object",
        }

    # override
    def get_response_type(self) -> Type:
        return QuotaGetResponse
