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

from typing import Any, Callable, Dict, List

from kubernetes import client, config

import dg.utils.network

from dg.lib.error import DataGateCLIException
from dg.lib.openshift.credentials.credentials import AbstractCredentials
from dg.lib.openshift.data.global_pull_secret_data import GlobalPullSecretData
from dg.lib.openshift.types.kind_metadata import KindMetadata
from dg.lib.openshift.types.object_meta import ObjectMeta
from dg.lib.openshift.types.role import Role
from dg.lib.openshift.types.role_binding import RoleBinding
from dg.lib.openshift.types.role_rule import RoleRule
from dg.lib.openshift.types.service_account import ServiceAccount

logger = logging.getLogger(__name__)


class OpenShiftAPIManager:
    """Manages REST communication with the OpenShift REST API

    This class uses the Kubernetes Python client
    (https://github.com/kubernetes-client/python). The OpenShift Python
    client (https://github.com/openshift/openshift-restclient-python) was
    deliberately not used as its performance suffers from the amount of REST
    API calls during endpoint discovery.
    """

    def __init__(self, credentials: AbstractCredentials):
        self._credentials = credentials
        self._kube_config_initialized = False

    def cluster_role_exists(self, name: str) -> bool:
        """Returns whether the cluster role with the given name exists

        Parameters
        ----------
        name
            cluster role name

        Returns
        -------
        bool
            true, if the cluster role exists
        """

        return self.execute_kubernetes_client(
            self._custom_object_exists,
            kind_metadata=KindMetadata("rbac.authorization.k8s.io", "ClusterRole", "clusterroles", "v1"),
            name=name,
        )

    def cluster_role_binding_exists(self, name: str) -> bool:
        """Returns whether the cluster role binding with the given name exists

        Parameters
        ----------
        name
            cluster role binding name

        Returns
        -------
        bool
            true, if the cluster role binding exists
        """

        return self.execute_kubernetes_client(
            self._custom_object_exists,
            kind_metadata=KindMetadata("rbac.authorization.k8s.io", "ClusterRoleBinding", "clusterrolebindings", "v1"),
            name=name,
        )

    def create_cluster_role(self, name: str, rules: List[RoleRule]):
        """Creates a cluster role

        Parameters
        ----------
        name
            cluster role name
        rules
            cluster role rule specifications
        """

        self.execute_kubernetes_client(
            self._create_cluster_role,
            metadata={
                "name": name,
            },
            rules=rules,
        )

    def create_cluster_role_binding(self, name: str, subjects: List[ObjectMeta], role_ref_name: str):
        """Creates a cluster role binding

        Parameters
        ----------
        name
            cluster role binding name
        subjects
            subjects that the permissions defined in the cluster role with the given
            name are granted to
        role_ref_name
            cluster role defining permissions granted to the given subjects
        """

        self.execute_kubernetes_client(
            self._create_cluster_role_binding,
            metadata={
                "name": name,
            },
            role_ref_name=role_ref_name,
            subjects=subjects,
        )

    def create_deployment(self, project: str, deployment: Any):
        """Creates a deployment

        Parameters
        ----------
        project
            project in which the deployment shall be created
        deployment
            deployment specification
        """

        self.execute_kubernetes_client(self._create_deployment, deployment=deployment, project=project)

    def create_role(self, project: str, name: str, rules: List[RoleRule]):
        """Creates a role

        Parameters
        ----------
        project
            project in which the role shall be created
        name
            role name
        rules
            rule specifications
        """

        self.execute_kubernetes_client(self._create_role, name=name, project=project, rules=rules)

    def create_role_binding(self, project: str, name: str, subjects: List[ObjectMeta], role_ref_name: str):
        """Creates a role binding

        Parameters
        ----------
        project
            project in which the role binding shall be created
        name
            role binding name
        subjects
            subjects that the permissions defined in the role with the given name
            are granted to
        role_ref_name
            role defining permissions granted to the given subjects
        """

        self.execute_kubernetes_client(
            self._create_role_binding, name=name, project=project, role_ref_name=role_ref_name, subjects=subjects
        )

    def create_storage_class(self, name: str, provisioner: str, parameters: Dict[str, str]):
        """Creates a storage class

        Parameters
        ----------
        name
            storage class name
        provisioner
            storage class provisioner name
        parameters
            additional parameters
        """

        self.execute_kubernetes_client(
            self._create_storage_class,
            name=name,
            parameters=parameters,
            provisioner=provisioner,
        )

    def create_system_cluster_role(self, name: str, rules: List[RoleRule]):
        """Creates a system cluster role

        Parameters
        ----------
        name
            cluster role name
        rules
            cluster role rule specifications
        """

        self.execute_kubernetes_client(
            self._create_cluster_role,
            metadata={
                "creationTimestamp": None,
                "name": name,
            },
            rules=rules,
        )

    def create_system_cluster_role_binding(self, name: str, subjects: List[ObjectMeta], role_ref_name: str):
        """Creates a system cluster role binding

        Parameters
        ----------
        name
            cluster role binding name
        subjects
            subjects that the permissions defined in the cluster role with the given
            name are granted to
        role_ref_name
            cluster role defining permissions granted to the given subjects
        """

        self.execute_kubernetes_client(
            self._create_cluster_role_binding,
            metadata={
                "creationTimestamp": None,
                "name": name,
            },
            role_ref_name=role_ref_name,
            subjects=subjects,
        )

    def create_service_account(self, project: str, name: str):
        """Creates a service account

        Parameters
        ----------
        project
            project in which the service account shall be created
        name
            service account name
        """

        self.execute_kubernetes_client(self._create_service_account, name=name, project=project)

    def credentials_exist(self, registry_location: str) -> bool:
        """Returns whether the global pull secret contains credentials for the
        given registry location

        Parameters
        ----------
        registry_location
            registry location to be searched for

        Returns
        -------
        bool
            true, if the global pull secret contains credentials for the given
            registry location
        """

        global_pull_secret_data = self.get_global_pull_secret_data()

        return global_pull_secret_data.contains(registry_location)

    def delete_credentials(self, registry_location: str):
        """Deletes credentials for the given registry location from the global
        pull secret

        Parameters
        ----------
        registry_location
            registry location for which credentials shall be deleted
        """

        global_pull_secret_data = self.get_global_pull_secret_data()
        global_pull_secret_data.delete_credentials(registry_location)

        self.execute_kubernetes_client(self._patch_credentials, global_pull_secret_data=global_pull_secret_data)

    def deployment_exists(self, project: str, name: str) -> bool:
        """Returns whether the deployment with the given name exists in the
        given project

        Parameters
        ----------
        project
            project to be searched for deployments
        name
            deployment name

        Returns
        -------
        bool
            true, if the deployment exists
        """

        return self.execute_kubernetes_client(
            self._namespaced_custom_object_exists,
            kind_metadata=KindMetadata("apps", "Deployment", "deployments", "v1"),
            name=name,
            project=project,
        )

    def execute_kubernetes_client(self, method: Callable[..., Any], **kwargs) -> Any:
        if not self._kube_config_initialized:
            self._set_kube_config()

        if self._credentials.insecure_skip_tls_verify:
            dg.utils.network.disable_insecure_request_warning()

        result: Any = None

        try:
            result = method(**kwargs)
        except client.ApiException as exception:
            if exception.status == 401:
                if not self._credentials.is_refreshable():
                    raise DataGateCLIException("OAuth access token expired and cannot be refreshed")

                self._credentials.refresh_access_token()
                self._set_kube_config()
                result = method(**kwargs)
            else:
                raise exception
        finally:
            dg.utils.network.enable_insecure_request_warning()

        return result

    def get_global_pull_secret_data(self) -> GlobalPullSecretData:
        """Returns the global pull secret as a data object

        Returns
        -------
        GlobalPullSecretData
            global pull secret data object
        """

        return self.execute_kubernetes_client(self._get_credentials)

    def patch_credentials(self, global_pull_secret_data: GlobalPullSecretData):
        """Patches the global pull secret based on the given data object

        Parameters
        ----------
        global_pull_secret_data
            global pull secret data object
        """

        self.execute_kubernetes_client(self._patch_credentials, global_pull_secret_data=global_pull_secret_data)

    def role_binding_exists(self, project: str, name: str) -> bool:
        """Returns whether the role binding with the given name exists in the
        given project

        Parameters
        ----------
        project
            project to be searched for role bindings
        name
            role binding name

        Returns
        -------
        bool
            true, if the role binding exists
        """

        return self.execute_kubernetes_client(
            self._namespaced_custom_object_exists,
            kind_metadata=KindMetadata("rbac.authorization.k8s.io", "RoleBinding", "rolebindings", "v1"),
            name=name,
            project=project,
        )

    def role_exists(self, project: str, name: str) -> bool:
        """Returns whether the role with the given name exists in the given
        project

        Parameters
        ----------
        project
            project to be searched for roles
        name
            role name

        Returns
        -------
        bool
            true, if the role exists
        """

        return self.execute_kubernetes_client(
            self._namespaced_custom_object_exists,
            kind_metadata=KindMetadata("rbac.authorization.k8s.io", "Role", "roles", "v1"),
            name=name,
            project=project,
        )

    def set_credentials(self, registry_location: str, username: str, password: str):
        """Sets credentials for the given registry location

        Parameters
        ----------
        registry_location
            registry location for which credentials shall be set
        username
            registry location username
        password
            registry location password
        """

        global_pull_secret_data = self.get_global_pull_secret_data()
        global_pull_secret_data.set_credentials(registry_location, username, password)

        self.patch_credentials(global_pull_secret_data)

    def service_account_exists(self, project: str, name: str) -> bool:
        """Returns whether the service account with the given name exists in the
        given project

        Parameters
        ----------
        project
            project to be searched for service accounts
        name
            service account name

        Returns
        -------
        bool
            true, if the service account exists
        """

        return self.execute_kubernetes_client(self._service_account_exists, name=name, project=project)

    def storage_class_exists(self, name: str) -> bool:
        """Returns whether the storage class with the given name exists

        Parameters
        ----------
        project
            project to be searched for storage classes
        name
            storage class name

        Returns
        -------
        bool
            true, if the storage class exists
        """

        return self.execute_kubernetes_client(
            self._custom_object_exists,
            kind_metadata=KindMetadata("storage.k8s.io", "StorageClass", "storageclasses", "v1"),
            name=name,
        )

    def _create_cluster_role(self, metadata: ObjectMeta, rules: List[RoleRule]):
        cluster_role: Role = {
            "kind": "ClusterRole",
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "metadata": metadata,
            "rules": rules,
        }

        custom_objects_api = client.CustomObjectsApi()
        custom_objects_api.create_cluster_custom_object("rbac.authorization.k8s.io", "v1", "clusterroles", cluster_role)

    def _create_cluster_role_binding(self, metadata: ObjectMeta, subjects: List[ObjectMeta], role_ref_name: str):
        cluster_role_binding: RoleBinding = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "ClusterRoleBinding",
            "metadata": metadata,
            "roleRef": {
                "apiGroup": "rbac.authorization.k8s.io",
                "kind": "ClusterRole",
                "name": role_ref_name,
            },
            "subjects": [],
        }

        for subject in subjects:
            cluster_role_binding["subjects"].append(
                {
                    "kind": "ServiceAccount",
                    "name": subject["name"],
                    "namespace": subject["namespace"] if "namespace" in subject else "default",
                }
            )

        custom_objects_api = client.CustomObjectsApi()
        custom_objects_api.create_cluster_custom_object(
            "rbac.authorization.k8s.io", "v1", "clusterrolebindings", cluster_role_binding
        )

    def _create_deployment(self, project: str, deployment: Any):
        custom_objects_api = client.CustomObjectsApi()
        custom_objects_api.create_namespaced_custom_object("apps", "v1", project, "deployments", deployment)

    def _create_role(self, project: str, name: str, rules: List[RoleRule]):
        role: Role = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "Role",
            "metadata": {
                "name": name,
                "namespace": project,
            },
            "rules": rules,
        }

        custom_objects_api = client.CustomObjectsApi()
        custom_objects_api.create_namespaced_custom_object("rbac.authorization.k8s.io", "v1", project, "roles", role)

    def _create_role_binding(self, project: str, name: str, subjects: List[ObjectMeta], role_ref_name: str):
        role_binding: RoleBinding = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "RoleBinding",
            "metadata": {
                "name": name,
                "namespace": project,
            },
            "roleRef": {
                "apiGroup": "rbac.authorization.k8s.io",
                "kind": "Role",
                "name": role_ref_name,
            },
            "subjects": [],
        }

        for subject in subjects:
            role_binding["subjects"].append(
                {
                    "kind": "ServiceAccount",
                    "name": subject["name"],
                    "namespace": project,
                }
            )

        custom_objects_api = client.CustomObjectsApi()
        custom_objects_api.create_namespaced_custom_object(
            "rbac.authorization.k8s.io", "v1", project, "rolebindings", role_binding
        )

    def _create_service_account(self, project: str, name: str):
        service_account: ServiceAccount = {
            "apiVersion": "v1",
            "kind": "ServiceAccount",
            "metadata": {
                "name": "nfs-client-provisioner",
                "namespace": project,
            },
        }

        core_v1_api = client.CoreV1Api()
        core_v1_api.create_namespaced_service_account(project, service_account)

    def _create_storage_class(self, name: str, provisioner: str, parameters: Dict[str, str]):
        storage_class = {
            "apiVersion": "storage.k8s.io/v1",
            "kind": "StorageClass",
            "metadata": {
                "name": "managed-nfs-storage",
            },
            "provisioner": "k8s-sigs.io/nfs-subdir-external-provisioner",
        }

        storage_class["parameters"] = parameters

        custom_objects_api = client.CustomObjectsApi()
        custom_objects_api.create_cluster_custom_object("storage.k8s.io", "v1", "storageclasses", storage_class)

    def _custom_object_exists(self, name: str, kind_metadata: KindMetadata) -> bool:
        custom_objects_api = client.CustomObjectsApi()
        result = True

        try:
            custom_objects_api.get_cluster_custom_object(
                kind_metadata.group, kind_metadata.version, kind_metadata.plural, name
            )
        except client.ApiException as exception:
            if exception.status == 404:
                result = False
            else:
                raise exception

        return result

    def _get_credentials(self) -> GlobalPullSecretData:
        core_v1_api = client.CoreV1Api()
        core_v1_api_result: Any = core_v1_api.read_namespaced_secret("pull-secret", "openshift-config")

        return GlobalPullSecretData(core_v1_api_result.data)

    def _namespaced_custom_object_exists(self, project: str, name: str, kind_metadata: KindMetadata) -> bool:
        custom_objects_api = client.CustomObjectsApi()
        result = True

        try:
            custom_objects_api.get_namespaced_custom_object(
                kind_metadata.group, kind_metadata.version, project, kind_metadata.plural, name
            )
        except client.ApiException as exception:
            if exception.status == 404:
                result = False
            else:
                raise exception

        return result

    def _patch_credentials(self, global_pull_secret_data: GlobalPullSecretData):
        core_v1_api = client.CoreV1Api()
        core_v1_api.patch_namespaced_secret("pull-secret", "openshift-config", global_pull_secret_data.get_json_patch())

    def _service_account_exists(self, project: str, name: str) -> bool:
        core_v1_api = client.CoreV1Api()
        result = True

        try:
            core_v1_api.read_namespaced_service_account(name, project)
        except client.ApiException as exception:
            if exception.status == 404:
                result = False
            else:
                raise exception

        return result

    def _set_kube_config(self):
        """Sets the Kubernetes configuration of the Kubernetes Python client"""

        config.load_kube_config_from_dict(
            {
                "clusters": [
                    {
                        "cluster": {
                            "insecure-skip-tls-verify": self._credentials.insecure_skip_tls_verify,
                            "server": self._credentials.server,
                        },
                        "name": "cluster",
                    }
                ],
                "contexts": [
                    {
                        "context": {
                            "cluster": "cluster",
                            "user": "user",
                        },
                        "name": "context",
                    }
                ],
                "current-context": "context",
                "users": [
                    {
                        "name": "user",
                        "user": {
                            "token": self._credentials.get_access_token(),
                        },
                    }
                ],
            }
        )
