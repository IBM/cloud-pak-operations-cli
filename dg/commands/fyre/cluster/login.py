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

from typing import Union

import click

import dg.config.cluster_credentials_manager
import dg.lib.click

from dg.lib.fyre.cluster.fyre_cluster_factory import fyre_cluster_factory


@click.command(
    context_settings=dg.lib.click.create_default_map_from_dict(
        dg.config.cluster_credentials_manager.cluster_credentials_manager.get_current_credentials()
    )
)
@click.option("--cluster-name", required=True, help="cluster name")
@click.option("--username", help="OpenShift username")
@click.option("--password", help="OpenShift password")
@click.pass_context
def login(
    ctx: click.Context,
    cluster_name: str,
    username: Union[str, None],
    password: Union[str, None],
):
    """Log in to an OpenShift cluster"""

    cluster = fyre_cluster_factory.create_cluster_using_cluster_name(
        cluster_name, locals().copy()
    )

    cluster.login()
