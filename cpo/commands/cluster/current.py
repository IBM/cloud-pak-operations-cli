#  Copyright 2021, 2026 IBM Corporation
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

import click

import cpo.config.cluster_credentials_manager

from cpo.utils.logging import loglevel_command


@loglevel_command()
@click.option(
    "--print-alias", help="Print the alias used to reference a cluster instead of its server URL", is_flag=True
)
def current(print_alias: bool | None):
    """Get the current registered OpenShift cluster"""

    current_cluster_file_entry = (
        cpo.config.cluster_credentials_manager.cluster_credentials_manager.get_current_cluster_file_entry()
    )

    if current_cluster_file_entry is not None:
        if not print_alias:
            click.echo(current_cluster_file_entry.server)
        else:
            if "alias" in current_cluster_file_entry.cluster_data:
                click.echo(current_cluster_file_entry.cluster_data["alias"])
