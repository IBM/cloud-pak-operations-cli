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

from typing import List

import click

from tabulate import tabulate

from cpo.lib.fyre.types.ocp_status_get_response import VM, OCPStatusGetResponse


class OCPPlusClusterStatus:
    def __init__(self, ocp_status_get_response: OCPStatusGetResponse):
        self._ocp_status_get_response = ocp_status_get_response

    def format(self, use_json: bool = False):
        if use_json:
            click.echo(json.dumps(self._ocp_status_get_response, indent="\t", sort_keys=True))
        else:
            vm_list: List[List[str]] = []
            headers = [
                "VM ID",
                "hostname",
                "KVM state",
                "platform",
                "job status",
                "job completion",
                "pingable",
                "pingable last checked",
                "sshable",
                "sshable last checked",
            ]

            for vm in self._ocp_status_get_response["vm"]:
                pingable_last_checked = vm["pingable_last_checked"]

                vm_list.append(
                    [
                        vm["vm_id"],
                        vm["name"],
                        vm["kvm_state"],
                        vm["platform"],
                        self._get_job_status(vm),
                        self._get_job_completion_percent(vm),
                        "✓" if vm["pingable"] == "y" else "-",
                        pingable_last_checked if pingable_last_checked is not None else "-",
                        "✓" if ("sshable" in vm) and (vm["sshable"] == "y") else "-",
                        vm["sshable_last_checked"] if "sshable_last_checked" in vm else "-",
                    ]
                )

            click.echo(tabulate(vm_list, headers=headers))

    def _get_job_completion_percent(self, vm: VM) -> str:
        return str(vm["job_status"]["completion_percent"]) if "job_status" in vm else "-"

    def _get_job_status(self, vm: VM) -> str:
        return vm["job_status"]["status"] if "job_status" in vm else "-"
