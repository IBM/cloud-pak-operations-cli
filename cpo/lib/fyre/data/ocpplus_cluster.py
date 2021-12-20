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

from typing import List, Optional

import click

from tabulate import tabulate

from cpo.lib.error import DataGateCLIException
from cpo.lib.fyre.types.ocp_get_response_for_single_cluster import (
    VM,
    OCPGetResponseForSingleCluster,
)


class OCPPlusCluster:
    def __init__(self, ocp_get_response_for_single_cluster: OCPGetResponseForSingleCluster):
        self._ocp_get_response_for_single_cluster = ocp_get_response_for_single_cluster

    def format(self, use_json: bool = False):
        if use_json:
            click.echo(json.dumps(self._ocp_get_response_for_single_cluster, indent="\t", sort_keys=True))
        else:
            cluster = self._ocp_get_response_for_single_cluster["clusters"][0]
            vm_list: List[List[str]] = []
            headers = [
                "VM ID",
                "hostname",
                "public IP address",
                "private IP address",
                "OS state",
                "CPUs",
                "RAM (GiB)",
                "OS disk (GiB)",
                "additional disks (GiB)",
            ]

            for vm in cluster["vms"]:
                private_ip_address = self._get_ip_address(vm, "private")
                public_ip_address = self._get_ip_address(vm, "public")

                vm_list.append(
                    [
                        vm["vm_id"],
                        vm["hostname"],
                        public_ip_address if public_ip_address is not None else "-",
                        private_ip_address if private_ip_address is not None else "-",
                        vm["os_state"],
                        vm["cpu"],
                        vm["memory"],
                        vm["os_disk"],
                        ", ".join(vm["additional_disk"]) if "additional_disk" in vm else "-",
                    ]
                )

            click.echo(tabulate(vm_list, headers=headers))

    def get_private_ip_address_of_infrastructure_node(self) -> str:
        """Returns the private IP address of the infrastructure node

        Returns
        -------
        str
            private IP address of the infrastructure node
        """

        cluster = self._ocp_get_response_for_single_cluster["clusters"][0]
        result: Optional[str] = None

        for vm in cluster["vms"]:
            private_ip_address = self._get_ip_address(vm, "private")
            public_ip_address = self._get_ip_address(vm, "public")

            if private_ip_address is not None and public_ip_address is not None:
                result = private_ip_address

                break

        if result is None:
            raise DataGateCLIException("Infrastructure node could not be identified")

        return result

    def _get_ip_address(self, vm: VM, type: str) -> Optional[str]:
        result: Optional[str] = None

        for ip_address in vm["ips"]:
            if ip_address["type"] == type:
                result = ip_address["address"]

                break

        return result
