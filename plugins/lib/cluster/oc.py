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
import re as regex

from cpo.lib.openshift import oc


def _get_app_name_from_deployment_name(deployment_name: str) -> str:
    search_result = ""
    m = regex.match(r"(dg-[0-9]+)-data-gate", deployment_name)

    if m and m.group(1):
        search_result = m.group(1)
    else:
        raise Exception(f"Unable to retrieve app name for Db2 Data Gate deployment name '{deployment_name}'")

    return search_result


def get_db2_data_gate_pod_name_from_deployment_name(deployment_name: str) -> str:
    app_name = _get_app_name_from_deployment_name(deployment_name)
    search_string = app_name + "-data-gate"

    pod_name = oc.get_pod_name(search_string)

    if pod_name:
        result = pod_name[0]
    else:
        raise Exception(f"Unable to retrieve pod name for Data Gate deployment '{deployment_name}'")

    return result


def is_pod_ready(pod_name: str) -> bool:
    return oc.get_pod_status(pod_name).is_ready()


def is_pod_running_from_deployment(deployment_name: str) -> bool:
    result = False

    try:
        pod_name = get_db2_data_gate_pod_name_from_deployment_name(deployment_name)
        result = oc.get_pod_status(pod_name).is_running()
    except Exception:
        pass

    return result


def is_pod_not_running_from_deployment(deployment_name: str) -> bool:
    result = False

    try:
        result = is_pod_running_from_deployment(deployment_name)
    except Exception:
        pass

    return not result


def infer_custom_resource_id_from_deployment_name(deployment_name: str) -> str:
    result = ""

    try:
        app_name = _get_app_name_from_deployment_name(deployment_name)
        result = app_name.replace("-", "")
    except Exception:
        raise Exception(
            f"Unable to retrieve custom resource ID for Db2 Data Gate deployment name '{deployment_name}'"
        )

    return result


def replace_image_in_db2_data_gate_instance_service_custom_resource(
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
