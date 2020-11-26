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

from dg.lib.ibmcloud.cluster.rm import delete_ibmcloud_cluster


@click.command()
@click.option("-c", "--cluster-name", required=True, help="cluster name")
@click.option(
    "--force",
    "force_deletion",
    required=False,
    help="Force deletion of the cluster",
    is_flag=True,
)
def rm(cluster_name: str, force_deletion: bool):
    """Delete an existing OpenShift cluster on IBM Cloud"""

    delete_ibmcloud_cluster(cluster_name, force_deletion)
