#  Copyright 2021, 2022 IBM Corporation
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

from cpo.lib.ibmcloud.ibm_cloud_api_manager import IBMCloudAPIManager
from cpo.lib.ibmcloud.oc.cluster.roks_cluster_factory import roks_cluster_factory
from cpo.utils.error import CloudPakOperationsCLIException
from cpo.utils.logging import loglevel_command


@loglevel_command()
@click.option("--cluster-name", help="cluster name", required=True)
def login(cluster_name: str):
    """Log in to a Red Hat OpenShift on IBM Cloud cluster"""

    cluster_status = IBMCloudAPIManager().get_cluster_status(cluster_name)

    if cluster_status.is_ready():
        cluster = roks_cluster_factory.create_cluster(cluster_status.get_server_url(), {})
        cluster.login()
    else:
        raise CloudPakOperationsCLIException(f"Cluster {cluster_name} is not yet ready")
