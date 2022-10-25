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
import cpo.lib.click.utils
import cpo.utils.network

from cpo.lib.fyre.ocp_plus_api_manager import OCPPlusAPIManager
from cpo.lib.fyre.utils.click import fyre_command_options
from cpo.utils.logging import loglevel_command


@loglevel_command(
    context_settings=cpo.lib.click.utils.create_default_map_from_json_file(
        cpo.config.configuration_manager.get_credentials_file_path()
    )
)
@fyre_command_options
@click.option("--json", help="Prints the command output in JSON format", is_flag=True)
@click.option("--platform", help="Platform", required=True, type=click.Choice(["p", "x", "z"]))
@click.option("--site", help="OCP+ site", type=click.Choice(["rtp", "svl"]))
def get_default_sizes(
    fyre_api_user_name: str,
    fyre_api_key: str,
    disable_strict_response_schema_check: bool,
    json: bool,
    platform: str,
    site: Optional[str],
):
    """Get default node sizes"""

    cpo.utils.network.disable_insecure_request_warning()
    OCPPlusAPIManager(fyre_api_user_name, fyre_api_key, disable_strict_response_schema_check).get_default_sizes(
        platform, site
    ).format_default_sizes(json)
