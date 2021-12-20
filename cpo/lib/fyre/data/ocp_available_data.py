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
import semver

from tabulate import tabulate

from cpo.lib.fyre.types.ocp_available_get_response import (
    OCPAvailableGetResponse,
)


class OCPAvailableData:
    def __init__(self, ocp_available_get_response: OCPAvailableGetResponse):
        self._ocp_available_get_response = ocp_available_get_response

    def format_default_sizes(self, use_json: bool = False):
        if use_json:
            click.echo(json.dumps(self._ocp_available_get_response, indent="\t", sort_keys=True))
        else:
            keys_union: List[str] = []
            keys_union += self._ocp_available_get_response["default_size"]["inf"].keys()
            keys_union += self._ocp_available_get_response["default_size"]["master"].keys()
            keys_union += self._ocp_available_get_response["default_size"]["worker"].keys()
            keys_union = list(dict.fromkeys(keys_union))
            keys_union.sort()

            default_sizes_list: List[List[str]] = []

            for key in keys_union:
                default_size_list: List[str] = [key]

                default_size_list.append(
                    self._ocp_available_get_response["default_size"]["inf"][key]
                    if key in self._ocp_available_get_response["default_size"]["inf"]
                    else "-"
                )

                default_size_list.append(
                    self._ocp_available_get_response["default_size"]["master"][key]
                    if key in self._ocp_available_get_response["default_size"]["master"]
                    else "-"
                )

                default_size_list.append(
                    self._ocp_available_get_response["default_size"]["worker"][key]
                    if key in self._ocp_available_get_response["default_size"]["worker"]
                    else "-"
                )

                default_sizes_list.append(default_size_list)

            click.echo(tabulate(default_sizes_list, headers=["default size", "inf", "master", "worker"]))

    def format_openshift_versions(self, use_json: bool = False):
        if use_json:
            click.echo(json.dumps(self._ocp_available_get_response, indent="\t", sort_keys=True))
        else:
            ocp_versions = self.get_openshift_versions()

            click.echo(
                list(
                    map(
                        lambda ocp_version: str(ocp_version),
                        ocp_versions,
                    )
                )
            )

    def get_openshift_versions(self) -> List[semver.VersionInfo]:
        ocp_versions = list(
            map(
                lambda ocp_version: semver.VersionInfo.parse(ocp_version),
                self._ocp_available_get_response["ocp_versions"],
            )
        )

        ocp_versions.sort()

        return ocp_versions
