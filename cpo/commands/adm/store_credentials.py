#  Copyright 2021, 2022 IBM Corporation
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

import cpo.config

from cpo.utils.logging import loglevel_command


@loglevel_command()
@click.option("--artifactory-password", help="Artifactory password")
@click.option("--artifactory-username", help="Artifactory username")
@click.option(
    "--ibm-cloud-pak-for-data-entitlement-key",
    help="IBM Cloud Pak for Data entitlement key (see https://myibm.ibm.com/products-services/containerlibrary)",
)
def store_credentials(
    artifactory_password: Optional[str],
    artifactory_username: Optional[str],
    ibm_cloud_pak_for_data_entitlement_key: Optional[str],
):
    """Store credentials in a configuration file"""

    credentials_to_be_stored = locals().copy()

    cpo.config.configuration_manager.store_credentials(credentials_to_be_stored)
