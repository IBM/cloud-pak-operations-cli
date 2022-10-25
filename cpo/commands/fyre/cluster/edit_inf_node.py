#  Copyright 2021, 2022 IBM Corporation
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

import cpo.config
import cpo.config.cluster_credentials_manager
import cpo.lib.click.utils
import cpo.lib.fyre.cluster
import cpo.utils.network

from cpo.lib.fyre.ocp_plus_api_manager import OCPPlusAPIManager
from cpo.lib.fyre.utils.click import fyre_command_options
from cpo.utils.logging import loglevel_command


@loglevel_command(
    context_settings=cpo.lib.click.utils.create_default_map_from_dict(
        cpo.config.cluster_credentials_manager.cluster_credentials_manager.get_current_credentials()
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
    disable_strict_response_schema_check: bool,
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

        cpo.utils.network.disable_insecure_request_warning()
        OCPPlusAPIManager(fyre_api_user_name, fyre_api_key, disable_strict_response_schema_check).edit_inf_node(
            cluster_name, additional_disk_size, site
        )
