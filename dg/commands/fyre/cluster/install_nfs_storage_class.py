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
import re
import urllib.parse

from typing import Final, Union

import click

import dg.config.cluster_credentials_manager
import dg.utils.click
import dg.utils.download
import dg.utils.openshift
import dg.utils.ssh

SET_UP_OC4_URL: Final[
    str
] = "https://github.ibm.com/api/v3/repos/PrivateCloud/cpd-fyre-cluster/contents/set_up_oc4.sh"


def get_private_ip_address_of_infrastructure_node(hostname_result: str):
    search_result = re.search("(10\\.\\d+\\.\\d+\\.\\d+)", hostname_result)

    if search_result is not None:
        return search_result[1]
    else:
        raise Exception("Private IP address not found")


@click.command(
    context_settings=dg.utils.click.create_default_map_from_dict(
        dg.config.cluster_credentials_manager.cluster_credentials_manager.get_current_credentials()
    )
)
@click.option(
    "--infrastructure-node-hostname", required=True, help="Infrastructure node hostname"
)
@click.option(
    "--ibm-github-api-key",
    required=True,
    help="IBM GitHub API key (https://github.ibm.com/settings/tokens)",
)
@click.option("--server", required=True, help="OpenShift API server URL")
@click.option("--username", help="OpenShift username")
@click.option("--password", help="OpenShift password")
@click.option("--token", help="OpenShift OAuth access token")
@click.pass_context
def install_nfs_storage_class(
    ctx: click.Context,
    infrastructure_node_hostname: str,
    ibm_github_api_key: str,
    server: str,
    username: Union[str, None],
    password: Union[str, None],
    token: Union[str, None],
):
    """Install NFS storage class"""

    asyncio.get_event_loop().run_until_complete(
        _install_nfs_storage_class(
            ctx,
            infrastructure_node_hostname,
            ibm_github_api_key,
            server,
            username,
            password,
            token,
        )
    )


async def _install_nfs_storage_class(
    ctx: click.Context,
    infrastructure_node_hostname: str,
    ibm_github_api_key: str,
    server: str,
    username: Union[str, None],
    password: Union[str, None],
    token: Union[str, None],
):
    """Installs NFS storage class

    Parameters
    ----------
    infrastructure_node_hostname
        infrastructure node hostname
    ibm_github_api_key
        IBM GitHub API key
    server
        OpenShift API server URL
    username
        OpenShift username
    password
        OpenShift password
    token
        OpenShift OAuth access token
    """

    command = dg.utils.click.get_oc_login_command_for_remote_host(ctx, locals().copy())
    set_up_oc4_path = dg.utils.download.download_file(
        urllib.parse.urlsplit(SET_UP_OC4_URL),
        auth=("", ibm_github_api_key),
        headers={"Accept": "application/vnd.github.v3.raw"},
    )

    async with dg.utils.ssh.RemoteClient(infrastructure_node_hostname) as remoteClient:
        await remoteClient.connect()
        await remoteClient.execute(command)

        hostname_result = await remoteClient.execute(
            "hostname --all-ip-addresses", print_output=False
        )

        private_ip_address_of_infrastructure_node = (
            get_private_ip_address_of_infrastructure_node(hostname_result)
        )

        await remoteClient.upload(set_up_oc4_path)
        await remoteClient.execute("chmod a+x " + set_up_oc4_path.name)
        await remoteClient.execute(
            "./"
            + set_up_oc4_path.name
            + " "
            + private_ip_address_of_infrastructure_node
        )
