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

from typing import Optional, Union

import click

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
    CloudPakForDataServiceLicense,
    Db2ServiceLicense,
)
from dg.lib.cloud_pak_for_data.cpd_4_0_0.types.cloud_pak_for_data_storage_vendor import (
    CloudPakForDataStorageVendor,
)
from dg.lib.openshift.utils.click import openshift_server_options
from dg.utils.logging import loglevel_command

logger = logging.getLogger(__name__)


@loglevel_command(
    context_settings=dg.lib.click.utils.create_default_map_from_dict(
        dg.config.cluster_credentials_manager.cluster_credentials_manager.get_current_credentials()
    )
)
@openshift_server_options
@click.option("--accept-all-licenses", help="Accept all licenses", is_flag=True)
@click.option(
    "--db2-license",
    help="IBM Db2 license",
    required=True,
    type=click.Choice(
        list(map(lambda x: x.name.lower(), Db2ServiceLicense)),
        case_sensitive=False,
    ),
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
@click.option("--storage-class", help="Storage class used for installation")
@click.option(
    "--storage-vendor",
    help="Storage type used for installation",
    type=click.Choice(
        list(map(lambda x: x.name.lower(), CloudPakForDataStorageVendor)),
        case_sensitive=False,
    ),
)
@click.pass_context
def install_db2_data_gate_stack(
    ctx: click.Context,
    server: Optional[str],
    username: Optional[str],
    password: Optional[str],
    token: str,
    insecure_skip_tls_verify: Optional[bool],
    accept_all_licenses: bool,
    db2_license: str,
    license: str,
    project: str,
    storage_class: Optional[str],
    storage_vendor: Optional[str],
):
    """Install IBM Cloud Pak for Data service"""

    if not accept_all_licenses:
        raise click.UsageError("Missing option '--accept-all-licenses'", ctx)

    cloud_pak_for_data_manager = CloudPakForDataManager(
        dg.lib.click.utils.get_cluster_credentials(ctx, locals().copy())
    )

    cloud_pak_for_data_service_license = CloudPakForDataServiceLicense[license.capitalize()]
    cloud_pak_for_data_storage_vendor = (
        CloudPakForDataStorageVendor[storage_vendor.lower()] if storage_vendor is not None else None
    )

    if (storage_class is not None) and (storage_vendor is not None):
        raise click.UsageError("You must not set options '--storage-class' and '--storage_vendor'.", ctx)

    storage_option: Optional[Union[str, CloudPakForDataStorageVendor]] = (
        storage_class if storage_class is not None else cloud_pak_for_data_storage_vendor
    )

    if storage_option is None:
        raise click.UsageError(
            "You must set option '--storage-class' or '--storage_vendor' for the 'datagate' service."
        )

    if not cloud_pak_for_data_manager.cloud_pak_for_data_service_installed(project, "db2oltp"):
        logger.info("Installing Db2")

        cloud_pak_for_data_manager.install_cloud_pak_for_data_service(
            "ibm-common-services",
            project,
            "db2oltp",
            CloudPakForDataServiceLicense[db2_license.capitalize()],
            [],
            storage_option,
        )
    else:
        logger.info("Skippig installation of Db2")

    if not cloud_pak_for_data_manager.cloud_pak_for_data_service_installed(project, "db2wh"):
        logger.info("Installing Db2 Warehouse")

        cloud_pak_for_data_manager.install_cloud_pak_for_data_service(
            "ibm-common-services",
            project,
            "db2wh",
            cloud_pak_for_data_service_license,
            [],
            storage_option,
        )
    else:
        logger.info("Skippig installation of Db2 Warehouse")

    if not cloud_pak_for_data_manager.cloud_pak_for_data_service_installed(project, "dmc"):
        logger.info("Installing Db2 Data Management Console")

        cloud_pak_for_data_manager.install_cloud_pak_for_data_service(
            "ibm-common-services",
            project,
            "dmc",
            cloud_pak_for_data_service_license,
            [],
            storage_option,
        )
    else:
        logger.info("Skippig installation of Db2 Data Management Console")

    if not cloud_pak_for_data_manager.cloud_pak_for_data_service_installed(project, "datagate"):
        logger.info("Installing Db2 Data Gate")

        cloud_pak_for_data_manager.install_cloud_pak_for_data_service(
            "ibm-common-services",
            project,
            "datagate",
            cloud_pak_for_data_service_license,
            [],
            storage_option,
        )
    else:
        logger.info("Skippig installation of Db2 Data Gate")
