#  Copyright 2021, 2023 IBM Corporation
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

import cpo.config.cluster_credentials_manager

from cpo.utils.logging import loglevel_command


@loglevel_command()
@click.option(
    "--print-alias", help="Print the alias used to reference a cluster instead of its server URL", is_flag=True
)
def current(print_alias: Optional[bool]):
    """Get the current registered OpenShift cluster"""

    current_cluster = cpo.config.cluster_credentials_manager.cluster_credentials_manager.get_current_cluster()

    if current_cluster is not None:
        if not print_alias:
            click.echo(current_cluster.get_server())
        else:
            cluster_data = current_cluster.get_cluster_data()

            if "alias" in cluster_data:
                click.echo(cluster_data["alias"])
