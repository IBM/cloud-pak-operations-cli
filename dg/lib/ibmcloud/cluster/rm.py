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

from dg.lib.error import IBMCloudException
from dg.lib.ibmcloud import (
    execute_ibmcloud_command_interactively,
    execute_ibmcloud_command_without_check,
)


def delete_ibmcloud_cluster(name: str, force_deletion: bool):
    """Delete an existing OpenShift cluster on IBM Cloud"""

    command = ["oc", "cluster", "rm", "--cluster", name]
    return_code = 0

    if force_deletion:
        command.append("--force-delete-storage")
        command.append("-f")
        result = execute_ibmcloud_command_without_check(command, capture_output=True)

        if result.return_code != 0:
            raise IBMCloudException(
                "An error occurred while deleting the cluster", result.stderr
            )
        else:
            return_code = result.return_code
            click.echo(result.stdout)
    else:
        return_code = execute_ibmcloud_command_interactively(command)

    if return_code == 0:
        click.echo(
            f"Cluster deletion request for cluster {name} successfully submitted. It might take a "
            f"while until the cluster status changes. You can check the status using 'dg ibmcloud cluster status "
            f"--name {name}'"
        )
