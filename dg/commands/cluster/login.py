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
import dg.lib.click
import dg.lib.fyre.cluster.fyre_cluster_factory  # required to register FYREClusterFactory object
import dg.lib.ibmcloud.cluster.ibmcloud_cluster_factory  # required to register IBMCloudClusterFactory object

from dg.lib.error import DataGateCLIException


@click.command(
    context_settings=dg.lib.click.create_default_map_from_dict(
        dg.config.cluster_credentials_manager.cluster_credentials_manager.get_current_credentials()
    )
)
def login():
    """Log in to the current OpenShift cluster"""

    current_cluster = (
        dg.config.cluster_credentials_manager.cluster_credentials_manager.get_current_cluster()
    )

    if current_cluster is None:
        raise DataGateCLIException("No current cluster selected")

    current_cluster.login()
