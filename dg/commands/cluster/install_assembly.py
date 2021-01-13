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

from typing import Union

import click
import semver

from click_option_group import optgroup

import dg.config.cluster_credentials_manager
import dg.lib.click
import dg.lib.openshift
import dg.utils.download

from dg.lib.cloud_pak_for_data.cpd_manager import (
    AbstractCloudPakForDataManager,
    CloudPakForDataAssemblyBuildType,
)
from dg.lib.cloud_pak_for_data.cpd_manager_factory import (
    CloudPakForDataManagerFactory,
)


@click.command(
    context_settings=dg.lib.click.create_default_map_from_dict(
        dg.config.cluster_credentials_manager.cluster_credentials_manager.get_current_credentials()
    )
)
@optgroup.group("Shared options")
@optgroup.option("--server", required=True, help="OpenShift server URL")
@optgroup.option("--username", help="OpenShift username")
@optgroup.option("--password", help="OpenShift password")
@optgroup.option("--token", help="OpenShift OAuth access token")
@optgroup.option(
    "--assembly-name", required=True, help="Name of the assembly to be installed"
)
@optgroup.option(
    "--build-type",
    default=f"{CloudPakForDataAssemblyBuildType.RELEASE.name}",
    help=f"Build type (default: {CloudPakForDataAssemblyBuildType.RELEASE.name.lower()})",
    type=click.Choice(
        list(map(lambda x: x.name.lower(), CloudPakForDataAssemblyBuildType)),
        case_sensitive=False,
    ),
)
@optgroup.option(
    "--storage-class",
    required=True,
    help="Storage class used for installation",
)
@optgroup.option(
    "--version",
    default=AbstractCloudPakForDataManager.get_default_cloud_pak_for_data_version(),
    help="Cloud Pak for Data version",
)
@optgroup.group("Release build options")
@optgroup.option(
    "--ibm-cloud-pak-for-data-entitlement-key",
    help="IBM Cloud Pak for Data entitlement key",
)
@optgroup.group("Development build options")
@optgroup.option("--artifactory-user-name", help="Artifactory user name")
@optgroup.option("--artifactory-api-key", help="Artifactory API key")
@click.pass_context
def install_assembly(
    ctx: click.Context,
    ibm_cloud_pak_for_data_entitlement_key: Union[str, None],
    artifactory_user_name: str,
    artifactory_api_key: str,
    server: str,
    username: Union[str, None],
    password: Union[str, None],
    token: Union[str, None],
    assembly_name: str,
    build_type: str,
    storage_class: str,
    version: str,
):
    """Install an IBM Cloud Pak for Data assembly"""

    cloud_pak_for_data_assembly_build_type = CloudPakForDataAssemblyBuildType[
        build_type.upper()
    ]

    dg.lib.click.check_cloud_pak_for_data_options(
        ctx, cloud_pak_for_data_assembly_build_type, locals().copy()
    )

    dg.lib.click.log_in_to_openshift_cluster(ctx, locals().copy())

    cloud_pak_for_data_manager = (
        CloudPakForDataManagerFactory.get_cloud_pak_for_data_manager(
            semver.VersionInfo.parse(version)
        )(cloud_pak_for_data_assembly_build_type)
    )

    cloud_pak_for_data_manager.install_assembly_with_prerequisites(
        artifactory_user_name,
        artifactory_api_key,
        ibm_cloud_pak_for_data_entitlement_key,
        assembly_name,
        storage_class,
    )
