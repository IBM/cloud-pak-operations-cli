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

from typing import Optional

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
@click.option("--json", help="Prints the command output in JSON format", is_flag=True)
@click.option("--platform", help="Platform", required=True, type=click.Choice(["p", "x", "z"]))
@click.option("--site", help="OCP+ site", type=click.Choice(["rtp", "svl"]))
def get_default_sizes(fyre_user_name: str, fyre_api_key: str, json: bool, platform: str, site: Optional[str]):
    """Get default node sizes"""

    dg.utils.network.disable_insecure_request_warning()
    OCPPlusAPIManager(fyre_user_name, fyre_api_key).get_default_sizes(platform, site).format_default_sizes(json)