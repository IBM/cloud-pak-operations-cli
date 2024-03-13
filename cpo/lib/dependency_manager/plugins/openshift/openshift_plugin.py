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
import os
import pathlib
import re as regex
import urllib.parse

from abc import abstractmethod

import requests
import semver

import cpo.config
import cpo.utils.compression
import cpo.utils.download
import cpo.utils.file
import cpo.utils.operating_system

from cpo.lib.dependency_manager.dependency_manager_binary_plugin import DependencyManagerBinaryPlugIn
from cpo.lib.dependency_manager.dependency_manager_plugin import DependencyVersion
from cpo.utils.error import CloudPakOperationsCLIException
from cpo.utils.operating_system import OperatingSystem


class AbstractOpenShiftPlugIn(DependencyManagerBinaryPlugIn):
    # override
    def download_dependency_version(self, dependency_version: DependencyVersion):
        operating_system = cpo.utils.operating_system.get_operating_system()
        file_name = self._get_operating_system_file_name_dict().get(operating_system)

        if file_name is None:
            raise CloudPakOperationsCLIException(
                f"{self.get_dependency_name()} does not support {operating_system.value}"
            )

        url = f"https://mirror.openshift.com/pub/openshift-v4/clients/ocp/{str(dependency_version)}/{file_name}"

        try:
            archive_path = cpo.utils.download.download_file(urllib.parse.urlsplit(url))
        except requests.exceptions.HTTPError as exception:
            if (exception.response is not None) and (exception.response.status_code == 404):
                raise CloudPakOperationsCLIException(
                    f"{self.get_dependency_name()} {dependency_version} does not exist"
                )
            else:
                raise

        self._extract_archive(archive_path, dependency_version.version, operating_system)

    # override
    def get_latest_dependency_version(self) -> DependencyVersion:
        """Returns the latest version of the OpenShift CLI

        Returns
        -------
        semver.Version
            latest version of the OpenShift CLI
        """

        url = "https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/release.txt"

        with io.BytesIO() as buffer:
            cpo.utils.download.download_file_into_buffer(urllib.parse.urlsplit(url), buffer, silent=True)

            latest_version = self._parse_version_from_versions_file(buffer.getvalue().decode("utf-8"))

            return DependencyVersion(latest_version)

    # override
    def is_operating_system_supported(self, operating_system: OperatingSystem) -> bool:
        return operating_system in self._get_operating_system_file_name_dict()

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
            ((os.path.basename(path) == binary_name_with_os_specific_extension))
            and (file_type == cpo.utils.file.FileType.RegularFile)
        )

        target_directory_path = cpo.config.configuration_manager.get_bin_directory_path()

        cpo.utils.compression.extract_archive(
            archive_path,
            target_directory_path,
            memberIdentificationFunc=member_identification_func,
        )

        source_file_name = pathlib.Path(f"{target_directory_path}/{binary_name_with_os_specific_extension}")
        target_file_name = pathlib.Path(
            f"{source_file_name.parent}/{self.get_binary_name()}-{version}{source_file_name.suffix}"
        )

        pathlib.Path(target_directory_path / source_file_name).rename(target_file_name)

    @abstractmethod
    def _get_operating_system_file_name_dict(self) -> dict[OperatingSystem, str]:
        pass

    def _parse_version_from_versions_file(self, file_contents: str) -> semver.Version:
        """Parses the version contained in the given file contents

        Parameters
        ----------
        file_contents
            file contents to be parsed for a version

        Returns
        -------
        semver.Version
            parsed version
        """

        search_result = regex.search(
            "Version: {2}(\\d+\\.\\d+\\.\\d+)",
            file_contents,
        )

        if search_result is None:
            raise CloudPakOperationsCLIException(f"{self.get_dependency_name()} version could not be parsed")

        version = semver.Version.parse(f"{search_result.group(1)}")

        return version
