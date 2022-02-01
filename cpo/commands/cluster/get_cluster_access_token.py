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

from typing import Optional

import click

import cpo.config.cluster_credentials_manager
import cpo.lib.click.utils
import cpo.utils.network

from cpo.utils.logging import loglevel_command


@loglevel_command()
@click.option("--server", help="OpenShift server URL")
@click.option("--username", help="OpenShift cluster username")
@click.option("--password", help="OpenShift cluster password")
@click.option(
    "--print-login-command", help="Print oc login command instead of just the OAuth access token", is_flag=True
)
@click.pass_context
def get_cluster_access_token(
    ctx: click.Context,
    server: Optional[str],
    username: Optional[str],
    password: Optional[str],
    print_login_command: bool,
):
    """Obtain an OAuth access token for an OpenShift cluster"""

    cpo.utils.network.disable_insecure_request_warning()

    credentials = cpo.lib.click.utils.get_cluster_credentials(ctx, locals().copy())
    access_token = credentials.get_access_token(force_refresh_if_possible=True)

    if not print_login_command:
        click.echo(access_token)
    else:
        click.echo(f"oc login --insecure-skip-tls-verify --server={credentials.server} --token={access_token}")
