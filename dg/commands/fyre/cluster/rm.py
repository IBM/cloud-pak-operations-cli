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
import dg.utils.network

from dg.lib.fyre.api_manager import OCPPlusAPIManager
from dg.utils.logging import loglevel_command


@loglevel_command(
    context_settings=dg.lib.click.utils.create_default_map_from_dict(
        dg.config.cluster_credentials_manager.cluster_credentials_manager.get_current_credentials()
    )
)
@click.option("--fyre-user-name", help="FYRE API user name", required=True)
@click.option("--fyre-api-key", help="FYRE API key", required=True)
@click.option("--cluster-name", help="Name of the OCP+ cluster to be deleted", required=True)
@click.option("--force", "-f", help="Skip confirmation", is_flag=True)
@click.option("--site", help="OCP+ site", type=click.Choice(["rtp", "svl"]))
def rm(fyre_user_name: str, fyre_api_key: str, cluster_name: str, force: bool, site: Optional[str]):
    """Delete an OCP+ cluster"""

    if not force:
        click.confirm(f"Do you really want to delete cluster '{cluster_name}'?", abort=True)

    dg.utils.network.disable_insecure_request_warning()
    OCPPlusAPIManager(fyre_user_name, fyre_api_key).rm(cluster_name, site)

    server = f"https://api.{cluster_name}.cp.fyre.ibm.com:6443"
    cluster = dg.config.cluster_credentials_manager.cluster_credentials_manager.get_cluster(server)

    if cluster is not None:
        dg.config.cluster_credentials_manager.cluster_credentials_manager.remove_cluster(server)
