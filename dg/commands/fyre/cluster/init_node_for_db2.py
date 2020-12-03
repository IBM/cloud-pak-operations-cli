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
import dg.utils.click
import dg.utils.openshift
import dg.utils.ssh


@click.command(
    context_settings=dg.utils.click.create_default_map_from_dict(
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

    asyncio.get_event_loop().run_until_complete(
        _init_node_for_db2(
            ctx,
            infrastructure_node_hostname,
            server,
            username,
            password,
            token,
            node,
            db2_edition,
            use_host_path_storage,
        )
    )


async def _init_node_for_db2(
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
    command = dg.utils.click.get_oc_login_command_for_remote_host(ctx, locals().copy())

    async with dg.utils.ssh.RemoteClient(infrastructure_node_hostname) as remoteClient:
        await remoteClient.connect()
        await remoteClient.execute(command)
        await remoteClient.execute(
            "oc adm taint node {} icp4data=database-{}:NoSchedule".format(
                node, db2_edition
            )
        )

        await remoteClient.execute(
            "oc label node {} icp4data=database-{}".format(node, db2_edition)
        )

        await remoteClient.execute(
            "ssh core@{} sudo setsebool -P container_manage_cgroup true".format(node)
        )

        if use_host_path_storage:
            await _label_storage_path(remoteClient, node)


async def _label_storage_path(remoteClient: dg.utils.ssh.RemoteClient, node: str):
    """Labels the storage path on the given node

    See https://www.ibm.com/support/producthub/icpdata/docs/content/SSQNUZ_current/cpd/svc/dbs/ ↩
        hostpath-selinux-aese.html#hostpath-selinux-aese

    Parameters
    ----------
    remoteClient
        SSH client
    node
        node on which the storage path shall be labeled
    """

    await remoteClient.execute(
        "ssh core@{} mkdir --parents /var/home/core/data".format(node)
    )

    await remoteClient.execute("ssh core@{} chmod 777 /var/home/core/data".format(node))
    await remoteClient.execute(
        "ssh core@{} 'sudo semanage fcontext --add --type container_file_t \"/var/home/core/data(/.*)?\"'".format(
            node
        )
    )

    await remoteClient.execute(
        "ssh core@{} sudo restorecon -Rv /var/home/core/data".format(node)
    )
