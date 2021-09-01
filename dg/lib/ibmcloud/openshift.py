import json

from typing import Any, Optional

import semver

from dg.lib.cloud_pak_for_data.cpd3_manager import (
    AbstractCloudPakForDataManager,
)
from dg.lib.error import DataGateCLIException
from dg.lib.ibmcloud import execute_ibmcloud_command


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
