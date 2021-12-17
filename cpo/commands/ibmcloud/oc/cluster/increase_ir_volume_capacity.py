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

from typing import Final

import click

import cpo.lib.ibmcloud.volume

from cpo.utils.logging import loglevel_command

REQUIRED_OPENSHIFT_IMAGE_REGISTRY_VOLUME_CAPACITY_IN_GB: Final[int] = 200


@loglevel_command()
@click.option("--name", help="cluster name", required=True)
def increase_ir_volume_capacity(name: str):
    """Increase capacity of volume in openshift-image-registry namespace"""

    cpo.lib.ibmcloud.volume.increase_openshift_image_registry_volume_capacity(
        REQUIRED_OPENSHIFT_IMAGE_REGISTRY_VOLUME_CAPACITY_IN_GB, 30
    )
