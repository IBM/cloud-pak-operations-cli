#  Copyright 2022 IBM Corporation
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

from plugins.lib.cluster.oc import (
    get_db2_data_gate_pod_name_from_deployment_name,
    infer_custom_resource_id_from_deployment_name,
    is_pod_not_running_from_deployment,
    is_pod_ready,
    is_pod_running_from_deployment,
    replace_image_in_db2_data_gate_instance_service_custom_resource,
)

from cpo.lib.openshift import oc
from cpo.utils.logging import loglevel_command
from cpo.utils.wait import wait_for

logger = logging.getLogger(__name__)


@loglevel_command()
@click.option("--container-stunnel", help="container-stunnel image tag")
@click.option("--container-stunnel-init", help="container-stunnel-init image tag")
@click.option("--data-gate-api", help="data-gate-api image tag")
@click.option("--data-gate-apply", help="data-gate-apply image tag")
@click.option("--data-gate-init", help="data-gate-init image tag")
@click.option("--data-gate-server", help="data-gate-server image tag")
@click.option("--data-gate-ui", help="data-gate-ui image tag")
@click.option("--deployment-name", help="OpenShift deployment name")
@click.option("--pull-prefix", help="Pull prefix of the new component(s)")
def replace_db2_data_gate_images(
    container_stunnel: str,
    container_stunnel_init: str,
    data_gate_api: str,
    data_gate_apply: str,
    data_gate_init: str,
    data_gate_server: str,
    data_gate_ui: str,
    deployment_name: str,
    pull_prefix: str,
):
    """Replace a single or multiple specific component(s) of a given Db2 Data Gate deployment.
    The pull prefix has to be the same for all components to be replaced."""

    # if the user didn't specify a deployment name, search for "data-gate" in
    # the available deployments and use the first result
    deployment_name = deployment_name if (deployment_name is not None) else oc.get_deployment_name("data-gate")[0]

    components = {}
    if container_stunnel:
        components["container_stunnel"] = container_stunnel
    if container_stunnel_init:
        components["container_stunnel_init"] = container_stunnel_init
    if data_gate_apply:
        components["datagate_apply"] = data_gate_apply
    if data_gate_api:
        components["datagate_api"] = data_gate_api
    if data_gate_init:
        components["datagate_init"] = data_gate_init
    if data_gate_server:
        components["datagate_server"] = data_gate_server
    if data_gate_ui:
        components["datagate_ui"] = data_gate_ui

    dg_id = infer_custom_resource_id_from_deployment_name(deployment_name)
    custom_resource_json = oc.get_custom_resource("datagateinstanceservice", dg_id)

    for component, image_tag in components.items():
        replace_image_in_db2_data_gate_instance_service_custom_resource(
            custom_resource_json, component, image_tag, pull_prefix
        )

    oc.replace_custom_resource(custom_resource_json)

    data_gate_pod_name = get_db2_data_gate_pod_name_from_deployment_name(deployment_name)
    logger.info("Waiting for Db2 Data Gate pod to restart")
    logger.info("Waiting for pod to change from status 'Running' to another status")
    wait_for(
        300,
        30,
        f"Waiting for pod '{data_gate_pod_name}' to change from status 'Running' to another status",
        is_pod_not_running_from_deployment,
        deployment_name,
    )

    logger.info("Waiting for new pod to change to status 'Running'")
    wait_for(
        600,
        30,
        f"Waiting for pod '{data_gate_pod_name}' to change to status 'Running'",
        is_pod_running_from_deployment,
        deployment_name,
    )

    data_gate_pod_name = get_db2_data_gate_pod_name_from_deployment_name(deployment_name)
    logger.info(f"Waiting for pod '{data_gate_pod_name}' to become ready")
    wait_for(300, 30, f"Waiting for pod '{data_gate_pod_name}' to become ready", is_pod_ready, data_gate_pod_name)
