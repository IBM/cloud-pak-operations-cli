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

import logging

from subprocess import CalledProcessError

import click

from cpo.config import configuration_manager
from cpo.lib.dependency_manager import dependency_manager
from cpo.lib.dependency_manager.plugins.ibm_cloud_cli_plugin import (
    IBMCloudCLIPlugIn,
)
from cpo.lib.error import DataGateCLIException, IBMCloudException
from cpo.lib.ibmcloud import (
    EXTERNAL_IBM_CLOUD_API_KEY_NAME,
    INTERNAL_IBM_CLOUD_API_KEY_NAME,
    execute_ibmcloud_command_without_check,
)
from cpo.lib.ibmcloud.iam import delete_api_key_in_ibmcloud
from cpo.lib.ibmcloud.login import is_logged_in
from cpo.utils.logging import loglevel_command

logger = logging.getLogger(__name__)


@loglevel_command()
@click.option(
    "--delete-api-key",
    help="Delete the API key which was created for the IBM Cloud Pak Operations CLI (in IBM Cloud and on disk)",
    is_flag=True,
)
def logout(delete_api_key: bool):
    """Log out from IBM Cloud"""

    if delete_api_key:
        logger.info("Deleting the Data Gate API key in IBM Cloud")

        try:
            delete_api_key_in_ibmcloud()
        except CalledProcessError as error:
            if f"Multiple API keys matches found with name '{EXTERNAL_IBM_CLOUD_API_KEY_NAME}'" in error.stderr:
                raise DataGateCLIException(
                    f"Multiple API keys with the name {EXTERNAL_IBM_CLOUD_API_KEY_NAME} exist. You need to manually "
                    f"delete them using '{dependency_manager.get_binary_path(IBMCloudCLIPlugIn)} iam "
                    f"api-key-delete {EXTERNAL_IBM_CLOUD_API_KEY_NAME}'"
                )

        logger.info("Deleting the Data Gate API key on disk")
        configuration_manager.store_credentials({INTERNAL_IBM_CLOUD_API_KEY_NAME: ""})

    if is_logged_in():
        _perform_logout()


def _perform_logout():
    logout_command = execute_ibmcloud_command_without_check(["logout"], capture_output=True)

    if logout_command.return_code != 0:
        raise IBMCloudException("'ibmcloud logout' failed", logout_command.stderr)
