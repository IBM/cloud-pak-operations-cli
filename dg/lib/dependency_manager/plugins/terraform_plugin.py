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

import os
import pathlib
import stat
import urllib.parse

from typing import Optional

import semver

import dg.config
import dg.utils.compression
import dg.utils.download
import dg.utils.operating_system

from dg.lib.dependency_manager.dependency_manager_plugin import (
    AbstractDependencyManagerPlugIn,
)
from dg.lib.error import DataGateCLIException
from dg.utils.operating_system import OperatingSystem


class TerraformPlugin(AbstractDependencyManagerPlugIn):
    # override
    def download_dependency_version(self, version: semver.VersionInfo):
        operating_system = dg.utils.operating_system.get_operating_system()
        operating_system_to_file_name_suffix_dict = {
            OperatingSystem.LINUX_X86_64: "linux_amd64.zip",
            OperatingSystem.MAC_OS: "darwin_amd64.zip",
            OperatingSystem.WINDOWS: "windows_amd64.zip",
        }

        file_name_suffix = operating_system_to_file_name_suffix_dict[operating_system]
        file_name = f"terraform_{str(version)}_{file_name_suffix}"
        url = f"https://releases.hashicorp.com/terraform/{str(version)}/{file_name}"
        archive_path = dg.utils.download.download_file(urllib.parse.urlsplit(url))

        self._extract_archive(archive_path, operating_system)

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
    def get_latest_dependency_version(self) -> semver.VersionInfo:
        latest_version = self._get_latest_dependency_version_on_github("hashicorp", "terraform")

        if latest_version is None:
            raise DataGateCLIException(f"No {self.get_dependency_name()} release could be found on GitHub")

        return latest_version

    def _extract_archive(self, archive_path: pathlib.Path, operating_system: OperatingSystem):
        """Extracts the given archive in a dependency-specific manner

        Parameters
        ----------
        archive_path
            path of the archive to be extracted
        operating_system
            current operating system
        """

        target_directory_path = dg.config.data_gate_configuration_manager.get_dg_bin_directory_path()

        if (operating_system == dg.utils.operating_system.OperatingSystem.LINUX_X86_64) or (
            operating_system == dg.utils.operating_system.OperatingSystem.MAC_OS
        ):
            # change file mode (see https://bugs.python.org/issue15795)
            post_extraction_func: dg.utils.compression.PostExtractionFunc = lambda path: os.chmod(
                path,
                os.stat(path).st_mode | stat.S_IXGRP | stat.S_IXOTH | stat.S_IXUSR,
            )

            dg.utils.compression.extract_archive(
                archive_path,
                target_directory_path,
                postExtractionFunc=post_extraction_func,
            )
        else:
            dg.utils.compression.extract_archive(archive_path, target_directory_path)
