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
import urllib.parse

import semver

import cpo.config
import cpo.utils.compression
import cpo.utils.download
import cpo.utils.file
import cpo.utils.operating_system
import cpo.utils.process

from cpo.lib.dependency_manager.dependency_manager_binary_plugin import DependencyManagerBinaryPlugIn
from cpo.lib.dependency_manager.dependency_manager_plugin import DependencyVersion
from cpo.utils.error import CloudPakOperationsCLIException, IBMCloudException
from cpo.utils.operating_system import OperatingSystem


class IBMCloudCLIPlugIn(DependencyManagerBinaryPlugIn):
    def __init__(self):
        self._operating_system_to_file_name_suffix_dict = {
            OperatingSystem.LINUX_X86_64: "linux_amd64.tgz",
            OperatingSystem.MAC_OS: "macos.tgz",
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

        file_name = f"IBM_Cloud_CLI_{str(dependency_version)}_{file_name_suffix}"
        url = f"https://download.clis.cloud.ibm.com/ibm-cloud-cli/{str(dependency_version)}/binaries/{file_name}"
        archive_path = cpo.utils.download.download_file(urllib.parse.urlsplit(url))

        self._extract_archive(archive_path, dependency_version.version, operating_system)

    # override
    def execute_binary(
        self,
        version: semver.Version,
        args: list[str],
        env: dict[str, str] = os.environ.copy(),
        capture_output=False,
        check=True,
        print_captured_output=False,
    ) -> cpo.utils.process.ProcessResult:
        try:
            return super().execute_binary(
                version,
                args,
                env,
                capture_output=capture_output,
                check=check,
                print_captured_output=print_captured_output,
            )
        except CloudPakOperationsCLIException as exception:
            if exception.stderr is not None:
                raise IBMCloudException(exception.stderr)
            else:
                raise

    # override
    def get_binary_name(self) -> str | None:
        return "ibmcloud"

    # override
    def get_dependency_alias(self) -> str:
        return "ibmcloud"

    # override
    def get_dependency_name(self) -> str:
        return "IBM Cloud CLI"

    # override
    def get_latest_dependency_version(self) -> DependencyVersion:
        latest_version = self._get_latest_dependency_version_on_github("IBM-Cloud", "ibm-cloud-cli-release")

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
        """

        binary_name_with_os_specific_extension = (
            f"{self.get_binary_name()}.exe" if (operating_system == OperatingSystem.WINDOWS) else self.get_binary_name()
        )

        member_identification_func: cpo.utils.compression.MemberIdentificationFunc = lambda path, file_type: (
            os.path.basename(path) == binary_name_with_os_specific_extension
        ) and (file_type == cpo.utils.file.FileType.RegularFile)

        target_directory_path = cpo.config.configuration_manager.get_bin_directory_path()

        cpo.utils.compression.extract_archive(
            archive_path,
            target_directory_path,
            ignoreDirectoryStructure=True,
            memberIdentificationFunc=member_identification_func,
        )

        source_file_name = pathlib.Path(f"{target_directory_path}/{binary_name_with_os_specific_extension}")
        target_file_name = pathlib.Path(
            f"{source_file_name.parent}/{self.get_binary_name()}-{version}{source_file_name.suffix}"
        )

        pathlib.Path(target_directory_path / source_file_name).rename(target_file_name)
