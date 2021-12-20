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

import click

from cpo.lib.ibmcloud.oc.cluster.ls import list_existing_clusters
from cpo.utils.logging import loglevel_command


@loglevel_command()
@click.option("--json", help="Prints the command output in JSON format", is_flag=True)
def ls(json: bool):
    """List Red Hat OpenShift on IBM Cloud clusters"""

    click.echo(list_existing_clusters(json))
