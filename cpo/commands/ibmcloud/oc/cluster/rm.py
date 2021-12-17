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

from cpo.lib.ibmcloud.oc.cluster.rm import delete_ibmcloud_cluster
from cpo.utils.logging import loglevel_command


@loglevel_command()
@click.option("-c", "--cluster-name", help="cluster name", required=True)
@click.option("--force", "force_deletion", help="Force deletion of the cluster", is_flag=True)
def rm(cluster_name: str, force_deletion: bool):
    """Delete a Red Hat OpenShift on IBM Cloud cluster"""

    delete_ibmcloud_cluster(cluster_name, force_deletion)
