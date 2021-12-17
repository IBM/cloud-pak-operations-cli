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

import json
import logging

from typing import Any, Optional

from cpo.lib.error import DataGateCLIException
from cpo.lib.ibmcloud import execute_ibmcloud_command
from cpo.utils.process import ProcessResult

logger = logging.getLogger(__name__)


class VLANManager:
    """Determines available public and private VLANs for a zone in IBM
    Cloud"""

    def __init__(self, zone: str):
        ibmcloud_oc_vlan_ls_command_args = ["oc", "vlan", "ls", "--json", "--zone", zone]
        ibmcloud_oc_vlan_ls_command_result = execute_ibmcloud_command(
            ibmcloud_oc_vlan_ls_command_args, capture_output=True
        )

        ibmcloud_oc_vlan_ls_command_result_json = json.loads(ibmcloud_oc_vlan_ls_command_result.stdout)
        self._default_private_vlan = self._get_default_vlan_id(
            ibmcloud_oc_vlan_ls_command_result,
            ibmcloud_oc_vlan_ls_command_result_json,
            "private",
            zone,
        )

        self._default_public_vlan = self._get_default_vlan_id(
            ibmcloud_oc_vlan_ls_command_result,
            ibmcloud_oc_vlan_ls_command_result_json,
            "public",
            zone,
        )

    @property
    def default_private_vlan(self) -> str:
        return self._default_private_vlan

    @property
    def default_public_vlan(self) -> str:
        return self._default_public_vlan

    def _get_default_vlan_id(
        self,
        ibmcloud_oc_vlan_ls_command_result: ProcessResult,
        ibmcloud_oc_vlan_ls_command_result_json: Any,
        vlan_type: str,
        zone: str,
    ) -> str:
        vlan_id: Optional[str] = None

        for vlan in ibmcloud_oc_vlan_ls_command_result_json:
            if vlan["type"] == vlan_type and vlan["properties"]["vlan_type"] == "standard":
                vlan_id = vlan["id"]

                break

        if vlan_id is None:
            self._raise_error(ibmcloud_oc_vlan_ls_command_result, vlan_type, zone)

        return vlan_id

    def _raise_error(
        self,
        ibmcloud_oc_vlan_ls_command_result: ProcessResult,
        vlan_type: str,
        zone: str,
    ):
        logging.info("Returned VLAN information:\n" + ibmcloud_oc_vlan_ls_command_result.stdout)

        raise DataGateCLIException(f"Could not obtain default {vlan_type} VLAN ID for zone {zone}")
