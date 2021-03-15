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

import os
import pathlib
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


class IBMCloudCLIPlugIn(AbstractDownloadManagerPlugIn):
    # override
    def download_binary_version(self, version: semver.VersionInfo):
        operating_system = dg.utils.operating_system.get_operating_system()
        operating_system_directory_name_pattern_dict = {
            OperatingSystem.LINUX_X86_64: "linux64",
            OperatingSystem.MAC_OS: "osx",
            OperatingSystem.WINDOWS: "win64",
        }

        directory = operating_system_directory_name_pattern_dict[operating_system]
        url = f"https://clis.cloud.ibm.com/download/bluemix-cli/{str(version)}/{directory}/archive"
        archive_path = dg.utils.download.download_file(urllib.parse.urlsplit(url))

        self._extract_archive(archive_path)

    # override
    def get_binary_alias(self) -> str:
        return "ibmcloud"

    # override
    def get_latest_binary_version(self) -> semver.VersionInfo:
        latest_version = self._get_latest_binary_version_on_github("IBM-Cloud", "ibm-cloud-cli-release")

        if latest_version is None:
            raise DataGateCLIException("No IBM Cloud CLI release could be found on GitHub")

        return latest_version

    def _extract_archive(self, archive_path: pathlib.Path):
        """Extracts the given archive in a dependency-specific manner

        Parameters
        ----------
        archive_path
            path of the archive to be extracted
        """

        member_identification_func: dg.utils.compression.MemberIdentificationFunc = lambda path, file_type: (
            ((os.path.basename(path) == "ibmcloud") or (os.path.basename(path) == "ibmcloud.exe"))
            and (file_type == dg.utils.file.FileType.RegularFile)
        )

        target_directory_path = dg.config.data_gate_configuration_manager.get_dg_bin_directory_path()

        dg.utils.compression.extract_archive(
            archive_path,
            target_directory_path,
            ignoreDirectoryStructure=True,
            memberIdentificationFunc=member_identification_func,
        )
