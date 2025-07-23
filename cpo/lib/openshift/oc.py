#  Copyright 2021, 2025 IBM Corporation
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
import tempfile

from typing import Final

import semver

from kubernetes.config.config_exception import ConfigException
from kubernetes.config.kube_config import list_kube_config_contexts
from pydantic import TypeAdapter

import cpo.lib.openshift.credentials.cluster_based_user_credentials
import cpo.utils.process

from cpo.lib.cluster.cluster import AbstractCluster
from cpo.lib.cluster.types.context import Context
from cpo.lib.dependency_manager.dependency_manager import DependencyManager
from cpo.lib.dependency_manager.plugins.openshift.openshift_cli_plugin import OpenShiftCLIPlugIn
from cpo.lib.openshift.types.get_pod_entry import GetPodEntry
from cpo.utils.error import CloudPakOperationsCLIException

OPENSHIFT_REST_API_VERSION: Final[str] = "v1"


def enable_image_registry_default_route():
    """Enables the Image Registry default route with the Custom Resource
    Definition

    https://docs.openshift.com/container-platform/latest/registry/configuring-registry-operator.html#registry-operator-default-crd_configuring-registry-operator
    """

    oc_patch_args = [
        "patch",
        "configs.imageregistry.operator.openshift.io/cluster",
        "--patch",
        '{"spec":{"defaultRoute":true}}',
        "--type",
        "merge",
    ]

    execute_oc_command(oc_patch_args)


def execute_oc_command(
    args: list[str],
    capture_output=False,
    check=True,
    print_captured_output=False,
) -> cpo.utils.process.ProcessResult:
    """Executes the OpenShift Container Platform CLI

    Parameters
    ----------
    args
        arguments to be passed to the OpenShift Container Platform CLI
    capture_output
        flag indicating whether process output shall be captured
    check
        flag indicating whether an exception shall be thrown if the OpenShift
        Container Platform CLI returns with a nonzero return code
    oc_cli_path
        path to the OpenShift Container Platform CLI
    print_captured_output
        flag indicating whether captured process output shall also be written to
        stdout/stderr

    Returns
    -------
    ProcessResult
        object storing the return code and captured process output (if
        requested)
    """

    return DependencyManager.get_instance().execute_binary(
        OpenShiftCLIPlugIn,
        None,
        args,
        capture_output=capture_output,
        check=check,
        print_captured_output=print_captured_output,
    )


def get_current_token() -> str:
    """Returns the current OAuth access token stored in ~/.kube/config

    Returns
    -------
    str
        current OAuth access token stored in ~/.kube/config
    """

    oc_whoami_command_result = execute_oc_command(
        [
            "whoami",
            "--show-token",
        ],
        capture_output=True,
    )

    return oc_whoami_command_result.stdout.rstrip()


def get_oc_login_args_with_password(server: str, username: str, password: str) -> list[str]:
    return [
        "login",
        "--insecure-skip-tls-verify",
        "--password",
        password,
        "--server",
        server,
        "--username",
        username,
    ]


def get_oc_login_args_with_token(server: str, token: str) -> list[str]:
    return [
        "login",
        "--insecure-skip-tls-verify",
        "--server",
        server,
        "--token",
        token,
    ]


def get_oc_login_command_with_password_for_remote_host(server: str, username: str, password: str) -> str:
    return " ".join(["oc"] + get_oc_login_args_with_password(server, username, password))


def get_oc_login_command_with_token_for_remote_host(server: str, token: str) -> str:
    return " ".join(["oc"] + get_oc_login_args_with_token(server, token))


def get_image_registry_hostname(route_name: str = "default-route") -> str:
    """Returns the Image Registry hostname for the given route name

    Parameters
    ----------
    route_name
        route name

    Returns
    -------
    str
        Image Registry hostname for the given route name
    """

    oc_get_route_command_result = (
        execute_oc_command(
            [
                "get",
                "route",
                "--namespace",
                "openshift-image-registry",
                "--output",
                "jsonpath='{.items[?(@.metadata.name==\"" + route_name + "\")].spec.host}'",
            ],
            capture_output=True,
        )
        .stdout.removeprefix("'")
        .removesuffix("'")
    )

    return oc_get_route_command_result


def get_openshift_version() -> semver.Version:
    oc_version_command_result = json.loads(
        execute_oc_command(["version", "--output", "json"], capture_output=True).stdout
    )

    return semver.Version.parse(oc_version_command_result["openshiftVersion"])


def get_persistent_volume_name(namespace: str, persistent_volume_claim_name: str) -> str:
    oc_get_pvc_command_result = json.loads(
        execute_oc_command(
            [
                "get",
                "pvc",
                "--namespace",
                namespace,
                "--output",
                "json",
            ],
            capture_output=True,
        ).stdout
    )

    if len(oc_get_pvc_command_result["items"]) == 0:
        raise CloudPakOperationsCLIException(
            f"Namespace '{namespace}' does not contain a persistent volume claim with name "
            f"'{persistent_volume_claim_name}''"
        )

    volume_name = oc_get_pvc_command_result["items"][0]["spec"]["volumeName"]

    return volume_name


def get_persistent_volume_id(persistent_volume_name: str):
    oc_get_pv_command_result = (
        execute_oc_command(
            [
                "get",
                "pv",
                "--output",
                f"jsonpath='{{.items[?(@.metadata.name==\"{persistent_volume_name}\")].metadata.labels.volumeId}}'",
            ],
            capture_output=True,
        )
        .stdout.removeprefix("'")
        .removesuffix("'")
    )

    if oc_get_pv_command_result == "":
        raise CloudPakOperationsCLIException(
            f"Persistent volume with name '{persistent_volume_name}' could not be found"
        )

    return oc_get_pv_command_result


def log_in_to_openshift_cluster_with_password(server: str, username: str, password: str):
    """Logs in to a given Openshift cluster with the given credentials"""

    oc_login_args = get_oc_login_args_with_password(server, username, password)

    execute_oc_command(oc_login_args)


def log_in_to_openshift_cluster_with_token(server: str, token: str):
    """Logs in to a given Openshift cluster with the given OAuth access
    token"""

    oc_login_args = get_oc_login_args_with_token(server, token)

    execute_oc_command(oc_login_args)


def get_deployment_name(search_string: str) -> list[str]:
    """Returns the available OpenShift deployment(s) for a given search string"""

    oc_get_deployments_result = execute_oc_command(["get", "deployments"], capture_output=True).stdout
    result = []

    for line in oc_get_deployments_result.splitlines():
        if search_string in line:
            result.append(line.split()[0].strip())

    if not result:
        raise CloudPakOperationsCLIException(
            f"Deployment(s) containing the string '{search_string}' could not be found"
        )

    return result


def get_pod_name(search_string: str) -> list[str]:
    """Returns the available OpenShift pod(s) for a given search string"""

    oc_get_pods_result = execute_oc_command(["get", "pods"], capture_output=True).stdout
    result = []

    for line in oc_get_pods_result.splitlines():
        if search_string in line:
            result.append(line.split()[0].strip())

    if not result:
        raise CloudPakOperationsCLIException(f"Pod(s) containing the string '{search_string}' could not be found")

    return result


def get_pod_status(pod_name: str) -> GetPodEntry:
    """Returns the current pod status for a given pod name"""

    oc_get_pods_result = execute_oc_command(["get", "pods"], capture_output=True).stdout

    for line in oc_get_pods_result.splitlines():
        if pod_name in line:
            break

    return GetPodEntry.parse(line)


def get_custom_resource(custom_resource_kind: str, custom_resource_id: str) -> dict:
    """Get the custom resource for a given kind and ID"""

    oc_get_custom_resource_result = json.loads(
        execute_oc_command(
            ["get", custom_resource_kind, custom_resource_id, "--output", "json"], capture_output=True
        ).stdout
    )
    return oc_get_custom_resource_result


def login(current_cluster: AbstractCluster):
    credentials = cpo.lib.openshift.credentials.cluster_based_user_credentials.ClusterBasedUserCredentials(
        current_cluster
    )
    credentials.refresh_access_token()

    username = current_cluster.get_username()

    if username == "kubeadmin":
        username = "kube:admin"

    kube_config_cluster = current_cluster.get_server().removeprefix("https://").replace(".", "-")
    kube_config_username = f"{username}/{kube_config_cluster}"
    default_project_context = f"default/{kube_config_cluster}/{username}"

    execute_oc_command(
        ["config", "set-credentials", kube_config_username, "--token", credentials.get_access_token()],
        capture_output=True,
    )

    try:
        kube_config_contexts = TypeAdapter(tuple[list[Context], Context]).validate_python(list_kube_config_contexts())
        current_context = kube_config_contexts[1]

        if current_context.context.cluster != kube_config_cluster:
            contexts = kube_config_contexts[0]

            if not _context_exists(contexts, default_project_context):
                set_cluster(kube_config_cluster, current_cluster)

            set_context(kube_config_cluster, kube_config_username, default_project_context)
            use_context(kube_config_cluster, username)
    except ConfigException:
        set_cluster(kube_config_cluster, current_cluster)
        set_context(kube_config_cluster, kube_config_username, default_project_context)
        use_context(kube_config_cluster, username)


def replace_custom_resource(custom_resource_json: dict):
    with tempfile.NamedTemporaryFile(mode="w+") as json_file:
        json.dump(custom_resource_json, json_file)
        json_file.flush()

        oc_set_custom_resource_args = ["replace", "--filename", json_file.name]

        execute_oc_command(oc_set_custom_resource_args)


def set_cluster(kube_config_cluster: str, current_cluster: AbstractCluster):
    execute_oc_command(
        [
            "config",
            "set-cluster",
            kube_config_cluster,
            "--insecure-skip-tls-verify=true",
            "--server",
            current_cluster.get_server(),
        ],
        capture_output=True,
    )


def set_context(kube_config_cluster: str, kube_config_username: str, default_project_context):
    execute_oc_command(
        [
            "config",
            "set-context",
            default_project_context,
            "--cluster",
            kube_config_cluster,
            "--namespace",
            "default",
            "--user",
            kube_config_username,
        ],
        capture_output=True,
    )


def use_context(kube_config_cluster: str, username: str):
    execute_oc_command(["config", "use-context", f"default/{kube_config_cluster}/{username}"], capture_output=True)


def _context_exists(contexts: list[Context], context_name: str) -> bool:
    result = False

    for context in contexts:
        if context.name == context_name:
            result = True

            break

    return result
