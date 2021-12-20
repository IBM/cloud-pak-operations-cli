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

from typing import List, Optional, Tuple, Union

import click

import cpo.config
import cpo.config.cluster_credentials_manager
import cpo.lib.click.utils
import cpo.lib.cluster
import cpo.utils.download

from cpo.lib.click.cpd_service_spec_param_type import (
    CloudPakForDataServiceSpecParamType,
)
from cpo.lib.cloud_pak_for_data.cpd_4_0_0.cpd_manager import (
    CloudPakForDataManager,
)
from cpo.lib.cloud_pak_for_data.cpd_4_0_0.types.cloud_pak_for_data_service_license import (
    CloudPakForDataServiceLicense,
)
from cpo.lib.cloud_pak_for_data.cpd_4_0_0.types.cloud_pak_for_data_storage_vendor import (
    CloudPakForDataStorageVendor,
)
from cpo.lib.openshift.utils.click import openshift_server_options
from cpo.utils.logging import loglevel_command


@loglevel_command(
    context_settings=cpo.lib.click.utils.create_default_map_from_dict(
        cpo.config.cluster_credentials_manager.cluster_credentials_manager.get_current_credentials()
    )
)
@openshift_server_options
@click.option("--accept-license", help="Accept IBM Cloud Pak for Data license", is_flag=True)
@click.option(
    "--catalog-source",
    help="Catalog source for the service operator. If not specified, use default catalog for the operator \
(usually 'ibm-operator-catalog')"
)
@click.option(
    "--installation-option",
    help="Additional installation option",
    multiple=True,
    type=(str, CloudPakForDataServiceSpecParamType()),
)
@click.option(
    "--license",
    help="License",
    type=click.Choice(
        list(map(lambda x: x.name.lower(), CloudPakForDataServiceLicense)),
        case_sensitive=False,
    ),
)
@click.option("--project", default="zen", help="Project where the Cloud Pak for Data control plane is installed")
@click.option("--service-name", help="IBM Cloud Pak for Data service name", required=True)
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
def install(
    ctx: click.Context,
    server: Optional[str],
    username: Optional[str],
    password: Optional[str],
    token: str,
    insecure_skip_tls_verify: Optional[bool],
    accept_license: bool,
    catalog_source: Optional[str],
    installation_option: List[Tuple[str, Union[bool, int, str]]],
    license: Optional[str],
    project: str,
    service_name: str,
    storage_class: Optional[str],
    storage_vendor: Optional[str],
):
    """Install IBM Cloud Pak for Data service"""

    if not accept_license:
        raise click.UsageError("Missing option '--accept-license'", ctx)

    cloud_pak_for_data_manager = CloudPakForDataManager(
        cpo.lib.click.utils.get_cluster_credentials(ctx, locals().copy())
    )

    if license is None:
        license_types = ",\n\t".join(
            list(
                map(
                    lambda x: x.name.lower(),
                    cloud_pak_for_data_manager.get_license_types_for_cloud_pak_for_data_service(service_name),
                )
            )
        )

        raise click.UsageError(f"Missing option '--license'. Choose from:\n\t{license_types}", ctx)

    cloud_pak_for_data_service_license = CloudPakForDataServiceLicense[license.capitalize()]
    cloud_pak_for_data_storage_vendor = (
        CloudPakForDataStorageVendor[storage_vendor.lower()] if storage_vendor is not None else None
    )

    if (storage_class is not None) and (storage_vendor is not None):
        raise click.UsageError("You must not set options '--storage-class' and '--storage-vendor'.", ctx)

    storage_option: Optional[Union[str, CloudPakForDataStorageVendor]] = (
        storage_class if storage_class is not None else cloud_pak_for_data_storage_vendor
    )

    cloud_pak_for_data_manager.install_cloud_pak_for_data_service(
        "ibm-common-services",
        project,
        service_name,
        cloud_pak_for_data_service_license,
        installation_option,
        storage_option,
        catalog_source
    )
