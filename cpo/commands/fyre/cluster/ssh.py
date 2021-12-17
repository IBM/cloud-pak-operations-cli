#  Copyright 2021 IBM Corporation
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

import subprocess

import click

import cpo.config.cluster_credentials_manager
import cpo.lib.click.utils
import cpo.utils.network

from cpo.utils.logging import loglevel_command


@loglevel_command(
    context_settings=cpo.lib.click.utils.create_default_map_from_dict(
        cpo.config.cluster_credentials_manager.cluster_credentials_manager.get_current_credentials()
    )
)
@click.option("--disable-strict-host-key-checking", help="Disable strict host key checking", is_flag=True)
@click.option("--infrastructure-node-hostname", help="Infrastructure node hostname", required=True)
@click.pass_context
def ssh(
    ctx: click.Context,
    disable_strict_host_key_checking: bool,
    infrastructure_node_hostname: str,
):
    """Connect to the infrastructure node of an OCP+ cluster using SSH"""

    if not cpo.utils.network.is_hostname_localhost(infrastructure_node_hostname):
        args = ["ssh"]

        if disable_strict_host_key_checking:
            args.append("-o")
            args.append("StrictHostKeyChecking=no")

        args.append(f"root@{infrastructure_node_hostname}")

        subprocess.check_call(args)
