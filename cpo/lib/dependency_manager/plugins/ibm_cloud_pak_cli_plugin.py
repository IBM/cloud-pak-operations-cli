#  Copyright 2021, 2024 IBM Corporation
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

import pathlib
import urllib.parse

import semver

import cpo.config
import cpo.utils.compression
import cpo.utils.download
import cpo.utils.operating_system

from cpo.lib.dependency_manager.dependency_manager_binary_plugin import DependencyManagerBinaryPlugIn
from cpo.lib.dependency_manager.dependency_manager_plugin import DependencyVersion
from cpo.utils.error import CloudPakOperationsCLIException
from cpo.utils.operating_system import OperatingSystem


class IBMCloudPakCLIPlugIn(DependencyManagerBinaryPlugIn):
    def __init__(self):
        self._operating_system_to_file_name_infix_dict = {
            OperatingSystem.LINUX_X86_64: "linux",
            OperatingSystem.MAC_OS: "darwin",
            OperatingSystem.WINDOWS: "win",
        }

    # override
    def download_dependency_version(self, dependency_version: DependencyVersion):
        operating_system = cpo.utils.operating_system.get_operating_system()
        file_name_infix = self._operating_system_to_file_name_infix_dict[operating_system]
        file_name = f"cloudctl-{file_name_infix}-amd64.tar.gz"
        url = f"https://github.com/IBM/cloud-pak-cli/releases/download/v{str(dependency_version)}/{file_name}"
        archive_path = cpo.utils.download.download_file(urllib.parse.urlsplit(url))

        self._extract_archive(archive_path, dependency_version.version, operating_system)

    # override
    def get_binary_name(self) -> str | None:
        return "cloudctl"

    # override
    def get_dependency_alias(self) -> str:
        return "cloudctl"

    # override
    def get_dependency_name(self) -> str:
        return "IBM Cloud Pak CLI"

    # override
    def get_latest_dependency_version(self) -> DependencyVersion:
        latest_version = self._get_latest_dependency_version_on_github("IBM", "cloud-pak-cli")

        if latest_version is None:
            raise CloudPakOperationsCLIException(f"No {self.get_dependency_name()} release could be found on GitHub")

        return latest_version

    # override
    def is_operating_system_supported(self, operating_system: OperatingSystem) -> bool:
        return operating_system in self._operating_system_to_file_name_infix_dict

    def _extract_archive(self, archive_path: pathlib.Path, version: semver.Version, operating_system: OperatingSystem):
        """Extracts the given archive in a dependency-specific manner

        Parameters
        ----------
        archive_path
            path of the archive to be extracted
        operating_system
            current operating system
        """

        target_directory_path = cpo.config.configuration_manager.get_bin_directory_path()

        cpo.utils.compression.extract_archive(
            archive_path,
            target_directory_path,
        )

        file_name_infix = self._operating_system_to_file_name_infix_dict[operating_system]
        file_name_suffix = ".exe" if operating_system == OperatingSystem.WINDOWS else ""
        source_file_name = pathlib.Path(f"{target_directory_path}/cloudctl-{file_name_infix}-amd64{file_name_suffix}")
        target_file_name = pathlib.Path(f"{source_file_name.parent}/cloudctl-{version}{source_file_name.suffix}")

        pathlib.Path(target_directory_path / source_file_name).rename(target_file_name)
