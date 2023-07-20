#  Copyright 2021, 2023 IBM Corporation
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

from typing import Optional

import semver

import cpo.config
import cpo.utils.compression
import cpo.utils.download
import cpo.utils.file
import cpo.utils.operating_system
import cpo.utils.process

from cpo.lib.dependency_manager.dependency_manager_plugin import AbstractDependencyManagerPlugIn
from cpo.utils.error import CloudPakOperationsCLIException, IBMCloudException
from cpo.utils.operating_system import OperatingSystem


class IBMCloudCLIPlugIn(AbstractDependencyManagerPlugIn):
    # override
    def download_dependency_version(self, version: semver.VersionInfo):
        operating_system = cpo.utils.operating_system.get_operating_system()
        operating_system_directory_name_pattern_dict = {
            OperatingSystem.LINUX_X86_64: "linux_amd64",
            OperatingSystem.MAC_OS: "macos",
            OperatingSystem.WINDOWS: "windows_amd64",
        }

        file_name = f"IBM_Cloud_CLI_{str(version)}_{operating_system_directory_name_pattern_dict[operating_system]}.tgz"
        url = f"https://download.clis.cloud.ibm.com/ibm-cloud-cli/{str(version)}/binaries/{file_name}"
        archive_path = cpo.utils.download.download_file(urllib.parse.urlsplit(url))

        self._extract_archive(archive_path)

    # override
    def execute_binary(
        self,
        args: list[str],
        env: dict[str, str] = os.environ.copy(),
        capture_output=False,
        check=True,
        print_captured_output=False,
    ) -> cpo.utils.process.ProcessResult:
        try:
            return super().execute_binary(
                args, env, capture_output=capture_output, check=check, print_captured_output=print_captured_output
            )
        except CloudPakOperationsCLIException as exception:
            if exception.stderr is not None:
                raise IBMCloudException(exception.stderr)
            else:
                raise

    # override
    def get_binary_name(self) -> Optional[str]:
        return "ibmcloud"

    # override
    def get_dependency_alias(self) -> str:
        return "ibmcloud"

    # override
    def get_dependency_name(self) -> str:
        return "IBM Cloud CLI"

    # override
    def get_latest_dependency_version(self) -> semver.VersionInfo:
        latest_version = self._get_latest_dependency_version_on_github("IBM-Cloud", "ibm-cloud-cli-release")

        if latest_version is None:
            raise CloudPakOperationsCLIException(f"No {self.get_dependency_name()} release could be found on GitHub")

        return latest_version

    def _extract_archive(self, archive_path: pathlib.Path):
        """Extracts the given archive in a dependency-specific manner

        Parameters
        ----------
        archive_path
            path of the archive to be extracted
        """

        member_identification_func: cpo.utils.compression.MemberIdentificationFunc = lambda path, file_type: (
            ((os.path.basename(path) == "ibmcloud") or (os.path.basename(path) == "ibmcloud.exe"))
            and (file_type == cpo.utils.file.FileType.RegularFile)
        )

        target_directory_path = cpo.config.configuration_manager.get_bin_directory_path()

        cpo.utils.compression.extract_archive(
            archive_path,
            target_directory_path,
            ignoreDirectoryStructure=True,
            memberIdentificationFunc=member_identification_func,
        )
