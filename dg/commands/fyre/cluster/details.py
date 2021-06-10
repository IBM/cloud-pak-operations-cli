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

from typing import Optional

import click

import dg.config
import dg.config.cluster_credentials_manager
import dg.lib.click.utils
import dg.lib.fyre.cluster
import dg.utils.network

from dg.lib.fyre.api_manager import OCPPlusAPIManager
from dg.utils.logging import loglevel_command


@loglevel_command(
    context_settings=dg.lib.click.utils.create_default_map_from_dict(
        dg.config.cluster_credentials_manager.cluster_credentials_manager.get_current_credentials()
    )
)
@click.option("--fyre-user-name", help="FYRE API user name", required=True)
@click.option("--fyre-api-key", help="FYRE API key (see https://fyre.svl.ibm.com/account)", required=True)
@click.option("--cluster-name", help="Name of the OCP+ cluster whose details shall be listed", required=True)
@click.option("--json", help="Prints the command output in JSON format", is_flag=True)
@click.option("--site", help="OCP+ site", type=click.Choice(["rtp", "svl"]))
def details(fyre_user_name: str, fyre_api_key: str, cluster_name: str, json: bool, site: Optional[str]):
    """List details of an OCP+ cluster"""

    dg.utils.network.disable_insecure_request_warning()
    OCPPlusAPIManager(fyre_user_name, fyre_api_key).get_cluster_details(cluster_name, site).format(json)