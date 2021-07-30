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

from typing import List, Optional

import click

import dg.config
import dg.config.cluster_credentials_manager
import dg.lib.click.utils
import dg.lib.fyre.cluster
import dg.utils.network

from dg.lib.fyre.ocp_plus_api_manager import OCPPlusAPIManager
from dg.lib.fyre.utils.click import fyre_command_options
from dg.utils.logging import loglevel_command


@loglevel_command(
    context_settings=dg.lib.click.utils.create_default_map_from_dict(
        dg.config.cluster_credentials_manager.cluster_credentials_manager.get_current_credentials()
    )
)
@fyre_command_options
@click.option("--additional-disk-size", help="Size of additional disk", multiple=True, type=click.IntRange(1, 1000))
@click.option("--cluster-name", help="Name of the OCP+ cluster to be edited", required=True)
@click.option("--force", "-f", help="Skip confirmation", is_flag=True)
@click.option("--site", help="OCP+ site", type=click.Choice(["rtp", "svl"]))
def edit_inf_node(
    fyre_api_user_name: str,
    fyre_api_key: str,
    additional_disk_size: List[int],
    cluster_name: str,
    force: bool,
    site: Optional[str],
):
    """Edit the infrastructure node of an OCP+ cluster"""

    if len(additional_disk_size) != 0:
        if not force:
            click.confirm(
                f"Do you really want to edit the infrastructure node of cluster '{cluster_name}'?", abort=True
            )

        dg.utils.network.disable_insecure_request_warning()
        OCPPlusAPIManager(fyre_api_user_name, fyre_api_key).edit_inf_node(cluster_name, additional_disk_size, site)
