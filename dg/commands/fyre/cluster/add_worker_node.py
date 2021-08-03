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


def validate_worker_node_additional_disk_size(ctx, param, value: Optional[List[int]]):
    if value is not None and len(value) > 6:
        raise click.BadParameter("Each worker node can only have up to six additional disks.")

    return value


@loglevel_command(
    context_settings=dg.lib.click.utils.create_default_map_from_dict(
        dg.config.cluster_credentials_manager.cluster_credentials_manager.get_current_credentials()
    )
)
@fyre_command_options
@click.option("--cluster-name", help="Name of the OCP+ cluster to whom a worker node shall be added", required=True)
@click.option("--disable-scheduling", help="?", is_flag=True)
@click.option("--force", "-f", help="Skip confirmation", is_flag=True)
@click.option("--site", help="OCP+ site", type=click.Choice(["rtp", "svl"]))
@click.option(
    "--worker-node-additional-disk-size",
    callback=validate_worker_node_additional_disk_size,
    help="Size of additional worker node disk",
    multiple=True,
    type=click.IntRange(1, 1000),
)
@click.option("--worker-node-count", help="Number of worker nodes", type=click.INT)
@click.option("--worker-node-num-cpus", help="Number of CPUs per worker node", type=click.IntRange(1, 16))
@click.option("--worker-node-ram-size", help="RAM size per worker node", type=click.IntRange(1, 64))
def add_worker_node(
    fyre_api_user_name: str,
    fyre_api_key: str,
    cluster_name: str,
    disable_scheduling: bool,
    force: bool,
    site: Optional[str],
    worker_node_additional_disk_size: List[int],
    worker_node_count: Optional[int],
    worker_node_num_cpus: Optional[int],
    worker_node_ram_size: Optional[int],
):
    """Add an additional worker node to an OCP+ cluster"""

    if not force:
        click.confirm(f"Do you really want to add an additional worker node to cluster '{cluster_name}'?", abort=True)

    dg.utils.network.disable_insecure_request_warning()
    OCPPlusAPIManager(fyre_api_user_name, fyre_api_key).add_node(
        cluster_name,
        disable_scheduling,
        site,
        worker_node_additional_disk_size,
        worker_node_count,
        worker_node_num_cpus,
        worker_node_ram_size,
    )
