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

from dg.utils.logging import loglevel_command


@loglevel_command()
def current():
    """Get the current registered OpenShift cluster"""

    current_cluster = dg.config.cluster_credentials_manager.cluster_credentials_manager.get_current_cluster()

    if current_cluster is not None:
        click.echo(current_cluster.get_server())
