#  Copyright 2021, 2024 IBM Corporation
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
import cpo.lib.click.utils

from cpo.lib.openshift.openshift_api_manager import OpenShiftAPIManager
from cpo.lib.openshift.utils.click import openshift_server_options
from cpo.utils.logging import loglevel_command


@loglevel_command(default_log_level="WARNING")
@openshift_server_options
@click.option("--json", help="Prints the command output in JSON format", is_flag=True)
@click.pass_context
def ls(
    ctx: click.Context,
    server: str | None,
    username: str | None,
    password: str | None,
    token: str | None,
    insecure_skip_tls_verify: bool | None,
    use_cluster: str | None,
    json: bool,
):
    """List registry credentials stored in the global pull secret"""

    OpenShiftAPIManager(
        cpo.lib.click.utils.get_cluster_credentials(ctx, locals().copy())
    ).get_global_pull_secret_data().format(json)
