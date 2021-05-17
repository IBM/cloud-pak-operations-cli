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

from typing import List

import click

from tabulate import tabulate

from dg.lib.fyre.types.ocp_quick_burn_sizes_response import (
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
                headers=["quick burn size", "node", "node count", "CPU", "memory"],
            )
        )

    def _format_node_size_specification_data(
        self, platform_quick_burn_size_specification_data: PlatformQuickBurnSizeSpecificationData, size: str
    ) -> List[List[str]]:
        node_size_specification_data: NodeSizeSpecificationData = platform_quick_burn_size_specification_data[size]

        node_size_specification_data_list: List[List[str]] = []
        node_size_specification_data_list.append(
            [
                size,
                "infrastructure node",
                node_size_specification_data["inf"]["count"],
                node_size_specification_data["inf"]["cpu"],
                node_size_specification_data["inf"]["memory"],
            ]
        )

        node_size_specification_data_list.append(
            [
                size,
                "master node",
                node_size_specification_data["master"]["count"],
                node_size_specification_data["master"]["cpu"],
                node_size_specification_data["master"]["memory"],
            ]
        )

        node_size_specification_data_list.append(
            [
                size,
                "worker node",
                node_size_specification_data["worker"]["count"],
                node_size_specification_data["worker"]["cpu"],
                node_size_specification_data["worker"]["memory"],
            ]
        )

        return node_size_specification_data_list
