#  Copyright 2023, 2024 IBM Corporation
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

import importlib.metadata
import logging

import click
import semver

import cpo.config.cluster_credentials_manager
import cpo.lib.click.utils

from cpo.lib.ibm_internal_plugin.ibm_internal_plugin_manager import IBMInternalPluginInstaller
from cpo.utils.logging import loglevel_command

logger = logging.getLogger(__name__)


@loglevel_command(
    context_settings=cpo.lib.click.utils.create_default_map_from_dict(
        cpo.config.cluster_credentials_manager.cluster_credentials_manager.get_current_credentials()
    )
)
@click.option(
    "--artifactory-username",
    help="Artifactory username (IBM e-mail address)",
    required=True,
)
@click.option(
    "--artifactory-password",
    help="Artifactory identity token (Artifactory website → 'Edit Profile' → 'Identity Tokens')",
    required=True,
)
@click.option(
    "--repository-url",
    default="https://na.artifactory.swg-devops.com/artifactory/api/pypi/hyc-cloud-pak-operations-cli-team-pypi-local/"
    "simple",
)
@click.option("--user", help="Install to user site-packages directory", is_flag=True)
def upgrade_plugins(
    artifactory_username: str,
    artifactory_password: str,
    repository_url: str,
    user: bool,
):
    """Upgrade IBM-internal CLI plug-ins"""

    ibm_internal_plugin_installer = IBMInternalPluginInstaller(
        artifactory_username, artifactory_password, repository_url
    )

    for package in ibm_internal_plugin_installer.get_packages():
        try:
            distribution_package_name = package[0]
            local_package_version = semver.Version.parse(importlib.metadata.version(distribution_package_name))
            latest_package_version = semver.Version.parse(package[1])

            if local_package_version < latest_package_version:
                logger.info(
                    f"Upgrading plug-in '{distribution_package_name}' from version {local_package_version} to "
                    f"{latest_package_version}"
                )

                IBMInternalPluginInstaller(artifactory_username, artifactory_password, repository_url).install(
                    distribution_package_name, user=user, upgrade=True
                )
        except importlib.metadata.PackageNotFoundError:
            pass
