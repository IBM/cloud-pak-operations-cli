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
import dg.lib.ibmcloud.cluster
import dg.lib.ibmcloud.status

from dg.utils.logging import loglevel_command


@loglevel_command()
@click.option(
    "--alias", help="Alias used to reference a cluster instead of its server URL"
)
@click.option(
    "--cluster-name",
    required=True,
    help="Name of the OpenShift cluster to be registered",
)
def add(alias: str, cluster_name: str):
    """Register an existing OpenShift cluster on IBM Cloud"""

    server = dg.lib.ibmcloud.status.get_cluster_status(cluster_name).get_server_url()

    dg.config.cluster_credentials_manager.cluster_credentials_manager.add_cluster(
        alias if (alias is not None) else "",
        server,
        dg.lib.ibmcloud.cluster.CLUSTER_TYPE,
        {
            "cluster_name": cluster_name,
        },
    )
