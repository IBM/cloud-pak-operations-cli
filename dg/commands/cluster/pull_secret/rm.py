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

from typing import Optional

import click

import dg.config.cluster_credentials_manager
import dg.lib.click.utils

from dg.lib.openshift.openshift_api_manager import OpenShiftAPIManager
from dg.lib.openshift.utils.click import openshift_server_options
from dg.utils.logging import loglevel_command


@loglevel_command()
@openshift_server_options
@click.option("--registry-location", help="Container registry location", required=True)
@click.pass_context
def rm(
    ctx: click.Context,
    server: Optional[str],
    username: Optional[str],
    password: Optional[str],
    token: Optional[str],
    insecure_skip_tls_verify: Optional[bool],
    registry_location: str,
):
    """Remove registry credentials from the global pull secret"""

    OpenShiftAPIManager(dg.lib.click.utils.get_cluster_credentials(ctx, locals().copy())).delete_credentials(
        registry_location
    )
