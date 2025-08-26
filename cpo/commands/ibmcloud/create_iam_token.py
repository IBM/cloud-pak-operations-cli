#  Copyright 2025 IBM Corporation
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

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

import cpo.config.cluster_credentials_manager
import cpo.lib.click.utils

from cpo.utils.logging import loglevel_command


@loglevel_command(
    context_settings=cpo.lib.click.utils.create_default_map_from_dict(
        cpo.config.cluster_credentials_manager.cluster_credentials_manager.get_current_credentials()
    )
)
@click.option("--ibm-cloud-api-key", help="IBM Cloud API key", required=True)
def create_iam_token(ibm_cloud_api_key: str):
    """Create an IAM token"""

    click.echo(IAMAuthenticator(ibm_cloud_api_key).token_manager.get_token())
