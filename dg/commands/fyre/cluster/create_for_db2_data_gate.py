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

import re as regex

from typing import List, Optional

import click

from click_option_group import optgroup

import dg.config
import dg.lib.click.utils
import dg.utils.network

from dg.lib.fyre.data.ocpplus_cluster_specification import (
    HAProxyTimoutSettings,
    OCPPlusClusterSpecification,
    WorkerNodeSettings,
)
from dg.lib.fyre.ocp_plus_api_manager import OCPPlusAPIManager
from dg.lib.fyre.utils.click import fyre_command_optgroup_options
from dg.utils.logging import loglevel_command


def validate_haproxy_timeout_setting(ctx, param, value):
    if value is not None:
        search_result = regex.match("\\d+[d|h|m|ms|s|us]", value)

        if search_result is None:
            raise click.BadParameter("Invalid string format")

    return value


def validate_ocp_version(ctx, param, value):
    if value is not None and regex.match("\\d+\\.\\d+(\\.\\d)*", value) is None:
        raise click.BadParameter("Invalid string format")

    return value


def validate_worker_node_additional_disk_size(ctx, param, value: Optional[List[int]]):
    if value is not None and len(value) > 6:
        raise click.BadParameter("Each worker node can only have up to six additional disks.")

    return value


@loglevel_command(
    context_settings=dg.lib.click.utils.create_default_map_from_json_file(
        dg.config.data_gate_configuration_manager.get_dg_credentials_file_path()
    )
)
@optgroup.group("Shared options")
@fyre_command_optgroup_options
@optgroup.option("--alias", help="Alias used to reference a cluster instead of its server URL")
@optgroup.option("--cluster-name", help="Name of the OCP+ cluster to be deployed")
@optgroup.option("--description", help="Cluster description")
@optgroup.option("--expiration", help="Cluster expiration (hours)", type=click.INT)
@optgroup.option("--fips", help="Enable FIPS encryption", is_flag=True)
@optgroup.option("--haproxy-timeout-check", callback=validate_haproxy_timeout_setting, help="HAProxy check timeout")
@optgroup.option("--haproxy-timeout-client", callback=validate_haproxy_timeout_setting, help="HAProxy client timeout")
@optgroup.option("--haproxy-timeout-connect", callback=validate_haproxy_timeout_setting, help="HAProxy connect timeout")
@optgroup.option(
    "--haproxy-timeout-http-keep-alive",
    callback=validate_haproxy_timeout_setting,
    help="HAProxy http-keep-alive timeout",
)
@optgroup.option(
    "--haproxy-timeout-http-request", callback=validate_haproxy_timeout_setting, help="HAProxy http-request timeout"
)
@optgroup.option("--haproxy-timeout-queue", callback=validate_haproxy_timeout_setting, help="HAProxy queue timeout")
@optgroup.option("--haproxy-timeout-server", callback=validate_haproxy_timeout_setting, help="HAProxy server timeout")
@optgroup.option("--ocp-version", callback=validate_ocp_version, default="4.7", help="OpenShift version")
@optgroup.option("--platform", help="Platform", type=click.Choice(["p", "x", "z"]))
@optgroup.option("--product-group-id", help="FYRE product group ID", type=click.INT)
@optgroup.option("--pull-secret", help="Pull secret")
@optgroup.option("--site", help="OCP+ site", type=click.Choice(["rtp", "svl"]))
@optgroup.option("--ssh-key", help="SSH key")
@optgroup.group("Worker node options")
@optgroup.option(
    "--worker-node-additional-disk-size",
    callback=validate_worker_node_additional_disk_size,
    help="Size of additional worker node disk",
    multiple=True,
    type=click.IntRange(1, 1000),
)
@optgroup.option("--worker-node-count", help="Number of worker nodes", type=click.INT)
@click.pass_context
def create_for_db2_data_gate(
    ctx: click.Context,
    fyre_api_user_name: str,
    fyre_api_key: str,
    alias: Optional[str],
    cluster_name: Optional[str],
    description: Optional[str],
    expiration: Optional[int],
    fips: bool,
    haproxy_timeout_check: Optional[str],
    haproxy_timeout_client: Optional[str],
    haproxy_timeout_connect: Optional[str],
    haproxy_timeout_http_keep_alive: Optional[str],
    haproxy_timeout_http_request: Optional[str],
    haproxy_timeout_queue: Optional[str],
    haproxy_timeout_server: Optional[str],
    ocp_version: Optional[str],
    platform: Optional[str],
    product_group_id: Optional[int],
    pull_secret: Optional[str],
    site: Optional[str],
    ssh_key: str,
    worker_node_additional_disk_size: List[int],
    worker_node_count: Optional[int],
):
    """Create a new OCP+ cluster for IBM Db2 Data Gate on IBM Cloud Pak for
    Data"""

    dg.utils.network.disable_insecure_request_warning()

    assigned_cluster_name = OCPPlusAPIManager(fyre_api_user_name, fyre_api_key).create_cluster(
        OCPPlusClusterSpecification(
            alias,
            cluster_name,
            description,
            expiration,
            fips,
            HAProxyTimoutSettings(
                haproxy_timeout_check,
                haproxy_timeout_client,
                haproxy_timeout_connect,
                haproxy_timeout_http_keep_alive,
                haproxy_timeout_http_request,
                haproxy_timeout_queue,
                haproxy_timeout_server,
            ),
            ocp_version,
            platform,
            product_group_id,
            pull_secret,
            None,
            ssh_key,
            WorkerNodeSettings(worker_node_additional_disk_size, worker_node_count, 16, 64),
        ),
        site,
    )

    click.echo(f"Created cluster '{assigned_cluster_name}'")
