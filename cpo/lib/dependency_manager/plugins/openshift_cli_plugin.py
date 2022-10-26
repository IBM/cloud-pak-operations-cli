#  Copyright 2021, 2022 IBM Corporation
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
import os
import pathlib
import re as regex
import urllib.parse

from typing import Optional

import semver

import cpo.config
import cpo.utils.compression
import cpo.utils.download
import cpo.utils.file
import cpo.utils.operating_system

from cpo.lib.dependency_manager.dependency_manager_plugin import AbstractDependencyManagerPlugIn
from cpo.utils.error import CloudPakOperationsCLIException
from cpo.utils.operating_system import OperatingSystem


class OpenShiftCLIPlugIn(AbstractDependencyManagerPlugIn):
    # override
    def download_dependency_version(self, version: semver.VersionInfo):
        operating_system = cpo.utils.operating_system.get_operating_system()
        operating_system_file_name_pattern_dict = {
            OperatingSystem.LINUX_X86_64: "openshift-client-linux.tar.gz",
            OperatingSystem.MAC_OS: "openshift-client-mac.tar.gz",
            OperatingSystem.WINDOWS: "openshift-client-windows.zip",
        }

        file_name = operating_system_file_name_pattern_dict[operating_system]
        url = f"https://mirror.openshift.com/pub/openshift-v4/clients/ocp/{str(version)}/{file_name}"
        archive_path = cpo.utils.download.download_file(urllib.parse.urlsplit(url))

        self._extract_archive(archive_path)

    # override
    def get_binary_name(self) -> Optional[str]:
        return "oc"

    # override
    def get_dependency_alias(self) -> str:
        return "oc"

    # override
    def get_dependency_name(self) -> str:
        return "OpenShift CLI"

    # override
    def get_latest_dependency_version(self) -> semver.VersionInfo:
        """Returns the latest version of the OpenShift CLI

        Returns
        -------
        semver.VersionInfo
            latest version of the OpenShift CLI
        """

        url = "https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/release.txt"

        with io.BytesIO() as buffer:
            cpo.utils.download.download_file_into_buffer(urllib.parse.urlsplit(url), buffer, silent=True)

            latest_version = self._parse_openshift_client_cli_version_from_versions_file(
                buffer.getvalue().decode("utf-8")
            )

            return latest_version

    def _extract_archive(self, archive_path: pathlib.Path):
        """Extracts the given archive in a dependency-specific manner

        Parameters
        ----------
        archive_path
            path of the archive to be extracted
        """

        member_identification_func: cpo.utils.compression.MemberIdentificationFunc = lambda path, file_type: (
            (os.path.basename(path) == "oc") and (file_type == cpo.utils.file.FileType.RegularFile)
        )

        target_directory_path = cpo.config.configuration_manager.get_bin_directory_path()

        cpo.utils.compression.extract_archive(
            archive_path,
            target_directory_path,
            memberIdentificationFunc=member_identification_func,
        )

    def _parse_openshift_client_cli_version_from_versions_file(self, file_contents: str) -> semver.VersionInfo:
        """Parses the OpenShift CLI version contained in the given file
        contents

        Parameters
        ----------
        file_contents
            file contents to be parsed for an OpenShift CLI version

        Returns
        -------
        semver.VersionInfo
            parsed OpenShift CLI version
        """

        search_result = regex.search(
            "Version: {2}(\\d+\\.\\d+\\.\\d+)",
            file_contents,
        )

        if search_result is None:
            raise CloudPakOperationsCLIException(f"{self.get_dependency_name()} could not be parsed")

        version = semver.VersionInfo.parse(f"{search_result.group(1)}")

        return version
