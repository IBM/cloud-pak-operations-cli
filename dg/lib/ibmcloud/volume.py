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

import logging
import time

from typing import Any, Final

import dg.commands.ibmcloud.common
import dg.utils.openshift

MAX_NUM_MODIFICATION_CHECKS: Final[int] = 30
NUM_SECONDS_TO_WAIT_BETWEEN_ITERATIONS: Final[int] = 10


def increase_openshift_image_registry_volume_capacity(
    required_volume_capacity: int,
    max_num_modification_checks=MAX_NUM_MODIFICATION_CHECKS,
    num_seconds_to_wait_between_iterations=NUM_SECONDS_TO_WAIT_BETWEEN_ITERATIONS,
):
    """Increases the capacity of the volume in the openshift-image-registry
    namespace

    Parameters
    ----------
    required_volume_capacity
        capacity that the volume shall be increased to
    max_num_modification_checks
        maximum number of checks whether the modification was applied
    num_seconds_to_wait_between_iterations
        number of seconds to wait between checks
    """

    persistent_volume_name = dg.utils.openshift.get_persistent_volume_name(
        "openshift-image-registry", "image-registry-storage"
    )

    volume_id = dg.utils.openshift.get_persistent_volume_id(
        "openshift-image-registry", persistent_volume_name
    )

    volume_details = dg.commands.ibmcloud.common.get_volume_details(volume_id)
    volume_capacity = _get_volume_capacity(volume_details)

    if volume_capacity < required_volume_capacity:
        dg.commands.ibmcloud.common.modify_volume_capacity(
            volume_id, required_volume_capacity
        )

        for i in range(max_num_modification_checks):
            volume_details = dg.commands.ibmcloud.common.get_volume_details(volume_id)
            volume_capacity = _get_volume_capacity(volume_details)

            if volume_capacity == required_volume_capacity:
                logging.info(
                    "OpenShift image registry volume capacity change succeeded"
                )

                break
            else:
                if i == max_num_modification_checks - 1:
                    raise Exception(
                        f"OpenShift image registry volume capacity change was not applied yet – timeout was reached "
                        f"after {max_num_modification_checks * num_seconds_to_wait_between_iterations} seconds"
                    )

                logging.info(
                    f"OpenShift image registry volume capacity change was not applied yet – sleeping "
                    f"{num_seconds_to_wait_between_iterations} seconds"
                )

                time.sleep(num_seconds_to_wait_between_iterations)
    else:
        logging.warning(
            f"OpenShift image registry volume capacity is already greater than or equal to {required_volume_capacity} "
            f"GiB"
        )


def _get_volume_capacity(volume_details: dict[str, Any]):
    assert "capacityGb" in volume_details

    return volume_details["capacityGb"]
