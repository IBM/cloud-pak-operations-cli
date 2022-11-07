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
from cpo.utils.logging import loglevel_command


@loglevel_command()
@click.option("--cluster-name", help="Name of the Red Hat OpenShift on IBM Cloud cluster to be deleted", required=True)
@click.option("--force", help="Skip confirmation", is_flag=True)
def rm(cluster_name: str, force: bool):
    """Delete a Red Hat OpenShift on IBM Cloud cluster"""

    if not force:
        click.confirm(f"Do you really want to delete cluster '{cluster_name}'?", abort=True)

    IBMCloudAPIManager().delete_cluster(cluster_name)
