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
import cpo.lib.ibmcloud.oc.cluster
import cpo.lib.ibmcloud.status

from cpo.utils.logging import loglevel_command


@loglevel_command()
@click.option("--alias", help="Alias used to reference a cluster instead of its server URL")
@click.option(
    "--cluster-name", help="Name of the Red Hat OpenShift on IBM Cloud cluster to be registered", required=True
)
def add(alias: Optional[str], cluster_name: str):
    """Register an existing Red Hat OpenShift on IBM Cloud cluster"""

    server = cpo.lib.ibmcloud.status.get_cluster_status(cluster_name).get_server_url()

    cpo.config.cluster_credentials_manager.cluster_credentials_manager.add_cluster(
        alias if (alias is not None) else "",
        server,
        cpo.lib.ibmcloud.oc.cluster.CLUSTER_TYPE_ID,
        {
            "cluster_name": cluster_name,
        },
    )
