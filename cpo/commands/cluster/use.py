#  Copyright 2021, 2025 IBM Corporation
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

from cpo.lib.openshift.oc import login
from cpo.utils.logging import loglevel_command


@loglevel_command()
@click.argument("alias_or_server")
@click.option(
    "--oc-login",
    help="Log in to the current OpenShift cluster",
    is_flag=True,
)
def use(alias_or_server: str, oc_login: bool):
    """Set the current registered OpenShift cluster"""

    current_cluster = cpo.config.cluster_credentials_manager.cluster_credentials_manager.set_cluster(alias_or_server)

    if oc_login:
        login(current_cluster)
