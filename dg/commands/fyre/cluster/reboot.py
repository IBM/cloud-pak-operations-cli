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

import json

from typing import Final

import click
import requests

import dg.config
import dg.lib.click
import dg.utils.network

from dg.lib.error import DataGateCLIException
from dg.utils.logging import loglevel_command

IBM_FYRE_REBOOT_CLUSTER_URL: Final[
    str
] = "https://api.fyre.ibm.com/rest/v1/?operation=reboot"


@loglevel_command(
    context_settings=dg.lib.click.create_default_map_from_json_file(
        dg.config.data_gate_configuration_manager.get_dg_credentials_file_path()
    )
)
@click.option(
    "--cluster-name",
    required=True,
    help="Name of the OpenShift cluster to be reboot",
)
@click.option("--fyre-user-name", required=True, help="FYRE API user name")
@click.option("--fyre-api-key", required=True, help="FYRE API key")
def reboot(cluster_name: str, fyre_user_name: str, fyre_api_key: str):
    """Reboot a cluster on FYRE"""

    request_specification = {"cluster_name": cluster_name}

    dg.utils.network.disable_insecure_request_warning()

    response = requests.post(
        IBM_FYRE_REBOOT_CLUSTER_URL,
        auth=(fyre_user_name, fyre_api_key),
        data=json.dumps(request_specification),
        verify=False,
    )

    if response.ok:
        json_response = response.json()
        status = json_response["status"]

        if status != "submitted":
            raise DataGateCLIException(
                "Failed to reboot FYRE cluster ({})".format(json_response["details"])
            )
    else:
        raise DataGateCLIException(
            "Failed to reboot FYRE cluster (HTTP status code: {})".format(
                response.status_code
            )
        )
