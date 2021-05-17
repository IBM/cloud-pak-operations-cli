#  Copyright 2020 IBM Corporation
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

from dg.lib.fyre.types.ocp_get_response_for_single_cluster import (
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
                vm_list.append(
                    [
                        vm["vm_id"],
                        vm["hostname"],
                        self._get_ip_address(vm, "public"),
                        self._get_ip_address(vm, "private"),
                        vm["os_state"],
                        vm["cpu"],
                        vm["memory"],
                        vm["os_disk"],
                        ", ".join(vm["additional_disk"]) if "additional_disk" in vm else "-",
                    ]
                )

            click.echo(tabulate(vm_list, headers=headers))

    def _get_ip_address(self, vm: VM, type: str) -> str:
        result: Optional[str] = None

        for ip_address in vm["ips"]:
            if ip_address["type"] == type:
                result = ip_address["address"]

                break

        if result is None:
            result = "-"

        return result
