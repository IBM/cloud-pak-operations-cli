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

import json

from typing import Any

import cpo.utils.logging

from cpo.lib.error import DataGateCLIException, IBMCloudException
from cpo.lib.ibmcloud import execute_ibmcloud_command
from cpo.lib.ibmcloud.oc.cluster.ls import list_existing_clusters
from cpo.utils.wait import wait_for


class ClusterStatus:
    def __init__(self, status_output: Any):
        self._status_output = status_output

    def __str__(self) -> str:
        # TODO improve output
        return self.get_json()

    def get_json(self) -> str:
        return json.dumps(self._status_output, indent="\t", sort_keys=True)

    def get_server_url(self) -> str:
        result = ""

        if "masterURL" in self._status_output:
            # IBM Cloud Kubernetes Service cluster
            result = self._status_output["masterURL"]
        elif "serverURL" in self._status_output:
            # Red Hat OpenShift on IBM Cloud cluster
            result = self._status_output["serverURL"]

        return result

    def has_name(self, name: str) -> bool:
        return ("name" in self._status_output) and (self._status_output["name"] == name)

    def is_ready(self) -> bool:
        result = False

        if (
            ("ingressHostname" in self._status_output)
            and (self._status_output["ingressHostname"] != "")
            and (self._status_output["masterHealth"] == "normal")
            and (self._status_output["masterState"] == "deployed")
            and (self._status_output["masterStatus"] == "Ready")
            and (self._status_output["state"] == "normal")
        ):
            result = True

        return result


class IngressStatus:
    def __init__(self, status_output: Any):
        self._status_output = status_output

    def is_ready(self) -> bool:
        result = False

        if ("status" in self._status_output) and (self._status_output["status"] == "healthy"):
            result = True

        return result


def get_cluster_status(cluster_name: str) -> ClusterStatus:
    """Returns the status of the cluster with the given name

    Parameters
    ----------
    cluster_name
        name of the cluster whose status shall be returned

    Returns
    -------
    ClusterStatus
        status of the cluster with the given name
    """

    args = ["oc", "cluster", "get", "--cluster", cluster_name, "--json"]
    command_result = execute_ibmcloud_command(args, capture_output=True)

    try:
        status = ClusterStatus(json.loads(command_result.stdout))

        return status
    except json.JSONDecodeError as exception:
        command_string = "ibmcloud " + " ".join(args)

        raise DataGateCLIException(
            f"Invalid JSON received from command {command_string}:\n{command_result.stdout}"
        ) from exception


def get_ingress_status(cluster_name: str) -> IngressStatus:
    """Returns the status of Ingress components of the cluster with the
    given name

    Parameters
    ----------
    cluster_name
        name of the cluster whose status of Ingress components shall be returned

    Returns
    -------
    IngressStatus
        status of Ingress components of the cluster with the given name
    """

    args = ["ks", "ingress", "status", "--cluster", cluster_name, "--json"]
    command_result = execute_ibmcloud_command(args, capture_output=True)

    try:
        status = IngressStatus(json.loads(command_result.stdout))

        return status
    except json.JSONDecodeError as exception:
        command_string = "ibmcloud " + " ".join(args)

        raise DataGateCLIException(
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


def _is_cluster_ready(cluster_name: str) -> bool:
    result = False

    try:
        result = get_cluster_status(cluster_name).is_ready()
    except IBMCloudException as exception:
        if not _service_is_unavailable(exception):
            raise exception

    return result


def _is_ingress_ready(cluster_name: str) -> bool:
    result = False

    try:
        result = get_ingress_status(cluster_name).is_ready()
    except IBMCloudException as exception:
        if not _service_is_unavailable(exception):
            raise exception

    return result


def wait_for_cluster_deletion(cluster_name: str):
    wait_for(
        1200,
        10,
        f"Cluster deletion for cluster {cluster_name}",
        _cluster_not_exists,
        cluster_name,
    )


def wait_for_cluster_readiness(cluster_name: str):
    """Waits for the cluster with the given name to be ready

    Parameters
    ----------
    cluster_name
        name of the cluster whose readiness shall be waited for
    """

    with cpo.utils.logging.ScopedLoggingDisabler():
        wait_for(
            5400,
            30,
            f"Waiting for creation of cluster '{cluster_name}'",
            _is_cluster_ready,
            cluster_name,
        )


def wait_for_ingress_readiness(cluster_name: str):
    """Waits for the status of Ingress components of the cluster with the
    given name to be healthy

    Parameters
    ----------
    cluster_name
        name of the cluster whose status of Ingress components shall be waited
        for
    """

    with cpo.utils.logging.ScopedLoggingDisabler():
        wait_for(
            1800,
            30,
            f"Waiting for Ingress components status of cluster '{cluster_name}' to be healthy",
            _is_ingress_ready,
            cluster_name,
        )


def _service_is_unavailable(exception: IBMCloudException) -> bool:
    return (
        IBMCloudException.get_parsed_error_message_without_incident_id(exception.get_error_message())
        == "Error response from server. Status code: 503"
    )
