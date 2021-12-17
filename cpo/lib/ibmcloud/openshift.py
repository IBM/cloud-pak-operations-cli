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

import json

from typing import Any, Optional

import semver

from cpo.lib.cloud_pak_for_data.cpd3_manager import (
    AbstractCloudPakForDataManager,
)
from cpo.lib.error import DataGateCLIException
from cpo.lib.ibmcloud import execute_ibmcloud_command


def get_full_openshift_version(openshift_version: semver.VersionInfo) -> str:
    full_openshift_version: Optional[str] = None
    ibm_cloud_supported_cloud_pak_for_data_version = AbstractCloudPakForDataManager.get_ibm_cloud_supported_version()
    version_command_result_json = _get_oc_versions_as_json()

    if version_command_result_json and "openshift" in version_command_result_json:
        for version in version_command_result_json["openshift"]:
            major = version["major"]
            minor = version["minor"]
            patch = version["patch"]

            if semver.VersionInfo.parse(f"{major}.{minor}.{patch}") == openshift_version:
                if not AbstractCloudPakForDataManager.is_openshift_version_supported(
                    ibm_cloud_supported_cloud_pak_for_data_version, openshift_version
                ):
                    raise DataGateCLIException(
                        f"OpenShift {str(openshift_version)} is not supported by IBM Cloud Pak for Data "
                        f"{str(ibm_cloud_supported_cloud_pak_for_data_version)}"
                    )

                full_openshift_version = f"{str(openshift_version)}_openshift"

                break

    if full_openshift_version is None:
        raise DataGateCLIException(f"OpenShift {str(openshift_version)} is not supported by IBM Cloud")

    return full_openshift_version


def get_latest_supported_openshift_version() -> str:
    current_openshift_version: Optional[semver.VersionInfo] = None
    ibm_cloud_supported_cloud_pak_for_data_version = AbstractCloudPakForDataManager.get_ibm_cloud_supported_version()
    version_command_result_json = _get_oc_versions_as_json()

    if version_command_result_json and "openshift" in version_command_result_json:
        for version in version_command_result_json["openshift"]:
            major = version["major"]
            minor = version["minor"]
            patch = version["patch"]
            openshift_version = semver.VersionInfo.parse(f"{major}.{minor}.{patch}")

            if AbstractCloudPakForDataManager.is_openshift_version_supported(
                ibm_cloud_supported_cloud_pak_for_data_version, openshift_version
            ) and ((current_openshift_version is None) or (openshift_version.compare(current_openshift_version) == 1)):
                current_openshift_version = openshift_version

    if current_openshift_version is None:
        raise DataGateCLIException(
            f"None of the OpenShift versions available in IBM Cloud is supported by IBM Cloud Pak for Data "
            f"{str(ibm_cloud_supported_cloud_pak_for_data_version)}:\n{version_command_result_json}"
        )

    full_openshift_version = f"{str(current_openshift_version)}_openshift"

    return full_openshift_version


def _get_oc_versions_as_json() -> Any:
    args = ["oc", "versions", "--json"]
    version_command_result = execute_ibmcloud_command(args, capture_output=True)
    version_command_result_json = json.loads(version_command_result.stdout)

    return version_command_result_json
