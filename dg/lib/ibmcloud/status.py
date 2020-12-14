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

import json

from typing import Any

from dg.lib.ibmcloud.cluster.ls import list_existing_clusters
from dg.lib.thirdparty import execute_ibmcloud_command_with_check
from dg.utils.wait import wait_for


class ClusterStatus:
    def __init__(self, status_output: Any):
        self._status_output = status_output

    def __str__(self) -> str:
        # TODO improve output
        return json.dumps(self._status_output, indent=4)

    def get_json(self) -> str:
        return self._status_output

    def get_server_url(self) -> str:
        return self._status_output["serverURL"]

    def has_name(self, name: str) -> bool:
        return ("name" in self._status_output) and (self._status_output["name"] == name)

    def is_ready(self) -> bool:
        result = False

        if (
            ("ingressHostname" in self._status_output)
            and (self._status_output["ingressHostname"] != "")
            and (self._status_output["state"] == "normal")
        ):
            result = True

        return result


def get_cluster_status(cluster_name: str) -> ClusterStatus:
    """Returns the status of the given cluster

    Parameters
    ----------
    cluster_name
        name of the cluster whose status shall be returned

    Returns
    -------
    Status
        status of the given cluster
    """

    args = ["oc", "cluster", "get", "--cluster", cluster_name, "--json"]
    command_result = execute_ibmcloud_command_with_check(args)
    result: ClusterStatus

    try:
        status = ClusterStatus(json.loads(command_result.stdout))

        return status
    except json.JSONDecodeError as exception:
        command_string = "ibmcloud " + " ".join(args)

        raise Exception(
            f"Invalid JSON received from command {command_string}:\n{command_result.stdout}"
        ) from exception


def cluster_exists(cluster_name: str) -> bool:
    existing_clusters = list_existing_clusters(True)

    if cluster_name in existing_clusters:
        return True
    else:
        return False


def _cluster_not_exists(cluster_name: str) -> bool:
    return not cluster_exists(cluster_name)


def _is_cluster_ready(cluster_name: str):
    return get_cluster_status(cluster_name).is_ready()


def wait_for_cluster_deletion(cluster_name: str):
    wait_for(
        1200,
        10,
        f"Cluster deletion for cluster {cluster_name}",
        _cluster_not_exists,
        cluster_name,
    )


def wait_for_cluster_readiness(cluster_name: str):
    """Waits for the given cluster to be completely ready. This includes availability of the ingress hostname.

    Parameters
    ----------
    cluster_name
        name of the cluster whose status shall be returned
    """

    try:
        wait_for(
            3600,
            30,
            f"Cluster creation for cluster {cluster_name}",
            _is_cluster_ready,
            cluster_name,
        )
    except Exception:
        raise Exception(
            f"Timeout for cluster creation exceeded, current cluster status:\n{get_cluster_status(cluster_name)}"
        )
