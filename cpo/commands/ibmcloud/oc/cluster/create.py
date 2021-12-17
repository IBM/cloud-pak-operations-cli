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

import logging

from typing import Optional

import click
import semver

import cpo.config.cluster_credentials_manager
import cpo.lib.ibmcloud.oc.cluster
import cpo.lib.ibmcloud.status

from cpo.config.cluster_credentials_manager import cluster_credentials_manager
from cpo.lib.error import IBMCloudException
from cpo.lib.ibmcloud import (
    execute_ibmcloud_command,
    execute_ibmcloud_command_without_check,
)
from cpo.lib.ibmcloud.install import install_cp4d_with_preinstall
from cpo.lib.ibmcloud.login import login as login_to_ibm_cloud
from cpo.lib.ibmcloud.oc.cluster.rm import delete_ibmcloud_cluster
from cpo.lib.ibmcloud.openshift import (
    get_full_openshift_version,
    get_latest_supported_openshift_version,
)
from cpo.lib.ibmcloud.status import (
    cluster_exists,
    wait_for_cluster_deletion,
    wait_for_cluster_readiness,
    wait_for_ingress_readiness,
)
from cpo.lib.ibmcloud.vlan_manager import VLANManager
from cpo.utils.logging import loglevel_command

logger = logging.getLogger(__name__)


def validate_ocp_version(ctx, param, value) -> Optional[semver.VersionInfo]:
    result: Optional[semver.VersionInfo] = None

    if value is not None:
        try:
            result = semver.VersionInfo.parse(value)
        except ValueError:
            raise click.BadParameter("Invalid string format")

    return result


@loglevel_command()
@click.option("-a", "--alias", help="Alias used to reference a cluster instead of its server URL")
@click.option("-c", "--cluster-name", help="cluster name", required=True)
@click.option("-f", "--force", help="Remove any prompts during cluster creation.", is_flag=True)
@click.option(
    "-i",
    "--full-install",
    "full_installation",
    help="Perform a full installation of Cloud Pak for Data after the cluster is provisioned.",
    is_flag=True,
)
@click.option("-o", "--openshift-version", callback=validate_ocp_version, help="OpenShift version")
@click.option(
    "-r",
    "--rm",
    "remove_existing",
    help="Delete any existing cluster with the given name before creating a new one.",
    is_flag=True,
)
def create(
    alias: Optional[str],
    cluster_name: str,
    force: bool,
    full_installation: bool,
    openshift_version: Optional[semver.VersionInfo],
    remove_existing: bool,
):
    """Create a new Red Hat OpenShift on IBM Cloud cluster"""

    if alias is not None:
        cluster_credentials_manager.raise_if_alias_exists(alias)

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
            logging.info(f"Skipping deletion, as cluster '{cluster_name}' could not be found")

    logging.info(
        click.style(
            f"Creating cluster with name '{cluster_name}' in IBM Cloud",
            bold=True,
        )
    )

    full_openshift_version: Optional[str] = None

    if openshift_version is None:
        full_openshift_version = get_latest_supported_openshift_version()
    else:
        full_openshift_version = get_full_openshift_version(openshift_version)

    zone = "sjc03"
    vlan_manager = VLANManager(zone)
    ibmcloud_oc_cluster_create_classic_args = [
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
        "--private-vlan",
        vlan_manager.default_private_vlan,
        "--public-service-endpoint",
        "--public-vlan",
        vlan_manager.default_public_vlan,
        "--version",
        full_openshift_version,
        "--workers",
        "3",
        "--zone",
        zone,
    ]

    ibmcloud_oc_cluster_create_classic_result = execute_ibmcloud_command_without_check(
        ibmcloud_oc_cluster_create_classic_args, capture_output=True
    )

    if ibmcloud_oc_cluster_create_classic_result.return_code != 0:
        if "E0007" in ibmcloud_oc_cluster_create_classic_result.stderr:
            # a cluster with the same name already exists
            raise IBMCloudException(ibmcloud_oc_cluster_create_classic_result.stderr)
        else:
            if cluster_exists(cluster_name):
                # There was an error, but the cluster was created nonetheless, print a warning
                logging.warning(
                    f"An error occurred while creating the cluster, but 'ibmcloud oc cluster ls' shows a cluster with "
                    f"the name '{cluster_name}' – error details:\n"
                    f"{IBMCloudException.get_parsed_error_message(ibmcloud_oc_cluster_create_classic_result.stderr)}"
                )
            else:
                raise IBMCloudException(ibmcloud_oc_cluster_create_classic_result.stderr)
    else:
        click.echo(ibmcloud_oc_cluster_create_classic_result.stdout)

    logging.info(f"Waiting for creation of cluster '{cluster_name}' to complete:")
    wait_for_cluster_readiness(cluster_name)
    # although the /global/v2/getCluster REST endpoint returns the status of
    # Ingress components, it is only set once the /global/v2/alb/getStatus
    # REST endpoint was called, which also returns the status of Ingress components
    logging.info(f"Waiting for Ingress components status of cluster '{cluster_name}' to be healthy:")
    wait_for_ingress_readiness(cluster_name)

    server = cpo.lib.ibmcloud.status.get_cluster_status(cluster_name).get_server_url()

    cluster_credentials_manager.add_cluster(
        alias if (alias is not None) else "",
        server,
        cpo.lib.ibmcloud.oc.cluster.CLUSTER_TYPE_ID,
        {
            "cluster_name": cluster_name,
        },
    )

    # without this step, "oc login …" fails with the following error:
    # Error from server (InternalError): Internal error occurred: unexpected response: 500”
    execute_ibmcloud_command(["oc", "cluster", "config", "--cluster", cluster_name])

    if full_installation:
        logging.info(
            click.style(
                f"Installing Cloud Pak for Data on cluster '{cluster_name}'",
                bold=True,
            )
        )

        install_cp4d_with_preinstall(cluster_name)
