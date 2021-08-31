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

import dg.lib.ibmcloud.iam

from dg.config import data_gate_configuration_manager
from dg.lib.error import DataGateCLIException
from dg.lib.ibmcloud import (
    EXTERNAL_IBM_CLOUD_API_KEY_NAME,
    INTERNAL_IBM_CLOUD_API_KEY_NAME,
)
from dg.lib.ibmcloud.iam import api_key_exists, delete_api_key_in_ibmcloud
from dg.utils.logging import loglevel_command


@loglevel_command()
@click.option(
    "--delete-existing-api-key",
    help=(
        "Delete the API key created for the Db2 Data Gate CLI (in IBM Cloud and on disk) prior to generating a new one"
    ),
    is_flag=True,
)
def generate_api_key(delete_existing_api_key: bool) -> str:
    """Generates an IBM Cloud API key and stores it in the Db2 Data Gate CLI
    credentials file"""

    if delete_existing_api_key:
        if api_key_exists(EXTERNAL_IBM_CLOUD_API_KEY_NAME):
            try:
                delete_api_key_in_ibmcloud()
            except CalledProcessError as error:
                if f"Multiple API keys matches found with name '{EXTERNAL_IBM_CLOUD_API_KEY_NAME}'" in error.stderr:
                    raise DataGateCLIException(
                        f"Multiple API keys with the name {EXTERNAL_IBM_CLOUD_API_KEY_NAME} exist. You need to "
                        f"manually delete them using '{str(data_gate_configuration_manager.get_ibmcloud_cli_path())} "
                        f"iam api-key-delete {EXTERNAL_IBM_CLOUD_API_KEY_NAME}'"
                    )

        data_gate_configuration_manager.store_credentials({INTERNAL_IBM_CLOUD_API_KEY_NAME: ""})

    api_key = dg.lib.ibmcloud.iam.generate_api_key()

    data_gate_configuration_manager.store_credentials({INTERNAL_IBM_CLOUD_API_KEY_NAME: api_key})

    return api_key
