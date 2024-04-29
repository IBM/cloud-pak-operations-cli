#  Copyright 2023, 2024 IBM Corporation
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

import io
import re as regex
import urllib.parse

import semver

import cpo.utils.download
import cpo.utils.operating_system

from cpo.lib.dependency_manager.plugins.openshift.openshift_plugin import AbstractOpenShiftPlugIn
from cpo.utils.error import CloudPakOperationsCLIException
from cpo.utils.operating_system import OperatingSystem


class OpenShiftInstallPlugIn(AbstractOpenShiftPlugIn):
    # override
    def get_binary_name(self) -> str | None:
        return "openshift-install"

    # override
    def get_dependency_alias(self) -> str:
        return "openshift-install"

    # override
    def get_dependency_name(self) -> str:
        return "openshift-install"

    def get_latest_minor_release_version(self, minor_release: str) -> semver.Version:
        """Returns the latest version of the OpenShift CLI

        Returns
        -------
        semver.Version
            latest version of the OpenShift CLI
        """

        search_result = regex.search("^4\\.((?!0)[0-9]+)$", minor_release)

        if search_result is None:
            raise CloudPakOperationsCLIException(f"Invalid OpenShift Container Platform version: {minor_release}")

        url = f"https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest-{minor_release}/release.txt"

        with io.BytesIO() as buffer:
            cpo.utils.download.download_file_into_buffer(urllib.parse.urlsplit(url), buffer, silent=True)

            latest_version = self._parse_version_from_versions_file(buffer.getvalue().decode("utf-8"))

            return latest_version

    # override
    def _get_operating_system_file_name_dict(self) -> dict[OperatingSystem, str]:
        return {
            OperatingSystem.LINUX_X86_64: "openshift-install-linux.tar.gz",
            OperatingSystem.MAC_OS: "openshift-install-mac.tar.gz",
        }
