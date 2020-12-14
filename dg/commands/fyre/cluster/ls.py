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

from typing import Final

import click
import requests

from tabulate import tabulate

import dg.config
import dg.lib.click
import dg.utils.network

IBM_FYRE_SHOW_OPENSHIFT_CLUSTERS_URL: Final[
    str
] = "https://api.fyre.ibm.com/rest/v1/?operation=query&request=showclusters"


@click.command(
    context_settings=dg.lib.click.create_default_map_from_json_file(
        dg.config.data_gate_configuration_manager.get_dg_credentials_file_path()
    )
)
@click.option("--fyre-user-name", required=True, help="Fyre API user name")
@click.option("--fyre-api-key", required=True, help="Fyre API key")
def ls(fyre_user_name: str, fyre_api_key: str):
    """List OpenShift clusters on FYRE"""

    dg.utils.network.disable_insecure_request_warning()

    response = requests.get(
        IBM_FYRE_SHOW_OPENSHIFT_CLUSTERS_URL,
        auth=(fyre_user_name, fyre_api_key),
        verify=False,
    )

    if not response.ok:
        raise Exception(
            "Failed to get FYRE clusters (HTTP status code: {})".format(
                response.status_code
            )
        )

    clusters = response.json()["clusters"]

    if len(clusters) != 0:
        cluster_list: list[list[str]] = []
        headers = clusters[0].keys()

        for cluster in clusters:
            cluster_list.append(list(cluster.values()))

        click.echo(tabulate(cluster_list, headers=headers))
