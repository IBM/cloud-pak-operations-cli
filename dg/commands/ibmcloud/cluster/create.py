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

import logging

import click

from dg.lib.error import IBMCloudException
from dg.lib.ibmcloud import execute_ibmcloud_command_without_check
from dg.lib.ibmcloud.cluster.rm import delete_ibmcloud_cluster
from dg.lib.ibmcloud.install import install_cp4d_with_preinstall
from dg.lib.ibmcloud.login import is_logged_in
from dg.lib.ibmcloud.login import login as login_to_ibm_cloud
from dg.lib.ibmcloud.oc import get_latest_supported_openshift_version
from dg.lib.ibmcloud.status import (
    cluster_exists,
    wait_for_cluster_deletion,
    wait_for_cluster_readiness,
)
from dg.lib.ibmcloud.vlan import (
    get_default_private_vlan,
    get_default_public_vlan,
)
from dg.utils.logging import loglevel_command

logger = logging.getLogger(__name__)


@loglevel_command()
@click.option("-c", "--cluster-name", required=True, help="cluster name")
@click.option(
    "-i",
    "--full-install",
    "full_installation",
    required=False,
    help="Perform a full installation of Cloud Pak for Data after the cluster is provisioned.",
    is_flag=True,
)
@click.option(
    "-r",
    "--rm",
    "remove_existing",
    required=False,
    help="Delete any existing cluster with the given name before creating a new one.",
    is_flag=True,
)
@click.option(
    "-f",
    "--force",
    required=False,
    help="Remove any prompts during cluster creation.",
    is_flag=True,
)
def create(cluster_name: str, full_installation: bool, remove_existing: bool, force: bool):
    """Create a new OpenShift cluster on IBM Cloud"""

    if not is_logged_in():
        login_to_ibm_cloud()

    if remove_existing:
        logger.info(
            click.style(
                f"Deleting existing cluster '{cluster_name}'.",
                bold=True,
            )
        )

        if cluster_exists(cluster_name):
            delete_ibmcloud_cluster(cluster_name, force)
            wait_for_cluster_deletion(cluster_name)
        else:
            logging.info(f"Skipping deletion, as cluster '{cluster_name}' could not be found.")

    logging.info(
        click.style(
            f"Creating OpenShift cluster with name '{cluster_name}' in IBM Cloud.",
            bold=True,
        )
    )

    openshift_version = get_latest_supported_openshift_version()
    zone = "sjc03"
    private_vlan = get_default_private_vlan(zone)
    public_vlan = get_default_public_vlan(zone)

    command = [
        "oc",
        "cluster",
        "create",
        "classic",
        "--entitlement",
        "cloud_pak",
        "--flavor",
        "b3c.16x64",
        "--hardware",
        "dedicated",
        "--name",
        cluster_name,
        "--public-vlan",
        public_vlan,
        "--public-service-endpoint",
        "--private-vlan",
        private_vlan,
        "--version",
        openshift_version,
        "--workers",
        "3",
        "--zone",
        zone,
    ]

    result = execute_ibmcloud_command_without_check(command, capture_output=True)

    if result.return_code != 0:
        if "E0007" in result.stderr:
            # a cluster with the same name already exists
            raise IBMCloudException(result.stderr)
        else:
            if cluster_exists(cluster_name):
                # There was an error, but the cluster was created nonetheless, print a warning

                logging.warning(
                    f"An error occurred while creating the cluster, but 'ibmcloud oc cluster ls' shows a cluster with "
                    f"the name '{cluster_name}' – error details:\n"
                    f"{IBMCloudException.get_parsed_error_message(result.stderr)}"
                )
            else:
                raise IBMCloudException(result.stderr)
    else:
        click.echo(result.stdout)

    if full_installation:
        logging.info(f"Waiting for creation of cluster '{cluster_name}' to complete.")
        wait_for_cluster_readiness(cluster_name)

        logging.info(
            click.style(
                f"Installing Cloud Pak for Data on cluster '{cluster_name}'.",
                bold=True,
            )
        )

        install_cp4d_with_preinstall(cluster_name)
