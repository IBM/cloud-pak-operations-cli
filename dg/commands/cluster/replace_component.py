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
import dg.lib.openshift

from dg.lib.error import DataGateCLIException
from dg.utils.logging import loglevel_command


@loglevel_command()
@click.option("--deployment-name", help="OpenShift deployment name")
@click.option("--component", help="Component to be replaced", required=True)
@click.option("--image-tag", help="Image tag of the new component", required=True)
@click.option("--pull-prefix", help="Pull prefix of the new component")
def replace_component(deployment_name: str, component: str, image_tag: str, pull_prefix: str):
    """Replace a specific component of a given deployment"""

    if not _is_component_supported(component):
        raise DataGateCLIException(
            f"Component '{component}' is not supported. Supported components are: {_supported_components()}"
        )

    # if the user didn't specify a deployment name, search for "data-gate" in the available deployments and use the first result
    deployment_name = (
        deployment_name if (deployment_name is not None) else dg.lib.openshift.get_deployment_name("data-gate")[0]
    )

    click.echo(deployment_name)

    #dg.lib.openshift.scale_deployment(deployment_name, 0)

    # TODO edit datagateserviceinstance

    #dg.lib.openshift.scale_deployment(deployment_name, 1)


def _supported_components() -> List[str]:
    return [
        "container_stunnel",
        "container_stunnel_init",
        "datagate_apply",
        "datagate_api",
        "datagate_init",
        "datagate_server",
        "datagate_ui",
    ]


def _is_component_supported(component: str) -> bool:
    return component in _supported_components()
