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

import click

import cpo.config.cluster_credentials_manager
import cpo.lib.click.utils

from cpo.lib.ibm_internal_plugin.ibm_internal_plugin_manager import IBMInternalPluginInstaller
from cpo.utils.logging import loglevel_command


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
@click.argument("distribution-package-names", nargs=-1)
def install(
    artifactory_username: str,
    artifactory_password: str,
    distribution_package_names: list[str],
    repository_url: str,
    user: bool,
):
    """Install IBM-internal CLI plug-ins"""

    for distribution_package_name in distribution_package_names:
        IBMInternalPluginInstaller(artifactory_username, artifactory_password, repository_url).install(
            distribution_package_name, user
        )
