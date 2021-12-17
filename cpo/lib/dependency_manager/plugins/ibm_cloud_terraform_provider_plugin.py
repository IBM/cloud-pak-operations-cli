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
import urllib.parse

import semver

import cpo.config
import cpo.utils.compression
import cpo.utils.download
import cpo.utils.operating_system

from cpo.lib.dependency_manager.dependency_manager_plugin import (
    AbstractDependencyManagerPlugIn,
)
from cpo.lib.error import DataGateCLIException
from cpo.utils.operating_system import OperatingSystem


class IBMCloudTerraformProviderPlugIn(AbstractDependencyManagerPlugIn):
    def __init__(self):
        self._ibmcloud_terraform_provider_plugin_configuration_data_dict = {
            OperatingSystem.LINUX_X86_64: {
                "ibm_cloud_terraform_provider_file_name": "terraform-provider-ibm_{version}_linux_amd64.zip",
                "terraform_plugins_directory_path": ".terraform.d/plugins",
            },
            OperatingSystem.MAC_OS: {
                "ibm_cloud_terraform_provider_file_name": "terraform-provider-ibm_{version}_darwin_amd64.zip",
                "terraform_plugins_directory_path": ".terraform.d/plugins",
            },
            OperatingSystem.WINDOWS: {
                "ibm_cloud_terraform_provider_file_name": "terraform-provider-ibm_{version}_windows_amd64.zip",
                "terraform_plugins_directory_path": "AppData/Roaming/terraform.d/plugins",
            },
        }

    # override
    def download_dependency_version(self, version: semver.VersionInfo):
        operating_system = cpo.utils.operating_system.get_operating_system()
        file_name = self._ibmcloud_terraform_provider_plugin_configuration_data_dict[operating_system][
            "ibm_cloud_terraform_provider_file_name"
        ].format(version=str(version))

        url = f"https://github.com/IBM-Cloud/terraform-provider-ibm/releases/download/v{str(version)}/{file_name}"
        archive_path = cpo.utils.download.download_file(urllib.parse.urlsplit(url))
        target_directory_path = self.get_terraform_plugins_directory_path()

        self._extract_archive(archive_path, target_directory_path)

    # override
    def get_dependency_alias(self) -> str:
        return "ibmcloud_terraform_provider_plugin"

    # override
    def get_dependency_name(self) -> str:
        return "IBM Cloud Terraform Provider"

    # override
    def get_latest_dependency_version(self) -> semver.VersionInfo:
        latest_version = self._get_latest_dependency_version_on_github("IBM-Cloud", "terraform-provider-ibm")

        if latest_version is None:
            raise DataGateCLIException(f"No {self.get_dependency_name()} release could be found on GitHub")

        return latest_version

    def get_terraform_plugins_directory_path(self) -> pathlib.Path:
        """Returns the Terraform plug-ins directory path

        Returns
        -------
        pathlib.Path
            Terraform plug-ins directory path
        """

        operating_system = cpo.utils.operating_system.get_operating_system()

        return (
            cpo.config.configuration_manager.get_home_directory_path()
            / self._ibmcloud_terraform_provider_plugin_configuration_data_dict[operating_system][
                "terraform_plugins_directory_path"
            ]
        )

    def _extract_archive(self, archive_path: pathlib.Path, target_directory_path: pathlib.Path):
        """Extracts the given archive in a dependency-specific manner

        Parameters
        ----------
        archive_path
            path of the archive to be extracted
        target_directory_path
            path of the directory the archive shall be extracted to
        """

        for entry in pathlib.Path(target_directory_path).glob("terraform-provider-ibm*"):
            os.remove(entry)

        cpo.utils.compression.extract_archive(archive_path, target_directory_path)
