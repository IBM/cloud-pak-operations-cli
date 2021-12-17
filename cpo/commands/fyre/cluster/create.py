#  Copyright 2020, 2021 IBM Corporation
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

import cpo.config
import cpo.lib.click.utils
import cpo.utils.network

from cpo.lib.fyre.data.ocpplus_cluster_specification import (
    HAProxyTimoutSettings,
    OCPPlusClusterSpecification,
    QuickBurnSettings,
    WorkerNodeSettings,
)
from cpo.lib.fyre.ocp_plus_api_manager import OCPPlusAPIManager
from cpo.lib.fyre.utils.click import fyre_command_optgroup_options
from cpo.utils.logging import loglevel_command


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
    context_settings=cpo.lib.click.utils.create_default_map_from_json_file(
        cpo.config.configuration_manager.get_credentials_file_path()
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
@optgroup.option(
    "--ocp-version",
    callback=validate_ocp_version,
    help='OpenShift version (see "cpo fyre info get-openshift-versions")',
)
@optgroup.option("--platform", help="Platform", type=click.Choice(["p", "x", "z"]))
@optgroup.option("--product-group-id", help="FYRE product group ID", type=click.INT)
@optgroup.option("--pull-secret", help="Pull secret")
@optgroup.option("--site", help="OCP+ site", type=click.Choice(["rtp", "svl"]))
@optgroup.option(
    "--ssh-key", help='Public SSH key to be installed on the infrastructure node (e.g., "$(cat ~/.ssh/id_rsa.pub)")'
)
@optgroup.group("Worker node options")
@optgroup.option(
    "--worker-node-additional-disk-size",
    callback=validate_worker_node_additional_disk_size,
    help="Size of additional worker node disk",
    multiple=True,
    type=click.IntRange(1, 1000),
)
@optgroup.option("--worker-node-count", help="Number of worker nodes", type=click.INT)
@optgroup.option("--worker-node-num-cpus", help="Number of CPUs per worker node", type=click.IntRange(1, 16))
@optgroup.option("--worker-node-ram-size", help="RAM size per worker node", type=click.IntRange(1, 64))
@optgroup.group("Quick burn options")
@optgroup.option("--quick-burn-size", help="Quick burn size", type=click.Choice(["medium", "large"]))
@optgroup.option("--quick-burn-time-to-live", help="Quick burn TTL (hours)", type=click.INT)
@click.pass_context
def create(
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
    worker_node_num_cpus: Optional[int],
    worker_node_ram_size: Optional[int],
    quick_burn_size: Optional[str],
    quick_burn_time_to_live: Optional[int],
):
    """Create a new OCP+ cluster"""

    if ((quick_burn_size is not None) and (quick_burn_time_to_live is None)) or (
        (quick_burn_size is None) and (quick_burn_time_to_live is not None)
    ):
        raise click.UsageError(
            "You must either set options '--quick-burn-size' and '--quick-burn-time-to-live' or none of them.",
            ctx,
        )

    quick_burn_settings: Optional[QuickBurnSettings] = None

    if (quick_burn_size is not None) and (quick_burn_time_to_live is not None):
        quick_burn_settings = QuickBurnSettings(quick_burn_size, quick_burn_time_to_live)

        if (
            (len(worker_node_additional_disk_size) != 0)
            or (worker_node_count is not None)
            or (worker_node_num_cpus is not None)
            or (worker_node_ram_size is not None)
        ):
            raise click.UsageError("Worker node options must not be specified when using quick burn options.")

    cpo.utils.network.disable_insecure_request_warning()

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
            quick_burn_settings,
            ssh_key,
            WorkerNodeSettings(
                worker_node_additional_disk_size, worker_node_count, worker_node_num_cpus, worker_node_ram_size
            ),
        ),
        site,
    )

    click.echo(f"Created cluster '{assigned_cluster_name}'")
