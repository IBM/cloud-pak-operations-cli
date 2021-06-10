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

import dg.lib.ibmcloud.status

from dg.utils.logging import loglevel_command


@loglevel_command()
@click.option("--cluster-name", help="cluster name", required=True)
@click.option("--json", help="Prints the command output in JSON format", is_flag=True)
def status(cluster_name: str, json: bool):
    """Display the status of a Red Hat OpenShift on IBM Cloud cluster"""

    cluster_status = dg.lib.ibmcloud.status.get_cluster_status(cluster_name)
    status_output = cluster_status.get_json() if json else str(cluster_status)

    click.echo(status_output)
