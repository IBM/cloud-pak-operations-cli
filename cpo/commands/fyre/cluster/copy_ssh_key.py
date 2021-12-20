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

import subprocess

import click

import cpo.config.cluster_credentials_manager
import cpo.lib.click.utils

from cpo.utils.logging import loglevel_command


@loglevel_command(
    context_settings=cpo.lib.click.utils.create_default_map_from_dict(
        cpo.config.cluster_credentials_manager.cluster_credentials_manager.get_current_credentials()
    )
)
@click.option("--infrastructure-node-hostname", help="Infrastructure node hostname", required=True)
def copy_ssh_key(infrastructure_node_hostname: str):
    """Copy the current user's public SSH key to the infrastructure node of
    an OCP+ cluster"""

    args = ["ssh-copy-id", "-o", "StrictHostKeyChecking=no", f"root@{infrastructure_node_hostname}"]

    subprocess.run(args, check=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
