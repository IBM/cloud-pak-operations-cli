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

import click

import dg.config

from dg.lib.ibmcloud import INTERNAL_IBM_CLOUD_API_KEY_NAME
from dg.lib.ibmcloud.iam import generate_api_key
from dg.lib.ibmcloud.plugin import (
    install_catalogs_management_plugin,
    install_container_service_plugin,
    is_catalogs_management_plugin_installed,
    is_container_service_plugin_installed,
)
from dg.lib.thirdparty import (
    execute_ibmcloud_command,
    execute_ibmcloud_command_interactively,
)


def login():
    """Log in to IBM Cloud"""

    _disable_update_notifications()

    api_key = dg.config.data_gate_configuration_manager.get_value_from_credentials_file(
        INTERNAL_IBM_CLOUD_API_KEY_NAME
    )

    if api_key is not None:
        # implicit login using $HOME/.dg/credentials.json
        _login_using_api_key(api_key)
    else:
        # if not available: interactive login
        _login_interactively()
        generate_and_save_api_key()

    if not is_catalogs_management_plugin_installed():
        install_catalogs_management_plugin()

    if not is_container_service_plugin_installed():
        install_container_service_plugin()


def _login_using_api_key(apikey: str):
    login_command = execute_ibmcloud_command(
        ["login", "--apikey", apikey, "--no-region"]
    )

    if login_command.returncode != 0:
        raise Exception(
            f"Login to IBM Cloud using the given API key failed:\n{login_command.stdout}"
        )
    else:
        click.echo(login_command.stdout)


def _login_interactively():
    login_command_return_code = execute_ibmcloud_command_interactively(
        ["login", "--no-region", "--sso"]
    )

    if login_command_return_code != 0:
        raise Exception("Interactive login to IBM Cloud failed.")


def _disable_update_notifications():
    """Disables IBM Cloud CLI version check when setting API endpoint or
    logging in.

    Some commands will hang or skip with return code 0 if there is a pending
    version update for the IBM Cloud CLI.

    ibmcloud config --check-version=false disables this behavior"""

    disable_command = execute_ibmcloud_command(["config", "--check-version=false"])

    if disable_command.returncode != 0:
        raise Exception(
            f"Disabling IBM Cloud CLI update notifications failed:\n{disable_command.stdout}"
        )


def generate_and_save_api_key():
    api_key = generate_api_key()

    dg.config.data_gate_configuration_manager.store_credentials(
        {INTERNAL_IBM_CLOUD_API_KEY_NAME: api_key}
    )
