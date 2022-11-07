#  Copyright 2022 IBM Corporation
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
import cpo.lib.ibm_internal_plugin.install

from cpo.utils.logging import loglevel_command


@loglevel_command(
    context_settings=cpo.lib.click.utils.create_default_map_from_dict(
        cpo.config.cluster_credentials_manager.cluster_credentials_manager.get_current_credentials()
    )
)
@click.argument("distribution-package-name")
@click.option(
    "--artifactory-username",
    help="Artifactory username. The username is usually the IBM e-mail address.",
    required=True,
)
@click.option(
    "--artifactory-password",
    help="Artifactory password. The password is usually the API key located in the 'Edit Profile' page in Artifactory.",
    required=True,
)
def install(distribution_package_name: str, artifactory_username: str, artifactory_password: str):
    """Install an IBM-internal CLI plug-in"""

    cpo.lib.ibm_internal_plugin.install.install(distribution_package_name, artifactory_username, artifactory_password)
