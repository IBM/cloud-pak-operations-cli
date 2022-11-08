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

import logging

import click

from cpo.lib.ibmcloud.ibm_cloud_api_manager import IBMCloudAPIManager
from cpo.utils.logging import loglevel_command

logger = logging.getLogger(__name__)


@loglevel_command()
@click.option(
    "--delete-api-key",
    help="Delete the API key created for the IBM Cloud Pak Operations CLI (in IBM Cloud and on disk)",
    is_flag=True,
)
def logout(delete_api_key: bool):
    """Log out from IBM Cloud"""

    ibm_cloud_api_manager = IBMCloudAPIManager()

    if delete_api_key:
        ibm_cloud_api_manager.delete_api_key_in_ibm_cloud_and_on_disk()

    ibm_cloud_api_manager.log_out()
