#  Copyright 2020, 2021 IBM Corporation
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
import json
import pathlib
import re as regex
import urllib.parse

from typing import Any, Optional, Tuple

import requests
import semver

import cpo.config
import cpo.lib.cloud_pak_for_data.cpd3_manager
import cpo.lib.openshift.oc
import cpo.utils.compression
import cpo.utils.download
import cpo.utils.file
import cpo.utils.operating_system

from cpo.config.binaries_manager import binaries_manager
from cpo.lib.cloud_pak_for_data.cpd3_manager import (
    AbstractCloudPakForDataManager,
    CloudPakForDataAssemblyBuildType,
    CloudPakForDataVersion,
)
from cpo.lib.error import DataGateCLIException
from cpo.utils.operating_system import OperatingSystem

cloud_pak_for_data_configuration_data_dict = {
    OperatingSystem.LINUX_X86_64: {
        "extension": "tgz",
        "file_name_infix": "linux",
    },
    OperatingSystem.MAC_OS: {
        "extension": "tgz",
        "file_name_infix": "darwin",
    },
    OperatingSystem.WINDOWS: {
        "extension": "zip",
        "file_name_infix": "windows",
    },
}


class CloudPakForDataManager(AbstractCloudPakForDataManager):
    """IBM Cloud Pak for Data 3.5.0 management class"""

    def __init__(self, build_type: CloudPakForDataAssemblyBuildType):
        super().__init__(build_type)

        self._cloud_pak_for_data_version = semver.VersionInfo.parse("3.5.0")

    # override
    def download_cpd_installer(self):
        cloud_pak_for_data_version: CloudPakForDataVersion = (
            AbstractCloudPakForDataManager._cloud_pak_for_data_versions[str(self._cloud_pak_for_data_version)]
        )

        if self._build_type == CloudPakForDataAssemblyBuildType.DEV:
            directory_alias = cloud_pak_for_data_version["development"]["directory_alias"]
            current_version = binaries_manager.get_binary_version(directory_alias)
            latest_version = self._get_cpd_installer_latest_development_version(cloud_pak_for_data_version)

            if (current_version is None) or (latest_version.compare(current_version) == 1):
                file_name = self._get_cpd_installer_development_version_file_name(latest_version)

                self._download_cpd_installer_development(cloud_pak_for_data_version, file_name)
                binaries_manager.set_binary_version(directory_alias, str(latest_version))
        else:
            directory_alias = cloud_pak_for_data_version["release"]["directory_alias"]
            current_version = binaries_manager.get_binary_version(directory_alias)
            (
                latest_version,
                download_url,
            ) = self._get_cpd_installer_latest_release_version(cloud_pak_for_data_version)

            if (current_version is None) or (latest_version.compare(current_version) == 1):
                self._download_cpd_installer_release(cloud_pak_for_data_version, download_url)
                binaries_manager.set_binary_version(directory_alias, str(latest_version))

    # override
    def install_assembly(
        self,
        assembly_name: str,
        accept_all_licenses: bool,
        yaml_file_path: pathlib.Path,
        storage_class: str,
        **kwargs: Any,
    ):
        cpd_installer_path = self.get_cloud_pak_for_data_installer_path()

        # install as cluster admin to generate (and apply) preinstall YAML files
        args = ["adm"]

        if accept_all_licenses:
            args.append("--accept-all-licenses")

        args += [
            "--apply",
            "--assembly",
            assembly_name,
            "--download-path",
            str(cpd_installer_path.parent / "cpd-cli-workspace"),
            "--namespace",
            "zen",
            "--repo",
            str(yaml_file_path),
        ]

        self.execute_cloud_pak_for_data_installer(args)

        if self._build_type == CloudPakForDataAssemblyBuildType.DEV:
            # install assembly
            args = ["install"]

            if accept_all_licenses:
                args.append("--accept-all-licenses")

            args += [
                "--assembly",
                assembly_name,
                "--download-path",
                str(cpd_installer_path.parent / "cpd-cli-workspace"),
                "--namespace",
                "zen",
            ]

            if "override_yaml_file_path" in kwargs:
                args += ["--override", str(kwargs["override_yaml_file_path"])]

            args += [
                "--repo",
                str(yaml_file_path),
                "--storageclass",
                storage_class,
                "--verbose",
            ]
        else:
            # install assembly
            args = ["install"]

            if accept_all_licenses:
                args.append("--accept-all-licenses")

            args += [
                "--assembly",
                assembly_name,
                "--cluster-pull-prefix",
                "image-registry.openshift-image-registry.svc:5000/zen",
                "--download-path",
                str(cpd_installer_path.parent / "cpd-cli-workspace"),
                "--insecure-skip-tls-verify",
                "--namespace",
                "zen",
            ]

            if "override_yaml_file_path" in kwargs:
                args += ["--override", str(kwargs["override_yaml_file_path"])]

            image_registry_hostname = cpo.lib.openshift.oc.get_image_registry_hostname()
            target_registry_password = cpo.lib.openshift.oc.get_current_token()

            args += [
                "--repo",
                str(yaml_file_path),
                "--storageclass",
                storage_class,
                "--target-registry-password",
                target_registry_password,
                "--target-registry-username",
                "kubeadmin",
                "--transfer-image-to",
                f"{image_registry_hostname}/zen",
                "--verbose",
            ]

        self.execute_cloud_pak_for_data_installer(args)

    def _download_cpd_installer_development(self, cloud_pak_for_data_version: CloudPakForDataVersion, file_name: str):
        """Downloads the IBM Cloud Pak for Data 3.5.0 development build
        installer with the given file name

        Parameters
        ----------
        cloud_pak_for_data_version
            IBM Cloud Pak for Data version information
        file_name
            name of the file to be downloaded
        """

        archive_path = cpo.utils.download.download_file(
            urllib.parse.urlsplit(cloud_pak_for_data_version["development"]["download_url"] + file_name)
        )

        self._extract_cpd_installer(
            cloud_pak_for_data_version,
            archive_path,
        )

    def _download_cpd_installer_release(self, cloud_pak_for_data_version: CloudPakForDataVersion, download_url: str):
        """Downloads the IBM Cloud Pak for Data 3.5.0 release build installer

        Parameters
        ----------
        cloud_pak_for_data_version
            IBM Cloud Pak for Data version information
        download_url
            URL of the IBM Cloud Pak for Data 3.5.0 release build to be downloaded
        """

        archive_path = cpo.utils.download.download_file(urllib.parse.urlsplit(download_url))

        self._extract_cpd_installer(cloud_pak_for_data_version, archive_path)

    def _extract_cpd_installer(
        self,
        cloud_pak_for_data_version: CloudPakForDataVersion,
        archive_path: pathlib.Path,
    ):
        """Extracts the IBM Cloud Pak for Data 3.5.0 release build installer
        archive

        Parameters
        ----------
        cloud_pak_for_data_version
            IBM Cloud Pak for Data version information
        archive_path
            path of the IBM Cloud Pak for Data 3.5.0 release build installer archive
        """

        target_directory_path = (
            cpo.config.configuration_manager.get_bin_directory_path()
            / cloud_pak_for_data_version[
                "development" if self._build_type == CloudPakForDataAssemblyBuildType.DEV else "release"
            ]["directory_alias"]
        )

        if self._build_type == CloudPakForDataAssemblyBuildType.DEV:
            operating_system = cpo.utils.operating_system.get_operating_system()
            cloud_pak_for_data_configuration_data = cloud_pak_for_data_configuration_data_dict[operating_system]
            file_name_infix = cloud_pak_for_data_configuration_data["file_name_infix"]

            cpo.utils.compression.extract_archive(
                archive_path,
                target_directory_path,
                directoryPathToStartExtraction=f"cpd-cli-{file_name_infix}-EE-\\d+.\\d+.\\d+-\\d+",
            )
        else:
            cpo.utils.compression.extract_archive(
                archive_path,
                target_directory_path,
            )

    # override
    def _get_cloud_pak_for_data_version(self) -> semver.VersionInfo:
        return self._cloud_pak_for_data_version

    def _get_cpd_installer_development_version_file_name(self, version: semver.VersionInfo) -> str:
        """Returns the file name of the given development build version of the
        IBM Cloud Pak for Data 3.5.0 installer to be downloaded

        Parameters
        ----------
        cloud_pak_for_data_version
            IBM Cloud Pak for Data version information
        version
            version of the IBM Cloud Pak for Data 3.5.0 installer to be downloaded

        Returns
        -------
        str
            file name of the given development build version of the IBM Cloud Pak
            for Data 3.5.0 installer to be downloaded
        """

        operating_system = cpo.utils.operating_system.get_operating_system()
        cloud_pak_for_data_configuration_data = cloud_pak_for_data_configuration_data_dict[operating_system]
        extension = cloud_pak_for_data_configuration_data["extension"]
        file_name_infix = cloud_pak_for_data_configuration_data["file_name_infix"]
        file_name = f"cpd-cli-{file_name_infix}-EE-{version.major}.{version.minor}.{version.patch}.{extension}"

        return file_name

    def _get_cpd_installer_latest_development_version(
        self, cloud_pak_for_data_version: CloudPakForDataVersion
    ) -> semver.VersionInfo:
        """Returns the latest development build version of the IBM Cloud Pak for
        Data 3.5.0 installer

        Parameters
        ----------
        cloud_pak_for_data_version
            IBM Cloud Pak for Data version information

        Returns
        -------
        semver.VersionInfo
            latest development build version of the IBM Cloud Pak for Data 3.5.0
            installer
        """

        with io.BytesIO() as buffer:
            cpo.utils.download.download_file_into_buffer(
                urllib.parse.urlsplit(cloud_pak_for_data_version["development"]["download_url"] + "VERSIONS.txt"),
                buffer,
            )

            latest_version = self._parse_cloud_pak_for_data_version_from_versions_file(
                buffer.getvalue().decode("utf-8")
            )

            return latest_version

    def _get_cpd_installer_latest_release_version(
        self, cloud_pak_for_data_version: CloudPakForDataVersion
    ) -> Tuple[semver.VersionInfo, str]:
        """Returns the latest release build version of the IBM Cloud Pak for
        Data 3.5.0 installer and the corresponding URL

        Parameters
        ----------
        cloud_pak_for_data_version
            IBM Cloud Pak for Data version information

        Returns
        -------
        tuple[semver.VersionInfo, str]
            latest release build version of the IBM Cloud Pak for Data 3.5.0
            installer and the corresponding URL
        """

        response = requests.get(cloud_pak_for_data_version["release"]["download_url"])
        response.raise_for_status()

        response_json = json.loads(response.content)
        result: Optional[Tuple[semver.VersionInfo, str]] = None

        for release in response_json:
            search_result = regex.search(
                f".*({self._cloud_pak_for_data_version.major}\\.{self._cloud_pak_for_data_version.minor}"
                f"\\.\\d+(-\\d+)*).*",
                release["name"],
            )

            if search_result is not None:
                browser_download_url = self._get_cpd_installer_latest_release_version_browser_download_url(
                    release["assets"]
                )

                result = (
                    semver.VersionInfo.parse(search_result.group(1)),
                    browser_download_url,
                )

                break

        if result is None:
            raise DataGateCLIException(
                f"IBM Cloud Pak for Data installer release for Cloud Pak for Data "
                f"{self._get_cloud_pak_for_data_version()} could not be found on GitHub"
            )

        return result

    def _get_cpd_installer_latest_release_version_browser_download_url(self, assets: Any) -> str:
        """Returns the URL of the latest release build version of the IBM Cloud
        Pak for Data 3.5.0 installer

        Parameters
        ----------
        assets
            JSON object with GitHub release assets
            (see https://developer.github.com/v3/repos/releases/#list-releases)

        Returns
        -------
        str
            URL of the latest release build version of the IBM Cloud Pak for Data
            3.5.0 installer
        """

        operating_system = cpo.utils.operating_system.get_operating_system()
        cloud_pak_for_data_configuration_data = cloud_pak_for_data_configuration_data_dict[operating_system]
        extension = cloud_pak_for_data_configuration_data["extension"]
        file_name_infix = cloud_pak_for_data_configuration_data["file_name_infix"]
        result = None

        for asset in assets:
            if (
                regex.search(
                    f"cpd-cli-{file_name_infix}-EE-\\d+.\\d+.\\d+(-\\d+)*\\.{extension}",
                    asset["name"],
                )
                is not None
            ):
                result = asset["browser_download_url"]

                break

        if result is None:
            raise DataGateCLIException(
                f"Download URL of IBM Cloud Pak for Data installer for Cloud Pak for Data "
                f"{self._get_cloud_pak_for_data_version()} could not be found on GitHub"
            )

        return result

    def _parse_cloud_pak_for_data_version_from_versions_file(self, file_contents: str) -> semver.VersionInfo:
        """Parses the IBM Cloud Pak for Data version contained in the given file
        contents

        Parameters
        ----------
        file_contents
            file contents to be parsed for an IBM Cloud Pak for Data version

        Returns
        -------
        semver.VersionInfo
            parsed IBM Cloud Pak for Data version
        """

        search_result = regex.search(
            "cpd-cli[\\S\\s]*?Build Number: (\\d*)[\\S\\s]*?CPD Release Version: ([\\d\\.]*)",
            file_contents,
        )

        if search_result is None:
            raise DataGateCLIException("Cloud Pak for Data version could not be parsed")

        version = semver.VersionInfo.parse(f"{search_result.group(2)}+{search_result.group(1)}")

        return version
