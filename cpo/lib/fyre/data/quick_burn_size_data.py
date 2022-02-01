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

import itertools
import json

from typing import List

import click

from tabulate import tabulate

from cpo.lib.fyre.types.ocp_quick_burn_sizes_response import (
    NodeSizeSpecification,
    NodeSizeSpecificationData,
    OCPQuickBurnSizesResponse,
    PlatformQuickBurnSizeSpecificationData,
)


class QuickBurnSizeData:
    def __init__(self, ocp_quick_burn_sizes_response: OCPQuickBurnSizesResponse):
        self._ocp_quick_burn_sizes_response = ocp_quick_burn_sizes_response

    def format(self, use_json: bool = False):
        if use_json:
            click.echo(json.dumps(self._ocp_quick_burn_sizes_response, indent="\t", sort_keys=True))
        else:
            self._format_platform_quick_burn_size_specification_data("p")
            click.echo()
            self._format_platform_quick_burn_size_specification_data("x")
            click.echo()
            self._format_platform_quick_burn_size_specification_data("z")

    def _add_node_size_specification_data_list_element(
        self,
        node_size_specification_data_list: List[List[str]],
        quick_burn_size: str,
        node: str,
        node_size_specification: NodeSizeSpecification,
    ):
        additional_disks: List[str] = []
        num_additional_disks = int(node_size_specification["additional_disk"])

        if num_additional_disks != 0:
            additional_disk_size = node_size_specification["additional_disk_size"]

            for _ in itertools.repeat(None, num_additional_disks):
                additional_disks.append(additional_disk_size)

        node_size_specification_data_list.append(
            [
                quick_burn_size,
                node,
                node_size_specification["count"],
                node_size_specification["cpu"],
                node_size_specification["memory"],
                node_size_specification["disk_size"],
                ", ".join(additional_disks) if len(additional_disks) != 0 else "-",
            ]
        )

    def _format_platform_quick_burn_size_specification_data(self, platform: str):
        platform_quick_burn_size_specification_data: PlatformQuickBurnSizeSpecificationData = (
            self._ocp_quick_burn_sizes_response[platform]
        )

        click.secho(f"Platform: {platform}", bold=True)

        node_size_specification_data_list: List[List[str]] = []
        node_size_specification_data_list = (
            node_size_specification_data_list
            + self._format_node_size_specification_data(platform_quick_burn_size_specification_data, "medium")
        )

        node_size_specification_data_list = (
            node_size_specification_data_list
            + self._format_node_size_specification_data(platform_quick_burn_size_specification_data, "large")
        )

        click.echo(
            tabulate(
                node_size_specification_data_list,
                headers=[
                    "quick burn size",
                    "node",
                    "node count",
                    "CPUs",
                    "RAM (GiB)",
                    "OS disk (GiB)",
                    "additional disks (GiB)",
                ],
            )
        )

    def _format_node_size_specification_data(
        self, platform_quick_burn_size_specification_data: PlatformQuickBurnSizeSpecificationData, quick_burn_size: str
    ) -> List[List[str]]:
        node_size_specification_data: NodeSizeSpecificationData = platform_quick_burn_size_specification_data[
            quick_burn_size
        ]

        node_size_specification_data_list: List[List[str]] = []
        self._add_node_size_specification_data_list_element(
            node_size_specification_data_list,
            quick_burn_size,
            "infrastructure node",
            node_size_specification_data["inf"],
        )

        self._add_node_size_specification_data_list_element(
            node_size_specification_data_list,
            quick_burn_size,
            "master node",
            node_size_specification_data["master"],
        )

        self._add_node_size_specification_data_list_element(
            node_size_specification_data_list,
            quick_burn_size,
            "worker node",
            node_size_specification_data["worker"],
        )

        return node_size_specification_data_list
