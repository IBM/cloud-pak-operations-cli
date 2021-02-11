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

from typing import Union

import click

import dg.config.cluster_credentials_manager
import dg.lib.click
import dg.lib.fyre.openshift
import dg.utils.network

from dg.utils.logging import loglevel_option


@click.command(
    context_settings=dg.lib.click.create_default_map_from_dict(
        dg.config.cluster_credentials_manager.cluster_credentials_manager.get_current_credentials()
    )
)
@click.option(
    "--infrastructure-node-hostname", required=True, help="Infrastructure node hostname"
)
@click.option("--server", required=True, help="OpenShift API server URL")
@click.option("--username", help="OpenShift username")
@click.option("--password", help="OpenShift password")
@click.option("--token", help="OpenShift OAuth access token")
@click.option(
    "--node", required=True, help="Hostname of the worker node to be initialized"
)
@click.option(
    "--db2-edition",
    required=True,
    type=click.Choice(["db2oltp", "db2wh"]),
    help="Db2 edition",
)
@click.option("--use-host-path-storage", is_flag=True, help="Use hostpath storage")
@loglevel_option()
@click.pass_context
def init_node_for_db2(
    ctx: click.Context,
    infrastructure_node_hostname: str,
    server: str,
    username: Union[str, None],
    password: Union[str, None],
    token: Union[str, None],
    node: str,
    db2_edition: str,
    use_host_path_storage: bool,
):
    """Initialize a worker node before creating a Db2 instance"""

    if dg.utils.network.is_hostname_localhost(infrastructure_node_hostname):
        dg.lib.click.log_in_to_openshift_cluster(ctx, locals().copy())
        dg.lib.fyre.openshift.init_node_for_db2(
            node, db2_edition, use_host_path_storage
        )
    else:
        oc_login_command_for_remote_host = (
            dg.lib.click.get_oc_login_command_for_remote_host(ctx, locals().copy())
        )

        asyncio.get_event_loop().run_until_complete(
            dg.lib.fyre.openshift.init_node_for_db2_from_remote_host(
                infrastructure_node_hostname,
                node,
                db2_edition,
                use_host_path_storage,
                oc_login_command_for_remote_host,
            )
        )
