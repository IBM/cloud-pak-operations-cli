#  Copyright 2022, 2023 IBM Corporation
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

from cpo.lib.click.utils import get_semver_version
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
    default="https://na.artifactory.swg-devops.com/artifactory/api/pypi/hyc-ibm-sap-cp4d-team-pypi-local/simple",
)
@click.option("--user", help="Install to user site-packages directory", is_flag=True)
@click.option("--version", callback=get_semver_version, help="Plug-in version")
@click.argument("distribution-package-names", nargs=-1)
def install(
    artifactory_username: str,
    artifactory_password: str,
    distribution_package_names: list[str],
    repository_url: str,
    user: bool,
    version: semver.Version | None,
):
    """Install IBM-internal CLI plug-ins"""

    for distribution_package_name in distribution_package_names:
        kwargs = {"user": user, "version": version}

        if version is not None:
            if (
                local_distribution_package_version := _get_distribution_package_version(distribution_package_name)
            ) is not None:
                if version == local_distribution_package_version:
                    logger.info(f"Plug-in '{distribution_package_name}' (version: {version}) is already installed")

                    continue

                if version > local_distribution_package_version:
                    logger.info(
                        f"Upgrading plug-in '{distribution_package_name}' from version "
                        f"{local_distribution_package_version} to {version}"
                    )
                else:
                    logger.info(
                        f"Downgrading plug-in '{distribution_package_name}' from version "
                        f"{local_distribution_package_version} to {version}"
                    )

                kwargs["upgrade"] = True

        IBMInternalPluginInstaller(artifactory_username, artifactory_password, repository_url).install(
            distribution_package_name, **kwargs
        )


def _get_distribution_package_version(distribution_package_name: str) -> semver.Version | None:
    distribution_package_version: semver.Version | None = None

    try:
        distribution_package_version = semver.Version.parse(importlib.metadata.version(distribution_package_name))
    except importlib.metadata.PackageNotFoundError:
        pass

    return distribution_package_version
