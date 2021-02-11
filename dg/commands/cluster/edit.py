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

import click

import dg.config.cluster_credentials_manager

from dg.utils.logging import loglevel_option


@click.command()
@click.argument("alias_or_server")
@click.option("--alias", help="Alias")
@click.option("--password", help="kubeadmin password")
@loglevel_option()
def edit(alias_or_server: str, alias: str, password: str):
    """Edit metadata of a registered OpenShift cluster"""

    metadata_to_be_edited = locals().copy()
    metadata_to_be_edited.pop("alias_or_server")

    if all(value is None for value in metadata_to_be_edited.values()):
        return

    metadata_to_be_edited = dict(
        filter(lambda pair: pair[1] is not None, metadata_to_be_edited.items())
    )

    dg.config.cluster_credentials_manager.cluster_credentials_manager.edit_cluster(
        alias_or_server, metadata_to_be_edited
    )
