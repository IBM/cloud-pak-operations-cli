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

import json
import logging

from time import sleep
from typing import Any

import click
import requests

from tqdm import tqdm

import cpo.config
import cpo.utils.logging

from cpo.lib.cloud_pak_for_data.cpd3_manager import (
    AbstractCloudPakForDataManager,
)
from cpo.lib.error import DataGateCLIException, IBMCloudException
from cpo.lib.ibmcloud import (
    INTERNAL_IBM_CLOUD_API_KEY_NAME,
    execute_ibmcloud_command,
)
from cpo.lib.ibmcloud.iam import get_oauth_token, get_tokens
from cpo.lib.ibmcloud.login import is_logged_in
from cpo.lib.ibmcloud.target import get_ibmcloud_account_target_information
from cpo.utils.wait import wait_for

logger = logging.getLogger(__name__)


def _get_cp4d_version_locator(cp4d_version: str) -> str:
    cp4d_identifier = "Cloud Pak for Data"

    catalog_search_result = execute_ibmcloud_command(
        [
            "catalog",
            "search",
            cp4d_identifier,
            "--output",
            "json",
            "--type",
            "software",
        ],
        capture_output=True,
    )
    offerings = json.loads(catalog_search_result.stdout)

    catalog_id = ""
    version = ""

    if offerings:
        for offering in offerings:
            if offering["label"] == cp4d_identifier:
                # we found Cloud Pak for Data, now iterate over available versions to find the right one
                catalog_id = offering["catalog_id"]
                for kind in offering["kinds"]:
                    for version in kind["versions"]:
                        if version["version"] == cp4d_version:
                            version = version["id"]
                            break
    else:
        raise IBMCloudException("Unable to retrieve version locator", catalog_search_result.stderr)

    version_locator = catalog_id + "." + version
    return version_locator


def execute_preinstall(cluster_id: str):
    version_locator = _get_cp4d_version_locator(str(AbstractCloudPakForDataManager.get_ibm_cloud_supported_version()))

    execute_ibmcloud_command(
        [
            "catalog",
            "offering",
            "preinstall",
            "--cluster",
            cluster_id,
            "--namespace",
            "zen",
            "--version-locator",
            version_locator,
        ]
    )


def _get_entitlement_key(api_key: str) -> str:
    result = ""

    if api_key is not None:
        entitlement_name = "IBM Cloud Pak for Data"

        token = get_tokens(api_key)
        auth_token = token["token_type"] + " " + token["access_token"]

        url = "https://billing.cloud.ibm.com/v1/licensing/entitlements"
        headers = {
            "Authorization": auth_token,
            "Accept": "application/json",
        }

        response = requests.get(url, headers=headers)

        if response.ok:
            resources = response.json()["resources"]
            for resource in resources:
                if entitlement_name in resource["name"]:
                    result = resource["apikey"]
                    break
        else:
            raise DataGateCLIException(
                f"Failed to retrieve Cloud Pak for Data entitlement key (HTTP status code: {response.status_code})"
            )
    else:
        raise DataGateCLIException("Unable to retrieve IBM Cloud API key")

    return result


def execute_install(cluster_id: str, api_key: str) -> Any:
    version_locator = _get_cp4d_version_locator(str(AbstractCloudPakForDataManager.get_ibm_cloud_supported_version()))

    token = get_tokens(api_key)
    auth_token = token["token_type"] + " " + token["access_token"]
    refresh_token = token["refresh_token"]
    target_information = get_ibmcloud_account_target_information()
    account_id = target_information["account"]["guid"]
    resource_group = "Default"
    entitlement_key = _get_entitlement_key(api_key)

    url = "https://cm.globalcatalog.cloud.ibm.com/api/v1-beta/versions/" + version_locator + "/install"
    headers = {
        "Accept": "application/json",
        "Authorization": auth_token,
        "X-Auth-Refresh-Token": refresh_token,
        "X-Auth-Resource-Account": account_id,
        "X-Auth-Resource-Group": resource_group,
    }
    data = {
        "cluster_id": cluster_id,
        "entitlement_apikey": entitlement_key,
        "namespace": "zen",
        "override_values": {
            "db2wh": "true",
            "datagate": "true",
            "storage": "ibmc-file-gold-gid",
        },
        "region": "sjc03",
        "version_locator_id": version_locator,
    }

    response = requests.post(url, headers=headers, json=data)

    if response.ok:
        logging.info("Installation request submitted successfully")
    else:
        raise DataGateCLIException(
            f"Failed to start Cloud Pak for Data installation on cluster {cluster_id}:\n"
            f"HTTP status code: {response.status_code}\n"
            f"HTTP response: {response.text}"
        )

    return response.json()


def get_schematics_workspace_details(install_details: Any) -> Any:
    result = ""

    if install_details is None or "workspace_id" not in install_details:
        raise DataGateCLIException("Unable to retrieve IBM Schematics workspace details")

    workspace_id = install_details["workspace_id"]
    auth_token = get_oauth_token()

    url = "https://schematics.cloud.ibm.com/v1/workspaces/" + workspace_id
    headers = {"Authorization": auth_token}

    response = requests.get(url, headers=headers)

    if response.ok:
        result = response.json()
    else:
        raise DataGateCLIException(
            f"Failed to get Cloud Pak for Data installation details for IBM Schematics workspace ID {workspace_id}:\n"
            f"HTTP status code: {response.status_code}\n"
            f"HTTP response: {response.text}"
        )

    return result


def get_install_status(install_details: Any) -> str:
    return get_schematics_workspace_details(install_details)["status"]


def is_installation_finished(install_details: Any) -> bool:
    status = get_install_status(install_details)

    if status == "FAILED":
        raise DataGateCLIException(f"Workspace '{install_details['workspace_id']}' is in status '{status}'")

    return status == "ACTIVE"


def wait_until_installation_is_finished(install_details: Any) -> None:
    try:
        with cpo.utils.logging.ScopedLoggingDisabler():
            wait_for(
                3600,
                30,
                "Cloud Pak for Data installation",
                is_installation_finished,
                install_details,
            )
    except Exception:
        raise DataGateCLIException(
            f"Timeout exceeded or workspace error, details can be found here: "
            f"https://cloud.ibm.com/schematics/workspaces/{install_details['workspace_id']}/activity"
        )


def wait_until_preinstallation_is_finished(interval: int, timeout: int) -> None:
    """Wait until the preinstallation is finished.

    This function will be obsolete as soon as 'ibmcloud preinstall-status' is
    working correctly.
    """

    progress_bar = tqdm(
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
        total=timeout,
    )

    time_passed = 0

    while time_passed < timeout:
        sleep(interval)
        time_passed += interval
        progress_bar.update(interval)

    progress_bar.close()


def get_installation_log(install_details: Any) -> str:
    result = ""

    try:
        log_path = get_schematics_workspace_details(install_details)["runtime_data"][0]["log_store_url"]
    except Exception:
        raise DataGateCLIException("Unable to retrieve log path value for IBM Schematics workspace")

    if install_details is None or "workspace_id" not in install_details or (log_path == ""):
        raise DataGateCLIException("Unable to retrieve IBM Schematics log path")

    workspace_id = install_details["workspace_id"]
    auth_token = get_oauth_token()

    url = log_path
    headers = {"Authorization": auth_token}

    response = requests.get(url, headers=headers)

    if response.ok:
        result = response.text
    else:
        raise DataGateCLIException(
            f"Failed to get Cloud Pak for Data installation log for workspace ID {workspace_id}:\n"
            f"HTTP status code: {response.status_code}\n"
            f"HTTP response: {response.text}"
        )

    return result


def get_workspace_output_values(install_details: Any) -> Any:
    result = ""

    if install_details is None or "workspace_id" not in install_details:
        raise DataGateCLIException("Unable to retrieve IBM Schematics workspace output values")

    workspace_id = install_details["workspace_id"]
    auth_token = get_oauth_token()

    url = "https://schematics.cloud.ibm.com/v1/workspaces/" + workspace_id + "/output_values"
    headers = {"Authorization": auth_token}

    response = requests.get(url, headers=headers)

    if response.ok:
        result = response.json()
    else:
        raise DataGateCLIException(
            f"Failed to get IBM Schematics output values for workspace ID {workspace_id}:\n"
            f"HTTP status code: {response.status_code}\n"
            f"HTTP response: {response.text}"
        )

    return result


def get_cp4d_url(install_details: Any) -> str:
    resource_controller_url = ""

    workspace_output_values = get_workspace_output_values(install_details)

    if workspace_output_values:
        try:
            resource_controller_url = workspace_output_values[0]["output_values"][0]["resource_cloud"]["value"][
                "resource_controller_url"
            ]
        except Exception:
            raise DataGateCLIException(
                f"Unable to retrieve Cloud Pak for Data URL. Details:\n{workspace_output_values}"
            )

    return resource_controller_url


def install_cp4d_with_preinstall(cluster_name: str):
    """Install Cloud Pak for Data, including Db2 Warehouse and Db2 Data Gate, on the given IBM Cloud cluster"""

    api_key = cpo.config.configuration_manager.get_value_from_credentials_file(INTERNAL_IBM_CLOUD_API_KEY_NAME)

    if not is_logged_in() or api_key is None:
        credentials_file_path = cpo.config.configuration_manager.get_credentials_file_path()

        raise DataGateCLIException(
            f"Not logged in to IBM Cloud or no API key found in {credentials_file_path}. Please run 'cpo ibmcloud "
            f"login' to log in."
        )

    logging.info(f"Executing Cloud Pak for Data pre-installation on cluster {cluster_name}")
    execute_preinstall(cluster_name)

    # TODO Use proper endpoint to obtain preinstall status (Current function in ibmcloud CLI is not working)
    logging.info(
        click.style(
            f"Waiting for preinstallation on cluster {cluster_name} to finish:",
            bold=True,
        )
    )

    wait_until_preinstallation_is_finished(1, 300)

    logging.info(f"Executing Cloud Pak for Data installation on cluster {cluster_name}")
    install_details = execute_install(cluster_name, api_key)

    logging.info(f"Waiting for installation on cluster {cluster_name} to finish:")
    wait_until_installation_is_finished(install_details)

    url = get_cp4d_url(install_details)
    logging.info(f"Cloud Pak for Data URL: {url}")
