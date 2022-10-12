#  Copyright 2021, 2022 IBM Corporation
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

from cpo.lib.fyre.response_managers.json_response_manager import AbstractJSONResponseManager
from cpo.lib.fyre.types.ocp_get_response_for_single_cluster import OCPGetResponseForSingleCluster


class OCPGetResponseManagerForSingleCluster(AbstractJSONResponseManager):
    """JSON response manager for ocp/{cluster name} REST endpoint (GET)"""

    def __init__(self, disable_strict_response_schema_check: bool):
        super().__init__(disable_strict_response_schema_check)

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
                "cluster": {
                    "additionalProperties": self._disable_strict_response_schema_check,
                    "properties": {
                        "access_url": {"type": "string"},
                        "auto_patch": {"type": "string"},
                        "cluster_count": {"type": "string"},
                        "cluster_id": {"type": "string"},
                        "cluster_name": {"type": "string"},
                        "cluster_type": {"type": "string"},
                        "compliance": {"type": "string"},
                        "created": {"type": "string"},
                        "deployment_status": {"type": "string"},
                        "description": {"type": "string"},
                        "expiration": {"type": "string"},
                        "fips_enabled": {"type": "string"},
                        "host_down": {"type": "string"},
                        "initial_ocp_version": {"type": "string"},
                        "kubeadmin_password": {"type": "string"},
                        "locked_for_delete": {"type": "string"},
                        "ocp_username": {"type": "string"},
                        "ocp_version": {"type": "string"},
                        "platform": {"type": "string"},
                        "product_group_id": {"type": "string"},
                        "user_id": {"type": "string"},
                        "vm_count": {"type": "integer"},
                        "vms": {
                            "items": {"$ref": "#/$defs/vm"},
                            "type": "array",
                        },
                    },
                    "required": [
                        "access_url",
                        "auto_patch",
                        "cluster_count",
                        "cluster_id",
                        "cluster_name",
                        "cluster_type",
                        "compliance",
                        "created",
                        "deployment_status",
                        "description",
                        "expiration",
                        "fips_enabled",
                        "host_down",
                        "locked_for_delete",
                        "ocp_username",
                        "ocp_version",
                        "platform",
                        "product_group_id",
                        "user_id",
                        "vm_count",
                        "vms",
                    ],
                    "type": "object",
                },
                "ip": {
                    "additionalProperties": self._disable_strict_response_schema_check,
                    "properties": {
                        "address": {"type": "string"},
                        "ip_scope": {"type": "string"},
                        "type": {"type": "string"},
                    },
                    "required": [
                        "address",
                        "ip_scope",
                        "type",
                    ],
                    "type": "object",
                },
                "vm": {
                    "additionalProperties": self._disable_strict_response_schema_check,
                    "properties": {
                        "additional_disk": {
                            "items": {"type": "string"},
                            "type": "array",
                        },
                        "cpu": {"type": "string"},
                        "host_down": {"type": "string"},
                        "hostname": {"type": "string"},
                        "in_progress": {"type": "string"},
                        "ip_address": {"type": "string"},
                        "ip_type": {"type": "string"},
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
                        "host_down",
                        "hostname",
                        "in_progress",
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
            "additionalProperties": self._disable_strict_response_schema_check,
            "properties": {
                "cluster_count": {"type": "integer"},
                "clusters": {
                    "items": {"$ref": "#/$defs/cluster"},
                    "maxItems": 1,
                    "minItems": 1,
                    "type": "array",
                },
                "location_name": {"type": "string"},
            },
            "required": [
                "cluster_count",
                "clusters",
                "location_name",
            ],
            "type": "object",
        }

    # override
    def get_response_type(self) -> Type:
        return OCPGetResponseForSingleCluster
