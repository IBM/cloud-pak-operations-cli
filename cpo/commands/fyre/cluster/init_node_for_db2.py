#  Copyright 2020, 2021 IBM Corporation
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

import cpo.config.cluster_credentials_manager
import cpo.lib.click.utils
import cpo.lib.fyre.utils.openshift
import cpo.utils.network

from cpo.utils.logging import loglevel_command


@loglevel_command(
    context_settings=cpo.lib.click.utils.create_default_map_from_dict(
        cpo.config.cluster_credentials_manager.cluster_credentials_manager.get_current_credentials()
    )
)
@click.option("--infrastructure-node-hostname", help="Infrastructure node hostname", required=True)
@click.option("--server", help="OpenShift server URL", required=True)
@click.option("--username", help="OpenShift username")
@click.option("--password", help="OpenShift password")
@click.option("--token", help="OpenShift OAuth access token")
@click.option("--node", help="Hostname of the worker node to be initialized", required=True)
@click.option("--db2-edition", help="Db2 edition", required=True, type=click.Choice(["db2oltp", "db2wh"]))
@click.option("--use-host-path-storage", help="Use hostpath storage", is_flag=True)
@click.pass_context
def init_node_for_db2(
    ctx: click.Context,
    infrastructure_node_hostname: str,
    server: str,
    username: Optional[str],
    password: Optional[str],
    token: Optional[str],
    node: str,
    db2_edition: str,
    use_host_path_storage: bool,
):
    """Initialize a worker node before creating a Db2 instance"""

    if cpo.utils.network.is_hostname_localhost(infrastructure_node_hostname):
        cpo.lib.click.utils.log_in_to_openshift_cluster(ctx, locals().copy())
        cpo.lib.fyre.utils.openshift.init_node_for_db2(node, db2_edition, use_host_path_storage)
    else:
        oc_login_command_for_remote_host = cpo.lib.click.utils.get_oc_login_command_for_remote_host(ctx, locals().copy())

        asyncio.get_event_loop().run_until_complete(
            cpo.lib.fyre.utils.openshift.init_node_for_db2_from_remote_host(
                infrastructure_node_hostname,
                node,
                db2_edition,
                use_host_path_storage,
                oc_login_command_for_remote_host,
            )
        )
