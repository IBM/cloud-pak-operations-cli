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
from cpo.lib.fyre.types.ocp_get_response import OCPGetResponse


class OCPGetResponseManager(AbstractJSONResponseManager):
    """JSON response manager for ocp REST endpoint (GET)"""

    # override
    def get_error_message(self, json_error_response: Any) -> str:
        return self.get_default_error_message(json_error_response)

    # override
    def get_error_response_schema(self) -> Optional[Any]:
        return self.get_default_error_response_schema()

    # override
    def get_response_schema(self) -> Any:
        return {
            "$defs": {
                "cluster": {
                    "additionalProperties": False,
                    "properties": {
                        "access_url": {"type": "string"},
                        "auto_patch": {"type": "string"},
                        "cluster_id": {"type": "string"},
                        "cluster_name": {"type": "string"},
                        "compliance": {"type": "string"},
                        "created": {"type": "string"},
                        "deployment_status": {"type": "string"},
                        "description": {"type": "string"},
                        "fips_enabled": {"type": "string"},
                        "kubeadmin_password": {"type": "string"},
                        "location_name": {"type": "string"},
                        "locked_for_delete": {"type": "string"},
                        "ocp_version": {"type": "string"},
                        "vm_count": {"type": "integer"},
                        "vms": {
                            "items": {"$ref": "#/$defs/vm"},
                            "type": "array",
                        },
                    },
                    "required": [
                        "access_url",
                        "auto_patch",
                        "cluster_id",
                        "cluster_name",
                        "compliance",
                        "created",
                        "deployment_status",
                        "description",
                        "fips_enabled",
                        "kubeadmin_password",
                        "location_name",
                        "locked_for_delete",
                        "ocp_version",
                        "vm_count",
                        "vms",
                    ],
                    "type": "object",
                },
                "ip": {
                    "additionalProperties": False,
                    "properties": {
                        "address": {"type": "string"},
                        "type": {"type": "string"},
                    },
                    "required": [
                        "address",
                        "type",
                    ],
                    "type": "object",
                },
                "vm": {
                    "additionalProperties": False,
                    "properties": {
                        "additional_disk": {
                            "items": {"type": "string"},
                            "type": "array",
                        },
                        "cpu": {"type": "string"},
                        "hostname": {"type": "string"},
                        "ips": {
                            "items": {"$ref": "#/$defs/ip"},
                            "type": "array",
                        },
                        "memory": {"type": "string"},
                        "os_disk": {"type": "string"},
                        "os_state": {"type": "string"},
                        "pingable_last_checked": {"type": ["string", "null"]},
                        "pingable": {"type": "string"},
                        "vm_id": {"type": "string"},
                    },
                    "required": [
                        "cpu",
                        "hostname",
                        "ips",
                        "memory",
                        "os_disk",
                        "os_state",
                        "pingable_last_checked",
                        "pingable",
                        "vm_id",
                    ],
                    "type": "object",
                },
            },
            "anyOf": [
                {
                    "additionalProperties": False,
                    "properties": {
                        "cluster_count": {"type": "integer"},
                        "clusters": {
                            "items": {"$ref": "#/$defs/cluster"},
                            "type": "array",
                        },
                    },
                    "required": [
                        "cluster_count",
                        "clusters",
                    ],
                    "type": "object",
                },
                {
                    "additionalProperties": False,
                    "properties": {
                        "details": {"type": "string"},
                        "status": {"const": "info"},
                    },
                    "required": [
                        "details",
                        "status",
                    ],
                    "type": "object",
                },
            ],
        }

    # override
    def get_response_type(self) -> Type:
        return OCPGetResponse
