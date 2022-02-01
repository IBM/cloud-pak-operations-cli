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

from typing import List

import click
import semver

from tabulate import tabulate


class OpenShiftVersionData:
    def __init__(
        self,
        openshift_versions_p: List[semver.VersionInfo],
        openshift_versions_x: List[semver.VersionInfo],
        openshift_versions_z: List[semver.VersionInfo],
    ):
        self._openshift_versions_p = openshift_versions_p
        self._openshift_versions_x = openshift_versions_x
        self._openshift_versions_z = openshift_versions_z

    def format(self):
        openshift_versions_union: List[semver.VersionInfo] = []
        openshift_versions_union += self._openshift_versions_p
        openshift_versions_union += self._openshift_versions_x
        openshift_versions_union += self._openshift_versions_z
        openshift_versions_union = list(dict.fromkeys(openshift_versions_union))
        openshift_versions_union.sort()

        openshift_versions_list: List[List[str]] = []
        openshift_versions_list.append(
            self._add_openshift_versions_list_element("p", openshift_versions_union, self._openshift_versions_p)
        )

        openshift_versions_list.append(
            self._add_openshift_versions_list_element("x", openshift_versions_union, self._openshift_versions_x)
        )
        openshift_versions_list.append(
            self._add_openshift_versions_list_element("z", openshift_versions_union, self._openshift_versions_z)
        )

        click.echo(
            tabulate(
                openshift_versions_list,
                headers=["Platform"]
                + list(
                    map(
                        lambda openshift_version: str(openshift_version),
                        openshift_versions_union,
                    )
                ),
            )
        )

    def get_openshift_versions_p(self) -> List[semver.VersionInfo]:
        return self._openshift_versions_p

    def get_openshift_versions_x(self) -> List[semver.VersionInfo]:
        return self._openshift_versions_x

    def get_openshift_versions_z(self) -> List[semver.VersionInfo]:
        return self._openshift_versions_z

    def _add_openshift_versions_list_element(
        self,
        platform: str,
        openshift_versions_union: List[semver.VersionInfo],
        openshift_versions: List[semver.VersionInfo],
    ):
        openshift_version_list: List[str] = [platform]

        for openshift_version in openshift_versions_union:
            openshift_version_list.append("✓" if openshift_version in openshift_versions else "-")

        return openshift_version_list
