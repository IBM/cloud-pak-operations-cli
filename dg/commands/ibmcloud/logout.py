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

from subprocess import CalledProcessError

import click

import dg.config

from dg.commands.ibmcloud.common import is_logged_in
from dg.lib.ibmcloud import (
    EXTERNAL_IBM_CLOUD_API_KEY_NAME,
    INTERNAL_IBM_CLOUD_API_KEY_NAME,
)
from dg.lib.ibmcloud.iam import delete_api_key_in_ibmcloud
from dg.lib.thirdparty import IBM_CLOUD_PATH, execute_ibmcloud_command


@click.command()
@click.option(
    "--delete-api-key",
    required=False,
    help="Delete the API key which was created for the Data Gate CLI (in IBM Cloud and on disk)",
    is_flag=True,
)
def logout(delete_api_key: bool):
    """Log out from IBM Cloud"""

    if delete_api_key:
        click.echo("Deleting the Data Gate API key in IBM Cloud")
        try:
            delete_api_key_in_ibmcloud()
        except CalledProcessError as error:
            if (
                f"Multiple API keys matches found with name '{EXTERNAL_IBM_CLOUD_API_KEY_NAME}'"
                in error.stderr
            ):
                raise Exception(
                    f"Multiple API keys with the name {EXTERNAL_IBM_CLOUD_API_KEY_NAME} exist. You need to manually "
                    f"delete them using '{str(IBM_CLOUD_PATH)} iam api-key-delete {EXTERNAL_IBM_CLOUD_API_KEY_NAME}'"
                )
        click.echo("Deleting the Data Gate API key on disk")
        dg.config.data_gate_configuration_manager.store_credentials(
            {INTERNAL_IBM_CLOUD_API_KEY_NAME: ""}
        )

    if is_logged_in():
        _perform_logout()
    else:
        click.echo("Not logged in, no need to logout")


def _perform_logout():
    logout_command = execute_ibmcloud_command(["logout"])
    if logout_command.returncode != 0:
        raise Exception(
            f"'ibmcloud logout' failed: {logout_command.stdout}\n{logout_command.stderr}"
        )
