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
import dg.lib.fyre.cluster

from dg.utils.logging import loglevel_command


@loglevel_command()
@click.option("--alias", help="Alias used to reference a cluster instead of its server URL")
@click.option(
    "--cluster-name",
    required=True,
    help="Name of the OpenShift cluster to be registered",
)
@click.option("--password", required=True, help="kubeadmin password")
def add(cluster_name: str, alias: str, password: str):
    """Register an existing OpenShift cluster on FYRE"""

    dg.config.cluster_credentials_manager.cluster_credentials_manager.add_cluster(
        alias if (alias is not None) else "",
        "https://api.{}.os.fyre.ibm.com:6443".format(cluster_name),
        dg.lib.fyre.cluster.CLUSTER_TYPE_ID,
        {
            "cluster_name": cluster_name,
            "infrastructure_node_hostname": "{}-inf.fyre.ibm.com".format(cluster_name),
            "password": password,
            "username": "kubeadmin",
        },
    )
