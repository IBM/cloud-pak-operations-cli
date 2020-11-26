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

import io
import pathlib
import socket
import tempfile
import urllib.parse

from abc import ABC, abstractmethod
from typing import Any, TypedDict, Union

import semver
import yaml

import dg.config
import dg.utils.download
import dg.utils.openshift
import dg.utils.operating_system

from dg.utils.operating_system import OperatingSystem


class CloudPakForDataVersion(TypedDict):
    assembly_versions: dict[str, str]
    development: dict[str, str]
    release: dict[str, str]
    cpd_installer_file_name_dict: dict[OperatingSystem, str]
    required_openshift_version: list[dict[str, str]]


CloudPakForDataVersions = TypedDict(
    "CloudPakForDataVersions",
    {
        "3.0.1": CloudPakForDataVersion,
        "3.5.0": CloudPakForDataVersion,
        "default_version": str,
        "ibm_cloud_supported_version": str,
    },
)


class AbstractCloudPakForDataManager(ABC):
    """Base class of all IBM Cloud Pak for Data management classes"""

    def __init__(self, use_dev: bool):
        self._use_dev = use_dev

    def check_openshift_version(self):
        cloud_pak_for_data_version = self._get_cloud_pak_for_data_version()
        openshift_version = dg.utils.openshift.get_openshift_version()

        if not AbstractCloudPakForDataManager.is_openshift_version_supported(
            cloud_pak_for_data_version, openshift_version
        ):
            raise Exception(
                f"Cloud Pak for Data {cloud_pak_for_data_version} cannot be installed on OpenShift {openshift_version}"
            )

    @abstractmethod
    def download_cpd_installer(self):
        """Downloads the version-specific IBM Cloud Pak for Data installer"""

        pass

    def get_assembly_version(self, assembly_name: str) -> str:
        """Returns the latest version of the assembly with the given name

        The version of an assembly may differ from the IBM Cloud Pak for Data
        version.

        Parameters
        ----------
        assembly_name
            name of the assembly for which the latest version shall be returned

        Returns
        -------
        str
            latest version of the assembly with the given name
        """

        cloud_pak_for_data_version_semver = str(self._get_cloud_pak_for_data_version())
        cloud_pak_for_data_version: CloudPakForDataVersion = (
            AbstractCloudPakForDataManager._cloud_pak_for_data_versions[
                cloud_pak_for_data_version_semver
            ]
        )

        version = (
            cloud_pak_for_data_version["assembly_versions"][assembly_name]
            if assembly_name in cloud_pak_for_data_version["assembly_versions"]
            else cloud_pak_for_data_version_semver
        )

        return version

    def get_cloud_pak_for_data_installer_path(self) -> pathlib.Path:
        """Returns the path of the IBM Cloud Pak for Data installer

        Returns
        -------
        pathlib.Path
            path of the IBM Cloud Pak for Data installer
        """

        cloud_pak_for_data_version: CloudPakForDataVersion = (
            AbstractCloudPakForDataManager._cloud_pak_for_data_versions[
                str(self._get_cloud_pak_for_data_version())
            ]
        )

        directory_alias = (
            cloud_pak_for_data_version["development"]["directory_alias"]
            if self._use_dev
            else cloud_pak_for_data_version["release"]["directory_alias"]
        )

        return (
            dg.config.data_gate_configuration_manager.get_dg_bin_directory_path()
            / directory_alias
            / cloud_pak_for_data_version["cpd_installer_file_name_dict"][
                dg.utils.operating_system.get_operating_system()
            ]
        )

    @staticmethod
    def get_default_cloud_pak_for_data_version() -> str:
        """Returns the default IBM Cloud Pak for Data version

        Returns
        -------
        str
            default IBM Cloud Pak for Data version
        """

        return AbstractCloudPakForDataManager._cloud_pak_for_data_versions[
            "default_version"
        ]

    @staticmethod
    def get_ibm_cloud_supported_version() -> semver.VersionInfo:
        """Returns the IBM Cloud Pak for Data version supported by IBM Cloud

        Returns
        -------
        semver.VersionInfo
            IBM Cloud Pak for Data version supported by IBM Cloud
        """

        return semver.VersionInfo.parse(
            AbstractCloudPakForDataManager._cloud_pak_for_data_versions[
                "ibm_cloud_supported_version"
            ]
        )

    @abstractmethod
    def install_assembly(
        self,
        assembly_name: str,
        yaml_file_path: pathlib.Path,
        storage_class: str,
        **kwargs: Any,
    ):
        """Installs an IBM Cloud Pak for Data assembly

        Parameters
        ----------
        assembly_name
            name of the assembly to be installed
        yaml_file_path
            path to the YAML file of the assembly to be installed
        storage_class
            storage class to be used for the installation
        **kwargs
            override_yaml_file_path: pathlib.Path
                path of a YAML file specifying configuration values to be used for the
                installation instead of the corresponding defaults
        """

        pass

    def install_assembly_with_prerequisites(
        self,
        artifactory_user_name: str,
        artifactory_api_key: str,
        ibm_cloud_pak_for_data_entitlement_key: Union[str, None],
        assembly_name: str,
        storage_class: str,
        **kwargs: Any,
    ):
        """Prepares the installation of an IBM Cloud Pak for Data assembly and
        installs the assembly

        Parameters
        ----------
        artifactory_user_name
            Artifactory user name
        artifactory_api_key
            Artifactory API key
        ibm_cloud_pak_for_data_entitlement_key
            IBM Cloud Pak for Data entitlement key
        assembly_name
            name of the assembly to be installed
        storage_class
            storage class to be used for the installation
        **kwargs
            override_yaml_file_path: pathlib.Path
                path of a YAML file specifying configuration values to be used for the
                installation instead of the corresponding defaults
        """

        self.download_cpd_installer()

        yaml_file_path = self.prepare_yaml_file(
            artifactory_user_name,
            artifactory_api_key,
            ibm_cloud_pak_for_data_entitlement_key,
            assembly_name,
        )

        if not self._use_dev:
            openshift_image_registry_route = (
                dg.utils.openshift.get_openshift_image_registry_default_route()
            )

            if openshift_image_registry_route == "":
                dg.utils.openshift.enable_openshift_image_registry_default_route()

        self.install_assembly(
            assembly_name,
            yaml_file_path,
            storage_class,
            **kwargs,
        )

    @staticmethod
    def is_openshift_version_in_range(
        openshift_version: semver.VersionInfo, allowed_ranges: dict
    ):
        """Returns whether the given OpenShift version is contained in one of
        the given allowed ranges


        Parameters
        ----------
        openshift_version
            OpenShift version to be checked whether it is contained in one of the
            given allowed ranges
        allowed_ranges
            allowed ranges of OpenShift versions

        Returns
        -------
        bool
            true, if the given OpenShift version is contained in one of the given
            allowed ranges
        """

        is_openshift_version_in_range = False

        for version_range in allowed_ranges:
            if ">=" in version_range and "<" in version_range:
                is_openshift_version_in_range = (
                    openshift_version.compare(version_range[">="]) >= 0
                ) and (openshift_version.compare(version_range["<"]) == -1)
            elif ">=" in version_range:
                is_openshift_version_in_range = (
                    openshift_version.compare(version_range[">="]) >= 0
                )
            elif "<" in version_range:
                is_openshift_version_in_range = (
                    openshift_version.compare(version_range["<"]) == -1
                )

            if is_openshift_version_in_range:
                break

        return is_openshift_version_in_range

    @staticmethod
    def is_openshift_version_supported(
        cloud_pak_for_data_version: semver.VersionInfo,
        openshift_version: semver.VersionInfo,
    ) -> bool:
        """Returns whether the given OpenShift version is supported by the given
        IBM Cloud Pak for Data version


        Parameters
        ----------
        cloud_pak_for_data_version
            IBM Cloud Pak for Data version
        openshift_version
            OpenShift version to be checked whether it is supported by the given IBM
            Cloud Pak for Data version

        Returns
        -------
        bool
            true, if the given OpenShift version is supported by the given IBM Cloud
            Pak for Data version
        """

        allowed_ranges = AbstractCloudPakForDataManager._cloud_pak_for_data_versions[
            str(cloud_pak_for_data_version)
        ]["required_openshift_version"]

        is_openshift_version_supported = (
            AbstractCloudPakForDataManager.is_openshift_version_in_range(
                openshift_version, allowed_ranges
            )
        )

        return is_openshift_version_supported

    def prepare_yaml_file(
        self,
        artifactory_user_name: str,
        artifactory_api_key: str,
        ibm_cloud_pak_for_data_entitlement_key: Union[str, None],
        assembly_name: str,
    ) -> pathlib.Path:
        """Prepares a YAML file for installing the assembly with the given name

        Parameters
        ----------
        artifactory_user_name
            Artifactory user name
        artifactory_api_key
            Artifactory API key
        ibm_cloud_pak_for_data_entitlement_key
            IBM Cloud Pak for Data entitlement key
        assembly_name
            name of the assembly to be installed
        """

        if self._use_dev:
            return self._prepare_yaml_file_for_development_build(
                artifactory_user_name, artifactory_api_key, assembly_name
            )
        else:
            return self._prepare_yaml_file_for_release_build(
                artifactory_user_name,
                artifactory_api_key,
                ibm_cloud_pak_for_data_entitlement_key,
                assembly_name,
            )

    @abstractmethod
    def _get_cloud_pak_for_data_version(self) -> semver.VersionInfo:
        """Returns the IBM Cloud Pak for Data version

        Returns
        -------
        semver.VersionInfo
            IBM Cloud Pak for Data version
        """

        pass

    def _prepare_yaml_file_for_development_build(
        self,
        artifactory_user_name: str,
        artifactory_api_key: str,
        assembly_name: str,
    ) -> pathlib.Path:
        """Downloads and prepares a YAML file for installing a development build
        of the assembly with the given name

        Parameters
        ----------
        artifactory_user_name
            Artifactory user name
        artifactory_api_key
            Artifactory API key
        assembly_name
            name of the assembly to be installed
        """

        url = (
            "http://icpfs1.svl.ibm.com/zen/cp4d-builds/"
            + str(self._get_cloud_pak_for_data_version())
            + "/dev/components/"
            + assembly_name
            + "/latest/repo.yaml"
        )

        yaml_content: Any = None

        with io.BytesIO() as buffer:
            file_name = dg.utils.download.download_file_into_buffer(
                urllib.parse.urlsplit(url), buffer
            )

            yaml_content = yaml.load(
                buffer.getvalue().decode("utf-8"), Loader=yaml.FullLoader
            )

        try:
            # add Artifactory credentials to YAML document
            for element in yaml_content["registry"]:
                element["apikey"] = artifactory_api_key
                element["username"] = artifactory_user_name

            # currently, cp4d-darwin cannot resolve icpfs1.svl.ibm.com to an IP
            # address
            # workaround START - TODO remove when cpd-darwin issue is fixed
            if (
                dg.utils.operating_system.get_operating_system()
                == OperatingSystem.MAC_OS
            ):
                for element in yaml_content["fileservers"]:
                    unresolved_file_server_url = element["url"]
                    resolved_url = unresolved_file_server_url.replace(
                        "icpfs1.svl.ibm.com", socket.gethostbyname("icpfs1.svl.ibm.com")
                    )

                    element["url"] = resolved_url
            # workaround END

            # save modified YAML document to a file
            file_path = pathlib.Path(tempfile.gettempdir()) / file_name

            with open(file_path, "w") as yaml_file:
                yaml.dump(
                    yaml_content,
                    yaml_file,
                )
        except yaml.YAMLError as exc:
            raise Exception(
                "Exception while adding Artifactory credentials to YAML file: "
                + str(exc)
            )

        return file_path

    def _prepare_yaml_file_for_release_build(
        self,
        artifactory_user_name: str,
        artifactory_api_key: str,
        ibm_cloud_pak_for_data_entitlement_key: Union[str, None],
        assembly_name: str,
    ) -> pathlib.Path:
        """Prepares a YAML file for installing a release build of the assembly
        with the given name

        Parameters
        ----------
        artifactory_user_name
            Artifactory user name
        artifactory_api_key
            Artifactory API key
        assembly_name
            name of the assembly to be installed
        """

        with open(
            dg.config.data_gate_configuration_manager.get_deps_directory_path()
            / f"repo-{str(self._get_cloud_pak_for_data_version())}.yaml"
        ) as repo_file:
            yaml_content = yaml.load(repo_file, Loader=yaml.FullLoader)
            yaml_content["registry"][0][
                "apikey"
            ] = ibm_cloud_pak_for_data_entitlement_key

            # Save modified YAML document to a file
            file_path = pathlib.Path(tempfile.gettempdir()) / "repo.yaml"

            with open(file_path, "w") as yaml_file:
                yaml.dump(
                    yaml_content,
                    yaml_file,
                )

            return file_path

    _cloud_pak_for_data_versions: CloudPakForDataVersions = {
        "3.0.1": {
            "assembly_versions": {
                "db2oltp": "3.0.2",
                "db2wh": "3.0.2",
            },
            "development": {
                "directory_alias": "cpd-3-0-1-dev",
                "download_url": "http://icpfs1.svl.ibm.com/zen/cp4d-builds/3.0.1/dev/installer/latest/",
            },
            "release": {
                "directory_alias": "cpd-3-0-1",
                "download_url": "https://api.github.com/repos/IBM/cpd-cli/releases",
            },
            "cpd_installer_file_name_dict": {
                OperatingSystem.LINUX_X86_64: "cpd-linux",
                OperatingSystem.MAC_OS: "cpd-darwin",
                OperatingSystem.WINDOWS: "cpd-windows.exe",
            },
            "required_openshift_version": [
                {">=": "4.3.0", "<": "4.4.0"},
                {">=": "4.5.0"},
            ],
        },
        "3.5.0": {
            "assembly_versions": {"lite": "3.5.1"},
            "development": {
                "directory_alias": "cpd-3-5-0-dev",
                "download_url": "http://icpfs1.svl.ibm.com/zen/cp4d-builds/3.5.0/dev/cpd-cli/latest/",
            },
            "release": {
                "directory_alias": "cpd-3-5-0",
                "download_url": "https://api.github.com/repos/IBM/cpd-cli/releases",
            },
            "cpd_installer_file_name_dict": {
                OperatingSystem.LINUX_X86_64: "cpd-cli",
                OperatingSystem.MAC_OS: "cpd-cli",
                OperatingSystem.WINDOWS: "cpd-cli.exe",
            },
            "required_openshift_version": [
                {">=": "4.3.0", "<": "4.4.0"},
                {">=": "4.5.0"},
            ],
        },
        "default_version": "3.5.0",
        "ibm_cloud_supported_version": "3.5.0",
    }
