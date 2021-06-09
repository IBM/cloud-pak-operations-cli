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

import click

import dg.config
import dg.lib.click.utils
import dg.utils.network

from dg.lib.fyre.api_manager import OCPPlusAPIManager
from dg.utils.logging import loglevel_command


@loglevel_command(
    context_settings=dg.lib.click.utils.create_default_map_from_json_file(
        dg.config.data_gate_configuration_manager.get_dg_credentials_file_path()
    )
)
@click.option("--fyre-user-name", help="FYRE API user name", required=True)
@click.option("--fyre-api-key", help="FYRE API key (see https://fyre.svl.ibm.com/account)", required=True)
@click.option("--request-id", help="Request ID", required=True)
def wait_for_request(fyre_user_name: str, fyre_api_key: str, request_id: str):
    """Wait for request to complete"""

    dg.utils.network.disable_insecure_request_warning()
    OCPPlusAPIManager(fyre_user_name, fyre_api_key).wait_for_request_completion(request_id)
