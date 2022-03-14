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

import logging
import re

import click

from cpo.lib.error import DataGateCLIException
from cpo.lib.openshift import oc
from cpo.utils.logging import loglevel_command
from cpo.utils.wait import wait_for

logger = logging.getLogger(__name__)


@loglevel_command()
@click.option("--deployment-name", help="OpenShift deployment name")
@click.option("--pull-prefix", help="Pull prefix of the new component(s)")
@click.option(
    "--timeout",
    help="""
            Timeout for completing the deployment rollout (cf. oc rollout status)
            If omitted or specified as 0s, the operation will wait until the rollout completes.
""",
)
@click.option("--container-stunnel", help="container-stunnel image tag")
@click.option("--container-stunnel-init", help="container-stunnel-init image tag")
@click.option("--data-gate-apply", help="data-gate-apply image tag")
@click.option("--data-gate-api", help="data-gate-api image tag")
@click.option("--data-gate-init", help="data-gate-init image tag")
@click.option("--data-gate-server", help="data-gate-server image tag")
@click.option("--data-gate-ui", help="data-gate-ui image tag")
def replace_data_gate_images(
    deployment_name: str,
    pull_prefix: str,
    timeout: str,
    container_stunnel: str,
    container_stunnel_init: str,
    data_gate_apply: str,
    data_gate_api: str,
    data_gate_init: str,
    data_gate_server: str,
    data_gate_ui: str,
):
    """Replace a single or multiple specific component(s) of a given deployment.
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

    dg_id = _infer_custom_resource_id_from_deployment_name(deployment_name)
    custom_resource_json = oc.get_custom_resource("datagateinstanceservice", dg_id)

    for component, image_tag in components.items():
        _replace_image_in_data_gate_instance_service_custom_resource(
            custom_resource_json, component, image_tag, pull_prefix
        )

    oc.replace_custom_resource(custom_resource_json)

    data_gate_pod_name = _get_data_gate_pod_name_from_deployment_name(deployment_name)
    logger.info("Waiting for Data Gate pod to restart")
    logger.info("Waiting for pod to change from status 'Running' to another status")
    wait_for(
        300,
        30,
        f"Waiting for pod '{data_gate_pod_name}' to change from status 'Running' to another status",
        _is_pod_not_running_from_deployment,
        deployment_name,
    )

    logger.info("Waiting for new pod to change to status 'Running'")
    wait_for(
        600,
        30,
        f"Waiting for pod '{data_gate_pod_name}' to change to status 'Running'",
        _is_pod_running_from_deployment,
        deployment_name,
    )

    data_gate_pod_name = _get_data_gate_pod_name_from_deployment_name(deployment_name)
    logger.info(f"Waiting for pod '{data_gate_pod_name}' to become ready")
    wait_for(300, 30, f"Waiting for pod '{data_gate_pod_name}' to become ready", _is_pod_ready, data_gate_pod_name)


def _get_app_name_from_deployment_name(deployment_name: str) -> str:
    result = ""
    m = re.match(r"(dg-[0-9]+)-data-gate", deployment_name)

    if m and m.group(1):
        result = m.group(1)
        logging.debug(f"App name: {result}")
    else:
        raise DataGateCLIException(f"Unable to retrieve app name for Data Gate deployment name '{deployment_name}'")

    return result


def _get_data_gate_pod_name_from_deployment_name(deployment_name: str) -> str:
    app_name = _get_app_name_from_deployment_name(deployment_name)
    search_string = app_name + "-data-gate"

    pod_name = oc.get_pod_name(search_string)

    if pod_name:
        result = pod_name[0]
    else:
        raise DataGateCLIException(f"Unable to retrieve pod name for Data Gate deployment '{deployment_name}'")

    return result


def _is_pod_ready(pod_name: str):
    return oc.get_pod_status(pod_name).is_ready()


def _is_pod_running_from_deployment(deployment_name: str):
    result = False

    try:
        pod_name = _get_data_gate_pod_name_from_deployment_name(deployment_name)
        result = oc.get_pod_status(pod_name).is_running()
    except Exception:
        pass

    return result


def _is_pod_not_running_from_deployment(deployment_name: str):
    result = False

    try:
        result = _is_pod_running_from_deployment(deployment_name)
    except Exception:
        pass

    return not result


def _infer_custom_resource_id_from_deployment_name(deployment_name: str) -> str:
    result = ""

    try:
        app_name = _get_app_name_from_deployment_name(deployment_name)
        result = app_name.replace("-", "")
    except DataGateCLIException:
        raise DataGateCLIException(
            f"Unable to retrieve custom resource id for Data Gate deployment name '{deployment_name}'"
        )

    return result


def _replace_image_in_data_gate_instance_service_custom_resource(
    custom_resource_json: dict, component: str, image_tag: str, pull_prefix: str
) -> dict:
    if "image_tags" not in custom_resource_json["spec"]:
        custom_resource_json["spec"]["image_tags"] = {}

    custom_resource_json["spec"]["image_tags"][component] = image_tag

    if pull_prefix:
        if "pull_prefix" not in custom_resource_json["spec"]:
            custom_resource_json["spec"]["pull_prefix"] = {}

        custom_resource_json["spec"]["pull_prefix"][component] = pull_prefix

    return custom_resource_json
