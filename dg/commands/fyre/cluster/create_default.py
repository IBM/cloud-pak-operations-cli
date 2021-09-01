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

from dg.lib.fyre.ocp_plus_api_manager import OCPPlusAPIManager
from dg.lib.fyre.utils.click import fyre_command_options
from dg.utils.logging import loglevel_command


@loglevel_command(
    context_settings=dg.lib.click.utils.create_default_map_from_json_file(
        dg.config.data_gate_configuration_manager.get_dg_credentials_file_path()
    )
)
@fyre_command_options
@click.option("--alias", help="Alias used to reference a cluster instead of its server URL")
@click.option("--platform", help="Platform", required=True, type=click.Choice(["p", "x", "z"]))
@click.option("--site", help="OCP+ site", type=click.Choice(["rtp", "svl"]))
def create_default(
    fyre_api_user_name: str, fyre_api_key: str, alias: Optional[str], platform: str, site: Optional[str]
):
    """Create a new OCP+ cluster with defaults"""

    dg.utils.network.disable_insecure_request_warning()

    assigned_cluster_name = OCPPlusAPIManager(fyre_api_user_name, fyre_api_key).create_cluster_with_defaults(
        alias, platform, site
    )

    click.echo(f"Created cluster '{assigned_cluster_name}'")
