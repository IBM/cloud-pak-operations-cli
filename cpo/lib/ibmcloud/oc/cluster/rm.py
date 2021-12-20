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

import cpo.lib.ibmcloud.status

from cpo.config.cluster_credentials_manager import cluster_credentials_manager
from cpo.lib.error import IBMCloudException
from cpo.lib.ibmcloud import (
    execute_ibmcloud_command_interactively,
    execute_ibmcloud_command_without_check,
)


def delete_ibmcloud_cluster(name: str, force_deletion: bool):
    """Delete an existing OpenShift cluster on IBM Cloud"""

    ibmcloud_oc_cluster_rm_args = ["oc", "cluster", "rm", "--cluster", name]
    return_code = 0
    server = cpo.lib.ibmcloud.status.get_cluster_status(name).get_server_url()

    if force_deletion:
        ibmcloud_oc_cluster_rm_args.append("--force-delete-storage")
        ibmcloud_oc_cluster_rm_args.append("-f")
        ibmcloud_oc_cluster_rm_result = execute_ibmcloud_command_without_check(
            ibmcloud_oc_cluster_rm_args, capture_output=True
        )

        if ibmcloud_oc_cluster_rm_result.return_code != 0:
            raise IBMCloudException(
                "An error occurred while deleting the cluster", ibmcloud_oc_cluster_rm_result.stderr
            )

        return_code = ibmcloud_oc_cluster_rm_result.return_code

        click.echo(ibmcloud_oc_cluster_rm_result.stdout)
    else:
        return_code = execute_ibmcloud_command_interactively(ibmcloud_oc_cluster_rm_args)

    if return_code == 0:
        click.echo(
            f"Cluster deletion request for cluster {name} successfully submitted. It might take a "
            f"while until the cluster status changes. You can check the status using 'cpo ibmcloud cluster status "
            f"--name {name}'"
        )

    cluster = cluster_credentials_manager.get_cluster(server)

    if cluster is not None:
        cluster_credentials_manager.remove_cluster(server)
