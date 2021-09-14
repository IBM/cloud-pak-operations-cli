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

from tabulate import tabulate

import dg.config
import dg.config.cluster_credentials_manager
import dg.lib.click.utils
import dg.lib.cluster
import dg.utils.download

from dg.lib.cloud_pak_for_data.cpd_4_0_0.cpd_manager import (
    CloudPakForDataManager,
)
from dg.lib.cloud_pak_for_data.cpd_4_0_0.types.cloud_pak_for_data_service_license import (
    CloudPakForDataLicense,
)
from dg.lib.openshift.utils.click import openshift_server_options
from dg.utils.logging import loglevel_command


@loglevel_command(
    context_settings=dg.lib.click.utils.create_default_map_from_dict(
        dg.config.cluster_credentials_manager.cluster_credentials_manager.get_current_credentials()
    )
)
@openshift_server_options
@click.option("--accept-license", help="Accept IBM Cloud Pak for Data license", is_flag=True)
@click.option("--force", "-f", help="Skip confirmation", is_flag=True)
@click.option(
    "--ibm-cloud-pak-for-data-entitlement-key",
    "-e",
    help="IBM Cloud Pak for Data entitlement key (see https://myibm.ibm.com/products-services/containerlibrary)",
    required=True,
)
@click.option(
    "--license",
    help="IBM Cloud Pak for Data license",
    required=True,
    type=click.Choice(
        list(map(lambda x: x.name.lower(), CloudPakForDataLicense)),
        case_sensitive=False,
    ),
)
@click.option("--project", default="zen", help="Project where the Cloud Pak for Data control plane is installed")
@click.option("--storage-class", help="Storage class used for installation", required=True)
@click.pass_context
def install(
    ctx: click.Context,
    server: Optional[str],
    username: Optional[str],
    password: Optional[str],
    token: Optional[str],
    insecure_skip_tls_verify: Optional[bool],
    accept_license: bool,
    force: bool,
    ibm_cloud_pak_for_data_entitlement_key: str,
    license: str,
    project: str,
    storage_class: str,
):
    """Install IBM Cloud Pak for Data"""

    if not accept_license:
        raise click.UsageError("Missing option '--accept-license'", ctx)

    if not force:
        click.confirm(
            f"Do you really want to install IBM Cloud Pak for Data on server {server} in project '{project}'?",
            abort=True,
        )

    cloud_pak_for_data_access_data = CloudPakForDataManager(
        dg.lib.click.utils.get_cluster_credentials(ctx, locals().copy())
    ).install_cloud_pak_for_data(
        "ibm-common-services",
        project,
        ibm_cloud_pak_for_data_entitlement_key,
        CloudPakForDataLicense[license.capitalize()],
        storage_class,
    )

    click.echo(
        tabulate(
            [
                [
                    "IBM Cloud Pak for Data URL",
                    cloud_pak_for_data_access_data.cloud_pak_for_data_url,
                ],
                [
                    "Initial admin password",
                    cloud_pak_for_data_access_data.initial_admin_password,
                ],
            ],
        )
    )
