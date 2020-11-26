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
import subprocess
import urllib.parse

from typing import Final, List

import kubernetes.config
import openshift.dynamic
import requests
import semver

import dg.config
import dg.utils.network

OPENSHIFT_REST_API_VERSION: Final[str] = "v1"

k8s_client = kubernetes.config.new_client_from_config()


def enable_openshift_image_registry_default_route():
    """Enables the Image Registry default route with the Custom Resource
    Definition

    https://docs.openshift.com/container-platform/latest/registry/configuring-registry-operator.html#registry-operator-default-crd_configuring-registry-operator
    """

    oc_cli_path = dg.config.data_gate_configuration_manager.get_oc_cli_path()
    oc_get_route_command = [
        str(oc_cli_path),
        "patch",
        "configs.imageregistry.operator.openshift.io/cluster",
        "--patch",
        '{"spec":{"defaultRoute":true}}',
        "--type",
        "merge",
    ]

    subprocess.check_call(oc_get_route_command)


def get_cluster_access_token(
    oauth_server_url: str, username: str, password: str
) -> str:
    """Obtains an OAuth access token from the given OpenShift server

    Parameters
    ----------
    oauth_server_url
        URL of the OpenShift server that the OAuth access token shall be
        obtained from
    username
        username used to authenticate with the OpenShift server
    password
        password used to authenticate with the OpenShift server

    Returns
    -------
    str
        OAuth access token obtained from the given OpenShift server
    """

    dg.utils.network.disable_insecure_request_warning()

    response = requests.get(
        oauth_server_url,
        allow_redirects=False,
        auth=(username, password),
        verify=False,
    )

    if "Location" not in response.headers:
        raise Exception("HTTP Location header not found")

    fragment = urllib.parse.parse_qs(
        urllib.parse.urlparse(response.headers["Location"]).fragment
    )

    if "access_token" not in fragment:
        raise Exception("access_token key not found in URL fragment")

    access_token = fragment["access_token"][0]

    return access_token


def get_current_token() -> str:
    """Returns the current OAuth access token stored in ~/.kube/config

    Returns
    -------
    str
        current OAuth access token stored in ~/.kube/config
    """

    oc_cli_path = dg.config.data_gate_configuration_manager.get_oc_cli_path()
    oc_whoami_command = [
        oc_cli_path,
        "whoami",
        "--show-token",
    ]

    oc_whoami_command_result = subprocess.check_output(oc_whoami_command, text=True)

    return oc_whoami_command_result.rstrip()


def get_oc_login_command_with_password(
    server: str, username: str, password: str
) -> List[str]:
    oc_cli_path = dg.config.data_gate_configuration_manager.get_oc_cli_path()

    return _get_oc_login_command_with_password(
        str(oc_cli_path), server, username, password
    )


def get_oc_login_command_with_token(server: str, token: str) -> List[str]:
    oc_cli_path = dg.config.data_gate_configuration_manager.get_oc_cli_path()

    return _get_oc_login_command_with_token(str(oc_cli_path), server, token)


def get_oc_login_command_with_password_for_remote_host(
    server: str, username: str, password: str
) -> str:
    return " ".join(
        _get_oc_login_command_with_password("oc ", server, username, password)
    )


def get_oc_login_command_with_token_for_remote_host(server: str, token: str) -> str:
    return " ".join(_get_oc_login_command_with_token("oc ", server, token))


def get_openshift_image_registry_default_route() -> str:
    """Returns the Image Registry default route

    Returns
    -------
    str
        Image Registry default route
    """

    oc_cli_path = dg.config.data_gate_configuration_manager.get_oc_cli_path()
    oc_get_route_command = [
        str(oc_cli_path),
        "get",
        "route",
        "--namespace",
        "openshift-image-registry",
        "--output",
        "jsonpath='{.items[?(@.metadata.name==\"default-route\")].spec.host}'",
    ]

    oc_get_route_command_result = (
        subprocess.check_output(oc_get_route_command, text=True)
        .removeprefix("'")
        .removesuffix("'")
    )

    return oc_get_route_command_result


def get_openshift_version() -> semver.VersionInfo:
    oc_cli_path = dg.config.data_gate_configuration_manager.get_oc_cli_path()
    oc_version_command = [str(oc_cli_path), "version", "--output", "json"]
    oc_version_command_result = json.loads(subprocess.check_output(oc_version_command))

    return semver.VersionInfo.parse(oc_version_command_result["openshiftVersion"])


def get_persistent_volume_name(
    namespace: str, persistent_volume_claim_name: str
) -> str:
    dyn_client = openshift.dynamic.DynamicClient(k8s_client)
    persistent_volume_claims = dyn_client.resources.get(
        api_version=OPENSHIFT_REST_API_VERSION, kind="PersistentVolumeClaim"
    )

    persistent_volume_claim = persistent_volume_claims.get(
        name=persistent_volume_claim_name, namespace=namespace
    )

    return persistent_volume_claim.spec.volumeName


def get_persistent_volume_id(namespace: str, persistent_volume_name: str):
    dyn_client = openshift.dynamic.DynamicClient(k8s_client)
    persistent_volumes = dyn_client.resources.get(
        api_version=OPENSHIFT_REST_API_VERSION, kind="PersistentVolume"
    )

    persistent_volume = persistent_volumes.get(
        name=persistent_volume_name, namespace=namespace
    )

    return persistent_volume.metadata.labels.volumeId


def log_in_to_openshift_cluster_with_password(
    server: str, username: str, password: str
):
    """Logs in to a given Openshift cluster with the given credentials"""

    oc_login_command = get_oc_login_command_with_password(server, username, password)

    subprocess.check_call(oc_login_command)


def log_in_to_openshift_cluster_with_token(server: str, token: str):
    """Logs in to a given Openshift cluster with the given OAuth access
    token"""

    oc_login_command = get_oc_login_command_with_token(server, token)

    subprocess.check_call(oc_login_command)


def _get_oc_login_command_with_password(
    oc_cli_path: str, server: str, username: str, password: str
) -> List[str]:
    return [
        oc_cli_path,
        "login",
        "--insecure-skip-tls-verify",
        "--password",
        password,
        "--server",
        server,
        "--username",
        username,
    ]


def _get_oc_login_command_with_token(
    oc_cli_path: str, server: str, token: str
) -> List[str]:
    return [
        oc_cli_path,
        "login",
        "--insecure-skip-tls-verify",
        "--server",
        server,
        "--token",
        token,
    ]
