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

from typing import Final, Union

import click
import requests

import dg.config
import dg.utils.network

from dg.lib.error import DataGateCLIException
from dg.utils.logging import loglevel_command

IBM_FYRE_SHOW_CLUSTERS_URL: Final[str] = "https://api.fyre.ibm.com/rest/v1/?operation=query&request=showclusters"


@loglevel_command()
@click.option("--fyre-api-key", required=True, help="FYRE API key")
@click.option("--fyre-user-name", required=True, help="FYRE user name")
def login(
    fyre_api_key: Union[str, None],
    fyre_user_name: Union[str, None],
):
    """Log in to FYRE"""

    credentials_to_be_stored = locals().copy()

    dg.utils.network.disable_insecure_request_warning()

    response = requests.post(
        IBM_FYRE_SHOW_CLUSTERS_URL,
        auth=(fyre_user_name, fyre_api_key),
        verify=False,
    )

    if not response.ok:
        raise DataGateCLIException("Failed to log in to FYRE (HTTP status code: {})".format(response.status_code))

    dg.config.data_gate_configuration_manager.store_credentials(credentials_to_be_stored)
