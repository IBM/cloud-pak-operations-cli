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

import dg.config
import dg.config.cluster_credentials_manager
import dg.lib.click
import dg.lib.cluster
import dg.lib.openshift
import dg.utils.download

from dg.lib.cloud_pak_for_data.cpd_manager import (
    AbstractCloudPakForDataManager,
)
from dg.lib.cloud_pak_for_data.cpd_manager_factory import (
    CloudPakForDataManagerFactory,
)


@click.command(
    context_settings=dg.lib.click.create_default_map_from_dict(
        dg.config.cluster_credentials_manager.cluster_credentials_manager.get_current_credentials()
    )
)
@click.option("--server", required=True, help="OpenShift server URL")
@click.option("--username", help="OpenShift username")
@click.option("--password", help="OpenShift password")
@click.option("--token", help="OpenShift OAuth access token")
@click.option("--artifactory-user-name", required=True, help="Artifactory user name")
@click.option("--artifactory-api-key", required=True, help="Artifactory API key")
@click.option(
    "--ibm-cloud-pak-for-data-entitlement-key",
    help="IBM Cloud Pak for Data entitlement key",
)
@click.option(
    "--storage-class",
    required=True,
    help="Storage class used for installation",
)
@click.option(
    "--version",
    default=AbstractCloudPakForDataManager.get_default_cloud_pak_for_data_version(),
    help="Cloud Pak for Data version",
)
@click.option("--use-dev", is_flag=True, help="Use development build")
@click.pass_context
def install_cloud_pak_for_data(
    ctx: click.Context,
    server: str,
    username: Union[str, None],
    password: Union[str, None],
    token: Union[str, None],
    artifactory_user_name: str,
    artifactory_api_key: str,
    ibm_cloud_pak_for_data_entitlement_key: Union[str, None],
    storage_class: str,
    version: str,
    use_dev: bool,
):
    """Install IBM Cloud Pak for Data"""

    if not use_dev and ibm_cloud_pak_for_data_entitlement_key is None:
        raise click.UsageError(
            "Missing option '--ibm-cloud-pak-for-data-entitlement-key'.",
            ctx,
        )

    dg.lib.click.log_in_to_openshift_cluster(ctx, locals().copy())

    override_yaml_file_path = (
        dg.config.data_gate_configuration_manager.get_deps_directory_path()
        / "override.yaml"
    )

    cloud_pak_for_data_manager = (
        CloudPakForDataManagerFactory.get_cloud_pak_for_data_manager(
            semver.VersionInfo.parse(version)
        )(use_dev)
    )

    cloud_pak_for_data_manager.check_openshift_version()
    cloud_pak_for_data_manager.install_assembly_with_prerequisites(
        artifactory_user_name,
        artifactory_api_key,
        ibm_cloud_pak_for_data_entitlement_key,
        "lite",
        storage_class,
        override_yaml_file_path=override_yaml_file_path,
    )
