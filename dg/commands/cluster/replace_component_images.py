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

from typing import List

import click

import dg.config.cluster_credentials_manager
import dg.lib.openshift.oc

from dg.utils.logging import loglevel_command


@loglevel_command()
@click.option("--deployment-name", help="OpenShift deployment name")
@click.option("--pull-prefix", help="Pull prefix of the new component(s)")
@click.option("--container-stunnel", help="container-stunnel image tag")
@click.option("--container-stunnel-init", help="container-stunnel-init image tag")
@click.option("--data-gate-apply", help="data-gate-apply image tag")
@click.option("--data-gate-api", help="data-gate-api image tag")
@click.option("--data-gate-init", help="data-gate-init image tag")
@click.option("--data-gate-server", help="data-gate-server image tag")
@click.option("--data-gate-ui", help="data-gate-ui image tag")
def replace_component_images(
    deployment_name: str,
    pull_prefix: str,
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

    # if the user didn't specify a deployment name, search for "data-gate" in the available deployments and use the first result
    deployment_name = (
        deployment_name if (deployment_name is not None) else dg.lib.openshift.oc.get_deployment_name("data-gate")[0]
    )

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

    dg.lib.openshift.oc.scale_deployment(deployment_name, 0)

    dg_id = dg.lib.openshift.oc.infer_custom_resource_id_from_deployment_name(deployment_name)
    custom_resource_json = dg.lib.openshift.oc.get_current_data_gate_instance_service_custom_resource(dg_id)

    for component, image_tag in components.items():
        dg.lib.openshift.oc.replace_image_in_data_gate_instance_service_custom_resource(
            custom_resource_json, component, image_tag, pull_prefix
        )

    dg.lib.openshift.oc.set_data_gate_instance_service_custom_resouce(custom_resource_json)

    dg.lib.openshift.oc.scale_deployment(deployment_name, 1)
