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

from cpo.lib.openshift.openshift_api_manager import OpenShiftAPIManager
from cpo.lib.openshift.utils.click import openshift_server_options
from cpo.utils.logging import loglevel_command


@loglevel_command()
@openshift_server_options
@click.option("--registry-location", help="Container registry location", required=True)
@click.option("--registry-location-username", help="Container registry username", required=True)
@click.option("--registry-location-password", help="Container registry password", required=True)
@click.pass_context
def set(
    ctx: click.Context,
    server: Optional[str],
    username: Optional[str],
    password: Optional[str],
    token: Optional[str],
    insecure_skip_tls_verify: Optional[bool],
    registry_location: str,
    registry_location_username: str,
    registry_location_password: str,
):
    """Store registry credentials in the global pull secret"""

    OpenShiftAPIManager(cpo.lib.click.utils.get_cluster_credentials(ctx, locals().copy())).set_credentials(
        registry_location, registry_location_username, registry_location_password
    )
