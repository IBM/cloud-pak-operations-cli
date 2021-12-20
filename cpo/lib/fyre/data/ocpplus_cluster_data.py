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
from cpo.lib.fyre.types.ocp_get_response import VM, Cluster, OCPGetResponse


class OCPPlusClusterData:
    def __init__(self, ocp_get_response: OCPGetResponse):
        self._ocp_get_response = ocp_get_response

    def format(self, use_json: bool = False):
        if use_json:
            click.echo(json.dumps(self._ocp_get_response, indent="\t", sort_keys=True))
        else:
            if "clusters" in self._ocp_get_response:
                clusters = self._ocp_get_response["clusters"]
                clusters.sort(key=lambda cluster: cluster["cluster_name"])

                cluster_list: List[List[str]] = []
                headers = [
                    "cluster name",
                    "cluster ID",
                    "description",
                    "creation date",
                    "deployment status",
                    "location name",
                    "OCP version",
                    "VM count",
                    "FIPS-enabled",
                    "🔒",
                ]

                for cluster in clusters:
                    cluster_list.append(
                        [
                            cluster["cluster_name"],
                            cluster["cluster_id"],
                            cluster["description"],
                            cluster["created"],
                            cluster["deployment_status"].upper(),
                            cluster["location_name"].upper(),
                            cluster["ocp_version"],
                            str(cluster["vm_count"]),
                            "✓" if cluster["fips_enabled"] == "y" else "-",
                            "✓" if cluster["locked_for_delete"] == "y" else "-",
                        ]
                    )

                click.echo(tabulate(cluster_list, headers=headers))

    def format_details(self, cluster_name: str):
        cluster = self.get_cluster(cluster_name)
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
            "pingable",
            "pingable last checked",
        ]

        for vm in cluster["vms"]:
            pingable_last_checked = vm["pingable_last_checked"]

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
                    "✓" if vm["pingable"] == "y" else "-",
                    pingable_last_checked if pingable_last_checked is not None else "-",
                ]
            )

        click.echo(tabulate(vm_list, headers=headers))

    def get_cluster(self, cluster_name: str) -> Cluster:
        result: Optional[Cluster] = None

        for cluster in self._ocp_get_response["clusters"]:
            if cluster["cluster_name"] == cluster_name:
                result = cluster

                break

        if result is None:
            raise DataGateCLIException(f"Cluster not found ({cluster_name})")

        return result

    def _get_ip_address(self, vm: VM, type: str) -> str:
        result: Optional[str] = None

        for ip_address in vm["ips"]:
            if ip_address["type"] == type:
                result = ip_address["address"]

                break

        if result is None:
            result = "-"

        return result
