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

import os
import pathlib
import stat
import urllib.parse

from typing import Optional

import semver

import cpo.config
import cpo.utils.compression
import cpo.utils.download
import cpo.utils.operating_system

from cpo.lib.dependency_manager.dependency_manager_binary_plugin import DependencyManagerBinaryPlugIn
from cpo.lib.dependency_manager.dependency_manager_plugin import DependencyVersion
from cpo.utils.error import CloudPakOperationsCLIException
from cpo.utils.operating_system import OperatingSystem


class TerraformPlugin(DependencyManagerBinaryPlugIn):
    def __init__(self):
        self._operating_system_to_file_name_suffix_dict = {
            OperatingSystem.LINUX_X86_64: "linux_amd64.zip",
            OperatingSystem.MAC_OS: "darwin_amd64.zip",
            OperatingSystem.WINDOWS: "windows_amd64.zip",
        }

    # override
    def download_dependency_version(self, dependency_version: DependencyVersion):
        operating_system = cpo.utils.operating_system.get_operating_system()
        file_name_suffix = self._operating_system_to_file_name_suffix_dict.get(operating_system)

        if file_name_suffix is None:
            raise CloudPakOperationsCLIException(
                f"{self.get_dependency_name()} does not support {operating_system.value}"
            )

        file_name = f"terraform_{str(dependency_version)}_{file_name_suffix}"
        url = f"https://releases.hashicorp.com/terraform/{str(dependency_version)}/{file_name}"
        archive_path = cpo.utils.download.download_file(urllib.parse.urlsplit(url))

        self._extract_archive(archive_path, dependency_version.version, operating_system)

    # override
    def get_binary_name(self) -> Optional[str]:
        return "terraform"

    # override
    def get_dependency_alias(self) -> str:
        return "terraform"

    # override
    def get_dependency_name(self) -> str:
        return "Terraform"

    # override
    def get_latest_dependency_version(self) -> DependencyVersion:
        latest_version = self._get_latest_dependency_version_on_github("hashicorp", "terraform")

        if latest_version is None:
            raise CloudPakOperationsCLIException(f"No {self.get_dependency_name()} release could be found on GitHub")

        return latest_version

    # override
    def is_operating_system_supported(self, operating_system: OperatingSystem) -> bool:
        return operating_system in self._operating_system_to_file_name_suffix_dict

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

        if (operating_system == cpo.utils.operating_system.OperatingSystem.LINUX_X86_64) or (
            operating_system == cpo.utils.operating_system.OperatingSystem.MAC_OS
        ):
            # change file mode (see https://bugs.python.org/issue15795)
            post_extraction_func: cpo.utils.compression.PostExtractionFunc = lambda path: os.chmod(
                path,
                os.stat(path).st_mode | stat.S_IXGRP | stat.S_IXOTH | stat.S_IXUSR,
            )

            cpo.utils.compression.extract_archive(
                archive_path,
                target_directory_path,
                postExtractionFunc=post_extraction_func,
            )
        else:
            cpo.utils.compression.extract_archive(archive_path, target_directory_path)

        binary_name_with_os_specific_extension = (
            f"{self.get_binary_name()}.exe" if (operating_system == OperatingSystem.WINDOWS) else self.get_binary_name()
        )

        source_file_name = pathlib.Path(f"{target_directory_path}/{binary_name_with_os_specific_extension}")
        target_file_name = pathlib.Path(
            f"{source_file_name.parent}/{self.get_binary_name()}-{version}{source_file_name.suffix}"
        )

        pathlib.Path(target_directory_path / source_file_name).rename(target_file_name)
