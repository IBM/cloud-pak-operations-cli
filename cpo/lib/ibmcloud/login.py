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

import click

import cpo.config
import cpo.lib.ibmcloud.plugin_manager

from cpo.lib.error import DataGateCLIException, IBMCloudException
from cpo.lib.ibmcloud import (
    INTERNAL_IBM_CLOUD_API_KEY_NAME,
    execute_ibmcloud_command_interactively,
    execute_ibmcloud_command_without_check,
)
from cpo.lib.ibmcloud.iam import generate_api_key
from cpo.lib.ibmcloud.target import get_ibmcloud_account_target_information


def is_logged_in() -> bool:
    target_information = get_ibmcloud_account_target_information()
    login_status = target_information and "user" in target_information

    return login_status


def is_logged_in_and_print_help_message_if_not():
    if not is_logged_in():
        click.echo(
            (
                "It seems you're not logged in to the IBM cloud CLI. Please execute `cpo ibmcloud login` (interactive) "
                "and afterwards re-run the current command."
            )
        )


def login():
    """Log in to IBM Cloud"""

    _disable_update_notifications()

    api_key = cpo.config.configuration_manager.get_value_from_credentials_file(INTERNAL_IBM_CLOUD_API_KEY_NAME)

    if api_key is not None:
        # implicit login using $HOME/.cpo/credentials.json
        _login_using_api_key(api_key)
    else:
        # if not available: interactive login
        _login_interactively()
        generate_and_save_api_key()

    cpo.lib.ibmcloud.plugin_manager.PlugInManager().install_required_plug_ins()


def _login_using_api_key(apikey: str):
    login_command = execute_ibmcloud_command_without_check(
        ["login", "--apikey", apikey, "--no-region"], capture_output=True
    )

    if login_command.return_code != 0:
        raise DataGateCLIException(f"Login to IBM Cloud using the given API key failed:\n{login_command.stdout}")
    else:
        click.echo(login_command.stdout)


def _login_interactively():
    login_command_return_code = execute_ibmcloud_command_interactively(["login", "--no-region", "--sso"])

    if login_command_return_code != 0:
        raise DataGateCLIException("Interactive login to IBM Cloud failed.")


def _disable_update_notifications():
    """Disables IBM Cloud CLI version check when setting API endpoint or
    logging in.

    Some commands will hang or skip with return code 0 if there is a pending
    version update for the IBM Cloud CLI.

    ibmcloud config --check-version=false disables this behavior"""

    disable_command = execute_ibmcloud_command_without_check(["config", "--check-version=false"], capture_output=True)

    if disable_command.return_code != 0:
        raise IBMCloudException(
            "Disabling IBM Cloud CLI update notifications failed",
            disable_command.stderr,
        )


def generate_and_save_api_key():
    api_key = generate_api_key()

    cpo.config.configuration_manager.store_credentials({INTERNAL_IBM_CLOUD_API_KEY_NAME: api_key})
