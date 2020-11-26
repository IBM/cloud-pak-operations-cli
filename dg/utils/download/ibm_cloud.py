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

import json
import os
import pathlib
import re
import urllib.parse

from typing import Final

import requests
import semver

import dg.config
import dg.utils.compression
import dg.utils.download
import dg.utils.file
import dg.utils.operating_system

from dg.utils.operating_system import OperatingSystem

IBM_CLOUD_CLI_DOWNLOAD_URL: Final[
    str
] = "https://clis.cloud.ibm.com/download/bluemix-cli/latest/{}/archive"

IBM_CLOUD_TERRAFORM_PROVIDER_DOWNLOAD_URL: Final[
    str
] = "https://github.com/IBM-Cloud/terraform-provider-ibm/releases/download/v{}.{}.{}/{}"

IBM_CLOUD_TERRAFORM_PROVIDER_RELEASES_URL: Final[
    str
] = "https://api.github.com/repos/IBM-Cloud/terraform-provider-ibm/releases/latest"

ibm_cloud_configuration_data_dict = {
    OperatingSystem.LINUX_X86_64: {
        "ibm_cloud_cli_download_directory_name": "linux64",
        "ibm_cloud_terraform_provider_file_name": "linux_amd64.zip",
        "terraform_plugins_directory_path": ".terraform.d/plugins",
    },
    OperatingSystem.MAC_OS: {
        "ibm_cloud_cli_download_directory_name": "osx",
        "ibm_cloud_terraform_provider_file_name": "darwin_amd64.zip",
        "terraform_plugins_directory_path": ".terraform.d/plugins",
    },
    OperatingSystem.WINDOWS: {
        "ibm_cloud_cli_download_directory_name": "win64",
        "ibm_cloud_terraform_provider_file_name": "windows_amd64.zip",
        "terraform_plugins_directory_path": "AppData/Roaming/terraform.d/plugins",
    },
}


def download_ibm_cloud_cli():
    """Downloads the latest IBM Cloud CLI version"""

    operating_system = dg.utils.operating_system.get_operating_system()
    directory_name = ibm_cloud_configuration_data_dict[operating_system][
        "ibm_cloud_cli_download_directory_name"
    ]

    url = IBM_CLOUD_CLI_DOWNLOAD_URL.format(directory_name)

    archive_path = dg.utils.download.download_file(urllib.parse.urlsplit(url))
    member_identification_func: dg.utils.compression.MemberIdentificationFunc = (
        lambda path, file_type: (
            (
                (os.path.basename(path) == "ibmcloud")
                or (os.path.basename(path) == "ibmcloud.exe")
            )
            and (file_type == dg.utils.file.FileType.RegularFile)
        )
    )

    target_directory_path = (
        dg.config.data_gate_configuration_manager.get_dg_bin_directory_path()
    )

    dg.utils.compression.extract_archive(
        archive_path,
        target_directory_path,
        ignoreDirectoryStructure=True,
        memberIdentificationFunc=member_identification_func,
    )


def download_ibm_cloud_terraform_provider():
    """Downloads the latest IBM Cloud Terraform Provider version"""

    latest_version = get_latest_ibm_cloud_terraform_provider_version(
        IBM_CLOUD_TERRAFORM_PROVIDER_RELEASES_URL
    )

    operating_system = dg.utils.operating_system.get_operating_system()
    file_name = ibm_cloud_configuration_data_dict[operating_system][
        "ibm_cloud_terraform_provider_file_name"
    ]

    url = IBM_CLOUD_TERRAFORM_PROVIDER_DOWNLOAD_URL.format(
        latest_version.major, latest_version.minor, latest_version.patch, file_name
    )

    archive_path = dg.utils.download.download_file(urllib.parse.urlsplit(url))
    target_directory_path = get_terraform_plugins_directory_path()

    remove_ibm_cloud_terraform_provider_versions()
    dg.utils.compression.extract_archive(archive_path, target_directory_path)


def get_latest_ibm_cloud_terraform_provider_version(
    url: str,
) -> semver.VersionInfo:
    """Returns the latest IBM Cloud Terraform Provider version

    Parameters
    ----------
    url
        GitHub Releases API URL of the IBM Cloud Terraform Provider
        (https://developer.github.com/v3/repos/releases/)


    Returns
    -------
    semver.VersionInfo
        latest IBM Cloud Terraform Provider version
    """

    response = requests.get(url)
    response.raise_for_status()

    tag_name = json.loads(response.content)["tag_name"]
    search_result = re.search("v(\\d+\\.\\d+\\.\\d+)$", tag_name)

    if not search_result:
        raise ValueError("Could not parse version: " + tag_name)

    return semver.VersionInfo.parse(search_result.group(1))


def get_terraform_plugins_directory_path() -> pathlib.Path:
    """Returns the Terraform plugins directory path

    Returns
    -------
    pathlib.Path
        Terraform plugins directory path
    """

    operating_system = dg.utils.operating_system.get_operating_system()
    target_directory_path = (
        pathlib.Path.home()
        / ibm_cloud_configuration_data_dict[operating_system][
            "terraform_plugins_directory_path"
        ]
    )

    return target_directory_path


def remove_ibm_cloud_terraform_provider_versions():
    """Removes all IBM Cloud Terraform Provider versions"""

    target_directory_path = get_terraform_plugins_directory_path()

    for entry in pathlib.Path(target_directory_path).glob("terraform-provider-ibm*"):
        os.remove(entry)
