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

import asyncio

from typing import Optional

import click

import dg.config.cluster_credentials_manager
import dg.lib.click.utils
import dg.lib.fyre.utils.nfs
import dg.utils.network

from dg.utils.logging import loglevel_command


@loglevel_command(
    context_settings=dg.lib.click.utils.create_default_map_from_dict(
        dg.config.cluster_credentials_manager.cluster_credentials_manager.get_current_credentials()
    )
)
@click.option("--infrastructure-node-hostname", help="Infrastructure node hostname", required=True)
@click.option("--server", help="OpenShift server URL", required=True)
@click.option("--username", help="OpenShift username")
@click.option("--password", help="OpenShift password")
@click.option("--token", help="OpenShift OAuth access token")
@click.option(
    "--ibm-github-personal-access-token",
    help="IBM GitHub personal access token (see https://github.ibm.com/settings/tokens)",
)
@click.pass_context
def install_nfs_storage_class(
    ctx: click.Context,
    infrastructure_node_hostname: str,
    server: str,
    username: Optional[str],
    password: Optional[str],
    token: Optional[str],
    ibm_github_personal_access_token: str,
):
    """Install NFS storage class"""

    if dg.utils.network.is_hostname_localhost(infrastructure_node_hostname):
        dg.lib.click.utils.log_in_to_openshift_cluster(ctx, locals().copy())
        dg.lib.fyre.utils.nfs.install_nfs_storage_class(ibm_github_personal_access_token)
    else:
        oc_login_command_for_remote_host = dg.lib.click.utils.get_oc_login_command_for_remote_host(ctx, locals().copy())

        asyncio.get_event_loop().run_until_complete(
            dg.lib.fyre.utils.nfs.install_nfs_storage_class_on_remote_host(
                infrastructure_node_hostname,
                ibm_github_personal_access_token,
                oc_login_command_for_remote_host,
            )
        )
