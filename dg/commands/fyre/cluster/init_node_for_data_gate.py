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

import click

import dg.config
import dg.config.cluster_credentials_manager
import dg.utils.click
import dg.utils.ssh


@click.command(
    context_settings=dg.utils.click.create_default_map_from_dict(
        dg.config.cluster_credentials_manager.cluster_credentials_manager.get_current_credentials()
    )
)
@click.option(
    "--infrastructure-node-hostname", required=True, help="Infrastructure node hostname"
)
@click.option("--node", required=True, help="Worker node to be initialized")
def init_node_for_data_gate(
    infrastructure_node_hostname: str,
    node: str,
):
    """Initialize a worker node before creating a Data Gate instance"""

    asyncio.get_event_loop().run_until_complete(
        _init_node_for_data_gate(infrastructure_node_hostname, node)
    )


async def _compile_selinux_policy_module(
    remoteClient: dg.utils.ssh.RemoteClient, node: str
):
    await remoteClient.execute(
        "ssh core@{} sudo checkmodule -m --mls --output db2u-nfs.mod db2u-nfs.te".format(
            node
        )
    )


async def _copy_type_enforcement_file_to_infrastructure_node(
    remoteClient: dg.utils.ssh.RemoteClient,
):
    await remoteClient.upload(
        dg.config.data_gate_configuration_manager.get_deps_directory_path()
        / "db2u-nfs"
        / "db2u-nfs.te"
    )


async def _copy_type_enforcement_file_to_worker_node(
    remoteClient: dg.utils.ssh.RemoteClient, node: str
):
    await remoteClient.execute("scp db2u-nfs.te core@{}:".format(node))


async def _create_selinux_policy_module_package(
    remoteClient: dg.utils.ssh.RemoteClient, node: str
):
    await remoteClient.execute(
        "ssh core@{} sudo semodule_package --module db2u-nfs.mod --outfile db2u-nfs.pp".format(
            node
        )
    )


async def _init_node_for_data_gate(
    infrastructure_node_hostname: str,
    node: str,
):
    async with dg.utils.ssh.RemoteClient(infrastructure_node_hostname) as remoteClient:
        await remoteClient.connect()
        await _copy_type_enforcement_file_to_infrastructure_node(remoteClient)
        await _copy_type_enforcement_file_to_worker_node(remoteClient, node)
        await _compile_selinux_policy_module(remoteClient, node)
        await _create_selinux_policy_module_package(remoteClient, node)
        await _install_selinux_policy_module_package(remoteClient, node)


async def _install_selinux_policy_module_package(
    remoteClient: dg.utils.ssh.RemoteClient, node: str
):
    await remoteClient.execute(
        "ssh core@{} sudo semodule --install db2u-nfs.pp".format(node)
    )
