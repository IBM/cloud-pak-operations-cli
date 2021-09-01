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

import dg.config.cluster_credentials_manager
import dg.lib.click.utils
import dg.lib.fyre.utils.network
import dg.utils.network

from dg.lib.fyre.ocp_plus_api_manager import OCPPlusAPIManager
from dg.lib.fyre.utils.click import fyre_command_options
from dg.lib.openshift.nfs.nfs_subdir_external_provisioner import (
    NFSSubdirExternalProvisioner,
)
from dg.utils.logging import loglevel_command


@loglevel_command(
    context_settings=dg.lib.click.utils.create_default_map_from_dict(
        dg.config.cluster_credentials_manager.cluster_credentials_manager.get_current_credentials()
    )
)
@fyre_command_options
@click.option(
    "--cluster-name", help="Name of the OCP+ cluster on which the NFS storage class shall be installed", required=True
)
@click.option(
    "--project",
    default="default",
    help="Project used to install the Kubernetes NFS Subdir External Provisioner",
    required=True,
)
@click.option("--site", help="OCP+ site", type=click.Choice(["rtp", "svl"]))
@click.pass_context
def install_nfs_storage_class(
    ctx: click.Context,
    fyre_api_user_name: str,
    fyre_api_key: str,
    cluster_name: str,
    project: str,
    site: Optional[str],
):
    """Install NFS storage class"""

    dg.utils.network.disable_insecure_request_warning()

    nfs_server = (
        OCPPlusAPIManager(fyre_api_user_name, fyre_api_key)
        .get_cluster_details(cluster_name, site)
        .get_private_ip_address_of_infrastructure_node()
    )

    NFSSubdirExternalProvisioner(
        dg.lib.click.utils.get_cluster_credentials(ctx, locals().copy()), project, nfs_server, "/data"
    ).install_nfs_subdir_external_provisioner()
