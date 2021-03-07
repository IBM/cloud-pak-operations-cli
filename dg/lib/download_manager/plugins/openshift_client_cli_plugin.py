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

import io
import os
import pathlib
import re as regex
import urllib.parse

import semver

import dg.config
import dg.utils.compression
import dg.utils.download
import dg.utils.file
import dg.utils.operating_system

from dg.lib.download_manager.download_manager_plugin import (
    AbstractDownloadManagerPlugIn,
)
from dg.lib.error import DataGateCLIException
from dg.utils.operating_system import OperatingSystem


class OpenShiftClientCLIPlugIn(AbstractDownloadManagerPlugIn):
    # override
    def download_binary_version(self, version: semver.VersionInfo):
        operating_system = dg.utils.operating_system.get_operating_system()
        operating_system_file_name_pattern_dict = {
            OperatingSystem.LINUX_X86_64: "openshift-client-linux.tar.gz",
            OperatingSystem.MAC_OS: "openshift-client-mac.tar.gz",
            OperatingSystem.WINDOWS: "openshift-client-windows.zip",
        }

        file_name = operating_system_file_name_pattern_dict[operating_system]
        url = f"https://mirror.openshift.com/pub/openshift-v4/clients/ocp/{str(version)}/{file_name}"
        archive_path = dg.utils.download.download_file(urllib.parse.urlsplit(url))

        self._extract_archive(archive_path)

    # override
    def get_binary_alias(self) -> str:
        return "oc"

    # override
    def get_latest_binary_version(self) -> semver.VersionInfo:
        """Returns the latest version of the OpenShift Client CLI

        Returns
        -------
        semver.VersionInfo
            latest version of the OpenShift Client CLI
        """

        url = "https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/release.txt"

        with io.BytesIO() as buffer:
            dg.utils.download.download_file_into_buffer(urllib.parse.urlsplit(url), buffer, silent=True)

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

        member_identification_func: dg.utils.compression.MemberIdentificationFunc = lambda path, file_type: (
            (os.path.basename(path) == "oc") and (file_type == dg.utils.file.FileType.RegularFile)
        )

        target_directory_path = dg.config.data_gate_configuration_manager.get_dg_bin_directory_path()

        dg.utils.compression.extract_archive(
            archive_path,
            target_directory_path,
            memberIdentificationFunc=member_identification_func,
        )

    def _parse_openshift_client_cli_version_from_versions_file(self, file_contents: str) -> semver.VersionInfo:
        """Parses the OpenShift Client CLI version contained in the given file
        contents

        Parameters
        ----------
        file_contents
            file contents to be parsed for an OpenShift Client CLI version

        Returns
        -------
        semver.VersionInfo
            parsed OpenShift Client CLI version
        """

        search_result = regex.search(
            "Version:  (\\d+\\.\\d+\\.\\d+)",
            file_contents,
        )

        if search_result is None:
            raise DataGateCLIException("OpenShift Client CLI could not be parsed")

        version = semver.VersionInfo.parse(f"{search_result.group(1)}")

        return version
