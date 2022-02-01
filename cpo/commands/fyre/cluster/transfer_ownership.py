#  Copyright 2021 IBM Corporation
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
import cpo.config.cluster_credentials_manager
import cpo.lib.click.utils
import cpo.lib.fyre.cluster
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
@click.option("--cluster-name", help="Name of the OCP+ cluster to be transferred", required=True)
@click.option("--comment", help="Comment")
@click.option("--new-owner", help="User ID, username, or e-mail address of new owner")
@click.option("--new-product-group-id", help="ID of new FYRE product group", type=click.INT)
@click.option("--site", help="OCP+ site", type=click.Choice(["rtp", "svl"]))
@click.pass_context
def transfer_ownership(
    ctx: click.Context,
    fyre_api_user_name: str,
    fyre_api_key: str,
    cluster_name: str,
    comment: Optional[str],
    new_owner: Optional[str],
    new_product_group: Optional[int],
    site: Optional[str],
):
    """Transfer ownership of an OCP+ cluster to a new user and/or product group"""

    if new_owner is None and new_product_group is None:
        raise click.UsageError("You must set options '--new-owner' and/or '--new-product-group-id'.", ctx)

    cpo.utils.network.disable_insecure_request_warning()
    OCPPlusAPIManager(fyre_api_user_name, fyre_api_key).transfer(
        cluster_name, new_owner, new_product_group, comment, site
    )
