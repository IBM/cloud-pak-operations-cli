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

from dg.lib.fyre.types.quota_get_response import (
    ProductGroupQuota,
    QuotaGetResponse,
)


class ProductGroupQuotaData:
    def __init__(self, quota_get_response: QuotaGetResponse):
        self._product_group_quotas = quota_get_response

    def format(self, use_json: bool = False):
        if use_json:
            click.echo(json.dumps(self._product_group_quotas, indent="\t", sort_keys=True))
        else:
            details = self._product_group_quotas["details"]

            if len(self._product_group_quotas) != 0:
                iterator = iter(details)

                self._format_product_group_quota(next(iterator))

                for product_group in iterator:
                    click.echo()
                    self._format_product_group_quota(product_group)

    def _format_product_group_quota(self, product_group_quota: ProductGroupQuota):
        click.secho(
            f"Product group: {product_group_quota['product_group_name']} (ID: "
            f"{product_group_quota['product_group_id']}):",
            bold=True,
        )

        quota_list: List[List[str]] = []

        if "p" in product_group_quota:
            product_group_quota_p = product_group_quota["p"]
            quota_list_element_p: List[str] = [
                "p",
                product_group_quota_p["cpu"] if "cpu" in product_group_quota_p else "-",
                str(product_group_quota_p["cpu_percent"]) if "cpu" in product_group_quota_p else "-",
                product_group_quota_p["disk"] if "disk" in product_group_quota_p else "-",
                str(product_group_quota_p["disk_percent"]) if "disk" in product_group_quota_p else "-",
                product_group_quota_p["memory"] if "memory" in product_group_quota_p else "-",
                str(product_group_quota_p["memory_percent"]) if "memory" in product_group_quota_p else "-",
            ]

            quota_list.append(quota_list_element_p)
        else:
            quota_list.append(["p", "-", "-", "-", "-", "-", "-"])

        if "x" in product_group_quota:
            product_group_quota_x = product_group_quota["x"]
            quota_list_element_x: List[str] = [
                "x",
                product_group_quota_x["cpu"] if "cpu" in product_group_quota_x else "-",
                str(product_group_quota_x["cpu_percent"]) if "cpu" in product_group_quota_x else "-",
                product_group_quota_x["disk"] if "disk" in product_group_quota_x else "-",
                str(product_group_quota_x["disk_percent"]) if "disk" in product_group_quota_x else "-",
                product_group_quota_x["memory"] if "memory" in product_group_quota_x else "-",
                str(product_group_quota_x["memory_percent"]) if "memory" in product_group_quota_x else "-",
            ]

            quota_list.append(quota_list_element_x)
        else:
            quota_list.append(["x", "-", "-", "-", "-", "-", "-"])

        if "z" in product_group_quota:
            product_group_quota_z = product_group_quota["z"]
            quota_list_element_z: List[str] = [
                "z",
                product_group_quota_z["cpu"] if "cpu" in product_group_quota_z else "-",
                str(product_group_quota_z["cpu_percent"]) if "cpu" in product_group_quota_z else "-",
                product_group_quota_z["disk"] if "disk" in product_group_quota_z else "-",
                str(product_group_quota_z["disk_percent"]) if "disk" in product_group_quota_z else "-",
                product_group_quota_z["memory"] if "memory" in product_group_quota_z else "-",
                str(product_group_quota_z["memory_percent"]) if "memory" in product_group_quota_z else "-",
            ]

            quota_list.append(quota_list_element_z)
        else:
            quota_list.append(["z", "-", "-", "-", "-", "-", "-"])

        click.echo(
            tabulate(
                quota_list,
                headers=[
                    "Platform",
                    "CPU (total)",
                    "CPU (used) [%]",
                    "Disk (total)",
                    "Disk (used) [%]",
                    "Memory (total)",
                    "Memory (used) [%]",
                ],
            )
        )
