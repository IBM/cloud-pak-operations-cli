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
import re
import stat
import urllib.parse

from html.parser import HTMLParser
from typing import Final, Optional

import requests
import semver

import dg.config
import dg.utils.compression
import dg.utils.download
import dg.utils.file
import dg.utils.operating_system

TERRAFORM_CLI_DOWNLOAD_URL: Final[str] = "https://releases.hashicorp.com/terraform/"


class TerraformHTMLParser(HTMLParser):
    """Class used to determine the latest version of the Terraform CLI"""

    def __init__(self):
        HTMLParser.__init__(self)
        self._is_data_to_be_handled = False
        self._versions: list[semver.VersionInfo] = []

    def get_latest_version(self) -> semver.VersionInfo:
        """Returns the latest version of the Terraform CLI

        Returns
        -------
        semver.VersionInfo
            latest version of the Terraform CLI
        """

        sorted_versions = sorted(
            self._versions,
            key=lambda version_info: (
                version_info.major,
                version_info.minor,
                version_info.patch,
            ),
        )

        return sorted_versions[len(sorted_versions) - 1]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]):
        if tag == "a":
            self._is_data_to_be_handled = True

    def handle_endtag(self, tag: str):
        if tag == "a":
            self._is_data_to_be_handled = False

    def handle_data(self, data: str):
        if self._is_data_to_be_handled:
            # ignore beta versions
            search_result = re.search("terraform_(\\d+\\.\\d+\\.\\d+)$", data)

            if search_result is not None:
                self._versions.append(semver.VersionInfo.parse(search_result.group(1)))


def download_terraform_cli():
    """Downloads the latest Terraform CLI version"""

    latest_terraform_cli_version = get_latest_terraform_cli_version()
    operating_system = dg.utils.operating_system.get_operating_system()
    operating_system_to_file_name_suffix_dict = {
        dg.utils.operating_system.OperatingSystem.LINUX_X86_64: "linux_amd64.zip",
        dg.utils.operating_system.OperatingSystem.MAC_OS: "darwin_amd64.zip",
        dg.utils.operating_system.OperatingSystem.WINDOWS: "windows_amd64.zip",
    }

    file_name_suffix = operating_system_to_file_name_suffix_dict[operating_system]
    file_name = "terraform_{}.{}.{}_{}".format(
        latest_terraform_cli_version.major,
        latest_terraform_cli_version.minor,
        latest_terraform_cli_version.patch,
        file_name_suffix,
    )

    url = "{}{}.{}.{}/{}".format(
        TERRAFORM_CLI_DOWNLOAD_URL,
        latest_terraform_cli_version.major,
        latest_terraform_cli_version.minor,
        latest_terraform_cli_version.patch,
        file_name,
    )

    archive_path = dg.utils.download.download_file(urllib.parse.urlsplit(url))
    target_directory_path = (
        dg.config.data_gate_configuration_manager.get_dg_bin_directory_path()
    )

    if (operating_system == dg.utils.operating_system.OperatingSystem.LINUX_X86_64) or (
        operating_system == dg.utils.operating_system.OperatingSystem.MAC_OS
    ):
        # change file mode (see https://bugs.python.org/issue15795)
        post_extraction_func: dg.utils.compression.PostExtractionFunc = (
            lambda path: os.chmod(
                path, os.stat(path).st_mode | stat.S_IXGRP | stat.S_IXOTH | stat.S_IXUSR
            )
        )

        dg.utils.compression.extract_archive(
            archive_path, target_directory_path, postExtractionFunc=post_extraction_func
        )
    else:
        dg.utils.compression.extract_archive(archive_path, target_directory_path)


def get_latest_terraform_cli_version() -> semver.VersionInfo:
    """Returns the latest Terraform CLI version

    Returns
    -------
    semver.VersionInfo
        latest Terraform CLI version
    """

    response = requests.get(TERRAFORM_CLI_DOWNLOAD_URL, stream=True)
    response.raise_for_status()

    parser = TerraformHTMLParser()
    parser.feed(response.content.decode(response.encoding))

    latest_version = parser.get_latest_version()

    return latest_version
