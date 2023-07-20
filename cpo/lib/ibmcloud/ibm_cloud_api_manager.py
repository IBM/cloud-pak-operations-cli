#  Copyright 2022, 2023 IBM Corporation
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
import os
import re as regex
import subprocess

from dataclasses import dataclass
from typing import Any, Final, Optional

import cpo.utils.process

from cpo.config import configuration_manager
from cpo.config.cluster_credentials_manager import cluster_credentials_manager
from cpo.lib.dependency_manager import dependency_manager
from cpo.lib.dependency_manager.plugins.ibm_cloud_cli_plugin import IBMCloudCLIPlugIn
from cpo.lib.ibmcloud import (
    EXTERNAL_IBM_CLOUD_API_KEY_NAME,
    INTERNAL_KEY_NAME_FOR_IBM_CLOUD_API_KEY,
    INTERNAL_KEY_NAME_FOR_IBM_CLOUD_API_KEY_ID,
)
from cpo.lib.ibmcloud.data.cluster_status import ClusterStatus
from cpo.lib.ibmcloud.data.ingress_status import IngressStatus
from cpo.utils.error import CloudPakOperationsCLIException, IBMCloudException


@dataclass
class IBMCloudAPIKey:
    api_key: str
    api_key_id: str


class IBMCloudAPIManager:
    """Manages communication with the IBM Cloud CLI"""

    def api_key_exists_in_ibm_cloud(self, ibm_cloud_api_key_id: str) -> bool:
        """Check if the IBM Cloud API key with the given ID exists

        Parameters
        ----------
        ibm_cloud_api_key_id
            ID of the IBM Cloud API key to be checked

        Returns
        -------
        bool
            true, if the IBM Cloud API key with the given ID exists
        """

        api_keys = self.get_api_keys()
        result = False

        if api_keys:
            for api_key in api_keys:
                if api_key["id"] == ibm_cloud_api_key_id:
                    result = True

                    break

        return result

    def delete_api_key_in_ibm_cloud(self, ibm_cloud_api_key_id: str):
        """Deletes the IBM Cloud API key with the given ID

        Parameters
        ----------
        ibm_cloud_api_key_id
            ID of the IBM Cloud API key to be deleted
        """

        self.execute_ibmcloud_command(
            [
                "iam",
                "api-key-delete",
                ibm_cloud_api_key_id,
                "--force",
            ]
        )

    def delete_api_key_in_ibm_cloud_and_on_disk(self):
        """Deletes the current IBM Cloud API key in IBM Cloud and on disk"""

        ibm_cloud_api_key = configuration_manager.get_value_from_credentials_file(
            INTERNAL_KEY_NAME_FOR_IBM_CLOUD_API_KEY
        )

        if ibm_cloud_api_key is None:
            raise CloudPakOperationsCLIException("IBM Cloud API key not found in credentials file")

        ibm_cloud_api_key_id = configuration_manager.get_value_from_credentials_file(
            INTERNAL_KEY_NAME_FOR_IBM_CLOUD_API_KEY_ID
        )

        if ibm_cloud_api_key_id is None:
            raise CloudPakOperationsCLIException("IBM Cloud API key ID not found in credentials file")

        self.delete_api_key_in_ibm_cloud(ibm_cloud_api_key_id)
        configuration_manager.store_credentials(
            {INTERNAL_KEY_NAME_FOR_IBM_CLOUD_API_KEY: "", INTERNAL_KEY_NAME_FOR_IBM_CLOUD_API_KEY_ID: ""}
        )

    def delete_cluster(self, name: str):
        """Deletes the Red Hat OpenShift on IBM Cloud cluster with the given
        name

        Parameters
        ----------
        name
            name of the Red Hat OpenShift on IBM Cloud cluster to be deleted
        """

        server = self.get_cluster_status(name).get_server_url()
        result = self.execute_ibmcloud_command_without_check(
            ["oc", "cluster", "rm", "--cluster", name, "--force-delete-storage", "-f"], capture_output=True
        )

        if result.return_code != 0:
            raise IBMCloudException("An error occurred while deleting the cluster", result.stderr)

        cluster = cluster_credentials_manager.get_cluster(server)

        if cluster is not None:
            cluster_credentials_manager.remove_cluster(server)

    def disable_update_notifications(self):
        """Disables the IBM Cloud CLI version check when setting an API endpoint
        or logging in.

        Some commands start hanging or are skipped with return code 0 if there
        is a pending version update for the IBM Cloud CLI.

        ibmcloud config --check-version=false disables this behavior
        """

        self._execute_ibmcloud_command(["config", "--check-version=false"], capture_output=True)

    def execute_ibmcloud_command(
        self, args: list[str], capture_output=False, check=True, print_captured_output=False, skip_login=False
    ) -> cpo.utils.process.ProcessResult:
        """Executes the IBM Cloud CLI

        Parameters
        ----------
        args
            arguments to be passed to the IBM Cloud CLI
        capture_output
            flag indicating whether process output shall be captured
        check
            flag indicating whether an exception shall be thrown if the IBM Cloud
            CLI returns with a nonzero return code
        print_captured_output
            flag indicating whether captured process output shall also be written to
            stdout/stderr
        skip_login
            flag indicating whether logging in to IBM Cloud shall be skipped

        Returns
        -------
        ProcessResult
            object storing the return code and captured process output (if
            requested)
        """

        api_key = configuration_manager.get_value_from_credentials_file(INTERNAL_KEY_NAME_FOR_IBM_CLOUD_API_KEY)

        if not skip_login:
            if api_key is None:
                raise CloudPakOperationsCLIException("IBM Cloud API key not found (use 'cpo ibmcloud login')")

            if not self.is_logged_in():
                self.log_in_using_api_key(api_key)

        result = self._execute_ibmcloud_command_without_check(
            args, capture_output=capture_output, print_captured_output=print_captured_output
        )

        if result.return_code != 0:
            if (
                regex.match(IBMCloudAPIManager._IBMCLOUD_CLI_ERROR_OAUTH_TOKEN_EXPIRED_ERROR_MESSAGE, result.stderr)
                is not None
            ) and not skip_login:
                self.log_in_using_api_key(api_key)

                result = self._execute_ibmcloud_command(
                    args, capture_output=capture_output, check=check, print_captured_output=print_captured_output
                )
            else:
                result.raise_for_status()

        return result

    def execute_ibmcloud_command_without_check(
        self, args: list[str], capture_output=False, print_captured_output=False
    ) -> cpo.utils.process.ProcessResult:
        """Executes the IBM Cloud CLI without checking its return code

        Parameters
        ----------
        args
            arguments to be passed to the IBM Cloud CLI
        capture_output
            flag indicating whether process output shall be captured
        print_captured_output
            flag indicating whether captured process output shall also be written to
            stdout/stderr

        Returns
        -------
        ProcessResult
            object storing the return code and captured process output (if
            requested)
        """

        return self.execute_ibmcloud_command(
            args,
            capture_output=capture_output,
            check=False,
            print_captured_output=print_captured_output,
        )

    def generate_api_key(self, skip_login=False) -> IBMCloudAPIKey:
        """Generates an IBM Cloud API key

        Parameters
        ----------
        skip_login
            flag indicating whether logging in to IBM Cloud shall be skipped

        Returns
        -------
        IBMCloudAPIKey
            object storing the IBM Cloud API key and the IBM Cloud API key ID
        """

        result = self.execute_ibmcloud_command(
            [
                "iam",
                "api-key-create",
                EXTERNAL_IBM_CLOUD_API_KEY_NAME,
                "--output",
                "json",
            ],
            capture_output=True,
            skip_login=skip_login,
        )

        json_result = json.loads(result.stdout)

        return IBMCloudAPIKey(json_result["apikey"], json_result["id"])

    def get_cluster_status(self, cluster_name: str) -> ClusterStatus:
        """Returns the status of the cluster with the given name

        Parameters
        ----------
        cluster_name
            name of the cluster whose status shall be returned

        Returns
        -------
        ClusterStatus
            status of the cluster with the given name
        """

        args = ["oc", "cluster", "get", "--cluster", cluster_name, "--json"]
        command_result = self.execute_ibmcloud_command(args, capture_output=True)

        try:
            status = ClusterStatus(json.loads(command_result.stdout))

            return status
        except json.JSONDecodeError as exception:
            command_string = "ibmcloud " + " ".join(args)

            raise CloudPakOperationsCLIException(
                f"Invalid JSON received from command {command_string}:\n{command_result.stdout}"
            ) from exception

    def get_ingress_status(self, cluster_name: str) -> IngressStatus:
        """Returns the status of Ingress components of the cluster with the
        given name

        Parameters
        ----------
        cluster_name
            name of the cluster whose status of Ingress components shall be returned

        Returns
        -------
        IngressStatus
            status of Ingress components of the cluster with the given name
        """

        args = ["ks", "ingress", "status", "--cluster", cluster_name, "--json"]
        command_result = self.execute_ibmcloud_command(args, capture_output=True)

        try:
            status = IngressStatus(json.loads(command_result.stdout))

            return status
        except json.JSONDecodeError as exception:
            command_string = "ibmcloud " + " ".join(args)

            raise CloudPakOperationsCLIException(
                f"Invalid JSON received from command {command_string}:\n{command_result.stdout}"
            ) from exception

    def regenerate_api_key(self):
        """Deletes the current IBM Cloud API key and generates a new one"""

        new_api_key = self.generate_api_key()

        self.delete_api_key_in_ibm_cloud_and_on_disk()
        self.save_api_key(new_api_key)

    def get_api_keys(self) -> Any:
        """Returns IBM Cloud API keys

        Returns
        -------
        Any
            IBM Cloud API keys
        """

        result = self.execute_ibmcloud_command(["iam", "api-keys", "--output", "json"], capture_output=True)

        return json.loads(result.stdout)

    def is_logged_in(self) -> bool:
        """Returns whether an OAuth token for the IBM Cloud API exists

        Returns
        -------
        bool
            true, if an OAuth token for the IBM Cloud API exists
        """

        ibmcloud_config_file_contents = self._read_ibmcloud_config_file_contents()

        if ibmcloud_config_file_contents is None:
            return False

        return (
            "IAMToken" in ibmcloud_config_file_contents
            and ibmcloud_config_file_contents["IAMToken"] != ""
            and "IAMRefreshToken" in ibmcloud_config_file_contents
            and ibmcloud_config_file_contents["IAMRefreshToken"] != ""
        )

    def log_in(self):
        """Log in to IBM Cloud"""

        self.disable_update_notifications()

        api_key = configuration_manager.get_value_from_credentials_file(INTERNAL_KEY_NAME_FOR_IBM_CLOUD_API_KEY)

        if api_key is not None:
            # implicit login using $HOME/.cpo/credentials.json
            self.log_in_using_api_key(api_key)
        else:
            # if not available: interactive login
            self.log_in_interactively()

            api_key = self.generate_api_key(skip_login=True)

            self.save_api_key(api_key)

        PlugInManager(self).install_required_plug_ins()

    def log_in_interactively(self):
        """Log in to IBM Cloud interactively"""

        login_command_return_code = self._execute_ibmcloud_command_interactively(["login", "--no-region", "--sso"])

        if login_command_return_code != 0:
            raise CloudPakOperationsCLIException("Interactive login to IBM Cloud failed.")

    def log_in_using_api_key(self, api_key: Optional[str] = None):
        """Log in to IBM Cloud using the given IBM Cloud API key

        Parameters
        ----------
        api_key
            IBM Cloud API key
        """

        if api_key is None:
            api_key = configuration_manager.get_value_from_credentials_file(INTERNAL_KEY_NAME_FOR_IBM_CLOUD_API_KEY)

            if api_key is None:
                raise CloudPakOperationsCLIException("IBM Cloud API key not found in credentials file")

        self._execute_ibmcloud_command(["login", "--apikey", api_key, "--no-region"], capture_output=True)

    def log_out(self):
        """Log out from IBM Cloud"""

        if self.is_logged_in():
            self.execute_ibmcloud_command(["logout"], capture_output=True, skip_login=True)

    def save_api_key(self, api_key: IBMCloudAPIKey):
        """Store the given IBM Cloud API key in the configuration

        Parameters
        ----------
        api_key
            IBM Cloud API key to be stored in the configuration
        """

        configuration_manager.store_credentials(
            {
                INTERNAL_KEY_NAME_FOR_IBM_CLOUD_API_KEY: api_key.api_key,
                INTERNAL_KEY_NAME_FOR_IBM_CLOUD_API_KEY_ID: api_key.api_key_id,
            }
        )

    def _execute_ibmcloud_command(
        self, args: list[str], capture_output=False, check=True, print_captured_output=False
    ) -> cpo.utils.process.ProcessResult:
        """Executes the IBM Cloud CLI

        Parameters
        ----------
        args
            arguments to be passed to the IBM Cloud CLI
        capture_output
            flag indicating whether process output shall be captured
        check
            flag indicating whether an exception shall be thrown if the IBM Cloud
            CLI returns with a nonzero return code
        print_captured_output
            flag indicating whether captured process output shall also be written to
            stdout/stderr

        Returns
        -------
        ProcessResult
            object storing the return code and captured process output (if
            requested)
        """

        env = os.environ.copy()
        env["IBMCLOUD_HOME"] = str(configuration_manager.get_cli_data_directory_path())

        return dependency_manager.execute_binary(
            IBMCloudCLIPlugIn,
            args,
            env,
            capture_output=capture_output,
            check=check,
            print_captured_output=print_captured_output,
        )

    def _execute_ibmcloud_command_interactively(self, args: list[str]) -> int:
        command = [str(dependency_manager.get_binary_path(IBMCloudCLIPlugIn))] + args

        logging.debug(f"Executing command: {' '.join(command)}")

        env = os.environ.copy()
        env["IBMCLOUD_HOME"] = str(configuration_manager.get_cli_data_directory_path())

        proc = subprocess.Popen(command, env=env)
        proc.communicate()

        return proc.returncode

    def _execute_ibmcloud_command_without_check(
        self, args: list[str], capture_output=False, print_captured_output=False
    ) -> cpo.utils.process.ProcessResult:
        """Executes the IBM Cloud CLI without checking its return code

        Parameters
        ----------
        args
            arguments to be passed to the IBM Cloud CLI
        capture_output
            flag indicating whether process output shall be captured
        print_captured_output
            flag indicating whether captured process output shall also be written to
            stdout/stderr

        Returns
        -------
        ProcessResult
            object storing the return code and captured process output (if
            requested)
        """

        return self._execute_ibmcloud_command(
            args,
            capture_output=capture_output,
            check=False,
            print_captured_output=print_captured_output,
        )

    def _read_ibmcloud_config_file_contents(self) -> Optional[Any]:
        """Returns the contents of the credentials file

        Returns
        -------
            Optional[str]
                contents of the credentials file or None if the credentials file does
                not exist or is empty
        """

        ibmcloud_config_file_path = configuration_manager.get_ibmcloud_data_directory_path() / "config.json"
        result: Optional[str] = None

        if ibmcloud_config_file_path.exists() and (ibmcloud_config_file_path.stat().st_size != 0):
            with open(ibmcloud_config_file_path) as json_file:
                result = json.load(json_file)

        return result

    _IBMCLOUD_CLI_ERROR_OAUTH_TOKEN_EXPIRED_ERROR_MESSAGE: Final[
        str
    ] = "FAILED\nClassic: Login token is expired. Please update tokens using 'ibmcloud login' and try again.*"


class PlugInManager:
    """Manages IBM Cloud CLI plug-ins"""

    def __init__(self, ibm_cloud_api_manager: IBMCloudAPIManager):
        self._ibm_cloud_api_manager = ibm_cloud_api_manager
        self.refresh()

    def install_required_plug_ins(self):
        self._install_plugin("catalogs-management")
        self._install_plugin("container-service")

    def refresh(self):
        self._plug_ins = self._get_plug_ins()

    def _get_plug_ins(self) -> list[str]:
        ibmcloud_plugin_list_command_args = ["plugin", "list", "--output", "json"]
        ibmcloud_plugin_list_command_result = self._ibm_cloud_api_manager.execute_ibmcloud_command(
            ibmcloud_plugin_list_command_args, capture_output=True
        )

        ibmcloud_plugin_list_command_result_json = json.loads(ibmcloud_plugin_list_command_result.stdout)
        plug_ins: list[str] = []

        for plugin in ibmcloud_plugin_list_command_result_json:
            if "Name" in plugin:
                plug_ins.append(plugin["Name"])

        return plug_ins

    def _install_plugin(self, plug_in_name: str):
        if plug_in_name not in self._plug_ins:
            logging.info(f"Installing IBM Cloud plug-in '{plug_in_name}'")

            ibmcloud_plugin_install_command_args = ["plugin", "install", plug_in_name]
            ibmcloud_plugin_install_command_result = self._ibm_cloud_api_manager.execute_ibmcloud_command_without_check(
                ibmcloud_plugin_install_command_args, capture_output=True
            )

            if ibmcloud_plugin_install_command_result.return_code != 0:
                raise IBMCloudException(
                    f"An error occurred when attempting to install IBM Cloud CLI plug-in {plug_in_name}",
                    ibmcloud_plugin_install_command_result.stderr,
                )
