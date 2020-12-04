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
import dg.utils.click

from dg.lib.fyre.cluster.fyre_cluster_factory import fyre_cluster_factory


@click.command(
    context_settings=dg.utils.click.create_default_map_from_dict(
        dg.config.cluster_credentials_manager.cluster_credentials_manager.get_current_credentials()
    )
)
@click.option(
    "--cluster-name",
    required=True,
    help="Name of the OpenShift cluster",
)
@click.option("--username", required=True, help="OpenShift cluster username")
@click.option("--password", required=True, help="OpenShift cluster password")
@click.option(
    "--print-login-command",
    help="Print oc login command instead of just the OAuth access token",
    is_flag=True,
)
@click.pass_context
def get_cluster_access_token(
    ctx: click.Context,
    cluster_name: str,
    username: str,
    password: str,
    print_login_command: bool,
):
    """Obtain an OAuth access token for an OpenShift cluster"""

    cluster = fyre_cluster_factory.create_cluster_using_cluster_name(
        cluster_name, locals().copy()
    )

    access_token = cluster.get_cluster_access_token()

    if not print_login_command:
        click.echo(access_token)
    else:
        click.echo(
            "oc login --insecure-skip-tls-verify --server={} --token={}".format(
                cluster.get_server(), access_token
            )
        )
